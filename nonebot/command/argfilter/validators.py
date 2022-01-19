"""
提供几种常用的验证器。

这些验证器的工厂函数全都接受可选参数 `message: Message_T | None`，用于在验证失败时向用户发送错误提示。使用这些的验证器时，必须先调用验证器的工厂函数，其返回结果才是真正的验证器，例如:

```python
session.get('arg1', prompt='请输入 arg1：',
            arg_filters=[extract_text， not_empty('输入不能为空')])
```

注意 `extract_text` 和 `not_empty` 使用上的区别。

版本: 1.2.0+
"""
import re
from typing import Callable, Any

from nonebot.typing import Filter_T
from nonebot.command.argfilter import ValidateError


class BaseValidator:
    """INTERNAL API"""

    def __init__(self, message=None):
        self.message = message

    def raise_failure(self):
        raise ValidateError(self.message)


def _raise_failure(message):
    raise ValidateError(message)


def not_empty(message=None) -> Filter_T:
    """验证输入不为空。"""

    def validate(value):
        if value is None:
            _raise_failure(message)
        if hasattr(value, '__len__') and value.__len__() == 0:
            _raise_failure(message)
        return value

    return validate


def fit_size(min_length: int = 0, max_length: int = None,
             message=None) -> Filter_T:
    """验证输入的长度（大小）在 `min_length` 到 `max_length` 之间（包括两者）。

    参数:
        min_length: 最小长度
        max_length: 最大长度
    """

    def validate(value):
        length = len(value) if value is not None else 0
        if length < min_length or \
                (max_length is not None and length > max_length):
            _raise_failure(message)
        return value

    return validate


def match_regex(pattern: str, message=None, *, flags=0,
                fullmatch: bool = False) -> Filter_T:
    """验证输入是否匹配正则表达式。

    参数:
        pattern: 正则表达式
        flags: 传入 `re.compile()` 的标志
        fullmatch: 是否使用完全匹配（`re.fullmatch()`）
    """

    pattern_ = re.compile(pattern, flags)

    def validate(value):
        if fullmatch:
            if not re.fullmatch(pattern_, value):
                _raise_failure(message)
        else:
            if not re.match(pattern_, value):
                _raise_failure(message)
        return value

    return validate


def ensure_true(bool_func: Callable[[Any], bool], message=None) -> Filter_T:
    """验证输入是否能使给定布尔函数返回 `True`。

    参数:
        bool_func: 接受输入、返回布尔值的函数
    """

    def validate(value):
        if bool_func(value) is not True:
            _raise_failure(message)
        return value

    return validate


def between_inclusive(start=None, end=None, message=None) -> Filter_T:
    """验证输入是否在 `start` 到 `end` 之间（包括两者）。

    参数:
        start: 范围开始
        end: 范围结束
    """

    def validate(value):
        if start is not None and value < start:
            _raise_failure(message)
        if end is not None and end < value:
            _raise_failure(message)
        return value

    return validate


__all__ = [
    'not_empty',
    'fit_size',
    'match_regex',
    'ensure_true',
    'between_inclusive',
]

__autodoc__ = {
    "BaseValidator": False
}
