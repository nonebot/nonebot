# nonebot.helpers

## _def_ `context_id(event, *, mode='default', use_hash=False)`

- **说明**

  获取事件对应的上下文的唯一 ID。

- **参数**

  - `event` (aiocqhttp.event.Event): 事件对象

  - `mode` (str): ID 的计算模式

    - `'default'`: 默认模式，任何一个上下文都有其唯一 ID
    - `'group'`: 群组模式，同一个群组或讨论组的上下文（即使是不同用户）具有相同 ID
    - `'user'`: 用户模式，同一个用户的上下文（即使在不同群组）具有相同 ID

  - `use_hash` (bool): 是否将计算出的 ID 使用 MD5 进行哈希

- **返回**

  - str: 事件对应的上下文的唯一 ID

- **用法**

  ```python
  ctx_id = context_id(session.event, use_hash=True)
  ```

  获取当前 Session 的事件对应的上下文的唯一 ID，并进行 MD5 哈希，得到的结果可用于图灵机器人等 API 的调用。

## _async def_ `send(bot, event, message, *, ensure_private=False, ignore_failure=True, **kwargs)`

- **说明**

  发送消息到指定事件的上下文中。

- **参数**

  - `bot` ([NoneBot](./index.md#class-nonebot-config-object-none)): NoneBot 对象

  - `event` (aiocqhttp.event.Event): 事件对象

  - `message` ([Message_T](./typing.md#var-message-t)): 要发送的消息内容

  - `ensure_private` (bool): 确保消息发送到私聊，对于群组和讨论组消息上下文，会私聊发送者

  - `ignore_failure` (bool): 发送失败时忽略 `CQHttpError` 异常

  - `**kwargs`: 其它传入 `CQHttp.send()` 的命名参数

- **返回**

  - Any <Badge text="1.1.0+"/>: 返回 CQHTTP 插件发送消息接口的调用返回值，具体见 aiocqhttp 的 [API 调用](https://aiocqhttp.nonebot.dev/#/what-happened#api-%E8%B0%83%E7%94%A8)

- **异常**

  - `CQHttpError`: 发送失败时抛出，实际由 [aiocqhttp] 抛出，等价于 `aiocqhttp.Error`

- **用法**

  ```python
  await send(bot, event, 'hello')
  ```

## _async def_ `send_to_superusers(bot, message, **kwargs)` <Badge text="1.7.0+"/>

- **说明**

  发送私聊消息到全体超级用户（即配置下的 `SUPERUSERS`）。

- **参数**

  - `bot` ([NoneBot](./index.md#class-nonebot-config-object-none)): NoneBot 对象

  - `message` ([Message_T](./typing.md#var-message-t)): 要发送的消息内容

  - `**kwargs`: 其它传入 `bot.send_private_msg()` 的命名参数

- **返回**

  - None

- **异常**

  - `CQHttpError`: 发送失败时抛出，实际由 [aiocqhttp] 抛出，等价于 `aiocqhttp.Error`

- **用法**

  ```python
  await send_to_superusers(bot, f'被群 {event.group_id} 踢出了')
  ```

## _def_ `render_expression(expr, *args, escape_args=True, **kwargs)`

- **说明**

  渲染 Expression。

- **参数**

  - `expr` ([Expression_T](./typing.md#var-expression-t)): 要渲染的 Expression，对于 Expression 的三种类型: `str`、`Sequence[str]`、`(*Any, **Any) -> str`，行为分别是

    - `str`: 以 `*args`、`**kwargs` 为参数，使用 `str.format()` 进行格式化
    - `Sequence[str]`: 随机选择其中之一，进行上面 `str` 的操作
    - `(*Any, **Any) -> str`: 以 `*args`、`**kwargs` 为参数，调用该可调用对象/函数，对返回的字符串进行上面 `str` 的操作

  - `*args`: 渲染参数

  - `escape_args` (bool): 是否对渲染参数进行转义

  - `**kwargs`: 渲染参数

- **返回**

  - str: 渲染出的消息字符串

- **用法**

  ```python
  msg1 = render_expression(
      ['你好，{username}！', '欢迎，{username}～'],
      username=username
  )
  msg2 = render_expression('你所查询的城市是{}', city)
  ```