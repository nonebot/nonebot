"""
提供几种常用的提取器。

版本: 1.2.0+
"""
import re
from typing import List

from aiocqhttp.message import Message

from nonebot.typing import Message_T


def extract_text(arg: Message_T) -> str:
    """提取消息中的纯文本部分（使用空格合并纯文本消息段）。"""
    arg_as_msg = Message(arg)
    return arg_as_msg.extract_plain_text()


def extract_image_urls(arg: Message_T) -> List[str]:
    """提取消息中的图片 URL 列表。"""
    arg_as_msg = Message(arg)
    return [
        s.data['url']
        for s in arg_as_msg
        if s.type == 'image' and 'url' in s.data
    ]


def extract_numbers(arg: Message_T) -> List[float]:
    """提取消息中的所有数字（浮点数）。"""
    s = str(arg)
    return list(map(float, re.findall(r'[+-]?(\d*\.?\d+|\d+\.?\d*)', s)))


__all__ = [
    'extract_text',
    'extract_image_urls',
    'extract_numbers',
]
