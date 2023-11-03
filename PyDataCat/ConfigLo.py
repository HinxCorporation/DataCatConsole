import os.path
import sqlite3


class ConfigSQLITE:
    def __init__(self, configfile=""):
        self.name = 'config'
        self.table_name = 'configs'
        self.query_select_value = f'SELECT value FROM {self.table_name} WHERE key = ?'
        self.query_select = f'SELECT key FROM {self.table_name} WHERE key = ?'
        self.query_update = f'UPDATE {self.table_name} SET value = ? WHERE key = ?'
        self.query_insert = f'INSERT INTO {self.table_name} (key, value, desc) VALUES (?, ?, ?)'

        if not configfile.endswith('.db'):
            configfile = configfile + '.db'
        self.config_file = configfile
        if not os.path.isfile(self.config_file):
            open(self.config_file, 'a').close()
        self.ensure_tables()

    def ensure_tables(self):
        query = f'''
            CREATE TABLE IF NOT EXISTS `{self.table_name}` (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE,
                value TEXT,
                type TEXT,
                desc TEXT
            )
        '''
        with sqlite3.connect(self.config_file) as cnx:
            cursor = cnx.cursor()
            cursor.execute(query)
            cnx.commit()

    def get_value(self, key) -> str:
        with sqlite3.connect(self.config_file) as cnx:
            cursor = cnx.cursor()
            cursor.execute(self.query_select_value, (key,))
            result = cursor.fetchone()
            if result is not None:
                return result[0]
            return ''

    def set_value(self, key, value, desc='') -> bool:
        with sqlite3.connect(self.config_file) as cnx:
            cursor = cnx.cursor()
            cursor.execute(self.query_select, (key,))
            exists = cursor.fetchone() is not None

            if exists:
                cursor.execute(self.query_update, (value, key))
                cnx.commit()
                return cursor.rowcount > 0
            else:
                cursor.execute(self.query_insert, (key, value, desc))
                cnx.commit()
                return cursor.lastrowid is not None

    def flush_records(self, records) -> bool:
        """insert values as config objects"""
        with sqlite3.connect(self.config_file) as cnx:
            cursor = cnx.cursor()
            try:
                cursor.executemany(self.query_insert, [(obj.key, obj.value, obj.desc) for obj in records])
                cnx.commit()
                return True
            except sqlite3.Error as e:
                print(f"An error occurred while flushing records: {e}")
                return False

    def flush_records_array(self, array):
        """insert values as array"""
        with sqlite3.connect(self.config_file) as cnx:
            cursor = cnx.cursor()
            try:
                cursor.executemany(self.query_insert, array)
                cnx.commit()
                return True
            except sqlite3.Error as e:
                print(f"An error occurred while flushing records: {e}")
                return False


class ConfigObject:
    def __init__(self, key, value, desc):
        self.key = key
        self.value = value
        self.desc = desc


if __name__ == '__main__':
    ConfigSQLITE('../config.db')
