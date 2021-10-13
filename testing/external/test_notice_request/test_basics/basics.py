from nonebot import on_request, RequestSession


# overload1
@on_request
async def all_request(session: RequestSession):
    if session.event.detail_type == 'group':
        await session.reject()


# overload2
@on_request('friend')
async def group_invite(session: RequestSession):
    await session.approve('tester')
