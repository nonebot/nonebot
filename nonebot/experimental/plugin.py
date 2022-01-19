"""
为了保持向前的兼容，在 1.9.0 后此模块仅导出与主包完全相同的 `on_command` 和 `on_natural_language` 两个函数。会在未来版本中移除。

版本: 1.8.0+
"""
from nonebot.plugin import on_command, on_natural_language


# backward compatibility
__all__ = [
    'on_command',
    'on_natural_language'
]
