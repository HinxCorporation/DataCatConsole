import argparse as aps
import cmd2 as cmd
from cmd2 import with_argparser
from tabulate import tabulate
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
