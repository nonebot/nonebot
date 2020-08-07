from typing import TYPE_CHECKING, Union, List, Dict, Any, Sequence, Callable, Tuple, Awaitable, Pattern, Iterable

if TYPE_CHECKING:
    from nonebot.command import CommandSession

Context_T = Dict[str, Any]
Message_T = Union[str, Dict[str, Any], List[Dict[str, Any]]]
Expression_T = Union[str, Sequence[str], Callable]
CommandName_T = Tuple[str, ...]
CommandArgs_T = Dict[str, Any]
CommandHandler_T = Callable[["CommandSession"], Any]
Patterns_T = Union[Iterable[str], str, Iterable[Pattern], Pattern]
State_T = Dict[str, Any]
Filter_T = Callable[[Any], Union[Any, Awaitable[Any]]]
