# nonebot.command.argfilter.validators <Badge text="1.2.0+"/>

提供几种常用的验证器。

这些验证器的工厂函数全都接受可选参数 `message: Message_T | None`，用于在验证失败时向用户发送错误提示。使用这些的验证器时，必须先调用验证器的工厂函数，其返回结果才是真正的验证器，例如:

```python
session.get('arg1', prompt='请输入 arg1：',
            arg_filters=[extract_text， not_empty('输入不能为空')])
```

注意 `extract_text` 和 `not_empty` 使用上的区别。

## _def_ `not_empty(message=None)`

- **说明**

  验证输入不为空。

- **参数**

  - `message`

- **返回**

  - (Any) -> Any | Awaitable[Any]

## _def_ `fit_size(min_length=0, max_length=None, message=None)`

- **说明**

  验证输入的长度（大小）在 `min_length` 到 `max_length` 之间（包括两者）。

- **参数**

  - `min_length` (int): 最小长度

  - `max_length` (int): 最大长度

  - `message`

- **返回**

  - (Any) -> Any | Awaitable[Any]

## _def_ `match_regex(pattern, message=None, *, flags=0, fullmatch=False)`

- **说明**

  验证输入是否匹配正则表达式。

- **参数**

  - `pattern` (str): 正则表达式

  - `message`

  - `flags`: 传入 `re.compile()` 的标志

  - `fullmatch` (bool): 是否使用完全匹配（`re.fullmatch()`）

- **返回**

  - (Any) -> Any | Awaitable[Any]

## _def_ `ensure_true(bool_func, message=None)`

- **说明**

  验证输入是否能使给定布尔函数返回 `True`。

- **参数**

  - `bool_func` ((Any) -> bool): 接受输入、返回布尔值的函数

  - `message`

- **返回**

  - (Any) -> Any | Awaitable[Any]

## _def_ `between_inclusive(start=None, end=None, message=None)`

- **说明**

  验证输入是否在 `start` 到 `end` 之间（包括两者）。

- **参数**

  - `start`: 范围开始

  - `end`: 范围结束

  - `message`

- **返回**

  - (Any) -> Any | Awaitable[Any]