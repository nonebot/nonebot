# nonebot.command.argfilter.converters <Badge text="1.2.0+"/>

提供几种常用的转换器。

## _def_ `simple_chinese_to_bool(text)`

- **说明**

  将中文（`好`、`不行` 等）转换成布尔值。

  例如:
      是的 -> True
      好的呀 -> True
      不要 -> False
      不用了 -> False
      你好呀 -> None

- **参数**

  - `text` (str)

- **返回**

  - bool | None

## _def_ `split_nonempty_lines(text)`

- **说明**

  按行切割文本，并忽略所有空行。

- **参数**

  - `text` (str)

- **返回**

  - list[str]

## _def_ `split_nonempty_stripped_lines(text)`

- **说明**

  按行切割文本，并对每一行进行 `str.strip`，再忽略所有空行。

- **参数**

  - `text` (str)

- **返回**

  - list[str]