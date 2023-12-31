import datetime
import hashlib
import os
import string

from tqdm import tqdm
from unidecode import unidecode

import Config.config
import DcConn.msqlutil
from Config import config
from PyDataCat import ConfigLo as dConf
from PyDataCat import querys

# output dirs for db
save_location = 'outputs'
# folder to counter
counted_folder = {}
# table name prefix
db_prefix = Config.config.get_table_prefix()
# create or read a db config.
my_config = dConf.ConfigSQLITE('config.db')


def run(recount=True):
    cnx = DcConn.msqlutil.create_conn()
    if not DcConn.msqlutil.check_connection(cnx):
        print("mysql connection fail, can not continue process")
        pass
    else:
        folders = collect_folders()
        print(f'read files {len(folders)} , ready to begin process')
        for folder in folders:
            rebuild_index_for_folder(folder, cnx, recount)
    cnx.close()
    print("All job is done.")


def rebuild_index_for_folder(full_path, cnx, recount=True):
    """
    create records to database
    :type cnx:
    :param full_path:
    :param recount:
    :return:
    """

    file_count = 0
    folder_count = 0
    if recount:
        tqs = tqdm(unit=' file', desc=f'Collecting files from {full_path}', total=0, unit_scale=True, unit_divisor=1000)
        file_count, folder_count = count_files(full_path, tqs)
        tqs.close()

    totals = file_count + folder_count
    is_large_collection = file_count > config.get_max_count_of_db_part() * 3

    print(f'begin processing {file_count} files and {folder_count} folders, is Large DB ? {is_large_collection}')

    if is_large_collection:
        subfolders = []
        for entry in os.scandir(full_path):
            if entry.is_dir():
                subfolders.append(entry.path)
        for subfolder in subfolders:
            rebuild_index_for_folder(subfolder, cnx)
        hi_create_db_for_folder_not_travel(full_path, cnx)
    else:
        hi_create_db_for_folder(full_path, cnx, totals)
        print(f'finished insert {totals} records')


def count_files(folder, tqs):
    """
    count files from a folder
    :param tqs:
    :param folder:
    :return:
    """
    if counted_folder.get(folder) is not None:
        return counted_folder.get(folder)
    total_files = 0
    total_folders = 1
    for entry in os.scandir(folder):
        tqs.update(1)
        if entry.is_file():
            total_files += 1
        else:
            f, d = count_files(entry.path, tqs)
            total_files += f
            total_folders += d
    result = total_files, total_folders
    counted_folder[folder] = result
    return result


def hi_create_db_for_folder_not_travel(full_path, cnx):
    """
    insert db but do not travel
    :param full_path:
    :param cnx:
    :return:
    """
    print(f'begin processing folder {full_path} , top only , pls wait ...')
    table_name = get_table_name(full_path)
    crs = cnx.cursor()
    tmp_table_name, insert_query, limited = ensure_table(table_name, cnx, crs)
    totals = 0
    tqs = tqdm(unit='queries', desc=f'Insert rec into db [{table_name}]',
               total=totals, unit_scale=True, unit_divisor=1000)

    count = 0
    for entry in os.scandir(full_path):
        if entry.is_file():
            insert(entry.path, crs, insert_query)
            count += 1
            tqs.update(1)
            if count % limited == 0:
                cnx.commit()
    tqs.close()
    cnx.commit()
    crs.execute(querys.drop_if_exist(table_name))
    cnx.commit()
    crs.execute(querys.rename(tmp_table_name, table_name))
    cnx.commit()
    crs.close()


def connect_table2path(dbname, full_path, desc):
    """链接两个数值"""
    my_config.set_value(full_path, dbname, desc)


def hi_create_db_for_folder(full_path, cnx, totals):
    """
    insert all data into a db from full path with total count
    :param full_path:
    :param cnx:
    :param totals:
    :return:
    """
    print(f'begin processing folder {full_path} , pls wait ...')
    table_name = get_table_name(full_path)
    crs = cnx.cursor()
    tmp_table_name, insert_query, limited = ensure_table(table_name, cnx, crs)
    tqs = tqdm(unit='queries', desc=f'Insert rec into db [{table_name}]',
               total=totals, unit_scale=True, unit_divisor=1000)

    travel(full_path, cnx, crs, insert_query, tqs, 0, limited)
    tqs.close()
    cnx.commit()
    crs.execute(querys.drop_if_exist(table_name))
    cnx.commit()
    crs.execute(querys.rename(tmp_table_name, table_name))
    cnx.commit()
    crs.close()


def insert(file_path, crs, insert_query):
    """
    crs do insert with create data from file path
    :param file_path:
    :param crs:
    :param insert_query:
    :return:
    """
    f_data = collect_file_data(file_path)
    try:
        crs.execute(insert_query, f_data)
    except Exception as e:
        print(f"execute error , \n{insert_query % f_data}\npls check\n{e}\n")
        raise Exception('exec query error.')


def travel(folder, cnx, crs, insert_query, tqs, counter, limited: int = 1000):
    """
    travel folder and deliver options
    :param folder:
    :param cnx:
    :param crs:
    :param insert_query:
    :param tqs:
    :param counter:
    :param limited:
    :return:
    """
    for entry in os.scandir(folder):
        tqs.update(1)
        if entry.is_file():
            insert(entry.path, crs, insert_query)
            counter += 1
            if counter % limited == 0:
                cnx.commit()
        else:
            counter = travel(entry.path, cnx, crs, insert_query, tqs, counter, limited)
    return counter


def ensure_table(table_name, cnx, crs):
    """
    ensure temp database end return a temp name
    :param table_name:
    :param cnx:
    :param crs:
    :return:
    """
    # make sure table is exist
    tmp_table_name = f'{table_name}_tmp'

    # drop old if exist tmp_table
    crs.execute(querys.drop_if_exist(tmp_table_name))
    cnx.commit()
    # create new if not exist
    create_tmp_query = querys.ensure_table_mysql(tmp_table_name)
    crs.execute(create_tmp_query)
    cnx.commit()

    # begin process
    insert_query = querys.insert_table_msql(tmp_table_name)
    limited = config.get_batch_size()
    return tmp_table_name, insert_query, limited


def get_table_name(path):
    """
    compute a table name from a given folder
    :param path:
    :return:
    """
    full_path = os.path.abspath(path)
    sha1 = hashlib.sha1()
    try:
        sha1.update(full_path.encode('utf-8'))
    except:
        try:
            sha1.update(full_path.encode('latin-1'))
        except:
            plain_str = trim_and_encode_utf8(full_path)
            sha1.update(plain_str)
    sha1_str = sha1.hexdigest()
    connect_table2path(sha1_str, full_path, 'database name with dir path')
    return db_prefix + sha1_str


def trim_and_encode_utf8(input_str):
    ascii_string = unidecode(input_str)
    utf8_string = ascii_string.encode('utf-8')
    return utf8_string


def collect_file_data(filepath):
    """
    collect file datas from a given file
    :param filepath:
    :return:
    """
    file_path = get_full_path(filepath)
    file_name, file_extension = os.path.splitext(os.path.basename(file_path))
    file_size = os.path.getsize(file_path)
    file_type = file_extension[1:] if file_extension else ""
    creation_time = datetime.datetime.fromtimestamp(os.path.getctime(file_path))
    access_time = datetime.datetime.fromtimestamp(os.path.getatime(file_path))

    try:
        modification_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
    except:
        # 如果获取修改时间失败则使用最早记录的时间
        modification_time = datetime.datetime.min
    data = (
        os.path.basename(filepath),  # name
        file_size,  # size
        file_type,  # file type
        os.path.abspath(filepath),  # path
        creation_time,  # creation time
        modification_time,  # modify time
        access_time,  # access time
        '',  # permissions
        '',  # owner
        '',  # last access
        file_to_storage_id(filepath),  # storage id
        '',  # md5
    )
    return data


def file_to_storage_id(file_path):
    """
    从文件计算文件的storage_id
    :param file_path:
    :return:
    """
    try:
        abs_path = os.path.abspath(file_path)
        file_size = os.path.getsize(abs_path)
        modification_time = datetime.datetime.fromtimestamp(os.path.getmtime(abs_path))
        context = f"{abs_path}|{file_size}|{modification_time}"
        return hashlib.md5(context.encode(encoding='utf-8')).hexdigest()
    except:
        return ''


def get_full_path(file_path: str) -> str:
    """
    获取绝对路径
    :return:
    :param file_path:
    :return:
    """
    # Check if the path is already a full path
    if os.path.isabs(file_path):
        return file_path
    # Get the current working directory
    current_dir = os.getcwd()
    # Join the current directory with the file name to get the full path
    full_path = os.path.abspath(os.path.join(current_dir, file_path))
    return full_path


def folder_to_db_name(folder: string):
    """
    文件名到DB文件名
    :param folder:
    :return:
    """
    md5 = hashlib.md5()
    # folder = folder.replace('\udcbf', '')
    md5.update(folder.encode('utf-16'))
    save_folder = os.path.join(os.getcwd(), save_location)
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)
    return f'{save_location}/{md5.hexdigest()}_{os.path.basename(folder)}.db'


def collect_folders():
    """
    from config read folder list to be set up
    :return:
    """
    configFile = "Config/folder_paths.txt"
    with open(configFile, 'r', encoding='utf-8') as ffile:
        lines = ffile.readlines()
    folders = []

    def test_append(test_dir):
        _su, _dir = get_abs_folder(test_dir)
        if _su:
            folders.append(_dir)

    for line in lines:
        if line.startswith('#'):
            # 注释的内容
            continue
        elif line.startswith('&'):
            tmpdir = line[1:]
            su, j_dir = get_abs_folder(tmpdir)
            if su:
                for entry in os.scandir(j_dir):
                    if entry.is_dir():
                        test_append(entry.path)
        else:
            test_append(line)
    return folders


def get_abs_folder(folder_path):
    """
    获取指定路径的绝对位置
    :param folder_path:
    :return:
    """
    # 处理相对路径、绝对路径和环境变量
    folder_path = folder_path.strip()

    if folder_path is None or folder_path == '':
        return False, ''

    processed_path = os.path.expandvars(os.path.expanduser(folder_path))

    if not os.path.isabs(processed_path):
        processed_path = os.path.abspath(processed_path)
    try:
        # 检测路径是否可读
        if os.path.isdir(processed_path) and os.access(processed_path, os.R_OK):
            return True, processed_path
        else:
            return False, processed_path
    except Exception as e:
        return False, e.args


def encode_string_with_replacement(plain_str):
    """
    将不能解释的字符转换成 **
    :param plain_str:
    :return:
    """
    # Replace unsupported characters with "**"
    cleaned_string = plain_str.encode("utf-8", "replace").decode("utf-8")
    # Encode the cleaned string
    encoded_string = cleaned_string.encode("utf-8")
    return encoded_string


def is_null_or_whitespace(input_str: str):
    return input_str is None or input_str.strip() == ''


def mark_error_file(file):
    file = encode_string_with_replacement(file)
    try:
        with open('error_files.txt', 'a', encoding='utf-16') as f:
            f.write(f'{file} \n')
    except:
        print(f'error with:{file}')
