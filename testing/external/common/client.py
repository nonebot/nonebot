import asyncio
import platform
import logging
import threading
import re
import json
import time
import subprocess
from typing import AsyncGenerator, Optional
from urllib.request import urlopen

import websockets
from nonebot.typing import Message_T


BOT_SELF_ID = 192837
TESTER_ID = 1234567
TESTER_GROUP = 45678

MERCY_TM = 1


class Client:
    def __init__(self):
        self.proxy = Proxy(self)
        self.nb_log_queue = asyncio.Queue()  # type: asyncio.Queue[logging.LogRecord]
        self.receive_queue = asyncio.Queue()
        self.submit_queue = asyncio.Queue()
        self.port = None

    def patch_nonebot(self):
        '''
        Patches the logger so that we can copy the logging output from nonebot.
        Add a stop endpoint so that we can exit NoneBot thread.
        '''
        que = self.nb_log_queue

        class _Handler(logging.Handler):
            def emit(self, record: logging.LogRecord) -> None:
                que.put_nowait(record)

        from nonebot.log import logger
        logger.addHandler(_Handler())

        from nonebot import get_bot
        bot = get_bot()

        @bot.server_app.route('/exit')
        async def _():
            import sys
            sys.exit(0)

    def stop_nonebot(self):
        try:
            urlopen(f'http://127.0.0.1:{self.port}/exit').read()
        except Exception:
            pass

    async def connect_to_nonebot(self, local_port: int, load_timeout: float = MERCY_TM) -> AsyncGenerator:
        '''Act as a OneBot instance that talks to local NoneBot thread.'''
        await self.wait_for_matching_log(r'^Running on .*$', tm=load_timeout)
        async with websockets.connect(f'ws://127.0.0.1:{local_port}/ws', extra_headers={  # type: ignore
            'X-Self-ID': BOT_SELF_ID,
            'X-Client-Role': 'Universal',
        }) as ws:
            self.port = local_port
            yield

            async def _receiver():
                while True:
                    msg = await ws.recv()
                    self.receive_queue.put_nowait(msg)

            async def _sender():
                while True:
                    msg = await self.submit_queue.get()
                    await ws.send(msg)

            async def gatherer():
                try:
                    await asyncio.gather(_receiver(), _sender())
                except websockets.exceptions.ConnectionClosedOK:  # type: ignore
                    pass
                except RuntimeError as e:
                    if 'Event loop is closed' in str(e):
                        pass
                    raise

            yield gatherer()
        yield

    async def run_client_until_test_done(self, local_port: int, load_timeout: float = MERCY_TM) -> AsyncGenerator:
        '''Provide this wrapper because it's very difficult to understand connect_to_nonebot'''
        cl_conn = self.connect_to_nonebot(local_port, load_timeout)
        await cl_conn.__anext__()
        task = asyncio.create_task(await cl_conn.__anext__())
        await asyncio.sleep(0)
        yield self
        task.cancel()
        await cl_conn.__anext__()
        self.stop_nonebot()

    async def wait_for_matching_log(self, *pats: str, tm: float = MERCY_TM):
        while True:
            try:
                log = await asyncio.wait_for(self.nb_log_queue.get(), timeout=tm)
            except asyncio.TimeoutError:
                raise Exception('No matching log record within acceptable timeout')
            for pat in pats:
                if re.match(pat, log.msg):
                    return log.msg

    def send_payload(self, payload):
        self.submit_queue.put_nowait(json.dumps(payload))

    async def receive_payload(self, tm: float = MERCY_TM):
        return json.loads(await asyncio.wait_for(self.receive_queue.get(), timeout=tm))


class Proxy:
    def __init__(self, cl: Client):
        self.cl = cl
        self.msgid = -1

    def get_msgid(self):
        self.msgid += 1
        return self.msgid

    def send_private_msg(self, content: Message_T, extra: Optional[dict] = None):
        # https://github.com/botuniverse/onebot/blob/master/v11/specs/event/message.md
        self.cl.send_payload(merge({
            'time': time.time(),
            'self_id': BOT_SELF_ID,
            'post_type': 'message',
            'message_type': 'private',
            'sub_type': 'friend',
            'message_id': self.get_msgid(),
            'user_id': TESTER_ID,
            'message': str(content),
            'raw_message': str(content),
            'sender': {
                'user_id': TESTER_ID,
                'nickname': 'tester_nickname',
                'sex': 'female',
                'age': 16,
            },
        }, extra))

    def send_group_msg(self, content: Message_T, extra: Optional[dict] = None):
        self.cl.send_payload(merge({
            'time': time.time(),
            'self_id': BOT_SELF_ID,
            'post_type': 'message',
            'message_type': 'group',
            'sub_type': 'normal',
            'message_id': self.get_msgid(),
            'group_id': TESTER_GROUP,
            'user_id': TESTER_ID,
            'anonymous': None,
            'message': str(content),
            'raw_message': str(content),
            'sender': {
                'user_id': TESTER_ID,
                'nickname': 'tester_nickname',
                'card': 'tester_card',
                'sex': 'female',
                'age': 16,
                'area': '',
                'role': 'member',
                'title': '',
            },
        }, extra))

    async def wait_for_handler_complete(self, tm: float = MERCY_TM):
        '''Wait until NoneBot has finished running handle_message function.'''
        return await self.cl.wait_for_matching_log(
            r'^Message .+ is ignored: .*$',
            r'^Message .+ is handled as a command$',
            r'^Message .+ is handled as natural language$',
            r'^Message .+ was not handled$',
            tm=tm)

    async def wait_for_api_call(self,
        payload_filter=lambda payload: None,
        stub_func=lambda payload: None,
        tm: float = MERCY_TM):
        while True:
            msg = await self.cl.receive_payload(tm)
            if not payload_filter(msg):
                continue
            self.cl.send_payload({
                'status': 'ok',
                'data': stub_func(msg),
                'echo': msg.get('echo', None),
            })
            return msg['params']

    async def wait_for_private_msg(self, tm: float = MERCY_TM):
        return await self.wait_for_api_call(
            payload_filter=lambda p: (p['action'] == 'send_msg' and p['params']['message_type'] == 'private')
                or (p['action'] == 'send_private_msg'),  # noqa: E131
            stub_func=lambda _: {
                'message_id': self.get_msgid(),
            },
            tm=tm,
        )

    async def wait_for_group_msg(self, tm: float = MERCY_TM):
        return await self.wait_for_api_call(
            payload_filter=lambda p: (p['action'] == 'send_msg' and p['params']['message_type'] == 'group')
                or (p['action'] == 'send_group_msg'),  # noqa: E131
            stub_func=lambda _: {
                'message_id': self.get_msgid(),
            },
            tm=tm,
        )


def merge(d1: dict, d2: Optional[dict] = None):
    if d2 is None:
        return d1
    for k in d1:
        if isinstance(d1[k], dict) and isinstance(d2.get(k, None), dict):
            d2[k] = merge(d1[k], d2[k])
    d1.update(d2)
    return d1


def run_test_as_subprocess(test_name: str) -> int:
    return subprocess.run(['python', '-m', 'pytest', f'testing/external/{test_name}/runner.py', '-vv', '-s']).returncode


def run_nonebot_in_thread(*args, **kwargs):
    def _nonebot_run_patched():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        if platform.system() == 'Linux':
            # avoid "set_wakeup_fd only works in main thread" exception when starting Quart server
            loop.add_signal_handler = lambda *a, **k: None  # type: ignore
        import nonebot
        nonebot.run(*args, **kwargs, loop=loop)
    threading.Thread(target=_nonebot_run_patched).start()
