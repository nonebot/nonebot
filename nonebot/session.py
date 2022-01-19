from typing import Any

from aiocqhttp import Event as CQEvent

from . import NoneBot
from .helpers import send
from .typing import Message_T


class BaseSession:
    """
    基础 session 类，`CommandSession` 等均继承自此类。
    """
    __slots__ = ('bot', 'event')

    def __init__(self, bot: NoneBot, event: CQEvent):
        self.bot = bot
        """Session 对应的 NoneBot 对象。

        用法:
            ```python
            await session.bot.send('hello')
            ```

            在当前 Session 对应的上下文中发送 `hello`。
        """
        self.event = event
        """
        CQHTTP 上报的事件数据对象，具体请参考 [`aiocqhttp.Event`](https://aiocqhttp.nonebot.dev/module/aiocqhttp/index.html#aiocqhttp.Event) 和 [事件上报](https://cqhttp.cc/docs/#/Post)。

        版本: 1.5.0+

        用法:
            ```python
            user_id = session.event['user_id']
            group_id = session.event.group_id
            ```

            获取当前事件的 `user_id` 和 `group_id` 字段。
        """

    @property
    def ctx(self) -> CQEvent:
        """CQHTTP 上报的事件数据对象，或称事件上下文，具体请参考 [事件上报](https://cqhttp.cc/docs/#/Post)。

        版本: 1.5.0-

        用法:
            ```python
            user_id = session.ctx['user_id']
            ```

            获取当前事件的 `user_id` 字段。
        """
        return self.event

    @ctx.setter
    def ctx(self, val: CQEvent) -> None:
        self.event = val

    @property
    def self_id(self) -> int:
        """
        当前 session 对应的 QQ 机器人账号，在多个机器人账号使用同一个 NoneBot 后端时可用于区分当前收到消息或事件的是哪一个机器人。

        等价于 `session.event.self_id`。

        版本: 1.1.0+

        用法:
            ```python
            await bot.send_private_msg(self_id=session.self_id, user_id=12345678, message='Hello')
            ```
        """
        return self.event.self_id

    async def send(self,
                   message: Message_T,
                   *,
                   at_sender: bool = False,
                   ensure_private: bool = False,
                   ignore_failure: bool = True,
                   **kwargs) -> Any:
        """发送消息到 Session 对应的上下文中。

        参数:
            message: 要发送的消息内容
            at_sender: 是否 @ 发送者，对私聊不起作用
            ensure_private: 确保消息发送到私聊，对于群组和讨论组消息上下文，会私聊发送者
            ignore_failure: 发送失败时忽略 `CQHttpError` 异常
            kwargs: 其它传入 `CQHttp.send()` 的命名参数

        返回:
            Any {version}`1.1.0+`: 返回 CQHTTP 插件发送消息接口的调用返回值，具体见 aiocqhttp 的 [API 调用](https://aiocqhttp.nonebot.dev/#/what-happened#api-%E8%B0%83%E7%94%A8)

        异常:
            CQHttpError: 发送失败时抛出，实际由 [aiocqhttp] 抛出，等价于 `aiocqhttp.Error`

        用法:
            ```python
            await session.send('hello')
            ```

            在当前 Session 对应的上下文中发送 `hello`。
        """
        return await send(self.bot,
                          self.event,
                          message,
                          at_sender=at_sender,
                          ensure_private=ensure_private,
                          ignore_failure=ignore_failure,
                          **kwargs)


__all__ = [
    'BaseSession',
]
