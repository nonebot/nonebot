import asyncio

from aiocqhttp.message import Message
import pytest

import nonebot
import testing.external.common.default_config as dc
from testing.external.common.client import TESTER_ID, Client, run_nonebot_in_thread
from testing.external.common.port import available_port


@pytest.mark.asyncio
class TestBasicsWork:
    @pytest.fixture(scope='class')
    def event_loop(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        yield loop
        loop.close()

    @pytest.fixture(scope='class')
    async def cl(self):
        nonebot.init(dc)
        nonebot.load_plugin('testing.external.test_command.test_basics_work.basics_work')

        cl = Client()
        cl.patch_nonebot()

        run_nonebot_in_thread()
        cl_conn = cl.connect_to_nonebot(available_port)
        await cl_conn.__anext__()
        task = asyncio.create_task(await cl_conn.__anext__())
        await asyncio.sleep(0)
        yield cl
        task.cancel()
        await cl_conn.__anext__()
        cl.stop_nonebot()

    async def test_everyone_ping(self, cl: Client):
        cl.proxy.send_private_msg('/ping')
        resp = await cl.proxy.wait_for_private_msg()
        assert Message(resp['message']) == Message('pong!')
        assert resp['user_id'] == TESTER_ID

    async def test_wrong_pong(self, cl: Client):
        cl.proxy.send_private_msg('/pong')
        await cl.proxy.wait_for_handler_complete()
        # no message should be sent
        with pytest.raises(asyncio.TimeoutError):
            await cl.proxy.wait_for_private_msg()
