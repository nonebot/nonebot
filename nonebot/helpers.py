import asyncio
import hashlib
import random
from typing import Sequence, Any

from aiocqhttp.message import escape
from aiocqhttp import Event as CQEvent

from . import NoneBot
from .exceptions import CQHttpError
from .typing import Message_T, Expression_T


def context_id(event: CQEvent, *, mode: str = 'default',
               use_hash: bool = False) -> str:
    """
    Calculate a unique id representing the context of the given event.

    mode:
      default: one id for one context
      group: one id for one group or discuss
      user: one id for one user

    :param event: the event object
    :param mode: unique id mode: "default", "group", or "user"
    :param use_hash: use md5 to hash the id or not
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
    """Send a message ignoring failure by default."""
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
    Send a private message to all superusers that are defined in config.

    :param bot: nonebot object
    :param message: message to send to each superuser
    :param kwargs: keyword arguments used in bot.send_private_msg()
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
    Render an expression to message string.

    :param expr: expression to render
    :param escape_args: should escape arguments or not
    :param args: positional arguments used in str.format()
    :param kwargs: keyword arguments used in str.format()
    :return: the rendered message
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


__all__ = [
    'context_id',
    'send',
    'send_to_superusers',
    'render_expression',
]
