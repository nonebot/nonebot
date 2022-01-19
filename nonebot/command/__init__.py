"""
快捷导入:

- `CommandGroup` -> {ref}`nonebot.command.group.CommandGroup`
"""
import re
import asyncio
import warnings
from datetime import datetime, timedelta
from functools import partial
from typing import (NoReturn, Tuple, Union, Iterable, Any, Optional, List, Dict,
                    Awaitable, Pattern, Type)

from aiocqhttp import Event as CQEvent
from aiocqhttp.message import Message

from nonebot import NoneBot
from nonebot.command.argfilter import ValidateError
from nonebot.helpers import context_id, send, render_expression
from nonebot.log import logger
from nonebot.session import BaseSession
from nonebot.typing import (CommandName_T, CommandArgs_T, CommandHandler_T,
                            Message_T, PermissionPolicy_T, State_T, Filter_T, Patterns_T)
from nonebot.permission import check_permission

# key: context id
# value: CommandSession object
_sessions = {}  # type: Dict[str, "CommandSession"]


class CommandInterrupt(Exception):
    """INTERNAL API"""
    pass


class _YieldException(CommandInterrupt):
    """
    Raised by command.run(), session indicating that the waiting session
    will resume and current execution path should return immediately.
    """
    pass


class _PauseException(CommandInterrupt):
    """
    Raised by session.pause() indicating that the command session
    should be paused to ask the user for some arguments.
    """
    pass


class _FinishException(CommandInterrupt):
    """
    Raised by session.finish() indicating that the command session
    should be stopped and removed.
    """

    def __init__(self, result: bool = True):
        """
        :param result: succeeded to call the command
        """
        self.result = result


class SwitchException(CommandInterrupt):
    """
    INTERNAL API

    Raised by session.switch() indicating that the command session
    should be stopped and replaced with a new one (going through
    handle_message() again).

    Since the new message will go through handle_message() again,
    the later function should be notified. So this exception is
    intended to be propagated to handle_message().
    """

    def __init__(self, new_message: Message):
        """
        :param new_message: new message which should be placed in event
        """
        self.new_message = new_message


class Command:
    """
    INTERNAL API

    Note ... (Ellipsis) is a valid value for field expire_timeout and run_timeout.
    However I cannot type it until Python 3.10. see bugs.python.org/issue41810.
    """
    __slots__ = ('name', 'func', 'only_to_me', 'privileged', 'args_parser_func',
                 'permission', 'expire_timeout', 'run_timeout', 'session_class')

    def __init__(self, *, name: CommandName_T, func: CommandHandler_T,
                 only_to_me: bool, privileged: bool,
                 permission: PermissionPolicy_T,
                 expire_timeout: Optional[timedelta],
                 run_timeout: Optional[timedelta],
                 session_class: Optional[Type['CommandSession']]):
        self.name = name
        self.func = func
        self.only_to_me = only_to_me
        self.privileged = privileged
        self.args_parser_func: Optional[CommandHandler_T] = None
        self.permission = permission  # includes EllipsisType
        self.expire_timeout = expire_timeout  # includes EllipsisType
        self.run_timeout = run_timeout  # includes EllipsisType
        self.session_class = session_class

    async def run(self,
                  session: 'CommandSession',
                  *,
                  check_perm: bool = True,
                  dry: bool = False) -> bool:
        """
        Run the command in a given session.

        :param session: CommandSession object
        :param check_perm: should check permission before running
        :param dry: just check any prerequisite, without actually running
        :return: the command is finished (or can be run, given dry == True)
        """
        has_perm = await self._check_perm(session) if check_perm else True
        if self.func and has_perm:
            if dry:
                return True

            if session.current_arg_filters is not None and \
                    session.current_key is not None:
                # argument-level filters are given, use them
                arg = session.current_arg
                config = session.bot.config
                for f in session.current_arg_filters:
                    try:
                        res = f(arg)
                        if isinstance(res, Awaitable):
                            res = await res
                        arg = res
                    except ValidateError as e:
                        # validation failed
                        if config.MAX_VALIDATION_FAILURES > 0:
                            # should check number of validation failures
                            session.state['__validation_failure_num'] = \
                                session.state.get(
                                    '__validation_failure_num', 0) + 1

                            if session.state['__validation_failure_num'] >= \
                                    config.MAX_VALIDATION_FAILURES:
                                # noinspection PyProtectedMember
                                session.finish(
                                    render_expression(
                                        config.
                                        TOO_MANY_VALIDATION_FAILURES_EXPRESSION
                                    ), **session._current_send_kwargs)

                        failure_message = e.message
                        if failure_message is None:
                            failure_message = render_expression(
                                config.DEFAULT_VALIDATION_FAILURE_EXPRESSION)
                        # noinspection PyProtectedMember
                        session.pause(failure_message,
                                      **session._current_send_kwargs)

                # passed all filters
                session.state[session.current_key] = arg
            else:
                # fallback to command-level args_parser_func
                if self.args_parser_func:
                    await self.args_parser_func(session)
                if session.current_key is not None and \
                        session.current_key not in session.state:
                    # args_parser_func didn't set state, here we set it
                    session.state[session.current_key] = session.current_arg
            if session.waiting:
                session._future.set_result(True)
                raise _YieldException()
            else:
                await self.func(session)
            return True
        return False

    async def _check_perm(self, session: 'CommandSession') -> bool:
        """
        Check if the session has sufficient permission to
        call the command.

        :param session: CommandSession object
        :return: the session has the permission
        """
        return await check_permission(session.bot, session.event,
            self.permission if self.permission is not ...
                else session.bot.config.DEFAULT_COMMAND_PERMISSION)

    def args_parser(self, parser_func: CommandHandler_T) -> CommandHandler_T:
        """
        Decorator to register a function as the arguments parser of
        the corresponding command.
        """
        self.args_parser_func = parser_func
        return parser_func

    def __repr__(self):
        return f'<Command, name={self.name.__repr__()}>'

    def __str__(self):
        return self.__repr__()


class CommandManager:
    """全局命令管理器。

    版本: 1.6.0+
    """
    _commands = {}  # type: Dict[CommandName_T, Command]
    _aliases = {}  # type: Dict[str, Command]
    _switches = {}  # type: Dict[Command, bool]
    _patterns = {}  # type: Dict[Pattern[str], Command]

    def __init__(self):
        self.commands = CommandManager._commands.copy()
        """命令字典。"""
        self.aliases = CommandManager._aliases.copy()
        """命令别名字典。"""
        self.switches = CommandManager._switches.copy()
        """命令开关状态字典。"""
        self.patterns = CommandManager._patterns.copy()
        """
        命令正则匹配字典。
        版本: 1.7.0+
        """

    @classmethod
    def add_command(cls, cmd_name: CommandName_T, cmd: Command) -> None:
        """注册一个 `Command` 对象。

        参数:
            cmd_name: 命令名称
            cmd: 命令对象

        用法:
            ```python
            cmd = Command(name, func, permission, only_to_me, privileged)
            CommandManager.add_command(name, cmd)
            ```
        """
        if cmd_name in cls._commands:
            warnings.warn(f"Command {cmd_name} already exists")
            return
        cls._switches[cmd] = True
        cls._commands[cmd_name] = cmd

    @classmethod
    def reload_command(cls, cmd_name: CommandName_T, cmd: Command) -> None:
        """更新一个已存在的命令。

        参数:
            cmd_name: 命令名词
            cmd: 命令对象

        用法:
            ```python
            cmd = Command(name, func, permission, only_to_me, privileged)
            CommandManager.reload_command(name, cmd)
            ```
        """
        if cmd_name not in cls._commands:
            warnings.warn(
                f"Command {cmd_name} does not exist. Please use add_command instead"
            )
            return

        cmd_ = cls._commands[cmd_name]
        if cmd_ in cls._switches:
            del cls._switches[cmd_]

        cls._switches[cmd] = True
        cls._commands[cmd_name] = cmd

    @classmethod
    def remove_command(cls, cmd_name: CommandName_T) -> bool:
        """移除一个已存在的命令。

        参数:
            cmd_name: 命令名称

        返回:
            bool: 是否成功移除命令

        用法:
            ```python
            CommandManager.remove_command(("test", ))
            ```
        """
        if cmd_name in cls._commands:
            cmd = cls._commands[cmd_name]
            for alias in list(
                    filter(lambda x: cls._aliases[x] == cmd,
                           cls._aliases.keys())):
                del cls._aliases[alias]
            del cls._commands[cmd_name]
            if cmd in cls._switches:
                del cls._switches[cmd]
            return True
        return False

    @classmethod
    def switch_command_global(cls,
                              cmd_name: CommandName_T,
                              state: Optional[bool] = None) -> None:
        """根据 `state` 更改 command 的全局状态。

        参数:
            cmd_name: 命令名称
            state:
                - `None(default)`: 切换状态，即 开 -> 关、关 -> 开
                - `bool`: 切换至指定状态，`True` -> 开、`False` -> 关

        用法:
            ```python
            from nonebot import message_preprocessor

            # 全局关闭命令test, 对所有消息生效
            CommandManager.switch_command_global(("test", ), state=False)

            @message_preprocessor
            async def processor(bot: NoneBot, event: CQEvent, plugin_manager: PluginManager):
                plugin_manager.cmd_manager.switch_command_global(("test", ), state=False)
            ```
        """
        cmd = cls._commands[cmd_name]
        cls._switches[cmd] = not cls._switches[cmd] if state is None else bool(
            state)

    @classmethod
    def add_aliases(cls, aliases: Union[Iterable[str], str], cmd: Command) -> None:
        """为 `Command` 添加命令别名。

        参数:
            aliases: 命令别名列表

        用法:
            ```python
            cmd = Command(name, func, permission, only_to_me, privileged)
            CommandManager.add_aliases({"别名", "test"}, cmd)
            ```
        """
        if isinstance(aliases, str):
            aliases = (aliases,)
        for alias in aliases:
            if not isinstance(alias, str):
                warnings.warn(f"Alias {alias} is not a string! Ignored")
                return
            elif alias in cls._aliases:
                warnings.warn(f"Alias {alias} already exists")
                return
            cls._aliases[alias] = cmd

    @classmethod
    def add_patterns(cls, patterns: Patterns_T, cmd: Command) -> None:
        """Register command alias(es)

        Args:
            patterns (Union[Iterable[Pattern], Pattern, Iterable[str], str]): Command patterns
            cmd (Command): Matched command
        """
        if isinstance(patterns, (str, Pattern)):
            patterns = (patterns,)
        for pattern in patterns:
            if isinstance(pattern, str):
                pattern = re.compile(pattern)
            if not isinstance(pattern, Pattern):
                warnings.warn(
                    f"Pattern {pattern} is not a regex or string! Ignored")
                continue
            elif pattern in cls._patterns:
                warnings.warn(f"Pattern {pattern} already exists")
                continue
            cls._patterns[pattern] = cmd

    def _find_command(self, name: Union[str,
                                        CommandName_T]) -> Optional[Command]:
        cmd_name = (name,) if isinstance(name, str) else name
        if not cmd_name:
            return None

        cmd = {
            name: cmd
            for name, cmd in self.commands.items()
            if self.switches.get(cmd, True)
        }.get(cmd_name)
        return cmd

    def parse_command(
            self, bot: NoneBot,
            cmd_string: str) -> Tuple[Optional[Command], Optional[str]]:
        logger.debug(f'Parsing command: {repr(cmd_string)}')

        matched_start = None
        for start in bot.config.COMMAND_START:
            # loop through COMMAND_START to find the longest matched start
            curr_matched_start = None
            if isinstance(start, str):
                if cmd_string.startswith(start):
                    curr_matched_start = start
            elif isinstance(start, Pattern):
                m = start.search(cmd_string)
                if m and m.start(0) == 0:
                    curr_matched_start = m.group(0)

            if curr_matched_start is not None and \
                    (matched_start is None or
                    len(curr_matched_start) > len(matched_start)):
                # a longer start, use it
                matched_start = curr_matched_start

        if matched_start is None:
            # it's not a command
            logger.debug('It\'s not a command')
            return None, None

        logger.debug(f'Matched command start: '
                     f'{matched_start}{"(empty)" if not matched_start else ""}')
        full_command = cmd_string[len(matched_start):].lstrip()

        if not full_command:
            # command is empty
            return None, None

        cmd_name_text, *cmd_remained = full_command.split(maxsplit=1)

        cmd_name = None
        for sep in bot.config.COMMAND_SEP:
            # loop through COMMAND_SEP to find the most optimized split
            curr_cmd_name = None
            if isinstance(sep, str):
                curr_cmd_name = tuple(cmd_name_text.split(sep))
            elif isinstance(sep, Pattern):
                curr_cmd_name = tuple(sep.split(cmd_name_text))

            if curr_cmd_name is not None and \
                    (not cmd_name or len(curr_cmd_name) > len(cmd_name)):
                # a more optimized split, use it
                cmd_name = curr_cmd_name

        if not cmd_name:
            cmd_name = (cmd_name_text,)
        logger.debug(f'Split command name: {cmd_name}')

        cmd = self._find_command(cmd_name)  # type: ignore
        if not cmd:
            logger.debug(f'Command {cmd_name} not found. Try to match aliases')
            cmd = {
                name: cmd
                for name, cmd in self.aliases.items()
                if self.switches.get(cmd, True)
            }.get(cmd_name_text)

        if not cmd:
            logger.debug(f'Alias {cmd_name} not found. Try to match patterns')
            patterns = {
                pattern: cmd
                for pattern, cmd in self.patterns.items()
                if self.switches.get(cmd, True)
            }
            for pattern in patterns:
                if pattern.search(full_command):
                    cmd = patterns[pattern]
                    logger.debug(
                        f'Pattern {pattern} of command {cmd.name} matched, function: {cmd.func}'
                    )
                    # if command matched by regex, it will use the full_command as the current_arg of the session
                    return cmd, full_command

        if not cmd:
            return None, None

        logger.debug(f'Command {cmd.name} found, function: {cmd.func}')
        return cmd, ''.join(cmd_remained)

    def switch_command(self,
                       cmd_name: CommandName_T,
                       state: Optional[bool] = None) -> None:
        """根据 `state` 更改 command 的状态。仅对当前消息有效。

        参数:
            cmd_name: 命令名称
            state:
                - `None(default)`: 切换状态，即 开 -> 关、关 -> 开
                - `bool`: 切换至指定状态，`True` -> 开、`False` -> 关

        用法:
            ```python
            from nonebot import message_preprocessor

            # 关闭命令test, 仅对当前消息生效
            @message_preprocessor
            async def processor(bot: NoneBot, event: CQEvent, plugin_manager: PluginManager):
                plugin_manager.cmd_manager.switch_command(("test", ), state=False)
            ```
        """
        cmd = self.commands[cmd_name]
        self.switches[cmd] = not self.switches[cmd] if state is None else bool(
            state)


class CommandSession(BaseSession):
    """继承自 `BaseSession` 类，表示命令 Session。"""

    __slots__ = ('cmd', 'current_key', 'current_arg_filters',
                 '_current_send_kwargs', 'current_arg', '_current_arg_text',
                 '_current_arg_images', '_state', '_last_interaction',
                 '_running', '_run_future', '_future')

    def __init__(self,
                 bot: NoneBot,
                 event: CQEvent,
                 cmd: Command,
                 *,
                 current_arg: Optional[str] = '',
                 args: Optional[CommandArgs_T] = None):
        super().__init__(bot, event)
        self.cmd = cmd  # Command object

        # unique key of the argument that is currently requesting (asking)
        self.current_key: Optional[str] = None
        """命令会话当前正在询问用户的参数的键（或称参数的名字）。第一次运行会话时，该属性为 `None`。"""

        # initialize current argument filters
        self.current_arg_filters: Optional[List[Filter_T]] = None

        self._current_send_kwargs: Dict[str, Any] = {}

        # initialize current argument
        self.current_arg: Optional[str] = ''  # with potential CQ codes
        """命令会话当前参数。实际上是 酷 Q 收到的消息去掉命令名的剩下部分，因此可能存在 CQ 码。"""
        self._current_arg_text = None
        self._current_arg_images = None
        self.refresh(event, current_arg=current_arg)  # fill the above

        self._run_future = partial(asyncio.run_coroutine_threadsafe,
                                   loop=bot.loop)

        self._state: State_T = {}
        if args:
            self._state.update(args)

        self._last_interaction = None  # last interaction time of this session
        self._running = False
        self._future: Optional[asyncio.Future] = None

    @property
    def state(self) -> State_T:
        """
        命令会话的状态数据（包括已获得的所有参数）。

        属性本身只读，但属性中的内容可读写。

        版本: 1.2.0+

        用法:
            ```python
            if not session.state.get('initialized'):
                # ... 初始化工作
                session.state['initialized'] = True
            ```

            在命令处理函数的开头进行**每次命令调用只应该执行一次的初始化操作**。
        """
        return self._state

    @property
    def running(self) -> bool:
        """INTERNAL API"""
        return self._running

    @running.setter
    def running(self, value) -> None:
        """INTERNAL API"""
        if self._running is True and value is False:
            # change status from running to not running, record the time
            self._last_interaction = datetime.now()
        self._running = value

    @property
    def waiting(self) -> bool:
        """INTERNAL API"""
        return self._future is not None and not self._future.done()

    @property
    def expire_timeout(self) -> Optional[timedelta]:
        """INTERNAL API"""
        if self.cmd.expire_timeout is not ...:
            return self.cmd.expire_timeout
        return self.bot.config.SESSION_EXPIRE_TIMEOUT

    @property
    def run_timeout(self) -> Optional[timedelta]:
        """INTERNAL API"""
        if self.cmd.run_timeout is not ...:
            return self.cmd.run_timeout
        return self.bot.config.SESSION_RUN_TIMEOUT

    @property
    def is_valid(self) -> bool:
        """
        INTERNAL API

        Check whether the session has expired or not.
        """
        tm = self.expire_timeout
        if tm and self._last_interaction and \
            datetime.now() - self._last_interaction > tm:
            return False
        return True

    @property
    def is_first_run(self) -> bool:
        """命令会话是否第一次运行。"""
        return self._last_interaction is None

    @property
    def current_arg_text(self) -> str:
        """`current_arg` 属性的纯文本部分（不包含 CQ 码），各部分使用空格连接。"""
        if self._current_arg_text is None:
            self._current_arg_text = Message(
                self.current_arg).extract_plain_text()
        return self._current_arg_text

    @property
    def current_arg_images(self) -> List[str]:
        """`current_arg` 属性中所有图片的 URL 的列表，如果参数中没有图片，则为 `[]`。"""
        if self._current_arg_images is None:
            self._current_arg_images = [
                s.data['url']
                for s in Message(self.current_arg)
                if s.type == 'image' and 'url' in s.data
            ]
        return self._current_arg_images

    @property
    def argv(self) -> List[str]:
        """
        命令参数列表，类似于 `sys.argv`，本质上是 `session.state.get('argv', [])`，**需要搭配 `on_command(..., shell_like=True)` 使用**。

        用法:
            ```python
            @on_command('some_cmd', shell_like=True)
            async def _(session: CommandSession):
                argv = session.argv
            ```
        """
        return self.state.get('argv', [])

    def refresh(self,
                event: CQEvent,
                *,
                current_arg: Optional[str] = '') -> None:
        """
        INTERNAL API

        Refill the session with a new message event.

        :param event: new message event
        :param current_arg: new command argument as a string
        """
        self.event = event
        self.current_arg = current_arg
        self._current_arg_text = None
        self._current_arg_images = None

    def get(self,
            key: str,
            *,
            prompt: Optional[Message_T] = None,
            arg_filters: Optional[List[Filter_T]] = None,
            **kwargs) -> Any:
        r"""
        从 `state` 属性获取参数，如果参数不存在，则暂停当前会话，向用户发送提示，并等待用户的新一轮交互。

        如果需要暂停当前会话，则命令处理器中，此函数调用之后的语句将不会被执行（除非捕获了此函数抛出的特殊异常）。

        注意，一旦传入 `arg_filters` 参数（参数过滤器），则等用户再次输入时，_command_func._`args_parser` 所注册的参数解析函数将不会被运行，而会在对 `current_arg` 依次运行过滤器之后直接将其放入 `state` 属性中。

        :::tip
        推荐使用下面的 `aget` 方法。
        :::

        参数:
            key: 参数的键
            prompt: 提示的消息内容
            arg_filters {version}`1.2.0+`: 用于处理和验证用户输入的参数的过滤器
            kwargs: 其它传入 `BaseSession.send()` 的命名参数

        返回:
            Any: 参数的值

        用法:
            ```python
            location = session.get('location', prompt='请输入要查询的地区')
            ```

            获取位置信息，如果当前还不知道，则询问用户。

            ```python
            from nonebot.command.argfilter import extractors, validators

            time = session.get(
                'time', prompt='你需要我在什么时间提醒你呢？',
                arg_filters=[
                    extractors.extract_text,  # 取纯文本部分
                    controllers.handle_cancellation(session),  # 处理用户可能的取消指令
                    str.strip,  # 去掉两边空白字符
                    # 正则匹配输入格式
                    validators.match_regex(r'^\d{4}-\d{2}-\d{2}$', '格式不对啦，请重新输入')
                ]
            )
            ```

            获取时间信息，如果当前还不知道，则询问用户，等待用户输入之后，会依次运行 `arg_filters` 参数中的过滤器，以确保参数内容和格式符合要求。
        """
        if key in self.state:
            return self.state[key]

        self.current_key = key
        self.current_arg_filters = arg_filters
        self._current_send_kwargs = kwargs
        self.pause(prompt, **kwargs)

    async def aget(self,
                   key: str = ...,
                   *,
                   prompt: Optional[Message_T] = None,
                   arg_filters: Optional[List[Filter_T]] = None,
                   force_update: bool = ...,
                   **kwargs) -> Any:
        r"""
        从 `state` 属性获取参数，如果参数不存在，则异步地暂停当前会话，向用户发送提示，并等待用户的进一步交互。

        当用户再次输入时，不会重新运行命令处理器，而是回到此函数调用之处继续执行。

        注意，一旦传入 `arg_filters` 参数（参数过滤器），则等用户再次输入时，_command_func._`args_parser` 所注册的参数解析函数将不会被运行，而会在对 `current_arg` 依次运行过滤器之后直接将其放入 `state` 属性中。

        版本: 1.8.0+

        参数:
            key: 参数的键，若不传入则使用默认键值
            prompt: 提示的消息内容
            arg_filters: 用于处理和验证用户输入的参数的过滤器
            force_update: 是否强制获取用户新的输入，若是，则会忽略已有的当前参数，若 `key` 不传入则为真，否则默认为假
            kwargs: 其它传入 `BaseSession.send()` 的命名参数

        返回:
            Any: 参数的值

        用法:
            ```python
            from nonebot.command.argfilter import extractors, validators

            note = await session.aget(
                'note', prompt='你需要我提醒你什么呢',
                arg_filters=[
                    extractors.extract_text,  # 取纯文本部分
                    controllers.handle_cancellation(session),  # 处理用户可能的取消指令
                    str.strip  # 去掉两边空白字符
                ]
            )

            time = await session.aget(
                'time', prompt='你需要我在什么时间提醒你呢？',
                arg_filters=[
                    extractors.extract_text,  # 取纯文本部分
                    controllers.handle_cancellation(session),  # 处理用户可能的取消指令
                    str.strip,  # 去掉两边空白字符
                    # 正则匹配输入格式
                    validators.match_regex(r'^\d{4}-\d{2}-\d{2}$', '格式不对啦，请重新输入')
                ]
            )
            ```

            连续获取多个参数，如果当前还不知道，则询问用户，等待用户输入之后，会依次运行 `arg_filters` 参数中的过滤器，以确保参数内容和格式符合要求。
        """
        if key is ...:
            key = '__default_argument'
            force_update = True
        if key in self.state:
            if force_update is True:
                del self.state[key]
            else:
                return self.state[key]

        self.current_key = key
        self.current_arg_filters = arg_filters
        self._current_send_kwargs = kwargs
        await self.apause(prompt, **kwargs)

        return self.state.get(key, self.current_arg)

    def pause(self, message: Optional[Message_T] = None, **kwargs) -> NoReturn:
        """
        暂停当前命令会话，并发送消息。此函数调用之后的语句将不会被执行（除非捕获了此函数抛出的特殊异常）。

        :::tip
        推荐使用下面的 `apause` 方法。
        :::

        参数:
            message: 要发送的消息，若不传入则不发送
            kwargs: 其它传入 `BaseSession.send()` 的命名参数

        用法:
            ```python
            if session.is_first_run:
                session.pause('请发送要处理的图片，发送 done 结束')
            if session.current_arg_text.strip() == 'done':
                session.finish('处理完成')
            process_images(session.current_arg_images)
            session.pause('请继续发送要处理的图片，发送 done 结束')
            ```

            需要连续接收用户输入，并且过程中不需要改变 `current_key` 时，使用此函数暂停会话。
        """
        if message:
            self._run_future(self.send(message, **kwargs))
        self._raise(_PauseException())

    async def apause(self, message: Optional[Message_T] = None, **kwargs) -> None:
        """
        异步地暂停当前命令会话，并发送消息。

        当用户再次输入时，不会重新运行命令处理器，而是回到此函数调用之处继续执行。

        版本: 1.8.0+

        参数:
            message: 要发送的消息，若不传入则不发送
            kwargs: 其它传入 `BaseSession.send()` 的命名参数

        用法:
            ```python
            await session.apause('请发送要处理的图片，发送 done 结束')
            while True:
                if session.current_arg_text.strip() == 'done':
                    session.finish('处理完成')
                process_images(session.current_arg_images)
                await session.apause('请继续发送要处理的图片，发送 done 结束')
            ```

            需要连续接收用户输入，并且过程中不需要改变 `current_key` 时，使用此函数暂停会话。
        """
        if message:
            self._run_future(self.send(message, **kwargs))
        if self.waiting:
            return
        while True:
            try:
                self._future = asyncio.get_event_loop().create_future()
                self.running = False
                timeout_opt = self.expire_timeout
                timeout = timeout_opt.total_seconds() if timeout_opt else None
                await asyncio.wait_for(self._future, timeout)
                break
            except _PauseException:
                continue
            except (_FinishException, asyncio.TimeoutError):
                raise

    def finish(self, message: Optional[Message_T] = None, **kwargs) -> NoReturn:
        """
        结束当前命令会话，并发送消息。此函数调用之后的语句将不会被执行（除非捕获了此函数抛出的特殊异常）。

        调用此函数后，命令将被视为已经完成，当前命令会话将被移除。

        参数:
            message: 要发送的消息，若不传入则不发送
            kwargs: 其它传入 `BaseSession.send()` 的命名参数

        用法:
            ```python
            session.finish('感谢您的使用～')
            ```
        """
        if message:
            self._run_future(self.send(message, **kwargs))
        self._raise(_FinishException())

    def switch(self, new_message: Message_T) -> NoReturn:
        """
        结束当前会话，改变当前消息事件中的消息内容，然后重新处理消息事件。

        此函数可用于从一个命令中跳出，将用户输入的剩余部分作为新的消息来处理，例如可实现以下对话:

        ```
        用户: 帮我查下天气
        Bot: 你要查询哪里的天气呢？
        用户: 算了，帮我查下今天下午南京到上海的火车票吧
        Bot: 今天下午南京到上海的火车票有如下班次: blahblahblah
        ```

        这里进行到第三行时，命令期待的是一个地点，但实际发现消息的开头是「算了」，于是调用 `switch('帮我查下今天下午南京到上海的火车票吧')`，结束天气命令，将剩下来的内容作为新的消息来处理（触发火车票插件的自然语言处理器，进而调用火车票查询命令）。

        参数:
            new_message: 要覆盖消息事件的新消息内容

        用法:
            ```python
            @my_cmd.args_parser
            async def _(session: CommandSession)
                if not session.is_first_run and session.current_arg.startswith('算了，'):
                    session.switch(session.current_arg[len('算了，'):])
            ```

            使用「算了」来取消当前命令，转而进入新的消息处理流程。这个例子比较简单，实际应用中可以使用更复杂的 NLP 技术来判断。
        """
        if self.is_first_run:
            # if calling this method during first run,
            # we think the command is not handled
            raise _FinishException(result=False)

        if not isinstance(new_message, Message):
            new_message = Message(new_message)
        self._raise(SwitchException(new_message))

    def _raise(self, e: Exception) -> NoReturn:
        """Raise an exception from the main execution path"""
        if self.waiting:
            self._future.set_exception(e)
            raise _YieldException
        raise e


async def handle_command(bot: NoneBot, event: CQEvent,
                         manager: CommandManager) -> Optional[bool]:
    """
    INTERNAL API

    Handle a message as a command.

    This function is typically called by "handle_message".

    :param bot: NoneBot instance
    :param event: message event
    :param manager: command manager
    :return: the message is handled as a command
    """
    cmd, current_arg = manager.parse_command(bot, str(event.message).lstrip())
    is_privileged_cmd = cmd and cmd.privileged
    if is_privileged_cmd and cmd.only_to_me and not event['to_me']:
        is_privileged_cmd = False
    disable_interaction = bool(is_privileged_cmd)

    if is_privileged_cmd:
        logger.debug(f'Command {cmd.name} is a privileged command')

    ctx_id = context_id(event)

    if not is_privileged_cmd:
        # wait for 1.5 seconds (at most) if the current session is running
        retry = 5
        while retry > 0 and \
                _sessions.get(ctx_id) and _sessions[ctx_id].running:
            retry -= 1
            await asyncio.sleep(0.3)

    check_perm = True
    session: Optional[CommandSession] = _sessions.get(
        ctx_id) if not is_privileged_cmd else None

    if session is not None:
        if session.running:
            logger.warning(f'There is a session of command '
                           f'{session.cmd.name} running, notify the user')
            asyncio.ensure_future(
                send(bot, event,
                     render_expression(bot.config.SESSION_RUNNING_EXPRESSION)))
            # pretend we are successful, so that NLP won't handle it
            return True

        if session.is_valid:
            logger.debug(f'Session of command {session.cmd.name} exists')
            # since it's in a session, the user must be talking to me
            event['to_me'] = True
            session.refresh(event, current_arg=str(event['message']))
            # there is no need to check permission for existing session
            check_perm = False
        else:
            # the session is expired, remove it
            logger.debug(f'Session of command {session.cmd.name} has expired')
            if ctx_id in _sessions:
                del _sessions[ctx_id]
            session = None

    if session is None:
        if not cmd:
            logger.debug('Not a known command, ignored')
            return False
        if cmd.only_to_me and not event['to_me']:
            logger.debug('Not to me, ignored')
            return False
        SessionClass = cmd.session_class or CommandSession
        session = SessionClass(bot, event, cmd, current_arg=current_arg)
        logger.debug(f'New session of command {session.cmd.name} created')

    assert isinstance(session, CommandSession)
    return await _real_run_command(session,
                                   ctx_id,
                                   check_perm=check_perm,
                                   disable_interaction=disable_interaction)


async def call_command(bot: NoneBot,
                       event: CQEvent,
                       name: Union[str, CommandName_T],
                       *,
                       current_arg: str = '',
                       args: Optional[CommandArgs_T] = None,
                       check_perm: bool = True,
                       disable_interaction: bool = False) -> Optional[bool]:
    """从内部直接调用命令。可用于在一个插件中直接调用另一个插件的命令。

    参数:
        bot: NoneBot 对象
        event: 事件对象
        name: 要调用的命令名
        current_arg: 命令会话的当前输入参数
        args: 命令会话的（初始）参数（将会被并入命令会话的 `state` 属性）
        check_perm: 是否检查命令的权限，若否，则即使当前事件上下文并没有权限调用这里指定的命令，也仍然会调用成功
        disable_interaction: 是否禁用交互功能，若是，则该命令的会话不会覆盖任何当前已存在的命令会话，新创建的会话也不会保留

    返回:
        bool: 命令是否调用成功

    用法:
        ```python
        await call_command(bot, event, 'say', current_arg='[CQ:face,id=14]', check_perm=False)
        ```

        从内部调用 `say` 命令，且不检查权限。
    """
    cmd = CommandManager()._find_command(name)
    if not cmd:
        return False
    SessionClass = cmd.session_class or CommandSession
    session = SessionClass(bot, event, cmd, current_arg=current_arg, args=args)
    return await _real_run_command(session,
                                   context_id(session.event),
                                   check_perm=check_perm,
                                   disable_interaction=disable_interaction)


async def _real_run_command(session: CommandSession,
                            ctx_id: str,
                            disable_interaction: bool = False,
                            **kwargs) -> Optional[bool]:
    if not disable_interaction:
        # override session only when interaction is not disabled
        _sessions[ctx_id] = session
    try:
        logger.debug(f'Running command {session.cmd.name}')
        session.running = True
        future = asyncio.ensure_future(session.cmd.run(session, **kwargs))
        timeout_opt = session.run_timeout
        timeout = timeout_opt.total_seconds() if timeout_opt else None

        try:
            await asyncio.wait_for(future, timeout)
            handled = future.result()
        except asyncio.TimeoutError:
            handled = True
        except CommandInterrupt:
            raise
        except Exception as e:
            logger.error(f'An exception occurred while '
                         f'running command {session.cmd.name}:')
            logger.exception(e)
            handled = True
        raise _FinishException(handled)
    except _PauseException:
        session.running = False
        if disable_interaction:
            # if the command needs further interaction, we view it as failed
            return False
        logger.debug(f'Further interaction needed for '
                     f'command {session.cmd.name}')
        # return True because this step of the session is successful
        return True
    except _YieldException:
        return True
        # return True because this step of the session is successful
    except (_FinishException, SwitchException) as e:
        session.running = False
        logger.debug(f'Session of command {session.cmd.name} finished')
        if not disable_interaction and ctx_id in _sessions:
            # the command is finished, remove the session,
            # but if interaction is disabled during this command call,
            # we leave the _sessions untouched.
            del _sessions[ctx_id]

        if isinstance(e, _FinishException):
            return e.result
        elif isinstance(e, SwitchException):
            # we are guaranteed that the session is not first run here,
            # which means interaction is definitely enabled,
            # so we can safely touch _sessions here.
            if ctx_id in _sessions:
                # make sure there is no session waiting
                del _sessions[ctx_id]
            logger.debug(f'Session of command {session.cmd.name} switching, '
                         f'new message: {e.new_message}')
            raise e  # this is intended to be propagated to handle_message()


def kill_current_session(event: CQEvent) -> None:
    """强行移除当前已存在的任何命令会话，即使它正在运行。该函数可用于强制移除执行时间超过预期的命令，以保证新的消息不会被拒绝服务。

    参数:
        event: 事件对象

    用法:
        ```python
        @on_command('kill', privileged=True)
        async def _(session: CommandSession):
            kill_current_session(session.event)
        ```

        在特权命令 `kill` 中强行移除当前正在运行的会话。
    """
    ctx_id = context_id(event)
    if ctx_id in _sessions:
        if _sessions[ctx_id].waiting:
            _sessions[ctx_id]._future.set_exception(_FinishException())
        del _sessions[ctx_id]


from nonebot.command.group import CommandGroup


__all__ = [
    'CommandManager',
    'CommandSession',
    'call_command',
    'kill_current_session',
    'CommandGroup',
]

__autodoc__ = {
    "CommandInterrupt": False,
    "SwitchException": False,
    "Command": False,
    "CommandManager.add_patterns": False,
    "CommandManager.parse_command": False,
    "CommandSession.running": False,
    "CommandSession.waiting": False,
    "CommandSession.expire_timeout": False,
    "CommandSession.run_timeout": False,
    "CommandSession.is_valid": False,
    "CommandSession.refresh": False,
    "handle_command": False
}
