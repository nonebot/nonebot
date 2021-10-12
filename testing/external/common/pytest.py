import asyncio

import pytest


class AsyncTestCase:
    @pytest.fixture(scope='class')
    def event_loop(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        yield loop
        loop.close()
