from aiocqhttp import Event

from nonebot import NoneBot, on_command, message_preprocessor, CommandSession
from nonebot.plugin import PluginManager
from testing.external.common.client import TESTER_ID


@on_command('ping')
async def ping(session: CommandSession):
    await session.send('pong!')


@message_preprocessor
async def echo(bot: NoneBot, event: Event, manager: PluginManager):
    await bot.send_private_msg(user_id=TESTER_ID, message='echo!')
