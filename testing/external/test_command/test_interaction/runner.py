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
        nonebot.load_plugin('docs.guide.code.awesome-bot-2.awesome.plugins.weather')

        cl = Client()
        cl.patch_nonebot()

        run_nonebot_in_thread()
        async for p in cl.run_client_until_test_done(available_port):
            yield p

    async def test_direct(self, cl: Client):
        cl.proxy.send_private_msg('/weather 合肥')
        resp = await cl.proxy.wait_for_private_msg()
        assert Message(resp['message']) == Message('合肥的天气是……')
        await cl.proxy.wait_for_handler_complete()

    async def test_once(self, cl: Client):
        cl.proxy.send_private_msg('/weather')
        resp = await cl.proxy.wait_for_private_msg()
        assert Message(resp['message']) == Message('你想查询哪个城市的天气呢？')
        cl.proxy.send_private_msg('合肥')
        resp = await cl.proxy.wait_for_private_msg()
        assert Message(resp['message']) == Message('合肥的天气是……')
        await cl.proxy.wait_for_handler_complete()

    async def test_loop(self, cl: Client):
        cl.proxy.send_private_msg('/weather')
        resp = await cl.proxy.wait_for_private_msg()
        assert Message(resp['message']) == Message('你想查询哪个城市的天气呢？')
        for _ in range(5):
            cl.proxy.send_private_msg(' ')
            resp = await cl.proxy.wait_for_private_msg()
            assert Message(resp['message']) == Message('要查询的城市名称不能为空呢，请重新输入')
        cl.proxy.send_private_msg('合肥')
        resp = await cl.proxy.wait_for_private_msg()
        assert Message(resp['message']) == Message('合肥的天气是……')
        await cl.proxy.wait_for_handler_complete()
