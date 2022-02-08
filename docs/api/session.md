# nonebot.session

## _class_ `BaseSession(bot, event)`

- **说明**

  基础 session 类，`CommandSession` 等均继承自此类。

- **参数**

  - `bot` ([NoneBot](./index.md#class-nonebot-config-object-none))

  - `event` (aiocqhttp.event.Event)

### _instance-var_ `bot`

- **类型:** 

- **说明:** Session 对应的 NoneBot 对象。

- **用法**

  ```python
  await session.bot.send('hello')
  ```

  在当前 Session 对应的上下文中发送 `hello`。

### _property_ `ctx` <Badge text="1.5.0-" type="error"/>

- **类型:** aiocqhttp.event.Event

- **说明:** CQHTTP 上报的事件数据对象，或称事件上下文，具体请参考 [事件上报](https://cqhttp.cc/docs/#/Post)。

- **用法**

  ```python
  user_id = session.ctx['user_id']
  ```

  获取当前事件的 `user_id` 字段。

### _instance-var_ `event` <Badge text="1.5.0+"/>

- **类型:** 

- **说明:** CQHTTP 上报的事件数据对象，具体请参考 [`aiocqhttp.Event`](https://aiocqhttp.nonebot.dev/module/aiocqhttp/index.html#aiocqhttp.Event) 和 [事件上报](https://cqhttp.cc/docs/#/Post)。

- **用法**

  ```python
  user_id = session.event['user_id']
  group_id = session.event.group_id
  ```

  获取当前事件的 `user_id` 和 `group_id` 字段。

### _property_ `self_id` <Badge text="1.1.0+"/>

- **类型:** int

- **说明**

  当前 session 对应的 QQ 机器人账号，在多个机器人账号使用同一个 NoneBot 后端时可用于区分当前收到消息或事件的是哪一个机器人。

  等价于 `session.event.self_id`。

- **用法**

  ```python
  await bot.send_private_msg(self_id=session.self_id, user_id=12345678, message='Hello')
  ```

### _async method_ `send(self, message, *, at_sender=False, ensure_private=False, ignore_failure=True, **kwargs)`

- **说明**

  发送消息到 Session 对应的上下文中。

- **参数**

  - `message` (str | dict[str, Any] | list[dict[str, Any]]): 要发送的消息内容

  - `at_sender` (bool): 是否 @ 发送者，对私聊不起作用

  - `ensure_private` (bool): 确保消息发送到私聊，对于群组和讨论组消息上下文，会私聊发送者

  - `ignore_failure` (bool): 发送失败时忽略 `CQHttpError` 异常

  - `**kwargs`: 其它传入 `CQHttp.send()` 的命名参数

- **返回**

  - Any <Badge text="1.1.0+"/>: 返回 CQHTTP 插件发送消息接口的调用返回值，具体见 aiocqhttp 的 [API 调用](https://aiocqhttp.nonebot.dev/#/what-happened#api-%E8%B0%83%E7%94%A8)

- **异常**

  - `CQHttpError`: 发送失败时抛出，实际由 [aiocqhttp] 抛出，等价于 `aiocqhttp.Error`

- **用法**

  ```python
  await session.send('hello')
  ```

  在当前 Session 对应的上下文中发送 `hello`。