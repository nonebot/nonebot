from nonebot import on_command, CommandSession


@on_command('ping')
async def ping(session: CommandSession):
    await session.send('pong!')
