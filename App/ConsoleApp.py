import argparse as aps

import cmd2 as cmd
from cmd2 import with_argparser
from tabulate import tabulate
from tqdm import tqdm

import DcConn
import DcConn.msqlutil
import DlistWorker
from PyDataCat import RebuildUtil


def create_arg_parser():
    parser = aps.ArgumentParser()
    parser.add_argument('arg_name', type=str, help='Help message for this argument')
    return parser


class ConsoleApp(cmd.Cmd):
    """
    Application center
    """

    # CLI prompt
    @property
    def prompt(self) -> str:
        return "DataCat CLI>> "

    def __init__(self):
        """
        Console Construction
        """
        # ignore cmds on default screen
        self.ignores_args: list[str] = [
            'alias', 'help', 'set', 'shell', 'edit',
            'eof', 'history', 'macro', 'run_pyscript',
            'cls', 'clear',
            'run_script', 'shortcuts']
        self.rebuild_count = True
        # Add the argument parser
        self.arg_parser = create_arg_parser()
        super().__init__()

    # noinspection PyArgumentList
    def do_exhelp(self, args: object):
        """查看原版help (使用所有原版arg)"""
        super().do_help(args)

    def do_help(self, args) -> None:
        """列举所有可用的方法"""

        # if args is not None:
        #     super().do_help(args)
        #     return

        commands = [cmdstr for cmdstr in self.get_all_commands()
                    if not cmdstr.startswith("_")
                    and cmdstr not in self.ignores_args]
        commands_with_statements = []
        for cmdstr in commands:
            statement = '--none--'
            try:
                method_name = 'do_' + cmdstr.strip()
                method = getattr(self, method_name)
                docstring = method.__doc__
                statement = docstring
            except:
                pass
            commands_with_statements.append([cmdstr, statement])
        # sort result by cmd name
        commands_with_statements.sort(key=lambda x: x[0])
        header = ['可用的指令', '描述']
        table = tabulate(commands_with_statements, header, tablefmt="fancy_grid")
        print(table)

    def do_cls(self):
        """Clear the screen"""
        self.poutput("\033[2J\033[H")

    def do_clear(self):
        """clear the screen"""
        self.do_cls()

    rebuild_arg_parser = aps.ArgumentParser()

    @with_argparser(rebuild_arg_parser)
    def do_rebuild(self, line):
        """
        从config中读取folders,并且为他们重新构建数据库,插入到指定的sql中.
        需要配置分表大小,若文件夹超过大小*3,则按照配置的大小进行分表处理
        ---默认规则为继续递归下级目录创建子数据库
        """
        RebuildUtil.run(self.rebuild_count)

    @with_argparser(aps.ArgumentParser())
    def do_ls_rebuild(self, line):
        """
        列举配置中可以读取文件夹列表 (用于检查列表)
        :return:
        """
        lst = RebuildUtil.collect_folders()
        sheet = [['dir', _dir, RebuildUtil.get_table_name(_dir)] for _dir in lst]
        headers = ["类型", "路径", "数据库名"]
        print(tabulate(sheet, headers, tablefmt="fancy_grid"))

    @with_argparser(aps.ArgumentParser())
    def do_ls_rules(self, line):
        """
        查阅跳过的文件夹规则
        :return:
        """
        rule_file = 'Config/skip_rules.txt'
        with open(rule_file, 'r') as file:
            lines = file.readlines()
        print('rule=\t'.join(lines))

    @with_argparser(aps.ArgumentParser())
    def do_test_count(self, line):
        """
        尝试列举文件列表并且进行计数
        :param line:
        :return:
        """
        tqs = tqdm(unit=' file',
                   desc=f'查找所有文件中 (可能会消耗大量时间,请稍后) ',
                   total=0, unit_scale=True, unit_divisor=1000)
        lst = RebuildUtil.collect_folders()
        result = []
        for read_dir in lst:
            s, d = RebuildUtil.count_files(read_dir, tqs)
            result.append([read_dir, f'{s + d} files'])
        tqs.close()
        header = ['位置', '文件总数']
        table = tabulate(result, header, tablefmt="fancy_grid")
        print(table)

    @with_argparser(aps.ArgumentParser())
    def do_test_dlist(self,args):
        """
        测试dlist工作者功能
        :param args:
        :return:
        """
        dlist_folder = 'dlist'
        woe = DlistWorker.DWorker(dlist_folder)
        woe.run()

    @with_argparser(aps.ArgumentParser())
    def do_test_conn(self, line):
        """
        测试mysql是否可以正常链接
        :param line:
        :return:
        """
        cnx = DcConn.msqlutil.create_conn()
        if not DcConn.msqlutil.check_connection(cnx):
            print("MySql 链接失败, 请检查配置")
            pass
        else:
            print("似乎一切都在正常工作(mysql) (*^▽^*)")
