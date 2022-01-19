import asyncio
import warnings
from typing import Any, List, Set, Iterable, Optional, Tuple, Union, NamedTuple

from aiocqhttp import Event as CQEvent
from aiocqhttp.message import Message

from .log import logger
from . import NoneBot
from .command import call_command
from .session import BaseSession
from .typing import CommandName_T, CommandArgs_T, NLPHandler_T, PermissionPolicy_T
from .permission import check_permission


class NLProcessor:
    """INTERNAL API"""
    __slots__ = ('func', 'keywords', 'only_to_me', 'only_short_message',
                 'allow_empty_message', 'permission')

    def __init__(self, *, func: NLPHandler_T, keywords: Optional[Iterable[str]],
                 only_to_me: bool, only_short_message: bool,
                 allow_empty_message: bool,
                 permission: PermissionPolicy_T):
        self.func = func
        self.keywords = keywords
        self.only_to_me = only_to_me
        self.only_short_message = only_short_message
        self.allow_empty_message = allow_empty_message
        self.permission = permission  # includes EllipsisType

    async def test(self, session: 'NLPSession', 
                   msg_text_length: Optional[int] = None) -> bool:
        """
        Test whether the session matches this (self) NL processor.

        :param session: NLPSession object
        :param msg_text_length: this argument is `len(session.msg_text)`,
                                designated to be cached if this function
                                is invoked in a loop
        :return: the session context matches this processor
        """
        if msg_text_length is None:
            msg_text_length = len(session.msg_text)

        if not self.allow_empty_message and not session.msg:
            # don't allow empty msg, but it is one, so no
            return False

        if self.only_short_message and \
            msg_text_length > session.bot.config.SHORT_MESSAGE_MAX_LENGTH:
            return False

        if self.only_to_me and not session.event['to_me']:
            return False

        if self.keywords:
            for kw in self.keywords:
                if kw in session.msg_text:
                    break
            else:
                # no keyword matches
                return False

        return await self._check_perm(session)

    async def _check_perm(self, session: 'NLPSession') -> bool:
        """
        Check if the session has sufficient permission to
        call the command.

        :param session: NLPSession object
        :return: the event has the permission
        """
        return await check_permission(session.bot, session.event,
            self.permission if self.permission is not ...
                else session.bot.config.DEFAULT_NLP_PERMISSION)


class NLPManager:
    """INTERNAL API"""
    _nl_processors: Set[NLProcessor] = set()

    def __init__(self):
        self.nl_processors = NLPManager._nl_processors.copy()

    @classmethod
    def add_nl_processor(cls, processor: NLProcessor) -> None:
        """Register a natural language processor
        
        Args:
            processor (NLProcessor): Processor object
        """
        if processor in cls._nl_processors:
            warnings.warn(f"NLProcessor {processor} already exists")
            return
        cls._nl_processors.add(processor)

    @classmethod
    def remove_nl_processor(cls, processor: NLProcessor) -> bool:
        """Remove a natural language processor globally
        
        Args:
            processor (NLProcessor): Processor to remove
        
        Returns:
            bool: Success or not
        """
        if processor in cls._nl_processors:
            cls._nl_processors.remove(processor)
            return True
        return False

    @classmethod
    def switch_nlprocessor_global(cls,
                                  processor: NLProcessor,
                                  state: Optional[bool] = None
                                  ) -> Optional[bool]:
        """Remove or add a natural language processor globally
        
        Args:
            processor (NLProcessor): Processor object
        
        Returns:
            bool: True if removed, False if added
        """
        if processor in cls._nl_processors and not state:
            cls._nl_processors.remove(processor)
            return True
        elif processor not in cls._nl_processors and state is not False:
            cls._nl_processors.add(processor)
            return False

    def switch_nlprocessor(self,
                           processor: NLProcessor,
                           state: Optional[bool] = None) -> Optional[bool]:
        """Remove or add a natural language processor
        
        Args:
            processor (NLProcessor): Processor to remove
        
        Returns:
            bool: True if removed, False if added
        """
        if processor in self.nl_processors and not state:
            self.nl_processors.remove(processor)
            return True
        elif processor not in self.nl_processors and state is not False:
            self.nl_processors.add(processor)
            return False


class NLPSession(BaseSession):
    """
    继承自 `BaseSession` 类，表示自然语言处理 Session。
    """
    __slots__ = ('msg', 'msg_text', 'msg_images')

    def __init__(self, bot: NoneBot, event: CQEvent, msg: str):
        super().__init__(bot, event)
        self.msg = msg
        """以字符串形式表示的消息内容，已去除开头的 @ 和机器人称呼，可能存在 CQ 码。"""
        tmp_msg = Message(msg)
        self.msg_text = tmp_msg.extract_plain_text()
        """消息内容的纯文本部分，已去除所有 CQ 码／非 `text` 类型的消息段。各纯文本消息段之间使用空格连接。"""
        self.msg_images = [
            s.data['url']
            for s in tmp_msg
            if s.type == 'image' and 'url' in s.data
        ]
        """消息内容中所有图片的 URL 的列表，如果消息中没有图片，则为 `[]`。"""


class IntentCommand(NamedTuple):
    """
    用于表示自然语言处理之后得到的意图命令，是一个 namedtuple，由自然语言处理器返回。

    版本: 1.2.0+
    """
    confidence: float
    """意图的置信度，即表示对当前推测的用户意图有多大把握。"""
    name: Union[str, CommandName_T]
    """命令的名字。"""
    args: Optional[CommandArgs_T] = None
    """命令的（初始）参数。"""
    current_arg: str = ''
    """命令的当前输入参数。"""


async def handle_natural_language(bot: NoneBot, event: CQEvent,
                                  manager: NLPManager) -> bool:
    """
    INTERNAL API

    Handle a message as natural language.

    This function is typically called by "handle_message".

    :param bot: NoneBot instance
    :param event: message event
    :param manager: natural language processor manager
    :return: the message is handled as natural language
    """
    session = NLPSession(bot, event, str(event.message))

    # use msg_text here because CQ code "share" may be very long,
    # at the same time some plugins may want to handle it
    msg_text_length = len(session.msg_text)

    # returns 1. processor result; 2. whether this processor is considered handled
    async def try_run_nlp(p: NLProcessor) -> Tuple[Any, bool]:
        try:
            should_run = await p.test(session, msg_text_length=msg_text_length)
            if should_run:
                return await p.func(session), True
            return None, False
        except Exception as e:
            logger.error('An exception occurred while running '
                         'some natural language processor:')
            logger.exception(e)
            return None, True

    intent_commands: List[IntentCommand] = []
    procs_empty = True

    for res in asyncio.as_completed([try_run_nlp(p) for p in manager.nl_processors]):
        result, should_run = await res
        if not should_run:
            continue
        procs_empty = False
        if isinstance(result, IntentCommand):
            intent_commands.append(result)

    if procs_empty:
        return False

    intent_commands.sort(key=lambda ic: ic.confidence, reverse=True)
    logger.debug(f'Intent commands: {intent_commands}')

    if intent_commands and intent_commands[0].confidence >= 60.0:
        # choose the intent command with highest confidence
        chosen_cmd = intent_commands[0]
        logger.debug(
            f'Intent command with highest confidence: {chosen_cmd}')
        return await call_command(bot,
                                  event,
                                  chosen_cmd.name,
                                  args=chosen_cmd.args,
                                  current_arg=chosen_cmd.current_arg,
                                  check_perm=False) or False
    logger.debug('No intent command has enough confidence')
    return False


__all__ = [
    'NLPSession',
    'IntentCommand',
]

__autodoc__ = {
    "NLProcessor": False,
    "NLPManager": False,
    "handle_natural_language": False
}
