from testing.external.common.client import run_test_as_subprocess


class TestBasicsWork:
    def test_basics_work(self):
        assert run_test_as_subprocess('test_command/test_basics_work') == 0
