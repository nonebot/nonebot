import time

import pytest

import nonebot
import testing.external.common.default_config as dc
from testing.external.common.client import BOT_SELF_ID, TESTER_ID, Client, run_nonebot_in_thread
from testing.external.common.pytest import AsyncTestCase
from testing.external.common.port import available_port


@pytest.mark.asyncio
class TestBasicsWork(AsyncTestCase):
    @pytest.fixture(scope='class')
    async def cl(self):
        nonebot.init(dc)
        nonebot.load_plugin('testing.external.test_notice_request.test_basics.basics')

        cl = Client()
        cl.patch_nonebot()

        run_nonebot_in_thread()
        async for p in cl.run_client_until_test_done(available_port):
            yield p

    async def test_fire_overload1(self, cl: Client):
        cl.send_payload({
            'time': time.time(),
            'self_id': BOT_SELF_ID,
            'post_type': 'request',
            'request_type': 'group',
            'sub_type': 'invite',
            'user_id': TESTER_ID,
            'comment': '',
        })
        await cl.proxy.wait_for_api_call(lambda p:
            p['action'] == '.handle_quick_operation_async'
            and p['params']['operation']['approve'] is False
            and p['params']['self_id'] == BOT_SELF_ID
            and p['params']['context']['user_id'] == TESTER_ID
        )

    async def test_fire_overload2(self, cl: Client):
        cl.send_payload({
            'time': time.time(),
            'self_id': BOT_SELF_ID,
            'post_type': 'request',
            'request_type': 'friend',
            'user_id': TESTER_ID,
            'comment': 'hello, I am your tester',
        })
        await cl.proxy.wait_for_api_call(lambda p:
            p['action'] == '.handle_quick_operation_async'
            and p['params']['operation']['approve'] is True
            and p['params']['operation']['remark'] == 'tester'
            and p['params']['self_id'] == BOT_SELF_ID
            and p['params']['context']['user_id'] == TESTER_ID
        )
