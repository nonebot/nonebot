import re
import asyncio
import warnings
from typing import Optional, Set, Iterable

from aiocqhttp import Event as CQEvent
from aiocqhttp.message import Message, MessageSegment
from aiocqhttp.message import escape, unescape

from . import NoneBot
from .log import logger
from .natural_language import handle_natural_language
from .command import handle_command, SwitchException
from .plugin import Plugin, PluginManager
from .typing import MessagePreprocessor_T


class MessagePreprocessor:
    """INTERNAL_API"""
    __slots__ = ('func',)

    def __init__(self, func: MessagePreprocessor_T):
        self.func = func


class MessagePreprocessorManager:
    """INTERNAL API"""
    preprocessors: Set[MessagePreprocessor] = set()

    @classmethod
    def add_message_preprocessor(cls, preprocessor: MessagePreprocessor) -> None:
        if preprocessor in cls.preprocessors:
            warnings.warn(f"Message preprocessor {preprocessor} already exists")
            return
        cls.preprocessors.add(preprocessor)

    @classmethod
    def remove_message_preprocessor(cls, preprocessor: MessagePreprocessor) -> None:
        cls.preprocessors.discard(preprocessor)

    @classmethod
    def switch_message_preprocessor_global(cls,
                                          preprocessor: MessagePreprocessor,
                                          state: Optional[bool] = None) -> None:
        if preprocessor in cls.preprocessors and not state:
            cls.preprocessors.discard(preprocessor)
        elif preprocessor not in cls.preprocessors and state is not False:
            cls.preprocessors.add(preprocessor)


# this is more consistent if it is in the plugin module, but still kept here for historical
# reasons
def message_preprocessor(func: MessagePreprocessor_T) -> MessagePreprocessor_T:
    """
    将函数装饰为消息预处理器。

    参数:
        func (nonebot.typing.MessagePreprocessor_T):

    返回:
        nonebot.typing.MessagePreprocessor_T: 装饰器闭包

    要求(1.6.0+):
        被装饰函数必须是一个 async 函数，且必须接收且仅接收三个位置参数，类型分别为 {ref}`nonebot.NoneBot` 、 `aiocqhttp.Event` 和 {ref}`nonebot.plugin.PluginManager`，即形如:

        ```python
        async def func(bot: NoneBot, event: aiocqhttp.Event, plugin_manager: PluginManager):
            pass
        ```

    用法:
        ```python
        @message_preprocessor
        async def _(bot: NoneBot, event: aiocqhttp.Event, plugin_manager: PluginManager):
            event["preprocessed"] = True

            # 关闭某个插件，仅对当前消息生效
            plugin_manager.switch_plugin("path.to.plugin", state=False)
        ```

        在所有消息处理之前，向消息事件对象中加入 `preprocessed` 字段。
    """
    mp = MessagePreprocessor(func)
    if Plugin.GlobalTemp.now_within_plugin:
        Plugin.GlobalTemp.msg_preprocessors.add(mp)
    else:
        warnings.warn('defining message_preprocessor outside a plugin is deprecated '
                      'and will not be supported in the future')
        MessagePreprocessorManager.add_message_preprocessor(mp)
    return func


class CanceledException(Exception):
    """
    取消消息处理异常

    版本: 1.6.0+

    要求:
        在消息预处理函数 `message_preprocessor` 中可以选择抛出该异常来阻止响应该消息。

    用法:
        ```python
        @message_preprocessor
        async def _(bot: NoneBot, event: aiocqhttp.Event, plugin_manager: PluginManager):
            raise CanceledException(reason)
        ```
    """

    def __init__(self, reason):
        """
        :param reason: reason to ignore the message
        """
        self.reason = reason


async def handle_message(bot: NoneBot, event: CQEvent) -> None:
    """INTERNAL API"""
    _log_message(event)

    assert isinstance(event.message, Message)
    if not event.message:
        event.message.append(MessageSegment.text(''))  # type: ignore

    raw_to_me = event.get('to_me', False)
    _check_at_me(bot, event)
    _check_calling_me_nickname(bot, event)
    event['to_me'] = raw_to_me or event['to_me']

    coros = []
    plugin_manager = PluginManager()
    for preprocessor in MessagePreprocessorManager.preprocessors:
        coros.append(preprocessor.func(bot, event, plugin_manager))
    if coros:
        try:
            await asyncio.gather(*coros)
        except CanceledException as e:
            logger.info(f'Message {event["message_id"]} is ignored: {e.reason}')
            return

    while True:
        try:
            handled = await handle_command(bot, event,
                                           plugin_manager.cmd_manager)
            break
        except SwitchException as e:
            # we are sure that there is no session existing now
            event['message'] = e.new_message
            event['to_me'] = True
    if handled:
        logger.info(f'Message {event.message_id} is handled as a command')
        return

    handled = await handle_natural_language(bot, event,
                                            plugin_manager.nlp_manager)
    if handled:
        logger.info(f'Message {event.message_id} is handled '
                    f'as natural language')
        return

    logger.debug(f'Message {event.message_id} was not handled')


def _check_at_me(bot: NoneBot, event: CQEvent) -> None:
    if event.detail_type == 'private':
        event['to_me'] = True
        return

    def is_at_me(seg):
        return seg.type == 'at' and str(seg.data['qq']) == str(event.self_id)

    # group or discuss
    event['to_me'] = False

    # check the first segment
    first_msg_seg = event.message[0]
    if is_at_me(first_msg_seg):
        event['to_me'] = True
        del event.message[0]

    if not event['to_me']:
        # check the last segment
        i = -1
        last_msg_seg = event.message[i]
        if last_msg_seg.type == 'text' and \
                not last_msg_seg.data['text'].strip() and \
                len(event.message) >= 2:
            i -= 1
            last_msg_seg = event.message[i]

        if is_at_me(last_msg_seg):
            event['to_me'] = True
            del event.message[i:]

    if not event.message:
        event.message.append(MessageSegment.text(''))


def _check_calling_me_nickname(bot: NoneBot, event: CQEvent) -> None:
    first_msg_seg = event.message[0]
    if first_msg_seg.type != 'text':
        return

    first_text = first_msg_seg.data['text']

    if bot.config.NICKNAME:
        # check if the user is calling me with my nickname
        if isinstance(bot.config.NICKNAME, str) or \
                not isinstance(bot.config.NICKNAME, Iterable):
            nicknames = (bot.config.NICKNAME,)
        else:
            nicknames = filter(lambda n: n, bot.config.NICKNAME)
        nickname_regex = '|'.join(nicknames)
        m = re.search(rf'^({nickname_regex})([\s,，]*|$)', first_text,
                      re.IGNORECASE)
        if m:
            nickname = m.group(1)
            logger.debug(f'User is calling me {nickname}')
            event['to_me'] = True
            first_msg_seg.data['text'] = first_text[m.end():]


def _log_message(event: CQEvent) -> None:
    msg_from = str(event.user_id)
    if event.detail_type == 'group':
        msg_from += f'@[群:{event.group_id}]'
    elif event.detail_type == 'discuss':
        msg_from += f'@[讨论组:{event.discuss_id}]'
    logger.info(f'Self: {event.self_id}, '
                f'Message {event.message_id} from {msg_from}: '
                f'{repr(str(event.message))}')


__all__ = [
    'message_preprocessor',
    'CanceledException',
    'Message',
    'MessageSegment',
    'escape',
    'unescape',
]

__autodoc__ = {
    "MessagePreprocessor": False,
    "MessagePreprocessorManager": False,
    "handle_message": False,
    "Message":
        """
        从 `aiocqhttp.message` 模块导入，继承自 `list`，用于表示一个消息。该类型是合法的 `Message_T`。

        请参考 [aiocqhttp 文档](https://aiocqhttp.nonebot.dev/module/aiocqhttp/message.html#aiocqhttp.message.Message) 来了解此类的使用方法。
        """,
    "MessageSegment":
        """
        从 `aiocqhttp.message` 模块导入，继承自 `dict`，用于表示一个消息段。该类型是合法的 `Message_T`。

        请参考 [aiocqhttp 文档](https://aiocqhttp.nonebot.dev/module/aiocqhttp/message.html#aiocqhttp.message.MessageSegment) 来了解此类的使用方法。

        更多关于消息段的内容，见 [消息格式](https://github.com/botuniverse/onebot/tree/master/v11/specs/message)。
        """,
    "escape":
        """
        - **说明:** 从 `aiocqhttp.message` 模块导入，对字符串进行转义。

        - **参数:**

            - `s: str`: 要转义的字符串

            - `escape_comma: bool`: 是否转义英文逗号 `,`

        - **返回:**

            - `str`: 转义后的字符串
        """,
    "unescape":
        """
        - **说明:** 从 `aiocqhttp.message` 模块导入，对字符串进行去转义。

        - **参数:**

            - `s: str`: 要去转义的字符串

        - **返回:**

            - `str`: 去转义后的字符串
        """
}
