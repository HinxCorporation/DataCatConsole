import configparser

cfg = configparser.ConfigParser()
cfg.read('Config/config.ini')


def get_db_dir():
    return cfg.get('dbs', 'path')


def get_tset_file():
    return cfg.get('dbs', 'test_file')


def get_mysql_host():
    return cfg.get('mysql', 'host')


def get_mysql_port():
    return cfg.get('mysql', 'port')


def get_mysql_user():
    return cfg.get('mysql', 'user')


def get_mysql_pwd():
    return cfg.get('mysql', 'passwd')


def get_mysql_database():
    return cfg.get('mysql', 'database')


def get_separate_db():
    return cfg.getboolean('Global', 'Separate_DB')


def get_max_count_of_db_part():
    """max size of a part of single table"""
    return cfg.getint('Global', 'MaxOfPart')


def get_table_prefix():
    """table name prefix"""
    return cfg.get('Global', 'DC_AUTO_')


def get_batch_size():
    """batch size"""
    return cfg.getint('Global', 'BatchSize')
