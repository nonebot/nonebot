from typing import TYPE_CHECKING, Union, List, Dict, Any, Sequence, Callable, Tuple, Awaitable, Pattern, Iterable

if TYPE_CHECKING:
    from aiocqhttp import Event as CQEvent
    from nonebot import NoneBot
    from nonebot.command import CommandSession

Context_T = Dict[str, Any]
Message_T = Union[str, Dict[str, Any], List[Dict[str, Any]]]
Expression_T = Union[str, Sequence[str], Callable[..., str]]
CommandName_T = Tuple[str, ...]
CommandArgs_T = Dict[str, Any]
CommandHandler_T = Callable[["CommandSession"], Any]
Patterns_T = Union[Iterable[str], str, Iterable[Pattern[str]], Pattern[str]]
State_T = Dict[str, Any]
Filter_T = Callable[[Any], Union[Any, Awaitable[Any]]]
PermChecker_T = Callable[["NoneBot", "CQEvent"], Awaitable[bool]]


__all__ = [
    'Context_T',
    'Message_T',
    'Expression_T',
    'CommandName_T',
    'CommandArgs_T',
    'CommandHandler_T',
    'Patterns_T',
    'State_T',
    'Filter_T',
    'PermChecker_T',
]
