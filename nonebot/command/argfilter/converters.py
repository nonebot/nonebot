"""
提供几种常用的转换器。

版本: 1.2.0+
"""
from typing import Optional, List


def simple_chinese_to_bool(text: str) -> Optional[bool]:
    """将中文（`好`、`不行` 等）转换成布尔值。

    例如:
        是的 -> True
        好的呀 -> True
        不要 -> False
        不用了 -> False
        你好呀 -> None
    """
    text = text.strip().lower().replace(' ', '') \
        .rstrip(',.!?~，。！？～了的呢吧呀啊呗啦')
    if text in {
            '要', '用', '是', '好', '对', '嗯', '行', 'ok', 'okay', 'yeah', 'yep',
            '当真', '当然', '必须', '可以', '肯定', '没错', '确定', '确认'
    }:
        return True
    if text in {
            '不', '不要', '不用', '不是', '否', '不好', '不对', '不行', '别', 'no', 'nono',
            'nonono', 'nope', '不ok', '不可以', '不能', '不可以'
    }:
        return False
    return None


def split_nonempty_lines(text: str) -> List[str]:
    """按行切割文本，并忽略所有空行。"""
    return list(filter(lambda x: x, text.splitlines()))


def split_nonempty_stripped_lines(text: str) -> List[str]:
    """按行切割文本，并对每一行进行 `str.strip`，再忽略所有空行。"""
    return list(filter(lambda x: x, map(lambda x: x.strip(),
                                        text.splitlines())))


__all__ = [
    'simple_chinese_to_bool',
    'split_nonempty_lines',
    'split_nonempty_stripped_lines',
]
