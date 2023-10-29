# tips = """
# 你应该不需要阅读此文件 , 此文件无任何参考意义, 后续将会放弃维护 ;
# this file is not deserve to read and it will stop upgrade in the future.
# """

create_table: str = '''
        CREATE TABLE IF NOT EXISTS "files" (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name TEXT,
            file_size NUMERIC,
            file_type TEXT,
            file_path TEXT,
            creation_date DATETIME,
            modification_date DATETIME,
            access_date DATETIME,
            file_permissions TEXT,
            owner TEXT,
            last_accessed_by TEXT,
            storage_id TEXT,
            md5 TEXT
        )
    '''

insert_table = '''
                           INSERT INTO "files" (
                               file_name,
                               file_size,
                               file_type,
                               file_path,
                               creation_date,
                               modification_date,
                               access_date,
                               file_permissions,
                               owner,
                               last_accessed_by,
                               storage_id,
                               md5
                           )
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                       '''

query_table = '''
                            SELECT 
                               file_name,
                               file_size,
                               file_type,
                               file_path,
                               creation_date,
                               modification_date,
                               access_date,
                               file_permissions,
                               owner,
                               last_accessed_by,
                               storage_id,
                               md5
                            FROM files LIMIT ? OFFSET ?;
    '''


def insert_table_msql(table_name):
    return f"""
    INSERT INTO `{table_name}` (
    file_name, 
    file_size, 
    file_type, 
    file_path, 
    creation_date, 
    modification_date, 
    access_date, 
    file_permissions, 
    owner, 
    last_accessed_by, 
    storage_id, 
    md5
    )
     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)    
    """


def drop_if_exist(table_name):
    return f"DROP TABLE IF EXISTS `{table_name}`; "


def rename(table, to_table):
    return f"RENAME TABLE `{table}` TO `{to_table}`;"


def ensure_table_mysql(table_name):
    return f'''
    CREATE TABLE IF NOT EXISTS `{table_name}` (
  `id` int NOT NULL AUTO_INCREMENT,
  `file_name` text,
  `file_size` bigint DEFAULT NULL,
  `file_type` text,
  `file_path` text,
  `creation_date` datetime DEFAULT NULL,
  `modification_date` datetime DEFAULT NULL,
  `access_date` datetime DEFAULT NULL,
  `file_permissions` text,
  `owner` text,
  `last_accessed_by` text,
  `storage_id` text,
  `md5` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
    '''
