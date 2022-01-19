from datetime import timedelta
from typing import Any, Dict, Tuple, Union, Callable, Iterable, Optional, Type

from nonebot.command import CommandSession
from nonebot.typing import CommandHandler_T, CommandName_T, Patterns_T, PermissionPolicy_T


class CommandGroup:
    """命令组，用于声明一组有相同名称前缀的命令。

    **注:** 在 1.8.1 之前，此类文档与实际表现不一致 ([issue 242](https://github.com/nonebot/nonebot/issues/242))。

    参数:
        name: 命令名前缀，若传入字符串，则会自动转换成元组
        permission {version}`1.9.0+`: 对应 `permission` 属性
        only_to_me: 对应 `only_to_me` 属性
        privileged: 对应 `privileged` 属性
        shell_like: 对应 `shell_like` 属性
        expire_timeout {version}`1.8.2+`: 对应 `expire_timeout` 属性
        run_timeout {version}`1.8.2+`: 对应 `expire_timeout` 属性
        session_class {version}`1.8.1+`: 对应 `session_class` 属性
    """

    basename: Tuple[str]
    """命令名前缀。"""
    base_kwargs: Dict[str, Any]
    """此对象初始化时传递的 `permission`, `only_to_me`, `privileged`, `shell_like`, `expire_timeout`, `run_timeout`, `session_class`。如果没有传递，则此字典也不存在相应键值。"""

    def __init__(self, name: Union[str, CommandName_T], *,
                 permission: Union[PermissionPolicy_T, Iterable[PermissionPolicy_T]] = ...,
                 only_to_me: bool = ...,
                 privileged: bool = ...,
                 shell_like: bool = ...,
                 expire_timeout: Optional[timedelta] = ...,
                 run_timeout: Optional[timedelta] = ...,
                 session_class: Optional[Type[CommandSession]] = ...): ...

    def command(self, name: Union[str, CommandName_T], *,
                aliases: Union[Iterable[str], str] = ...,
                patterns: Patterns_T = ...,
                permission: Union[PermissionPolicy_T, Iterable[PermissionPolicy_T]] = ...,
                only_to_me: bool = ...,
                privileged: bool = ...,
                shell_like: bool = ...,
                expire_timeout: Optional[timedelta] = ...,
                run_timeout: Optional[timedelta] = ...,
                session_class: Optional[Type[CommandSession]] = ...
                ) -> Callable[[CommandHandler_T], CommandHandler_T]:
        """将函数装饰为命令组中的命令处理器。使用方法和 `on_command` 装饰器完全相同。

        参数:
            name: 命令名，注册命令处理器时会加上命令组的前缀
            aliases: 和 `on_command` 装饰器含义相同，若不传入则使用命令组默认值，若命令组没有默认值时，则使用 `on_command` 装饰器的默认值
            patterns {version}`1.8.1+`: 同上
            permission {version}`1.9.0+`: 同上
            only_to_me: 同上
            privileged: 同上
            shell_like: 同上
            expire_timeout {version}`1.8.2+`: 同上
            run_timeout {version}`1.8.2+`: 同上
            session_class {version}`1.8.1+`: 同上

        用法:
            ```python
            sched = CommandGroup('scheduler')

            @sched.command('add', permission=PRIVATE)
            async def _(session: CommandSession):
                pass
            ```

            注册 `('scheduler', 'add')` 命令。
        """
