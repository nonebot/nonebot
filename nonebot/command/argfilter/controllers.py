"""
提供几种常用的控制器。

这些验证器通常需要提供一些参数进行一次调用，返回的结果才是真正的验证器，其中的技巧在于通过闭包使要控制的对象能够被内部函数访问。

版本: 1.3.0+
"""
import re

from nonebot import CommandSession
from nonebot.helpers import render_expression


def handle_cancellation(session: CommandSession):
    """
    在用户发送 `算了`、`不用了`、`取消吧`、`停` 之类的话的时候，结束当前传入的命令会话（调用 `session.finish()`），并发送配置项 `SESSION_CANCEL_EXPRESSION` 所填的内容。

    如果不是上述取消指令，则将输入原样输出。

    参数:
        session: 要控制的命令会话
    """

    def control(value):
        if _is_cancellation(value) is True:
            session.finish(
                render_expression(session.bot.config.SESSION_CANCEL_EXPRESSION))
        return value

    return control


def _is_cancellation(sentence: str) -> bool:
    for kw in ('算', '别', '不', '停', '取消'):
        if kw in sentence:
            # a keyword matches
            break
    else:
        # no keyword matches
        return False

    if re.match(r'^那?[算别不停]\w{0,3}了?吧?$', sentence) or \
            re.match(r'^那?(?:[给帮]我)?取消了?吧?$', sentence):
        return True

    return False


__all__ = [
    'handle_cancellation',
]
