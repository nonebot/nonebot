# nonebot

为方便使用，`nonebot` 模块从子模块导入了部分内容:

- `CQHttpError` -> [CQHttpError](./exceptions.md#library-attr-cqhttperror)
- `load_plugin` -> [load_plugin](./plugin.md#def-load-plugin-module-path-no-fast-false)
- `load_plugins` -> [load_plugins](./plugin.md#def-load-plugins-plugin-dir-module-prefix-no-fast-false)
- `load_builtin_plugins` -> [load_builtin_plugins](./plugin.md#def-load-builtin-plugins)
- `get_loaded_plugins` <Badge text="1.1.0+"/> -> [get_loaded_plugins](./plugin.md#def-get-loaded-plugins)
- `on_command` -> [on_command](./plugin.md#def-on-command-name-aliases-patterns-permission-only-to-me-true-privileged-false-shell-like-false-expire-timeout-run-timeout-session-class-none)
- `on_natural_language` -> [on_natural_language](./plugin.md#def-on-natural-language-keywords-none-permission-only-to-me-true-only-short-message-true-allow-empty-message-false)
- `on_notice` -> [on_notice](./plugin.md#def-on-notice-arg-none-events)
- `on_request` -> [on_request](./plugin.md#def-on-request-arg-none-events)
- `message_preprocessor` -> [message_preprocessor](./message.md#def-message-preprocessor-func)
- `Message` -> [Message](./message.md#library-attr-message)
- `MessageSegment` -> [MessageSegment](./message.md#library-attr-messagesegment)
- `CommandSession` -> [CommandSession](./command/index.md#class-commandsession-bot-event-cmd-current-arg-args-none)
- `CommandGroup` -> [CommandGroup](./command/group.md#class-commandgroup-name-permission-only-to-me-privileged-shell-like-expire-timeout-run-timeout-session-class)
- `NLPSession` -> [NLPSession](./natural_language.md#class-nlpsession-bot-event-msg)
- `NoticeSession` -> [NoticeSession](./notice_request.md#class-noticesession-bot-event)
- `RequestSession` -> [RequestSession](./notice_request.md#class-requestsession-bot-event)
- `context_id` <Badge text="1.2.0+"/> -> [context_id](./helpers.md#def-context-id-event-mode-default-use-hash-false)
- `SenderRoles` <Badge text="1.9.0+"/> -> [SenderRoles](./permission.md#class-senderroles-bot-event-sender)

## _class_ `NoneBot(config_object=None)`

- **说明**

  继承自 `aiocqhttp.CQHttp`

- **参数**

  - `config_object` (Any | None): 配置对象，类型不限，只要能够通过 `__getattr__` 和 `__dict__` 分别访问到单个和所有配置项即可，若没有传入，则使用默认配置

### _other-attr_ `asgi`

- **类型:** `Quart`

- **说明:**

    ASGI 对象，继承自 `aiocqhttp.CQHttp`，目前等价于 `server_app`。

### _other-attr_ `server_app`

- **类型:** `Quart`

- **说明:**

    内部的 Quart 对象，继承自 `aiocqhttp.CQHttp`。

### _other-attr_ `__getattr__`

- **说明:**

    获取用于 API 调用的 `Callable` 对象。

    对返回结果进行函数调用会调用 CQHTTP 的相应 API，请注意捕获 `CQHttpError` 异常，具体请参考 aiocqhttp 的 [API 调用](https://aiocqhttp.nonebot.dev/#/what-happened#api-%E8%B0%83%E7%94%A8)。

- **参数:**

    - `item: str`: 要调用的 API 动作名，请参考 CQHTTP 插件文档的 [API 列表](https://cqhttp.cc/docs/#/API?id=api-%E5%88%97%E8%A1%A8)

- **返回:**

    - `(*Any, **Any) -> Any`: 用于 API 调用的 `Callable` 对象

- **用法:**

    ```python
    bot = nonebot.get_bot()
    try:
        info = await bot.get_group_member_info(group_id=1234567, user_id=12345678)
    except CQHttpError as e:
        logger.exception(e)
    ```

### _instance-var_ `config`

- **类型:** 

- **说明:** 配置对象

### _method_ `run(self, host=None, port=None, *args, **kwargs)`

- **说明**

  运行 NoneBot。

  不建议直接运行 NoneBot 对象，而应该使用全局的 `run()` 函数。

- **参数**

  - `host` (str | None): 主机名／IP

  - `port` (int | None): 端口

  - `*args`: 其它传入 `CQHttp.run()` 的位置参数

  - `**kwargs`: 其它传入 `CQHttp.run()` 的命名参数

- **返回**

  - None

## _def_ `init(config_object=None, start_scheduler=True)`

- **说明**

  初始化全局 NoneBot 对象。

- **参数**

  - `config_object` (Any | None): 配置对象，类型不限，只要能够通过 `__getattr__` 和 `__dict__` 分别访问到单个和所有配置项即可，若没有传入，则使用默认配置

  - `start_scheduler` (bool) <Badge text="1.7.0+"/>: 是否要启动 `nonebot.scheduler`

- **返回**

  - None

- **用法**

  ```python
  import config
  nonebot.init(config)
  ```

  导入 `config` 模块并初始化全局 NoneBot 对象。

## _def_ `get_bot()`

- **说明**

  获取全局 NoneBot 对象。可用于在计划任务的回调中获取当前 NoneBot 对象。

- **返回**

  - NoneBot: 全局 NoneBot 对象

- **异常**

  - `ValueError`: 全局 NoneBot 对象尚未初始化

- **用法**

  ```python
  bot = nonebot.get_bot()
  ```

## _def_ `run(host=None, port=None, *args, **kwargs)`

- **说明**

  运行全局 NoneBot 对象。

- **参数**

  - `host` (str | None): 主机名／IP，若不传入则使用配置文件中指定的值

  - `port` (int | None): 端口，若不传入则使用配置文件中指定的值

  - `*args`: 其它传入 `CQHttp.run()` 的位置参数

  - `**kwargs`: 其它传入 `CQHttp.run()` 的命名参数

- **返回**

  - None

- **用法**

  ```python
  nonebot.run(host='127.0.0.1', port=8080)
  ```

  在 `127.0.0.1:8080` 运行全局 NoneBot 对象。

## _def_ `on_startup(func)` <Badge text="1.5.0+"/>

- **说明**

  将函数装饰为 NoneBot 启动时的回调函数。

- **参数**

  - `func` (() -> Awaitable[NoneType])

- **返回**

  - () -> Awaitable[NoneType]

- **用法**

  ```python
  @on_startup
  async def startup()
      await db.init()
  ```

  注册启动时回调，初始化数据库。

## _def_ `on_websocket_connect(func)` <Badge text="1.5.0+"/>

- **说明**

  将函数装饰为 CQHTTP 反向 WebSocket 连接建立时的回调函数。

  该装饰器等价于 `@bot.on_meta_event('lifecycle.connect')`。

- **参数**

  - `func` ((aiocqhttp.event.Event) -> Awaitable[NoneType])

- **返回**

  - () -> Awaitable[NoneType]

- **用法**

  ```python
  @on_websocket_connect
  async def connect(event: aiocqhttp.Event):
      bot = nonebot.get_bot()
      groups = await bot.get_group_list()
  ```

  注册 WebSocket 连接时回调，获取群列表。