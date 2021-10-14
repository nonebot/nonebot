from nonebot import on_command, CommandSession
from nonebot.message import unescape


@on_command('echo')
async def echo(session: CommandSession):
    await session.send(session.state.get('message') or session.current_arg)


@on_command('say', permission=lambda s: s.is_superuser)
async def say(session: CommandSession):
    await session.send(
        unescape(session.state.get('message') or session.current_arg))
