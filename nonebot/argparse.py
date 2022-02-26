from argparse import ArgumentParser

from .command import CommandSession


class ParserExit(RuntimeError):
    """INTERNAL API"""

    def __init__(self, status=0, message=None):
        self.status = status
        self.message = message


class ArgumentParser(ArgumentParser):
    """
    继承自 `argparse.ArgumentParser` 类，修改部分函数实现使其适用于命令型聊天机器人。

    此类可用于命令参数的解析。基本用法和 Python 内置的 `argparse.ArgumentParser` 类一致，下面主要列出与 Python 原生含义和行为不同的属性和方法。

    参数:
        session: 当前需要解析参数的命令会话，用于解析失败或遇到 `--help` 时发送提示消息
        usage: 命令的使用帮助，在参数为空或遇到 `--help` 时发送
        kwargs: 和 Python `argparse.ArgumentParser` 类一致

    用法:
        ```python
        USAGE = r'''
        创建计划任务

        使用方法：
        XXXXXX
        '''.strip()

        @on_command('schedule', shell_like=True)
        async def _(session: CommandSession):
            parser = ArgumentParser(session=session, usage=USAGE)
            parser.add_argument('-S', '--second')
            parser.add_argument('-M', '--minute')
            parser.add_argument('-H', '--hour')
            parser.add_argument('-d', '--day')
            parser.add_argument('-m', '--month')
            parser.add_argument('-w', '--day-of-week')
            parser.add_argument('-f', '--force', action='store_true', default=False)
            parser.add_argument('-v', '--verbose', action='store_true', default=False)
            parser.add_argument('--name', required=True)
            parser.add_argument('commands', nargs='+')

            args = parser.parse_args(session.argv)
            name = args.name
            # ...
        ```
    """

    def __init__(self, *args, **kwargs):
        self.session = kwargs.pop('session', None)
        super().__init__(*args, **kwargs)

    def _session_finish(self, message):
        if self.session and isinstance(self.session, CommandSession):
            self.session.finish(message)

    def _print_message(self, message, file=None):
        # do nothing
        pass

    def exit(self, status=0, message=None):
        raise ParserExit(status=status, message=message)

    def parse_args(self, args=None, namespace=None):
        """
        解析参数。

        Python 原生的「打印到控制台」行为变为「发送消息到用户」，「退出程序」变为「结束当前命令会话」。
        """
        try:
            return super().parse_args(args=args, namespace=namespace)
        except ParserExit as e:
            if e.status == 0:
                # --help
                self._session_finish(self.usage or self.format_help())
            else:
                self._session_finish('参数不足或不正确，请使用 --help 参数查询使用帮助')


__all__ = [
    'ArgumentParser',
]

__autodoc__ = {
    "ParserExit": False,
    "ArgumentParser.exit": False
}
