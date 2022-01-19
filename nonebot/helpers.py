import asyncio
import functools
import hashlib
import random
from typing import Callable, Iterable, List, Sequence, Any, Tuple

from aiocqhttp.message import escape
from aiocqhttp import Event as CQEvent

from . import NoneBot
from .exceptions import CQHttpError
from .typing import Message_T, Expression_T


def context_id(event: CQEvent, *, mode: str = 'default',
               use_hash: bool = False) -> str:
    """
    获取事件对应的上下文的唯一 ID。

    参数:
        event: 事件对象
        mode: ID 的计算模式
            - `'default'`: 默认模式，任何一个上下文都有其唯一 ID
            - `'group'`: 群组模式，同一个群组或讨论组的上下文（即使是不同用户）具有相同 ID
            - `'user'`: 用户模式，同一个用户的上下文（即使在不同群组）具有相同 ID
        use_hash: 是否将计算出的 ID 使用 MD5 进行哈希

    返回:
        str: 事件对应的上下文的唯一 ID

    用法:
        ```python
        ctx_id = context_id(session.event, use_hash=True)
        ```

        获取当前 Session 的事件对应的上下文的唯一 ID，并进行 MD5 哈希，得到的结果可用于图灵机器人等 API 的调用。
    """
    ctx_id = ''
    if mode == 'default':
        if event.group_id:
            ctx_id = f'/group/{event.group_id}'
        elif event.discuss_id:
            ctx_id = f'/discuss/{event.discuss_id}'
        if event.user_id:
            ctx_id += f'/user/{event.user_id}'
    elif mode == 'group':
        if event.group_id:
            ctx_id = f'/group/{event.group_id}'
        elif event.discuss_id:
            ctx_id = f'/discuss/{event.discuss_id}'
        elif event.user_id:
            ctx_id = f'/user/{event.user_id}'
    elif mode == 'user':
        if event.user_id:
            ctx_id = f'/user/{event.user_id}'

    if ctx_id and use_hash:
        ctx_id = hashlib.md5(ctx_id.encode('ascii')).hexdigest()
    return ctx_id


async def send(bot: NoneBot,
               event: CQEvent,
               message: Message_T,
               *,
               ensure_private: bool = False,
               ignore_failure: bool = True,
               **kwargs) -> Any:
    """
    发送消息到指定事件的上下文中。

    参数:
        bot: NoneBot 对象
        event: 事件对象
        message: 要发送的消息内容
        ensure_private: 确保消息发送到私聊，对于群组和讨论组消息上下文，会私聊发送者
        ignore_failure: 发送失败时忽略 `CQHttpError` 异常
        kwargs: 其它传入 `CQHttp.send()` 的命名参数

    返回:
        Any {version}`1.1.0+`: 返回 CQHTTP 插件发送消息接口的调用返回值，具体见 aiocqhttp 的 [API 调用](https://aiocqhttp.nonebot.dev/#/what-happened#api-%E8%B0%83%E7%94%A8)

    异常:
        CQHttpError: 发送失败时抛出，实际由 [aiocqhttp] 抛出，等价于 `aiocqhttp.Error`

    用法:
        ```python
        await send(bot, event, 'hello')
        ```
    """
    try:
        if ensure_private:
            event = event.copy()
            event['message_type'] = 'private'
        return await bot.send(event, message, **kwargs)
    except CQHttpError:
        if not ignore_failure:
            raise
        return None


async def send_to_superusers(bot: NoneBot,
                             message: Message_T,
                             **kwargs) -> None:
    """
    发送私聊消息到全体超级用户（即配置下的 `SUPERUSERS`）。

    版本: 1.7.0+

    参数:
        bot: NoneBot 对象
        message: 要发送的消息内容
        kwargs: 其它传入 `bot.send_private_msg()` 的命名参数

    异常:
        CQHttpError: 发送失败时抛出，实际由 [aiocqhttp] 抛出，等价于 `aiocqhttp.Error`

    用法:
        ```python
        await send_to_superusers(bot, f'被群 {event.group_id} 踢出了')
        ```
    """
    tasks = [
        bot.send_private_msg(user_id=user_id, message=message, **kwargs)
        for user_id in bot.config.SUPERUSERS
    ]
    await asyncio.gather(*tasks)


def render_expression(expr: Expression_T,
                      *args,
                      escape_args: bool = True,
                      **kwargs) -> str:
    """
    渲染 Expression。

    参数:
        expr: 要渲染的 Expression，对于 Expression 的三种类型: `str`、`Sequence[str]`、`(*Any, **Any) -> str`，行为分别是
            - `str`: 以 `*args`、`**kwargs` 为参数，使用 `str.format()` 进行格式化
            - `Sequence[str]`: 随机选择其中之一，进行上面 `str` 的操作
            - `(*Any, **Any) -> str`: 以 `*args`、`**kwargs` 为参数，调用该可调用对象/函数，对返回的字符串进行上面 `str` 的操作
        escape_args: 是否对渲染参数进行转义
        args: 渲染参数
        kwargs: 渲染参数

    返回:
        str: 渲染出的消息字符串

    用法:
        ```python
        msg1 = render_expression(
            ['你好，{username}！', '欢迎，{username}～'],
            username=username
        )
        msg2 = render_expression('你所查询的城市是{}', city)
        ```
    """
    result: str
    if callable(expr):
        result = expr(*args, **kwargs)
    elif isinstance(expr, Sequence) and not isinstance(expr, str):
        result = random.choice(expr)
    else:
        result = expr
    if escape_args:
        return result.format(
            *[escape(s) if isinstance(s, str) else s for s in args], **{
                k: escape(v) if isinstance(v, str) else v
                for k, v in kwargs.items()
            })
    return result.format(*args, **kwargs)


# the usage is still limited - we only allow "async def functions" to be identified as
# async funcs. those like "def" functions but returning coroutine objects are not supported.
# TODO: ParamSpec
def separate_async_funcs(funcs: Iterable[Callable]
                         ) -> Tuple[List[Callable], List[Callable]]:
    """INTERNAL API"""
    syncs = []
    asyncs = []
    for f in funcs:
        w = f
        while isinstance(w, functools.partial):
            w = w.func
        if asyncio.iscoroutinefunction(w) or (
            asyncio.iscoroutinefunction(w.__call__)):
            asyncs.append(f)
        else:
            syncs.append(f)
    return syncs, asyncs


__all__ = [
    'context_id',
    'send',
    'send_to_superusers',
    'render_expression',
]

__autodoc__ = {
    "separate_async_funcs": False
}
