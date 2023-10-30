import os.path
import tqdm
import Config.config as config
from DcConn import msqlutil
from DcConn import sql3util
from PyDataCat import querys


def file_to_table_name(file):
    """
    从文件名中提取数据库名称
    :param file:
    :return:
    """
    pure_name = os.path.basename(file)
    if '.' in pure_name:
        file_name_without_extension = pure_name.rsplit('.', 1)[0]
    else:
        file_name_without_extension = pure_name
    return file_name_without_extension


def insert_items_parts(total, max_per_section, ori_db_name, crs_1, crs_2, cnx, limited, query_sel):
    """
    分区加入数据库
    :param total:
    :param max_per_section:
    :param ori_db_name:
    :param crs_1:
    :param crs_2:
    :param cnx:
    :param limited:
    :param query_sel:
    :return:
    """
    offset = 0
    part_count = 1
    working = True
    target_db = ''
    if total > max_per_section:
        target_db = f'{ori_db_name}_part_{part_count}'
        part_count = part_count + 1
    while working:
        working, offset = begin_sync_dates(
            crs_1, crs_2, cnx,
            target_db, limited, query_sel, offset, max_per_section)
        if working:
            target_db = f'{ori_db_name}_part_{part_count}'
            part_count = part_count + 1


def insert_items(
        crs_1,
        crs_2,
        cnx,
        target_db,
        limited,
        query_sel,
        offset,
        total
):
    """
    一次性加入所有内容
    :param total:
    :param crs_1:
    :param crs_2:
    :param cnx:
    :param target_db:
    :param limited:
    :param query_sel:
    :param offset:
    :return:
    """
    insert_query = querys.insert_table_msql(target_db)
    crs_1.execute(query_sel, (limited, offset))
    record_batches = crs_1.fetchmany(limited)
    crs_2.execute(querys.ensure_table_mysql(table_name=target_db))
    progress = tqdm.tqdm(total=total, unit_scale=True, unit_divisor=1000, unit=' queries',
                         desc=f'updating {target_db} ')

    while record_batches:
        crs_2.executemany(insert_query, record_batches)
        cnx.commit()
        progress.update(len(record_batches))
        offset = offset + limited
        crs_1.execute(query_sel, (limited, offset))
        record_batches = crs_1.fetchmany(limited)
    progress.close()


def begin_sync_dates(
        crs_1,
        crs_2,
        cnx,
        target_db,
        limited,
        query_sel,
        offset,
        max_per_section):
    """
    分步骤同步数据
    :param crs_1:SQLITE3的Cursor
    :param crs_2:MYSQL的Cursor
    :param cnx:MYSQL的CONN
    :param target_db:目标数据库名称
    :param limited:batch的数量限制
    :param query_sel:从sqlite中选择数据的query
    :param offset:当前的偏移位置
    :param max_per_section:一份的最大容量.
    :return:
    """

    insert_query = querys.insert_table_msql(target_db)
    crs_1.execute(query_sel, (limited, offset))
    record_batches = crs_1.fetchmany(limited)
    crs_2.execute(querys.ensure_table_mysql(table_name=target_db))
    progress = tqdm.tqdm(
        total=max_per_section,
        unit_scale=True,
        unit_divisor=1000,
        unit=' queries',
        desc=f'updating {target_db} ')
    end_with = max_per_section + offset
    rich_max = False
    while record_batches:
        crs_2.executemany(insert_query, record_batches)
        cnx.commit()
        progress.update(len(record_batches))
        offset = offset + limited
        if offset > end_with:
            rich_max = True
            break
        crs_1.execute(query_sel, (limited, offset))
        record_batches = crs_1.fetchmany(limited)
    progress.close()
    return rich_max, offset


def query_total_items(crs_1):
    """
    查询并且返回表格中的所有数
    :param crs_1:
    :return:
    """
    crs_1.execute('select count(*) from files')
    total = crs_1.fetchone()[0]
    print(f'total :{total} items')
    return total


def test_insert(file):
    """
    测试插入所有sqlite数据到mysql
    :param file:
    :return:
    """
    cnx = msqlutil.create_conn()
    cnx_s3 = sql3util.read_cnx(file)
    crs_1 = cnx_s3.cursor()
    crs_2 = cnx.cursor()

    # read config from global
    separate = config.get_separate_db()
    max_per_section = config.get_max_count_of_db_part()
    limited = config.get_batch_size()
    offset = 0
    # init
    query_sel = querys.query_table
    ori_db_name = file_to_table_name(file)
    total = query_total_items(crs_1)

    if separate:
        insert_items_parts(total, max_per_section, ori_db_name, crs_1, crs_2, cnx, limited, query_sel)
    else:
        insert_items(crs_1, crs_2, cnx, ori_db_name, limited, query_sel, offset, total)

    # after work is done
    crs_1.close()
    crs_2.close()
    cnx_s3.close()
    cnx.close()
