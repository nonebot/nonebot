try:
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
except ImportError:
    # APScheduler is not installed
    AsyncIOScheduler = None

if AsyncIOScheduler:

    class Scheduler(AsyncIOScheduler):
        """
        继承自 `apscheduler.schedulers.asyncio.AsyncIOScheduler` 类，功能不变。

        当 Python 环境中没有安装 APScheduler 包时，此类不存在，`Scheduler` 为 `None`。
        """
        pass
else:
    Scheduler = None


__all__ = [
    'Scheduler',
]
