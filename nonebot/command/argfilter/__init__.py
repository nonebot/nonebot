"""
本模块主要用于命令参数过滤相关的功能。

命令参数过滤器主要有下面几种:

- 提取器，从用户输入的原始参数内容中提取需要的内容，`extractors` 子模块中提供了一些常用提取器
- 修剪器，将用户输入的原始参数内容进行适当修剪，例如 `str.strip` 可以去掉两遍的空白字符
- 验证器，验证参数的格式、长度等是否符合要求，`validators` 子模块中提供了一些常用验证器
- 转换器，将参数进行类型或格式上的转换，例如 `int` 可以将字符串转换成整数，`converters` 子模块中提供了一些常用转换器
- 控制器，根据用户输入或当前会话状态对会话进行相关控制，例如当用户发送 `算了` 时停止当前会话，`controllers` 子模块中提供了一些常用控制器

版本: 1.2.0+
"""
from typing import Optional

from nonebot.typing import Message_T


class ValidateError(ValueError):
    """用于表示验证失败的异常类。"""

    def __init__(self, message: Optional[Message_T] = None):
        self.message = message
        """验证失败时要发送的错误提示消息。如果为 `None`，则使用配置中的 `DEFAULT_VALIDATION_FAILURE_EXPRESSION`。"""


__all__ = [
    'ValidateError',
]
