from datetime import timedelta
from typing import Any, Dict, Tuple, Union, Callable, Iterable, Optional, Type

from nonebot.command import CommandSession
from nonebot.typing import CommandHandler_T, CommandName_T, Patterns_T


class CommandGroup:
    basename: Tuple[str]
    base_kwargs: Dict[str, Any]

    def __init__(self, name: Union[str, CommandName_T], *,
                 permission: int = ...,
                 only_to_me: bool = ...,
                 privileged: bool = ...,
                 shell_like: bool = ...,
                 expire_timeout: Optional[timedelta] = ...,
                 run_timeout: Optional[timedelta] = ...,
                 session_class: Optional[Type[CommandSession]] = ...): ...

    def command(self, name: Union[str, CommandName_T], *,
                aliases: Union[Iterable[str], str] = ...,
                patterns: Patterns_T = ...,
                permission: int = ...,
                only_to_me: bool = ...,
                privileged: bool = ...,
                shell_like: bool = ...,
                expire_timeout: Optional[timedelta] = ...,
                run_timeout: Optional[timedelta] = ...,
                session_class: Optional[Type[CommandSession]] = ...
                ) -> Callable[[CommandHandler_T], CommandHandler_T]: ...
