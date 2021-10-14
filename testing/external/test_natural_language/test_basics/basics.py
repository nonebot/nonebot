from nonebot import on_command, on_natural_language, NLPSession, CommandSession, IntentCommand


@on_command('weather_report')
async def ping(session: CommandSession):
    await session.send('weather_report response')


# overload1
@on_natural_language
async def nlp_all(session: NLPSession):
    if '天气' in session.msg_text:
        return IntentCommand(70, 'weather_report')


# overload2
@on_natural_language({'预报'})
async def nlp_param(session: NLPSession):
    return IntentCommand(60, 'weather_report')
