from testing.external.common.client import run_test_as_subprocess


class TestCommand:
    def test_basics_work(self):
        assert run_test_as_subprocess('test_command/test_basics') == 0

    def test_interaction(self):
        assert run_test_as_subprocess('test_command/test_interaction') == 0


class TestNaturalLanguage:
    def test_basics_work(self):
        assert run_test_as_subprocess('test_natural_language/test_basics') == 0


class TestMessage:
    def test_basics_work(self):
        assert run_test_as_subprocess('test_message/test_basics') == 0


class TestNoticeRequest:
    def test_basics_work(self):
        assert run_test_as_subprocess('test_notice_request/test_basics') == 0
