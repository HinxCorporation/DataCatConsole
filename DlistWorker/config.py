from configparser import RawConfigParser


class DwConfig:
    config_file = 'Config/DWorker.config.ini'
    config = None
    my_config = None

    def __init__(self):
        DwConfig.my_config = DwConfig.get_config()

    @classmethod
    def get_config(cls):
        if cls.config is None:
            cls.config = RawConfigParser()
            cls.config.read(cls.config_file)
        return cls.config

    @classmethod
    def create_block_if_missing(cls, block):
        if block not in DwConfig.my_config:
            DwConfig.my_config[block] = {}
            cls.create_properties(block)

    @classmethod
    def create_properties(cls, block):
        for key in DwConfig.my_config[block]:
            setattr(cls, f"get_{block}_{key}", cls.create_getter(block, key))

    @classmethod
    def create_getter(cls, block, key):
        return property(lambda self: DwConfig.my_config.get(block, key))

    def __getattr__(self, attr):
        block, key = attr.split("_", 1)
        self.create_block_if_missing(block)
        return getattr(self, attr)

    @staticmethod
    def get_loop_sleep_duration():
        return int(DwConfig.my_config.get("Program", "Sleep"))

    @staticmethod
    def get_db_type():
        return DwConfig.my_config.get('DB', 'type')

    @staticmethod
    def get_sqlite_destination():
        return DwConfig.my_config.get('SQLITE', 'db_file')

    @staticmethod
    def get_db_user():
        return DwConfig.my_config.get('MYSQL', 'user')

    @staticmethod
    def get_db_pwd():
        return DwConfig.my_config.get('MYSQL', 'passwd')

    @staticmethod
    def get_db_host():
        return DwConfig.my_config.get('MYSQL', 'host')

    @staticmethod
    def get_db_port():
        return DwConfig.my_config.get('MYSQL', 'port')

    @staticmethod
    def get_db_database():
        return DwConfig.my_config.get('MYSQL', 'db')
