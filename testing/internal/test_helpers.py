import functools

from nonebot.helpers import separate_async_funcs


def apply(f): return lambda o: f(o)


class Test_separate_async_funcs:
    def test_regular_funcs(self):
        sync1 = lambda _: True  # noqa: E731
        def sync2(_): return True
        async def async1(_): return True

        syncs, asyncs = separate_async_funcs([sync1, sync2, async1, sync2, async1])
        assert syncs == [sync1, sync2, sync2]
        assert asyncs == [async1, async1]

    def test_class_def(self):
        class sync1:
            @staticmethod
            def __call__(_): return True

        class sync2:
            @classmethod
            def __call__(cls, _): return True

        @apply(lambda c: c())
        class sync3:
            def __call__(self, _): return True

        class async1:
            @staticmethod
            async def __call__(_): return True

        class async2:
            @classmethod
            async def __call__(cls, _): return True

        @apply(lambda c: c())
        class async3:
            async def __call__(self, _): return True

        sync4 = sync2()
        async4 = async2()

        syncs, asyncs = separate_async_funcs([sync1, sync2, sync3, async1, async2, async3, sync4, async4])
        assert syncs == [sync1, sync2, sync3, sync4]
        assert asyncs == [async1, async2, async3, async4]

    def test_builtin_partial(self):
        def wrapme_sync(a, b, c): return True
        sync1 = functools.partial(wrapme_sync, 1, 2)
        sync2 = functools.partial(functools.partial(wrapme_sync, 1), 2)

        @apply(lambda c: functools.partial(c(), 1, 2))
        class sync3:
            def __call__(self, a, b, c): return True

        async def wrapme_async(a, b, c): return True
        async1 = functools.partial(wrapme_async, 1, 2)
        async2 = functools.partial(functools.partial(wrapme_async, 1), 2)

        @apply(lambda c: functools.partial(c(), 1, 2))
        class async3:
            async def __call__(self, a, b, c): return True

        syncs, asyncs = separate_async_funcs([sync1, sync2, sync3, async1, async2, async3])
        assert syncs == [sync1, sync2, sync3]
        assert asyncs == [async1, async2, async3]
