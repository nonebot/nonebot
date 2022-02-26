# nonebot.notice_request

## _class_ `NoticeSession(bot, event)`

- **说明**

  继承自 `BaseSession` 类，表示通知类事件的 Session。

- **参数**

  - `bot` ([NoneBot](./index.md#class-nonebot-config-object-none))

  - `event` (aiocqhttp.event.Event)

## _class_ `RequestSession(bot, event)`

- **说明**

  继承自 `BaseSession` 类，表示请求类事件的 Session。

- **参数**

  - `bot` ([NoneBot](./index.md#class-nonebot-config-object-none))

  - `event` (aiocqhttp.event.Event)

### _async method_ `approve(self, remark='')`

- **说明**

  同意当前请求。

- **参数**

  - `remark` (str): 好友备注，只在好友请求时有效

- **返回**

  - None

- **异常**

  - `CQHttpError`: 发送失败时抛出，实际由 [aiocqhttp] 抛出，等价于 `aiocqhttp.Error`

- **用法**

  ```python
  await session.approve()
  ```

### _async method_ `reject(self, reason='')`

- **说明**

  拒绝当前请求。

- **参数**

  - `reason` (str): 拒绝理由，只在群请求时有效

- **返回**

  - None

- **异常**

  - `CQHttpError`: 发送失败时抛出，实际由 [aiocqhttp] 抛出，等价于 `aiocqhttp.Error`

- **用法**

  ```python
  await session.reject()
  ```