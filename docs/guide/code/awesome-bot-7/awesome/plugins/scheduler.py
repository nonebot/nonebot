from datetime import datetime
from zoneinfo import ZoneInfo
import nonebot
from aiocqhttp.exceptions import Error as CQHttpError


@nonebot.scheduler.scheduled_job('cron', hour='*')
async def chime():
    bot = nonebot.get_bot()
    now = datetime.now(ZoneInfo('Asia/Shanghai'))
    try:
        await bot.send_group_msg(group_id=672076603, message=f'现在{now.hour}点整啦！')
    except CQHttpError:
        pass
