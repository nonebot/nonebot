from typing import TYPE_CHECKING, Optional, Union, List, Dict, Any, Sequence, Callable, Tuple, Awaitable, Pattern, Iterable

if TYPE_CHECKING:
    from aiocqhttp import Event as CQEvent
    from nonebot import NoneBot
    from nonebot.plugin import PluginManager
    from nonebot.command import CommandSession
    from nonebot.natural_language import NLPSession, IntentCommand
    from nonebot.notice_request import NoticeSession, RequestSession
    from nonebot.permission import SenderRoles

Context_T = Dict[str, Any]
"""
CQHTTP 上报的事件数据对象的类型
版本: 1.5.0-
"""
Message_T = Union[str, Dict[str, Any], List[Dict[str, Any]]]
"""消息对象的类型，通常表示 NoneBot 提供的消息相关接口所支持的类型，`nonebot.message.Message` 也是一个合法的 `Message_T`。"""
Expression_T = Union[str, Sequence[str], Callable[..., str]]
"""
Expression 对象的类型
类型版本: 1.8.0+
"""
CommandName_T = Tuple[str, ...]
"""命令名称的类型"""
CommandArgs_T = Dict[str, Any]
"""命令参数的类型"""
CommandHandler_T = Callable[["CommandSession"], Awaitable[Any]]
"""
命令处理函数
版本: 1.6.0+
类型版本: 1.8.1+
"""
Patterns_T = Union[Iterable[str], str, Iterable[Pattern[str]], Pattern[str]]
"""
正则参数类型，可以是正则表达式或正则表达式组
版本: 1.7.0+
类型版本: 1.8.0+
"""
State_T = Dict[str, Any]
"""
命令会话的状态（`state` 属性）的类型
版本: 1.2.0+
"""
Filter_T = Callable[[Any], Union[Any, Awaitable[Any]]]
"""
过滤器的类型
版本: 1.2.0+
用法:
    ```python
    async def validate(value):
        if value > 100:
            raise ValidateError('数值必须小于 100')
        return value
    ```
"""
PermChecker_T = Callable[["NoneBot", "CQEvent"], Awaitable[bool]]
"""
已弃用
版本: 1.8.0+
"""
NLPHandler_T = Callable[["NLPSession"], Awaitable[Optional["IntentCommand"]]]
"""
自然语言处理函数
版本: 1.8.1+
"""
NoticeHandler_T = Callable[["NoticeSession"], Awaitable[Any]]
"""
通知处理函数
版本: 1.8.1+
"""
RequestHandler_T = Callable[["RequestSession"] , Awaitable[Any]]
"""
请求处理函数
版本: 1.8.1+
"""
MessagePreprocessor_T = Callable[["NoneBot", "CQEvent", "PluginManager"], Awaitable[Any]]
"""
消息预处理函数
版本: 1.8.1+
"""
PermissionPolicy_T = Union[Callable[["SenderRoles"], bool], Callable[["SenderRoles"], Awaitable[bool]]]
"""
向命令或自然语言处理器传入的权限检查策略。此类型是一个（同步/异步）函数，接受 `SenderRoles` 作为唯一的参数。此函数返回布尔值，返回 `True` 则表示权限检查通过，可以进行下一步处理（触发命令），反之返回 `False`。
版本: 1.9.0+
"""
PluginLifetimeHook_T = Union[Callable[[], Any], Callable[[], Awaitable[Any]]]
"""
插件生命周期事件回调函数
版本: 1.9.0+
"""


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
    'NLPHandler_T',
    'NoticeHandler_T',
    'RequestHandler_T',
    'MessagePreprocessor_T',
    'PermissionPolicy_T',
    'PluginLifetimeHook_T',
]
