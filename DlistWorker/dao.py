import os.path
import sqlite3

import mysql.connector

from DlistWorker.config import DwConfig as conf


class database_connector:

    def __init__(self):
        self.name = ''
        self.type = conf.get_db_type()

    def connect(self):
        """
        Connect to the database (based on conf)
        """
        if self.type == 'sqlite':
            sqlite_file = conf.get_sqlite_destination()
            if not sqlite_file:
                return None
            if not os.path.exists(sqlite_file):
                open(sqlite_file, 'w').close()
            return sqlite3.connect(sqlite_file)
        elif self.type == 'mysql':
            usr = conf.get_db_user()
            pwd = conf.get_db_pwd()
            host = conf.get_db_host()
            port = conf.get_db_port()
            db = conf.get_db_database()
            return mysql.connector.connect(
                host=host,
                port=port,
                user=usr,
                password=pwd,
                database=db
            )
        else:
            return None

    def close_connect(self):
        print(self.name)


def get_connector() -> database_connector:
    return database_connector()


class process_folder_update:
    @staticmethod
    def process(path, crx):
        print(f'更新 - 文件夹:{path}')
        pass


class process_folder_insert:
    @staticmethod
    def process(path, crx):
        print(f'插入 - 文件夹:{path}')
        pass


class process_file_update:
    @staticmethod
    def process(path, crx):
        print(f'更新 - 文件:{path}')
        pass


class process_file_insert:
    @staticmethod
    def process(path, crx):
        print(f'插入 - 文件:{path}')
        pass
