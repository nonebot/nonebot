import pytest

import nonebot
from nonebot.message import Message
import testing.external.common.default_config as dc
from testing.external.common.client import Client, run_nonebot_in_thread
from testing.external.common.pytest import AsyncTestCase
from testing.external.common.port import available_port


@pytest.mark.asyncio
class TestBasicsWork(AsyncTestCase):
    @pytest.fixture(scope='class')
    async def cl(self):
        nonebot.init(dc)
        nonebot.load_plugin('testing.external.test_message.test_basics.basics')

        cl = Client()
        cl.patch_nonebot()

        run_nonebot_in_thread()
        async for p in cl.run_client_until_test_done(available_port):
            yield p

    async def test_fire_msg_preprocessor(self, cl: Client):
        cl.proxy.send_private_msg('hello all')
        resp = await cl.proxy.wait_for_private_msg()
        assert Message(resp['message']) == Message('echo!')
        await cl.proxy.wait_for_handler_complete()

        cl.proxy.send_private_msg('/ping')
        resp = await cl.proxy.wait_for_private_msg()
        assert Message(resp['message']) == Message('echo!')
        resp = await cl.proxy.wait_for_private_msg()
        assert Message(resp['message']) == Message('pong!')
        await cl.proxy.wait_for_handler_complete()
