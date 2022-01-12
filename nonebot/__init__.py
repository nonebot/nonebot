"""
为方便使用，`nonebot` 模块从子模块导入了部分内容:

- `CQHttpError` -> `nonebot.exceptions.CQHttpError`
- `load_plugin` -> `nonebot.plugin.load_plugin`
- `load_plugins` -> `nonebot.plugin.load_plugins`
- `load_builtin_plugins` -> `nonebot.plugin.load_builtin_plugins`
- `get_loaded_plugins` <Badge text="1.1.0+"/> -> `nonebot.plugin.get_loaded_plugins`
- `on_command` -> `nonebot.plugin.on_command`
- `on_natural_language` -> `nonebot.plugin.on_natural_language`
- `on_notice` -> `nonebot.plugin.on_notice`
- `on_request` -> `nonebot.plugin.on_request`
- `message_preprocessor` -> `nonebot.message.message_preprocessor`
- `Message` -> `nonebot.message.Message`
- `MessageSegment` -> `nonebot.message.MessageSegment`
- `CommandSession` -> `nonebot.command.CommandSession`
- `CommandGroup` -> `nonebot.command.CommandGroup`
- `NLPSession` -> `nonebot.natural_language.NLPSession`
- `NoticeSession` -> `nonebot.notice_request.NoticeSession`
- `RequestSession` -> `nonebot.notice_request.RequestSession`
- `context_id` <Badge text="1.2.0+"/> -> `nonebot.helpers.context_id`
- `SenderRoles` <Badge text="1.9.0+"/> -> `nonebot.permission.SenderRoles`
"""
__version__ = (1, 9, 1)

import asyncio
import logging
from typing import Any, Optional, Callable, Awaitable

import aiocqhttp
from aiocqhttp import CQHttp

from .log import logger
from .sched import Scheduler

if Scheduler:
    scheduler = Scheduler()
else:
    scheduler = None


class NoneBot(CQHttp):
    """
    继承自 `aiocqhttp.CQHttp`

    参数:
        config_object: 配置对象，类型不限，只要能够通过 `__getattr__` 和 `__dict__` 分别访问到单个和所有配置项即可，若没有传入，则使用默认配置

    属性:
        asgi:
            - **类型:** `Quart`

            - **说明:**

                ASGI 对象，继承自 `aiocqhttp.CQHttp`，目前等价于 `server_app`。

        server_app:
            - **类型:** `Quart`

            - **说明:**

                内部的 Quart 对象，继承自 `aiocqhttp.CQHttp`。

        __getattr__:
            - **说明:**

                获取用于 API 调用的 `Callable` 对象。

                对返回结果进行函数调用会调用 CQHTTP 的相应 API，请注意捕获 `CQHttpError` 异常，具体请参考 aiocqhttp 的 [API 调用](https://aiocqhttp.nonebot.dev/#/what-happened#api-%E8%B0%83%E7%94%A8)。

            - **参数:**

                - `item: str`: 要调用的 API 动作名，请参考 CQHTTP 插件文档的 [API 列表](https://cqhttp.cc/docs/#/API?id=api-%E5%88%97%E8%A1%A8)

            - **返回:**

                - `(*Any, **Any) -> Any`: 用于 API 调用的 `Callable` 对象

            - **用法:**

                ```python
                bot = nonebot.get_bot()
                try:
                    info = await bot.get_group_member_info(group_id=1234567, user_id=12345678)
                except CQHttpError as e:
                    logger.exception(e)
                ```
    """

    def __init__(self, config_object: Optional[Any] = None):
        if config_object is None:
            from . import default_config as config_object

        config_dict = {
            k: v
            for k, v in config_object.__dict__.items()
            if k.isupper() and not k.startswith('_')
        }
        logger.debug(f'Loaded configurations: {config_dict}')
        super().__init__(message_class=aiocqhttp.message.Message,
                         **{k.lower(): v for k, v in config_dict.items()})

        self.config = config_object
        """配置对象"""
        self.asgi.debug = self.config.DEBUG

        from .message import handle_message
        from .notice_request import handle_notice_or_request

        @self.on_message
        async def _(event: aiocqhttp.Event):
            asyncio.create_task(handle_message(self, event))

        @self.on_notice
        async def _(event: aiocqhttp.Event):
            asyncio.create_task(handle_notice_or_request(self, event))

        @self.on_request
        async def _(event: aiocqhttp.Event):
            asyncio.create_task(handle_notice_or_request(self, event))

    def run(self,
            host: Optional[str] = None,
            port: Optional[int] = None,
            *args,
            **kwargs) -> None:
        """
        运行 NoneBot。

        不建议直接运行 NoneBot 对象，而应该使用全局的 `run()` 函数。

        参数:
            host: 主机名／IP
            port: 端口
            args: 其它传入 `CQHttp.run()` 的位置参数
            kwargs: 其它传入 `CQHttp.run()` 的命名参数
        """
        host = host or self.config.HOST
        port = port or self.config.PORT

        kwargs.setdefault('debug', self.config.DEBUG)

        logger.info(f'Running on {host}:{port}')
        super().run(host=host, port=port, *args, **kwargs)


_bot: Optional[NoneBot] = None


def init(config_object: Optional[Any] = None,
         start_scheduler: bool = True) -> None:
    """
    初始化全局 NoneBot 对象。

    参数:
        config_object: 配置对象，类型不限，只要能够通过 `__getattr__` 和 `__dict__` 分别访问到单个和所有配置项即可，若没有传入，则使用默认配置
        start_scheduler {version}`1.7.0+`: 是否要启动 `nonebot.scheduler`

    用法:
        ```python
        import config
        nonebot.init(config)
        ```

        导入 `config` 模块并初始化全局 NoneBot 对象。
    """
    global _bot
    _bot = NoneBot(config_object)

    if _bot.config.DEBUG:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    if start_scheduler:
        _bot.server_app.before_serving(_start_scheduler)


async def _start_scheduler():
    if scheduler and not scheduler.running:
        scheduler.configure(_bot.config.APSCHEDULER_CONFIG)
        scheduler.start()
        logger.info('Scheduler started')


def get_bot() -> NoneBot:
    """
    获取全局 NoneBot 对象。可用于在计划任务的回调中获取当前 NoneBot 对象。

    返回:
        NoneBot: 全局 NoneBot 对象

    异常:
        ValueError: 全局 NoneBot 对象尚未初始化

    用法:
        ```python
        bot = nonebot.get_bot()
        ```
    """
    if _bot is None:
        raise ValueError('NoneBot instance has not been initialized')
    return _bot


def run(host: Optional[str] = None,
        port: Optional[int] = None,
        *args,
        **kwargs) -> None:
    """
    运行全局 NoneBot 对象。

    参数:
        host: 主机名／IP，若不传入则使用配置文件中指定的值
        port: 端口，若不传入则使用配置文件中指定的值
        args: 其它传入 `CQHttp.run()` 的位置参数
        kwargs: 其它传入 `CQHttp.run()` 的命名参数

    用法:
        ```python
        nonebot.run(host='127.0.0.1', port=8080)
        ```

        在 `127.0.0.1:8080` 运行全局 NoneBot 对象。
    """
    get_bot().run(host=host, port=port, *args, **kwargs)


def on_startup(func: Callable[[], Awaitable[None]]) \
        -> Callable[[], Awaitable[None]]:
    """
    将函数装饰为 NoneBot 启动时的回调函数。

    版本: 1.5.0+

    用法:
        ```python
        @on_startup
        async def startup()
            await db.init()
        ```

        注册启动时回调，初始化数据库。
    """
    return get_bot().server_app.before_serving(func)


def on_websocket_connect(func: Callable[[aiocqhttp.Event], Awaitable[None]]) \
        -> Callable[[], Awaitable[None]]:
    """
    将函数装饰为 CQHTTP 反向 WebSocket 连接建立时的回调函数。

    该装饰器等价于 `@bot.on_meta_event('lifecycle.connect')`。

    版本: 1.5.0+

    用法:
        ```python
        @on_websocket_connect
        async def connect(event: aiocqhttp.Event):
            bot = nonebot.get_bot()
            groups = await bot.get_group_list()
        ```

        注册 WebSocket 连接时回调，获取群列表。
    """
    return get_bot().on_meta_event('lifecycle.connect')(func)


from .exceptions import CQHttpError
from .command import CommandSession, CommandGroup
from .plugin import (on_command, on_natural_language, on_notice, on_request,
                     load_plugin, load_plugins, load_builtin_plugins,
                     get_loaded_plugins)
from .message import message_preprocessor, Message, MessageSegment
from .natural_language import NLPSession, IntentCommand
from .notice_request import NoticeSession, RequestSession
from .helpers import context_id
from .permission import SenderRoles

__all__ = [
    'NoneBot',
    'scheduler',
    'init',
    'get_bot',
    'run',
    'on_startup',
    'on_websocket_connect',
    'CQHttpError',
    'load_plugin',
    'load_plugins',
    'load_builtin_plugins',
    'get_loaded_plugins',
    'message_preprocessor',
    'Message',
    'MessageSegment',
    'on_command',
    'CommandSession',
    'CommandGroup',
    'on_natural_language',
    'NLPSession',
    'IntentCommand',
    'on_notice',
    'NoticeSession',
    'on_request',
    'RequestSession',
    'context_id',
    'SenderRoles',
]

__autodoc__ = {
    "default_config": False
}
