import json
import os
import time

import DlistWorker.utils as util
from DlistWorker import dao
from DlistWorker.Tools.Logging import Log
from DlistWorker.config import DwConfig


class DWorker:
    """
    Dlist worker
    """

    def __init__(self, folder: str):
        DwConfig()
        self.dlist_folder: str = folder
        self.cnr: dao.database_connector = dao.get_connector()
        self.sleep_time: int = DwConfig.get_loop_sleep_duration()
        Log()

    def run(self):
        Log.logger.info('开始处理数据')
        try:
            cnx = self.cnr.connect()
            Log.logger.info('数据链接准备完成')
            cursor = cnx.cursor()
        except Exception as e:
            Log.logger.warning('链接数据库失败, 程序提前结束')
            Log.logger.exception(e)
            return

        life_circle = 0
        while True:
            life_circle += 1
            Log.logger.info(f'正在进行第{life_circle}次生命循环')
            try:
                self.loop(cnx, cursor)
            except Exception as e:
                Log.logger.error("由于一些问题, 循环过程发生了错误 ..")
                Log.logger.exception(e)

            Log.logger.info(f'...休息{self.sleep_time},程序将继续执行')
            time.sleep(self.sleep_time)

    def loop(self, cnx, crx):
        su, nextfile = self.get_next_dlist()
        if su:
            if nextfile is not None and os.path.exists(nextfile):
                with open(nextfile, 'r') as file:
                    for line in file.readlines():
                        self.try_process(line, crx)
                    cnx.commit()
                os.rename(nextfile, nextfile + ".done")
            else:
                Log.logger.error(f'程序似乎回告了正常的待处理文件({nextfile}),但是本地缺无法方位该dlist')
        else:
            Log.logger.info('已经没有内容需要处理啦,great..')

    def get_next_dlist(self):
        files = []
        for entry in os.scandir(self.dlist_folder):
            if entry.is_file() and entry.path.endswith('.dlist'):
                files.append(entry.path)
        orders = [[util.get_is_rebuilds(file), util.get_time_index(file), file] for file in files]

        rebuilds = []
        hocks = []
        for order in orders:
            if order[0] == 'rebuild':
                rebuilds.append(order)
            else:
                hocks.append(order)

        # 返回最新的rebuild
        # order = cmd , time , file
        if len(rebuilds) > 0:
            Log.logger.info(f'找到{len(rebuilds)}个需要rebuild的指令')
            check_order = DWorker.get_oldest_order(rebuilds)
            return True, check_order[2]
        elif len(hocks) > 0:
            Log.logger.info(f'找到{len(hocks)}个需要update的指令')
            check_order = DWorker.get_oldest_order(hocks)
            return True, check_order[2]
        return False, ''

    @staticmethod
    def try_process(line: str, crx):
        """
        处理每一行指令
        :param line:
        :param crx:
        :return:
        """
        su, dat = DWorker.parse_json(line)
        if su:
            path = dat["path"]
            DWorker.get_processor(dat['op'], dat['is_file']).process(path, crx)
        else:
            Log.logger.error(f'未知的指令或者数据格式不正确, 无法处理 .. {line}')
        pass

    @staticmethod
    def get_processor(operate, is_file):
        if is_file:
            if operate == 'update':
                return dao.process_file_update
            else:
                return dao.process_file_insert
        else:
            if operate == 'update':
                return dao.process_folder_update
            else:
                return dao.process_folder_insert

    @staticmethod
    def parse_json(json_string):
        try:
            data = json.loads(json_string)
            return True, data
        except json.JSONDecodeError:
            return False, None

    @staticmethod
    def get_oldest_order(orders):
        """
        比较时间, 返回列表中最久的内容,
        :param orders:
        :return:
        """
        o_len = len(orders)
        if o_len == 0:
            Log.logger.error("数组为空, 这是不正确的")
            return None
        # order = cmd , time , file
        oldest_order = orders[0]
        latest_time: int = oldest_order[1]
        for order in orders:
            if order[1] < latest_time:
                oldest_order = order
                latest_time: int = oldest_order[1]
        return oldest_order

#
# if __name__ == '__mian__':
#     print('begin test program')
#     worker = DWorker("../dlist")
#     worker.run()
