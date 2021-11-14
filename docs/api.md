---
sidebar: auto
---

# API

在以下文档中提到的类，函数等被视为公开的 API，详情请见 [CONTRIBUTING](https://github.com/nonebot/nonebot/blob/master/CONTRIBUTING.md#%E4%BB%A3%E7%A0%81%E9%A3%8E%E6%A0%BC). 你可以使用这里没有暴露的 API（"INTERNAL APIs"），但是其行为可能会在不通知用户的情况下发生变化。

## 类型

下面的 API 文档中，「类型」部分使用 Python 的 Type Hint 语法，见 [PEP 484](https://www.python.org/dev/peps/pep-0484/), [PEP 526](https://www.python.org/dev/peps/pep-0526/), [PEP 604](https://www.python.org/dev/peps/pep-0604/) 和 [typing](https://docs.python.org/3/library/typing.html)。

除了 Python 内置的类型，下面还出现了如下 NoneBot 自定类型，实际上它们是 Python 内置类型的别名。

以下类型均可从 `nonebot.typing` 模块导入。

### `Context_T` <Badge text="1.5.0-" type="error"/>

- **类型:** `dict[str, Any]`

- **说明:**

  CQHTTP 上报的事件数据对象的类型。

### `Message_T`

- **类型:** `str | dict[str, Any] | list[dict[str, Any]]`

- **说明:**

  消息对象的类型，通常表示 NoneBot 提供的消息相关接口所支持的类型，`nonebot.message.Message` 也是一个合法的 `Message_T`。

### `Expression_T`

- **类型:** `str | Sequence[str] | (*Any, **Any) -> str` <Badge text="v1.8.0+"/>

- **说明:**

  Expression 对象的类型。

### `CommandName_T`

- **类型:** `tuple[str]`

- **说明:**

  命令名称的类型。

### `CommandArgs_T`

- **类型:** `dict[str, Any]`

- **说明:**

  命令参数的类型。

### `CommandHandler_T` <Badge text="1.6.0+"/>

- **类型:** `(CommandSession) -> Awaitable[Any]` <Badge text="1.8.1+"/>

- **说明:**

  命令处理函数

### `Patterns_T` <Badge text="1.7.0+"/>

- **类型:** `Iterable[str] | str | Iterable[Pattern[str]] | Pattern[str]` <Badge text="v1.8.0+"/>

- **说明:**

  正则参数类型，可以是正则表达式或正则表达式组。

### `State_T` <Badge text="1.2.0+"/>

- **类型:** `dict[str, Any]`

- **说明:**

  命令会话的状态（`state` 属性）的类型。

### `Filter_T` <Badge text="1.2.0+"/>

- **类型:** `(Any) -> (Any | Awaitable[Any])`

- **说明:**

  过滤器的类型。

  例如：

  ```python
  async def validate(value):
      if value > 100:
          raise ValidateError('数值必须小于 100')
      return value
  ```

### `PermChecker_T` <Badge text="v1.8.0+"/>

- **类型:** `(NoneBot, CQEvent) -> Awaitable[bool]`

- **说明:**

  已弃用。

### `NLPHandler_T` <Badge text="1.8.1+"/>

- **类型:** `(NLPSession) -> Awaitable[IntentCommand | None]`

- **说明:**

  自然语言处理函数。

### `NoticeHandler_T` <Badge text="1.8.1+"/>

- **类型:** `(NoticeSession) -> Awaitable[Any]`

- **说明:**

  通知处理函数。

### `RequestHandler_T` <Badge text="1.8.1+"/>

- **类型:** `(RequestSession) -> Awaitable[Any]`

- **说明:**

  请求处理函数。

### `MessagePreprocessor_T` <Badge text="1.8.1+"/>

- **类型:** `(NoneBot, CQEvent, PluginManager) -> Awaitable[Any]`

- **说明:**

  消息预处理函数。

### `PermissionPolicy_T` <Badge text="1.9.0+"/>

- **类型:** `(SenderRoles) -> bool | (SenderRoles) -> Awaitable[bool]`

- **说明:**

  向命令或自然语言处理器传入的权限检查策略。此类型是一个（同步/异步）函数，接受 `SenderRoles` 作为唯一的参数。此函数返回布尔值，返回 `True` 则表示权限检查通过，可以进行下一步处理（触发命令），反之返回 `False`。

### `PluginLifetimeHook_T` <Badge text="1.9.0+"/>

- **类型:** `() -> Any | () -> Awaitable[Any]`

- **说明:**

  插件生命周期事件回调函数。

## 配置

### `API_ROOT`

- **类型:** `str`

- **默认值:** `''`

- **说明:**

  CQHTTP 插件的 HTTP 接口地址，如果不使用 HTTP 通信，则无需设置。

- **用法:**

  ```python
  API_ROOT = 'http://127.0.0.1:5700'
  ```

  告诉 NoneBot CQHTTP 插件的 HTTP 服务运行在 `http://127.0.0.1:5700`。

### `ACCESS_TOKEN`

- **类型:** `str`

- **默认值:** `''`

- **说明:**

  需要和 CQHTTP 插件的配置中的 `access_token` 相同。

### `SECRET`

- **类型:** `str`

- **默认值:** `''`

- **说明:**

  需要和 CQHTTP 插件的配置中的 `secret` 相同。

### `HOST`

- **类型:** `str`

- **默认值:** `'127.0.0.1'`

- **说明:**

  NoneBot 的 HTTP 和 WebSocket 服务端监听的 IP／主机名。

- **用法:**

  ```python
  HOST = '0.0.0.0'
  ```

  监听服务器的所有 IP。

### `PORT`

- **类型:** `int`

- **默认值:** `8080`

- **说明:**

  NoneBot 的 HTTP 和 WebSocket 服务端监听的端口。

- **用法:**

  ```python
  PORT = 9876
  ```

  监听 9876 端口。

### `DEBUG`

- **类型:** `bool`

- **默认值:** `True`

- **说明:**

  是否以调试模式运行，生产环境需要设置为 `False` 以提高性能。

- **用法:**

  ```python
  DEBUG = False
  ```

  不使用调试模式运行。

### `SUPERUSERS`

- **类型:** `Collection[int]` <Badge text="1.7.0+"/>

- **默认值:** `set()`

- **说明:**

  超级用户的 QQ 号，用于命令的权限检查。

- **用法:**

  ```python
  SUPERUSERS = {12345678, 87654321}
  ```

  设置 `12345678` 和 `87654321` 为超级用户。

### `NICKNAME`

- **类型:** `str | Iterable[str]`

- **默认值:** `''`

- **说明:**

  机器人的昵称，用于辨别用户是否在和机器人说话。

- **用法:**

  ```python
  NICKNAME = {'奶茶', '小奶茶'}
  ```

  用户可以通过「奶茶」或「小奶茶」来呼唤机器人。

### `COMMAND_START`

- **类型:** `Iterable[str | Pattern]`

- **默认值:** `{'/', '!', '／', '！'}`

- **说明:**

  命令的起始标记，用于判断一条消息是不是命令。

- **用法:**

  ```python
  COMMAND_START = {'', '/', '!'}
  ```

  允许使用 `/`、`!` 作为命令起始符，或不用发送起始符。

### `COMMAND_SEP`

- **类型:** `Iterable[str | Pattern]`

- **默认值:** `{'/', '.'}`

- **说明:**

  命令的分隔标记，用于将文本形式的命令切分为元组（实际的命令名）。

- **用法:**

  ```python
  COMMAND_SEP = {'.'}
  ```

  将 `note.add` 这样的命令解析为 `('note', 'add')`。

### `DEFAULT_COMMAND_PERMISSION` <Badge text="1.9.0+"/>

- **类型:** `PermissionPolicy_T`

- **默认值:** `lambda _: True`

- **说明:**

  命令处理器的缺省权限。默认为允许所有用户触发。

- **用法:**

  ```python
  DEFAULT_COMMAND_PERMISSION = lambda s: s.is_superuser
  ```

  调用 `on_command` 而不提供 `permission` 参数时，命令仅能被超级用户触发。

### `DEFAULT_NLP_PERMISSION` <Badge text="1.9.0+"/>

- **类型:** `PermissionPolicy_T`

- **默认值:** `lambda _: True`

- **说明:**

  自然语言处理器的缺省权限。默认为允许所有用户触发。

### `SESSION_EXPIRE_TIMEOUT`

- **类型:** `datetime.timedelta | None`

- **默认值:** `datetime.timedelta(minutes=5)`

- **说明:**

  命令会话的过期超时时长，超时后会话将被移除。`None` 表示不超时。

- **用法:**

  ```python
  from datetime import timedelta
  SESSION_EXPIRE_TIMEOUT = timedelta(minutes=2)
  ```

  设置过期超时为 2 分钟，即用户 2 分钟不发消息后，会话将被关闭。

### `SESSION_RUN_TIMEOUT`

- **类型:** `datetime.timedelta | None`

- **默认值:** `None`

- **说明:**

  命令会话的运行超时时长，超时后会话将被移除，命令处理函数会被异常所中断。此时用户可以调用新的命令，开启新的会话。`None` 表示不超时。

- **用法:**

  ```python
  from datetime import timedelta
  SESSION_RUN_TIMEOUT = timedelta(seconds=10)
  ```

  设置运行超时为 10 秒，即命令会话运行达到 10 秒，NoneBot 将认为它已经结束。

### `SESSION_RUNNING_EXPRESSION`

- **类型:** `Expression_T`

- **默认值:** `'您有命令正在执行，请稍后再试'`

- **说明:**

  当有命令会话正在运行时，给用户新消息的回复。

- **用法:**

  ```python
  SESSION_RUNNING_EXPRESSION = ''
  ```

  设置为空，表示当有命令会话正在运行时，不回复用户的新消息。

### `SHORT_MESSAGE_MAX_LENGTH`

- **类型:** `int`

- **默认值:** `50`

- **说明:**

  短消息的最大长度。默认情况下（`only_short_message` 为 `True`），自然语言处理器只会响应消息中纯文本部分的长度总和小于等于此值的消息。

- **用法:**

  ```python
  SHORT_MESSAGE_MAX_LENGTH = 100
  ```

  设置最大长度为 100。

### `DEFAULT_VALIDATION_FAILURE_EXPRESSION` <Badge text="1.2.0+"/>

- **类型:** `Expression_T`

- **默认值:** `'您的输入不符合要求，请重新输入'`

- **说明:**

  命令参数验证失败（验证器抛出 `ValidateError` 异常）、且验证器没有指定错误信息时，默认向用户发送的错误提示。

- **用法:**

  ```python
  DEFAULT_VALIDATION_FAILURE_EXPRESSION = '你发送的内容格式不太对呢，请检查一下再发送哦～'
  ```

  设置更亲切的默认错误提示。

### `MAX_VALIDATION_FAILURES` <Badge text="1.3.0+"/>

- **类型:** `int`

- **默认值:** `3`

- **说明:**

  命令参数验证允许的最大失败次数，用户输入错误达到这个次数之后，将会提示用户输入错误太多次，并结束命令会话。

  设置为 `0` 将不会检查验证失败次数。

### `TOO_MANY_VALIDATION_FAILURES_EXPRESSION` <Badge text="1.3.0+"/>

- **类型:** `Expression_T`

- **默认值:** `'您输入错误太多次啦，如需重试，请重新触发本功能'`

- **说明:**

  命令参数验证失败达到 `MAX_VALIDATION_FAILURES` 次之后，向用户发送的提示。

- **用法:**

  ```python
  TOO_MANY_VALIDATION_FAILURES_EXPRESSION = (
      '你输错太多次啦，需要的时候再叫我吧',
      '你输错太多次了，建议先看看使用帮助哦～',
  )
  ```

### `SESSION_CANCEL_EXPRESSION` <Badge text="1.3.0+"/>

- **类型:** `Expression_T`

- **默认值:** `'好的'`

- **说明:**

  `nonebot.command.argfilter.controllers.handle_cancellation()` 控制器在用户发送了 `算了`、`取消` 等取消指令后，结束当前命令会话时，向用户发送的提示。

- **用法:**

  ```python
  SESSION_CANCEL_EXPRESSION = (
      '好的',
      '好的吧',
      '好吧，那奶茶就不打扰啦',
      '那奶茶先不打扰小主人啦',
  )
  ```

### `APSCHEDULER_CONFIG`

- **类型:** `dict[str, Any]`

- **默认值:** `{'apscheduler.timezone': 'Asia/Shanghai'}`

- **说明:**

  APScheduler 的配置对象，见 [Configuring the scheduler](https://apscheduler.readthedocs.io/en/latest/userguide.html#configuring-the-scheduler)。

## `nonebot` 模块

### 快捷导入

为方便使用，`nonebot` 模块从子模块导入了部分内容：

- `CQHttpError` -> `nonebot.exceptions.CQHttpError`
- `load_plugin` -> `nonebot.plugin.load_plugin`
- `load_plugins` -> `nonebot.plugin.load_plugins`
- `load_builtin_plugins` -> `nonebot.plugin.load_builtin_plugins`
- `get_loaded_plugins` <Badge text="1.1.0+"/> -> `nonebot.plugin.get_loaded_plugins`
- `on_command` -> `nonebot.plugin.on_command`
- `on_natural_language` -> `nonebot.plugin.on_natural_language`
- `on_notice` -> `nonebot.plugin.on_notice`
- `on_request` -> `nonebot.plugin.on_request`
- `message_preprocessor` -> `nonebot.message.message_preprocessor`
- `Message` -> `nonebot.message.Message`
- `MessageSegment` -> `nonebot.message.MessageSegment`
- `CommandSession` -> `nonebot.command.CommandSession`
- `CommandGroup` -> `nonebot.command.CommandGroup`
- `NLPSession` -> `nonebot.natural_language.NLPSession`
- `NoticeSession` -> `nonebot.notice_request.NoticeSession`
- `RequestSession` -> `nonebot.notice_request.RequestSession`
- `context_id` <Badge text="1.2.0+"/> -> `nonebot.helpers.context_id`
- `SenderRoles` <Badge text="1.9.0+"/> -> `nonebot.permission.SenderRoles`

### `scheduler`

- **类型:** `Scheduler`

- **说明:**

  全局的计划任务对象，只有当 Python 环境中安装了 APScheduler 时才有效，否则为 `None`。

### _class_ `NoneBot`

继承自 `aiocqhttp.CQHttp`。

#### `config`

- **类型:** `Any`

- **说明:**

  配置对象。

#### `asgi`

- **类型:** `Quart`

- **说明:**

  ASGI 对象，继承自 `aiocqhttp.CQHttp`，目前等价于 `server_app`。

#### `server_app`

- **类型:** `Quart`

- **说明:**

  内部的 Quart 对象，继承自 `aiocqhttp.CQHttp`。

#### `__init__(config_object=None)`

- **说明:**

  初始化 NoneBot 对象。配置对象会被保存到 `config` 属性，并且被传入父类的初始化函数。

  不建议手动创建 NoneBot 对象，而应该使用全局的 `init()` 函数。

- **参数:**

  - `config_object: Any | None`: 配置对象，类型不限，只要能够通过 `__getattr__` 和 `__dict__` 分别访问到单个和所有配置项即可，若没有传入，则使用默认配置

#### `__getattr__(item)`

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

#### `run(host=None, port=None, *args, **kwargs)`

- **说明:**

  运行 NoneBot。

  不建议直接运行 NoneBot 对象，而应该使用全局的 `run()` 函数。

- **参数:**

  - `host: str | None`: 主机名／IP
  - `port: int | None`: 端口
  - `*args: Any`: 其它传入 `CQHttp.run()` 的位置参数
  - `**kwargs: Any`: 其它传入 `CQHttp.run()` 的命名参数

#### _decorator_ `on_message(*events)`

- **说明:**

  将函数装饰为消息事件的处理函数，继承自 `aiocqhttp.CQHttp`。

  监听所有消息事件时，可以不加括号。

  此函数不是 NoneBot 自带的 API，其不遵循插件规定同时也不会在插件卸载时自动清除。如无特殊需要，建议使用 `on_command`, `on_natural_language` 或 `message_preprocessor` 代替。

- **参数:**

  - `*events: str`: 消息事件名，例如 `private`、`group`、`private.friend`，不传入表示监听所有消息事件

- **用法:**

  ```python
  bot = nonebot.get_bot()

  @bot.on_message('group')
  async def handle_group_message(event: aiocqhttp.Event)
      pass
  ```

  注册群消息事件处理函数。

#### _decorator_ `on_notice(*events)`

- **说明:**

  将函数装饰为通知事件的处理函数，继承自 `aiocqhttp.CQHttp`。

  监听所有通知事件时，可以不加括号。

  此函数不是 NoneBot 自带的 API，其不遵循插件规定同时也不会在插件卸载时自动清除。如无特殊需要，建议使用 `nonebot.plugin.on_notice` 代替。

- **参数:**

  - `*events: str`: 消息事件名，例如 `group_increase`、`group_decrease.leave`、`friend_add`，不传入表示监听所有通知事件

- **用法:**

  ```python
  bot = nonebot.get_bot()

  @bot.on_notice('group_increase')
  async def handle_group_increase(event: aiocqhttp.Event):
      pass
  ```

  注册群成员增加事件处理函数。

#### _decorator_ `on_request(*events)`

- **说明:**

  将函数装饰为请求事件的处理函数，继承自 `aiocqhttp.CQHttp`。

  监听所有请求事件时，可以不加括号。

  此函数不是 NoneBot 自带的 API，其不遵循插件规定同时也不会在插件卸载时自动清除。如无特殊需要，建议使用 `nonebot.plugin.on_request` 代替。

- **参数:**

  - `*events: str`: 消息事件名，例如 `friend`、`group`、`group.add`，不传入表示监听所有请求事件

- **用法:**

  ```python
  bot = nonebot.get_bot()

  @bot.on_request('friend', 'group.invite')
  async def handle_request(event: aiocqhttp.Event):
      pass
  ```

  注册加好友和邀请入群请求事件处理函数。

#### _decorator_ `on_meta_event(*events)`

- **说明:**

  将函数装饰为元事件的处理函数，继承自 `aiocqhttp.CQHttp`。

  监听所有元事件时，可以不加括号。

  此函数不是 NoneBot 自带的 API，其不遵循插件规定同时也不会在插件卸载时自动清除。

- **参数:**

  - `*events: str`: 消息事件名，例如 `heartbeat`，不传入表示监听所有元事件

- **用法:**

  ```python
  bot = nonebot.get_bot()

  @bot.on_meta_event('heartbeat')
  async def handle_heartbeat(event: aiocqhttp.Event):
      pass
  ```

  注册心跳元事件处理函数。

### `init(config_object=None, start_scheduler=True)`

- **说明:**

  初始化全局 NoneBot 对象。

- **参数:**

  - `config_object: Any | None`: 配置对象，类型不限，只要能够通过 `__getattr__` 和 `__dict__` 分别访问到单个和所有配置项即可，若没有传入，则使用默认配置
  - `start_scheduler: bool` <Badge text="1.7.0+"/>: 是否要启动 `nonebot.scheduler`

- **返回:**

  - `None`

- **用法:**

  ```python
  import config
  nonebot.init(config)
  ```

  导入 `config` 模块并初始化全局 NoneBot 对象。

### `get_bot()`

- **说明:**

  获取全局 NoneBot 对象。可用于在计划任务的回调中获取当前 NoneBot 对象。

- **返回:**

  - `NoneBot`: 全局 NoneBot 对象

- **异常:**

  - `ValueError`: 全局 NoneBot 对象尚未初始化

- **用法:**

  ```python
  bot = nonebot.get_bot()
  ```

### `run(host=None, port=None, *args, **kwargs)`

- **说明:**

  运行全局 NoneBot 对象。

- **参数:**

  - `host: str | None`: 主机名／IP，若不传入则使用配置文件中指定的值
  - `port: int | None`: 端口，若不传入则使用配置文件中指定的值
  - `*args: Any`: 其它传入 `CQHttp.run()` 的位置参数
  - `**kwargs: Any`: 其它传入 `CQHttp.run()` 的命名参数

- **返回:**

  - `None`

- **用法:**

  ```python
  nonebot.run(host='127.0.0.1', port=8080)
  ```

  在 `127.0.0.1:8080` 运行全局 NoneBot 对象。

### _decorator_ `on_startup` <Badge text="1.5.0+"/>

- **说明:**

  将函数装饰为 NoneBot 启动时的回调函数。

- **用法:**

  ```python
  @on_startup
  async def startup()
      await db.init()
  ```

  注册启动时回调，初始化数据库。

### _decorator_ `on_shutdown`

- **说明:**

  将函数装饰为 NoneBot 关闭时的回调函数。

- **用法:**

  ```python
  @on_shutdown
  async def shutdown()
      await db.close_connections()
  ```

  注册退出时的回调，关闭数据库连接。

### _decorator_ `on_websocket_connect` <Badge text="1.5.0+"/>

- **说明:**

  将函数装饰为 CQHTTP 反向 WebSocket 连接建立时的回调函数。

  该装饰器等价于 `@bot.on_meta_event('lifecycle.connect')`。

- **用法:**

  ```python
  @on_websocket_connect
  async def connect(event: aiocqhttp.Event):
      bot = nonebot.get_bot()
      groups = await bot.get_group_list()
  ```

  注册 WebSocket 连接时回调，获取群列表。

## `nonebot.exceptions` 模块

### _class_ `CQHttpError`

等价于 `aiocqhttp.Error`。

## `nonebot.plugin` 模块 <Badge text="1.1.0+"/>

### _class_ `Plugin`

用于包装已加载的插件模块的类。

#### `module`

- **类型:** `ModuleType`

- **说明:**

  已加载的插件模块（importlib 导入的 Python 模块）。

#### `name`

- **类型:** `str | None`

- **说明:**

  插件名称，从插件模块的 `__plugin_name__` 特殊变量获得，如果没有此变量，则为 `None`。

#### `usage`

- **类型:** `Any | None`

- **说明:**

  插件使用方法，从插件模块的 `__plugin_usage__` 特殊变量获得，如果没有此变量，则为 `None`。

#### `userdata` <Badge text="1.9.0+"/>

- **类型:** `Any | None`

- **说明:**

  插件作者可由此变量向外部暴露其他信息，从插件模块的 `__plugin_userdata__` 特殊变量获得，如果没有此变量，则为 `None`。

#### `commands` <Badge text="1.6.0+"/>

- **类型:** `set[Command]`

- **说明:**

  插件包含的命令，通过 `on_command` 装饰器注册。

#### `nl_processors` <Badge text="1.6.0+"/>

- **类型:** `set[NLProcessor]`

- **说明:**

  插件包含的自然语言处理器，通过 `on_natural_language` 装饰器注册。

#### `event_handlers` <Badge text="1.6.0+"/>

- **类型:** `set[EventHandler]`

- **说明:**

  插件包含的事件处理器（包含通知、请求），通过 `on_notice` 以及 `on_request` 装饰器注册。

#### `msg_preprocessors` <Badge text="1.9.0+"/>

- **类型:** `set[MessagePreprocessor]`

- **说明:**

  插件包含的消息预处理器，通过 `message_preprocessor` 装饰器注册。

#### `lifetime_hooks` <Badge text="1.9.0+"/>

- **类型:** `list[LifetimeHook]`

- **说明:**

  插件包含的生命周期事件回调，通过 `on_plugin` 装饰器注册。

#### `__await__()` <Badge text="1.9.0+"/>

- **说明:**

  当使用 `load_plugin`, `unload_plugin`, `reload_plugin` 时，其返回的 `Plugin` 对象可以（非必需）被 await 来等待其异步加载、卸载完成。详情请见这些函数的文档。

- **返回:**

  - `Generator[None, None, Plugin | None]`

### _class_ `PluginManager` <Badge text="1.6.0+" />

插件管理器：用于管理插件的加载以及插件中命令、自然语言处理器、事件处理器的开关。

#### `cmd_manager`

- **类型:** `CommandManager`

- **说明:**

  命令管理器实例。

#### `nlp_manager`

- **类型:** `NLPManager`

- **说明:**

  自然语言管理器实例。

#### _class method_ `add_plugin(cls, module_path, plugin)`

- **说明:**

  注册一个 `Plugin` 对象。

- **参数:**

  - `module_path: str`: 模块路径
  - `plugin: Plugin`: Plugin 对象

- **返回:**

  None

- **用法:**

  ```python
  plugin = Plugin(module, name, usage, commands, nl_processors, event_handlers)
  PluginManager.add_plugin("path.to.plugin", plugin)
  ```

#### _class method_ `get_plugin(cls, module_path)`

- **说明:**

  获取一个已经注册的 `Plugin` 对象。

- **参数:**

  - `module_path: str`: 模块路径

- **返回:**

  - `Plugin | None`: Plugin 对象

- **用法:**

  ```python
  plugin = PluginManager.get_plugin("path.to.plugin")
  ```

#### _class method_ `remove_plugin(cls, module_path)`

- **说明:**

  删除 Plugin 中的所有命令、自然语言处理器、事件处理器并从插件管理器移除 Plugin 对象。在 1.9.0 后，也会移除消息预处理器。

  :::danger
  这个方法实际并没有完全移除定义 Plugin 的模块。仅是移除其所注册的处理器。
  :::

- **参数:**

  - `module_path: str`: 模块路径

- **返回:**

  - `bool`: 是否移除了插件

- **用法:**

#### _class method_ `switch_plugin_global(cls, module_path, state=None)`

- **说明:**

  根据 `state` 更改 plugin 中 commands, nl_processors, event_handlers 的全局状态。在 1.9.0 后，msg_preprocessors 的状态也会被更改。

  :::warning
  更改插件状态并不会影响插件内 scheduler 等其他全局副作用状态
  :::

- **参数:**

  - `module_path: str`: 模块路径
  - `state: bool | None`:
    - `None(default)`: 切换状态，即 开 -> 关、关 -> 开
    - `bool`: 切换至指定状态，`True` -> 开、`False` -> 关

- **返回:**

  None

- **用法:**

  ```python
  # 全局关闭插件 path.to.plugin , 对所有消息生效
  PluginManager.switch_plugin_global("path.to.plugin", state=False)
  ```

#### _class method_ `switch_command_global(cls, module_path, state=None)`

- **说明:**

  根据 `state` 更改 plugin 中 commands 的全局状态。

- **参数:**

  - `module_path: str`: 模块路径
  - `state: bool | None`:
    - `None(default)`: 切换状态，即 开 -> 关、关 -> 开
    - `bool`: 切换至指定状态，`True` -> 开、`False` -> 关

- **返回:**

  None

- **用法:**

  ```python
  # 全局关闭插件 path.to.plugin 中所有命令, 对所有消息生效
  PluginManager.switch_command_global("path.to.plugin", state=False)
  ```

#### _class method_ `switch_nlprocessor_global(cls, module_path, state=None)`

- **说明:**

  根据 `state` 更改 plugin 中 nl_processors 的全局状态。

- **参数:**

  - `module_path: str`: 模块路径
  - `state: bool | None`:
    - `None(default)`: 切换状态，即 开 -> 关、关 -> 开
    - `bool`: 切换至指定状态，`True` -> 开、`False` -> 关

- **返回:**

  None

- **用法:**

  ```python
  from nonebot import message_preprocessor

  # 全局关闭插件 path.to.plugin 中所有自然语言处理器, 对所有消息生效
  PluginManager.switch_nlprocessor_global("path.to.plugin", state=False)

  @message_preprocessor
  async def processor(bot: NoneBot, event: CQEvent, plugin_manager: PluginManager):
      plugin_manager.switch_nlprocessor_global("path.to.plugin", state=False)
  ```

#### _class method_ `switch_eventhandler_global(cls, module_path, state=None)`

- **说明:**

  根据 `state` 更改 plugin 中 event handlers 的全局状态。

- **参数:**

  - `module_path: str`: 模块路径
  - `state: bool | None`:
    - `None(default)`: 切换状态，即 开 -> 关、关 -> 开
    - `bool`: 切换至指定状态，`True` -> 开、`False` -> 关

- **返回:**

  None

- **用法:**

  ```python
  # 全局关闭插件 path.to.plugin 中所有事件处理器, 对所有消息生效
  PluginManager.switch_eventhandler_global("path.to.plugin", state=False)
  ```

#### _class method_ `switch_messagepreprocessor_global(cls, module_path, state=None)` <Badge text="1.9.0+"/>

- **说明:**

  根据 `state` 更改 plugin 中 message preprocessors 的全局状态。

- **参数:**

  - `module_path: str`: 模块路径
  - `state: bool | None`:
    - `None(default)`: 切换状态，即 开 -> 关、关 -> 开
    - `bool`: 切换至指定状态，`True` -> 开、`False` -> 关

- **返回:**

  None

- **用法:**

  ```python
  # 全局关闭插件 path.to.plugin 中所有消息预处理器, 对所有消息生效
  PluginManager.switch_messagepreprocessor_global("path.to.plugin", state=False)
  ```

#### `switch_plugin(cls, module_path, state=None)`

- **说明:**

  根据 `state` 修改 plugin 中的 commands 和 nlprocessors 状态。仅对当前消息有效。

- **参数:**

  - `module_path: str`: 模块路径
  - `state: bool | None`:
    - `None(default)`: 切换状态，即 开 -> 关、关 -> 开
    - `bool`: 切换至指定状态，`True` -> 开、`False` -> 关

- **返回:**

  None

- **用法:**

  ```python
  from nonebot import message_preprocessor

  # 关闭插件 path.to.plugin , 仅对当前消息生效
  @message_preprocessor
  async def processor(bot: NoneBot, event: CQEvent, plugin_manager: PluginManager):
      plugin_manager.switch_plugin("path.to.plugin", state=False)
  ```

#### `switch_command(cls, module_path, state=None)`

- **说明:**

  根据 `state` 修改 plugin 中 commands 的状态。仅对当前消息有效。

- **参数:**

  - `module_path: str`: 模块路径
  - `state: bool | None`:
    - `None(default)`: 切换状态，即 开 -> 关、关 -> 开
    - `bool`: 切换至指定状态，`True` -> 开、`False` -> 关

- **返回:**

  None

- **用法:**

  ```python
  from nonebot import message_preprocessor

  # 关闭插件 path.to.plugin 中所有命令, 仅对当前消息生效
  @message_preprocessor
  async def processor(bot: NoneBot, event: CQEvent, plugin_manager: PluginManager):
      plugin_manager.switch_command("path.to.plugin", state=False)
  ```

#### `switch_nlprocessor(cls, module_path, state=None)`

- **说明:**

  根据 `state` 修改 plugin 中 nl_processors 的状态。仅对当前消息有效。

- **参数:**

  - `module_path: str`: 模块路径
  - `state: bool | None`:
    - `None(default)`: 切换状态，即 开 -> 关、关 -> 开
    - `bool`: 切换至指定状态，`True` -> 开、`False` -> 关

- **返回:**

  None

- **用法:**

  ```python
  from nonebot import message_preprocessor

  # 关闭插件 path.to.plugin 中所有自然语言处理器, 仅对当前消息生效
  @message_preprocessor
  async def processor(bot: NoneBot, event: CQEvent, plugin_manager: PluginManager):
      plugin_manager.switch_nlprocessor("path.to.plugin", state=False)
  ```

### `load_plugin(module_path, no_fast=False)`

- **说明:**

  加载插件（等价于导入模块）。

  此函数会调用插件中由 `on_plugin('loading')` 装饰器注册的函数（下称 「加载回调」），之后再添加插件中注册的处理器（如命令等）。

- **参数:**

  - `module_path: str`: 模块路径
  - `no_fast: bool` <Badge text="v1.9.1" />: 若此参数为 `True`，则无视 `unload_plugin` 中的 `fast` 选项而强制重新导入模块

- **返回:** <Badge text="1.6.0+" />

  - `Plugin | None`: 加载后生成的 `Plugin` 对象。根据插件组成不同，返回值包含如下情况：
    - 插件没有定义加载回调，或只定义了同步的加载回调（此为 1.9.0 前的唯一情况）：此函数会执行回调，在加载完毕后返回新的插件对象，其可以被 await，行为为直接返回插件本身（也就是可以不 await）。如果发生异常，则返回 `None`
    - 插件定义了异步加载回调，但 `load_plugin` 是在 NoneBot 启动前调用的：此函数会阻塞地运行异步函数，其余表现和上一致
    - 插件定义了异步加载回调，但 `load_plugin` 是在异步的情况下调用的（比如在 NoneBot 运行的事件循环中）：此函数会先执行部分同步的加载回调
      - 如果成功，返回一个插件对象。返回值可以被 await，行为为等待剩余的异步加载完毕然后返回插件本身，或如果在 await 中发生了错误，返回 `None`
      - 如果失败，返回 `None`

- **用法:**

  ```python
  nonebot.plugin.load_plugin('ai_chat')
  ```

  加载 `ai_chat` 插件。

  ```python
  # 此写法是通用的，即使插件没有异步的加载回调
  p = nonebot.plugin.load_plugin('my_own_plugin')
  if p is not None and await p is not None:
      # 插件成功加载完成, p 为新加载的 Plugin 对象
  else:
      # 插件加载失败
  ```
  加载 `my_own_plugin` 插件，并且等待其异步的加载回调（如果有）执行完成。

### `unload_plugin(module_path, fast=False)` <Badge text="1.9.0+" />

- **说明:**

  卸载插件，即移除插件的 commands, nlprocessors, event handlers 和 message preprocessors，运行由 `on_plugin('unloaded')` 注册的函数（下称 「卸载回调」），并将已导入的模块移除。

  :::danger
  该函数为强制卸载，如果使用不当，可能导致不可预测的错误！（如引用已经被移除的模块变量）

  此函数不会回滚已导入模块中产生过的其他副作用（比如已计划的任务，aiocqhttp 中注册的处理器等）。
  :::

- **参数:**

  - `module_path: str`: 模块路径
  - `fast: bool` <Badge text="v1.9.1" />: 若此参数为 `True`，则卸载时将不会移除已导入的模块。当未来的 `load_plugin` 调用将加载相同的插件时，将不会重新导入相应模块而是复用。

- **返回:**

  - `Plugin | None`: 执行卸载后遗留的 `Plugin` 对象，或 `None` 如果插件不存在。根据插件组成不同，`Plugin` 返回值包含如下情况：
    - 插件没有定义卸载回调，或只定义了同步的卸载回调：此函数会卸载处理器并执行回调，在卸载完毕后返回遗留的插件对象，其可以被 await，行为为直接返回此插件本身（也就是可以不 await）。
    - 插件定义了异步卸载回调，但 `unload_plugin` 是在 NoneBot 启动前调用的：此函数会阻塞地运行异步函数，其余表现和上一致
    - 插件定义了异步卸载回调，但 `unload_plugin` 是在异步的情况下调用的（比如在 NoneBot 运行的事件循环中）：此函数会卸载处理器并执行部分同步的卸载回调，返回遗留的插件对象。此对象可以被 await，行为为等待剩余的异步卸载回调执行完毕然后返回此插件本身。
    - 在此之后此返回值将不再有用

- **用法:**

  ```python
  nonebot.plugin.unload_plugin('ai_chat')
  ```

  卸载 `ai_chat` 插件。

  ```python
  # 此写法是通用的，即使插件没有异步的卸载回调
  p = nonebot.plugin.unload_plugin('my_own_plugin')
  if p is not None:
      await p
  ```
  卸载 `my_own_plugin` 插件，并且等待其异步的卸载回调（如果有）执行完成。

### `reload_plugin(module_path, fast=False)` <Badge text="1.6.0+" />

- **说明:**

  重载插件，也就是先 `unload_plugin`，再 `load_plugin`，期间等待相应回调执行完毕。

  :::danger
  该函数为强制重载，如果使用不当，可能导致不可预测的错误！
  :::

- **参数:**

  - `module_path: str`: 模块路径
  - `fast: bool` <Badge text="v1.9.1" />: 若此参数为 `True`，则卸载时将不会移除已导入的模块，加载时将不会重新导入相应模块而是复用。
    :::tip
    在 1.9.1 后，建议使用 `fast=True`。此参数的默认值 `False` 是由于历史原因。
    :::

- **返回:**

  - `Plugin | None`: 重载后生成的 Plugin 对象。根据插件组成不同，返回值包含如下情况：
    - 插件没有定义或只定义了同步的加载/卸载回调（此为 1.9.0 前的唯一情况）：此函数会执行两个步骤的回调，在重载完毕后返回新的插件对象，其可以被 await，行为为直接返回插件本身（也就是可以不 await）。如果发生异常，则返回 `None`
    - 插件定义了异步的回调，但 `reload_plugin` 是在 NoneBot 启动前调用的：此函数会阻塞地运行异步函数，其余表现和上一致
    - 插件定义了异步的回调，但 `reload_plugin` 是在异步的情况下调用的（比如在 NoneBot 运行的事件循环中）：此函数会卸载处理器并执行部分同步的卸载回调，返回遗留的插件对象。返回值可以被 await，行为为等待剩余的异步卸载完毕并且加载新插件完毕后然后返回新的插件对象，或如果在 await 中发生了错误，返回 `None`

- **用法:**

  ```python
  nonebot.plugin.reload_plugin('ai_chat')
  ```

  重载 `ai_chat` 插件。

  ```python
  # 此写法是通用的，即使插件没有异步的回调
  p = nonebot.plugin.reload_plugin('my_own_plugin')
  if p is not None and (p := await p) is not None:
      # 插件成功加载完成, p 为新加载的 Plugin 对象
  else:
      # 插件加载失败
  ```
  重载 `my_own_plugin` 插件，并且等待其异步的加载回调（如果有）执行完成。

### `load_plugins(plugin_dir, module_prefix, no_fast=False)`

- **说明:**

  查找指定路径（相对或绝对）中的非隐藏模块（隐藏模块名字以 `_` 开头）并通过指定的模块前缀导入。其返回值的表现与 `load_plugin` 一致。

- **参数:**

  - `plugin_dir: str`: 插件目录
  - `module_prefix: str`: 模块前缀
  - `no_fast: bool` <Badge text="v1.9.1" />: 若此参数为 `True`，则无视 `unload_plugin` 中的 `fast` 选项而强制重新导入模块

- **返回:** <Badge text="1.6.0+" />

  - `set[Plugin]`: 加载成功的 Plugin 对象

- **用法:**

  ```python
  nonebot.plugin.load_plugins(path.join(path.dirname(__file__), 'plugins'), 'plugins')
  ```

  加载 `plugins` 目录下的插件。

### `load_builtin_plugins()`

- **说明:**

  加载内置插件。

- **返回:** <Badge text="1.6.0+" />

  - `set[Plugin]:`: 加载成功的 Plugin 对象

- **用法:**

  ```python
  nonebot.plugin.load_builtin_plugins()
  ```

### `get_loaded_plugins()`

- **说明:**

  获取已经加载的插件集合。

- **返回:**

  - `set[Plugin]:` 已加载的插件集合

- **用法:**

  ```python
  plugins = nonebot.plugin.get_loaded_plugins()
  await session.send('我现在支持以下功能：\n\n' +
                     '\n'.join(map(lambda p: p.name, filter(lambda p: p.name, plugins))))
  ```

### _decorator_ `on_plugin(timing)` <Badge text="1.9.0+" />

- **说明:**、

  将函数设置为插件生命周期的回调函数。注册的加载回调会在调用 `load_plugin` 时被调用，注册的卸载回调会在调用 `unload_plugin` 时被调用。

- **参数:**

  - `timing: str`: `"loading"` 表示注册加载回调，`"unloaded"` 表示注册卸载回调

- **要求:**

  被装饰函数可为同步或异步（async def）函数，必须不接受参数，其返回值会被忽略:

  ```python
  def func():
      pass

  async def func():
      pass
  ```

  被 `on_plugin('unloaded')` 装饰的函数必须不能抛出 `Exception`，否则卸载时的行为将不能保证。

- **用法:**

  ```python
  necessary_info = []

  @on_plugin('loading')
  async def _():
      logger.info('正在加载插件...')
      async with httpx.AsyncClient() as client:
          r = await client.get('https://api.github.com/repos/nonebot/nonebot')
          necessary_info.append(r.json())
  ```

  注册一个加载回调为插件的加载做准备工作。

### _decorator_ `on_command(name, *, aliases=(), permission=..., only_to_me=True, privileged=False, shell_like=False, expire_timeout=..., run_timeout=..., session_class=None)` <Badge text="1.6.0+" />

- **说明:**

  将函数装饰为命令处理器 `CommandHandler_T` 。

  被装饰的函数将会获得一个 `args_parser` 属性，是一个装饰器，下面会有详细说明。

- **参数:**

  - `name: str | CommandName_T`: 命令名，如果传入的是字符串则会自动转为元组
  - `aliases: Iterable[str] | str`: 命令别名
  - `patterns: Patterns_T` <Badge text="1.7.0+"/>: 正则匹配，可以传入正则表达式或正则表达式组，来对整条命令进行匹配
    :::warning 注意
    滥用正则表达式可能会引发性能问题，请优先使用普通命令。另外一点需要注意的是，由正则表达式匹配到的匹配到的命令，`session` 中的 `current_arg` 会是整个命令，而不会删除匹配到的内容，以满足一些特殊需求。
    :::
  - `permission: PermissionPolicy_T | Iterable[PermissionPolicy_T] | EllipsisType` <Badge text="1.9.0+"/>: 命令所需要的权限，不满足权限的用户将无法触发该命令。若提供了多个，则默认使用 `aggregate_policy` 和其默认参数组合。如果不传入该参数（即为默认的 `...`），则使用配置项中的 `DEFAULT_COMMAND_PERMISSION`
  - `only_to_me: bool`: 是否只响应确定是在和「我」（机器人）说话的命令（在开头或结尾 @ 了机器人，或在开头称呼了机器人昵称）
  - `privileged: bool`: 是否特权命令，若是，则无论当前是否有命令会话正在运行，都会运行该命令，但运行不会覆盖已有会话，也不会保留新创建的会话
  - `shell_like: bool`: 是否使用类 shell 语法，若是，则会自动使用 `shlex` 模块进行分割（无需手动编写参数解析器），分割后的参数列表放入 `session.args['argv']`
  - `expire_timeout: (datetime.timedelta | None) | EllipsisType` <Badge text="1.8.2+"/>: 命令过期时间。如果不传入该参数（即为默认的 `...`），则使用配置项中的 `SESSION_EXPIRE_TIMEOUT`，如果提供则使用提供的值。
  - `run_timeout: (datetime.timedelta | None) | EllipsisType` <Badge text="1.8.2+"/>: 命令会话的运行超时时长。如果不传入该参数（即为默认的 `...`），则使用配置项中的 `SESSION_RUN_TIMEOUT`，如果提供则使用提供的值。
  - `session_class: Type[CommandSession] | None` <Badge text="1.7.0+"/>: 自定义 `CommandSession` 子类，若传入此参数，则命令处理函数的参数 `session` 类型为 `session_class`

- **要求:**

  被装饰函数必须是一个 async 函数，且必须接收且仅接收一个位置参数，类型为 `CommandSession`，即形如：

  ```python
  async def func(session: CommandSession):
      pass
  ```

- **用法:**

  ```python
  @on_command('echo', aliases=('复读',), permission=lambda sender: sender.is_superuser)
  async def _(session: CommandSession):
      await session.send(session.current_arg)
  ```

  一个仅对超级用户生效的复读命令。

### _decorator_ _command_func._`args_parser`

- **说明:**

  将函数装饰为命令层面的参数解析器，将在命令实际处理函数之前被运行。

  如果已经在 `on_command` 装饰器中使用了 `shell_like=True`，则无需手动使用编写参数解析器。

  如果使用 `CommandSession#get()` 方法获取参数，并且传入了 `arg_filters`（相当于单个参数层面的参数解析器），则不会再运行此装饰器注册的命令层面的参数解析器；相反，如果没有传入 `arg_filters`，则会运行。

- **要求:**

  对被装饰函数的要求同 `on_command` 装饰器。

- **用法:**

  ```python
  @my_cmd.args_parser
  async def _(session: CommandSession):
      stripped_text = session.current_arg_text.strip()
      if not session.current_key and stripped_text:
          session.current_key = 'initial_arg'
      session.state[session.current_key] = stripped_text  # 若使用 1.1.0 及以下版本，请使用 session.args
  ```

  一个典型的命令参数解析器。

### _decorator_ `on_natural_language(keywords=None, *, permission=..., only_to_me=True, only_short_message=True, allow_empty_message=False)` <Badge text="1.6.0+" />

- **说明:**

  将函数装饰为自然语言处理器。

- **参数:**

  - `keywords: (Iterable[str] | str) | None`: 要响应的关键词，若传入 `None`，则响应所有消息
  - `permission: PermissionPolicy_T | Iterable[PermissionPolicy_T] | EllipsisType` <Badge text="1.9.0+"/>: 自然语言处理器所需要的权限，不满足权限的用户将无法触发该处理器。若提供了多个，则默认使用 `aggregate_policy` 和其默认参数组合。如果不传入该参数（即为默认的 `...`），则使用配置项中的 `DEFAULT_NLP_PERMISSION`
  - `only_to_me: bool`: 是否只响应确定是在和「我」（机器人）说话的消息（在开头或结尾 @ 了机器人，或在开头称呼了机器人昵称）
  - `only_short_message: bool`: 是否只响应短消息
  - `allow_empty_message: bool`: 是否响应内容为空的消息（只有 @ 或机器人昵称）

- **要求:**

  被装饰函数必须是一个 async 函数，且必须接收且仅接收一个位置参数，类型为 `NLPSession`，即形如：

  ```python
  async def func(session: NLPSession):
      pass
  ```

- **用法:**

  ```python
  @on_natural_language({'天气'}, only_to_me=False)
  async def _(session: NLPSession):
      return IntentCommand('weather', 100.0)
  ```

  响应所有带有「天气」关键词的消息，当做 `weather` 命令处理。
  
  如果有多个自然语言处理器同时处理了一条消息，则置信度最高的 `IntentCommand` 会被选择。处理器可以返回 `None`，表示不把消息当作任何命令处理。

### _decorator_ `on_notice(*events)` <Badge text="1.6.0+" />

- **说明:**

  将函数装饰为通知处理器。

- **参数:**

  - `*events: str`: 要处理的通知类型（`notice_type`），若不传入，则处理所有通知

- **要求:**

  被装饰函数必须是一个 async 函数，且必须接收且仅接收一个位置参数，类型为 `NoticeSession`，即形如：

  ```python
  async def func(session: NoticeSession):
      pass
  ```

- **用法:**

  ```python
  @on_notice
  async def _(session: NoticeSession):
      logger.info('有新的通知事件：%s', session.event)

  @on_notice('group_increase')
  async def _(session: NoticeSession):
      await session.send('欢迎新朋友～')
  ```

  收到所有通知时打日志，收到新成员进群通知时除了打日志还发送欢迎信息。

### _decorator_ `on_request(*events)` <Badge text="1.6.0+" />

- **说明:**

  将函数装饰为请求处理器。

- **参数:**

  - `*events: str`: 要处理的请求类型（`request_type`），若不传入，则处理所有请求

- **要求:**

  被装饰函数必须是一个 async 函数，且必须接收且仅接收一个位置参数，类型为 `RequestSession`，即形如：

  ```python
  async def func(session: RequestSession):
      pass
  ```

- **用法:**

  ```python
  @on_request
  async def _(session: RequestSession):
      logger.info('有新的请求事件：%s', session.event)

  @on_request('group')
  async def _(session: RequestSession):
      await session.approve()
  ```

  收到所有请求时打日志，收到群请求时除了打日志还同意请求。

## `nonebot.message` 模块

### _decorator_ `message_preprocessor`

- **说明:**

  将函数装饰为消息预处理器。

- **要求:** <Badge text="1.6.0+" />

  被装饰函数必须是一个 async 函数，且必须接收且仅接收三个位置参数，类型分别为 `NoneBot` 、 `aiocqhttp.Event` 和 `nonebot.plugin.PluginManager`，即形如：

  ```python
  async def func(bot: NoneBot, event: aiocqhttp.Event, plugin_manager: PluginManager):
      pass
  ```

- **用法:**

  ```python
  @message_preprocessor
  async def _(bot: NoneBot, event: aiocqhttp.Event, plugin_manager: PluginManager):
      event["preprocessed"] = True

      # 关闭某个插件，仅对当前消息生效
      plugin_manager.switch_plugin("path.to.plugin", state=False)
  ```

  在所有消息处理之前，向消息事件对象中加入 `preprocessed` 字段。

### _exception_ `CanceledException` <Badge text="1.6.0+" />

- **说明:**

  取消消息处理异常

- **要求:**

  在消息预处理函数 `message_preprocessor` 中可以选择抛出该异常来阻止响应该消息。

- **用法:**

  ```python
  @message_preprocessor
  async def _(bot: NoneBot, event: aiocqhttp.Event, plugin_manager: PluginManager):
      raise CanceledException(reason)
  ```

### _class_ `MessageSegment`

从 `aiocqhttp.message` 模块导入，继承自 `dict`，用于表示一个消息段。该类型是合法的 `Message_T`。

请参考 [aiocqhttp 文档](https://aiocqhttp.nonebot.dev/module/aiocqhttp/message.html#aiocqhttp.message.MessageSegment) 来了解此类的使用方法。

更多关于消息段的内容，见 [消息格式](https://github.com/botuniverse/onebot-11/tree/master/message)。

### _class_ `Message`

从 `aiocqhttp.message` 模块导入，继承自 `list`，用于表示一个消息。该类型是合法的 `Message_T`。

请参考 [aiocqhttp 文档](https://aiocqhttp.nonebot.dev/module/aiocqhttp/message.html#aiocqhttp.message.Message) 来了解此类的使用方法。

### `escape(s, *, escape_comma=True)`

- **说明:**

  从 `aiocqhttp.message` 模块导入，对字符串进行转义。

- **参数:**

  - `s: str`: 要转义的字符串
  - `escape_comma: bool`: 是否转义英文逗号 `,`

- **返回:**

  - `str`: 转义后的字符串

### `unescape(s)`

- **说明:**

  从 `aiocqhttp.message` 模块导入，对字符串进行去转义。

- **参数:**

  - `s: str`: 要去转义的字符串

- **返回:**

  - `str`: 去转义后的字符串

## `nonebot.command` 模块

### _decorator_ `on_command(name, *, aliases=(), permission=perm.EVERYBODY, only_to_me=True, privileged=False, shell_like=False)` <Badge text="1.6.0-" type="error" />

- **说明:**

  将函数装饰为命令处理器。

  被装饰的函数将会获得一个 `args_parser` 属性，是一个装饰器，下面会有详细说明。

- **参数:**

  - `name: str | CommandName_T`: 命令名，如果传入的是字符串则会自动转为元组
  - `aliases: Iterable[str] | str`: 命令别名
  - `permission: int`: 命令所需要的权限，不满足权限的用户将无法触发该命令
  - `only_to_me: bool`: 是否只响应确定是在和「我」（机器人）说话的命令（在开头或结尾 @ 了机器人，或在开头称呼了机器人昵称）
  - `privileged: bool`: 是否特权命令，若是，则无论当前是否有命令会话正在运行，都会运行该命令，但运行不会覆盖已有会话，也不会保留新创建的会话
  - `shell_like: bool`: 是否使用类 shell 语法，若是，则会自动使用 `shlex` 模块进行分割（无需手动编写参数解析器），分割后的参数列表放入 `session.args['argv']`

- **要求:**

  被装饰函数必须是一个 async 函数，且必须接收且仅接收一个位置参数，类型为 `CommandSession`，即形如：

  ```python
  async def func(session: CommandSession):
      pass
  ```

- **用法:**

  ```python
  @on_command('echo', aliases=('复读',))
  async def _(session: CommandSession):
      await session.send(session.current_arg)
  ```

  一个简单的复读命令。

### _class_ `CommandGroup`

命令组，用于声明一组有相同名称前缀的命令。

- **注:**

  在 1.8.1 之前，此类文档与实际表现不一致 ([issue 242](https://github.com/nonebot/nonebot/issues/242))。

#### `basename`

- **类型:** `CommandName_T`

- **说明:**

  命令名前缀。

#### `base_kwargs`

- **类型:** `dict[str, Any]`

- **说明:**

  此对象初始化时传递的 `permission`, `only_to_me`, `privileged`, `shell_like`, `expire_timeout`, `run_timeout`, `session_class`。如果没有传递，则此字典也不存在相应键值。

#### `__init__(name, *, permission=..., only_to_me=..., privileged=..., shell_like=..., expire_timeout=..., run_timeout=... session_class=...)`

- **说明:**

  初始化命令组，参数即为上面的属性。

- **参数:**

  - `name: str | CommandName_T`: 命令名前缀，若传入字符串，则会自动转换成元组
  - `permission: PermissionPolicy_T | Iterable[PermissionPolicy_T]` <Badge text="1.9.0+"/>: 对应 `permission` 属性
  - `only_to_me: bool`: 对应 `only_to_me` 属性
  - `privileged: bool`: 对应 `privileged` 属性
  - `shell_like: bool`: 对应 `shell_like` 属性
  - `expire_timeout: (datetime.timedelta | None) | EllipsisType` <Badge text="1.8.2+"/>: 对应 `expire_timeout` 属性
  - `run_timeout: (datetime.timedelta | None) | EllipsisType` <Badge text="1.8.2+"/>: 对应 `run_timeout` 属性
  - `session_class: Type[CommandSession] | None` <Badge text="1.8.1+"/>：对应 `session_class` 属性

#### _decorator_ `command(name, *, aliases=..., patterns=..., permission=..., only_to_me=..., privileged=..., shell_like=..., expire_timeout=..., run_timeout=..., session_class=...)`

- **说明:**

  将函数装饰为命令组中的命令处理器。使用方法和 `on_command` 装饰器完全相同。

- **参数:**

  - `name: str | CommandName_T`: 命令名，注册命令处理器时会加上命令组的前缀
  - `aliases: Iterable[str], str]`: 和 `on_command` 装饰器含义相同，若不传入则使用命令组默认值，若命令组没有默认值时，则使用 `on_command` 装饰器的默认值
  - `patterns: Patterns_T` <Badge text="1.8.1+"/>：同上
  - `permission: PermissionPolicy_T | Iterable[PermissionPolicy_T]` <Badge text="1.9.0+"/>: 同上
  - `only_to_me: bool`: 同上
  - `privileged: bool`: 同上
  - `shell_like: bool`: 同上
  - `expire_timeout: (datetime.timedelta | None) | EllipsisType` <Badge text="1.8.2+"/>: 同上
  - `run_timeout: (datetime.timedelta | None) | EllipsisType` <Badge text="1.8.2+"/>: 同上
  - `session_class: Type[CommandSession] | None` <Badge text="1.8.1+"/>：同上

- **用法:**

  ```python
  sched = CommandGroup('scheduler')

  @sched.command('add', permission=PRIVATE)
  async def _(session: CommandSession):
      pass
  ```

  注册 `('scheduler', 'add')` 命令。

### _class_ `CommandManager` <Badge text="1.6.0+" />

#### `commands`

- **类型:** `dict[CommandName_T, Command]`

- **说明:**

  命令字典。

#### `aliases`

- **类型:** `dict[str, Command]`

- **说明:**

  命令别名字典。

#### `switches`

- **类型:** `dict[CommandName_T, bool]`

- **说明:**

  命令开关状态字典。

#### `patterns` <Badge text="1.7.0+"/>

- **类型:** `dict[Pattern[str], Command]`

- **说明:**

  命令正则匹配字典。

#### _class method_ `add_command(cls, cmd_name, cmd)`

- **说明:**

  注册一个 `Command` 对象。

- **参数:**

  - `cmd_name: CommandName_T`: 命令名称
  - `cmd: Command`: 命令对象

- **返回:**

  None

- **用法:**

  ```python
  cmd = Command(name, func, permission, only_to_me, privileged)
  CommandManager.add_command(name, cmd)
  ```

#### _class method_ `add_aliases(cls, aliases, cmd)`

- **说明:**

  为 `Command` 添加命令别名。

- **参数:**

  - `aliases: Iterable[str] | str`: 命令别名列表

- **返回:**

  None

- **用法:**

  ```python
  cmd = Command(name, func, permission, only_to_me, privileged)
  CommandManager.add_aliases({"别名", "test"}, cmd)
  ```

#### _class method_ `reload_command(cls, cmd_name, cmd)`

- **说明:**

  更新一个已存在的命令。

- **参数:**

  - `cmd_name: CommandName_T`: 命令名称
  - `cmd: Command`: 命令对象

- **返回:**

  None

- **用法:**

  ```python
  cmd = Command(name, func, permission, only_to_me, privileged)
  CommandManager.reload_command(name, cmd)
  ```

#### _class method_ `remove_command(cls, cmd_name)`

- **说明:**

  移除一个已存在的命令。

- **参数:**

  - `cmd_name: CommandName_T`: 命令名称

- **返回:**

  - `bool`: 是否成功移除命令

- **用法:**

  ```python
  CommandManager.remove_command(("test", ))
  ```

#### _class method_ `switch_command_global(cls, cmd_name, state)`

- **说明:**

  根据 `state` 更改 command 的全局状态。

- **参数:**

  - `cmd_name: CommandName_T`: 命令名称
  - `state: bool | None`:
    - `None(default)`: 切换状态，即 开 -> 关、关 -> 开
    - `bool`: 切换至指定状态，`True` -> 开、`False` -> 关

- **返回:**

  None

- **用法:**

  ```python
  from nonebot import message_preprocessor

  # 全局关闭命令test, 对所有消息生效
  CommandManager.switch_command_global(("test", ), state=False)

  @message_preprocessor
  async def processor(bot: NoneBot, event: CQEvent, plugin_manager: PluginManager):
      plugin_manager.cmd_manager.switch_command_global(("test", ), state=False)
  ```

#### `switch_command(self, cmd_name, state)`

- **说明:**

  根据 `state` 更改 command 的状态。仅对当前消息有效。

- **参数:**

  - `cmd_name: CommandName_T`: 命令名称
  - `state: bool | None`:
    - `None(default)`: 切换状态，即 开 -> 关、关 -> 开
    - `bool`: 切换至指定状态，`True` -> 开、`False` -> 关

- **返回:**

  None

- **用法:**

  ```python
  from nonebot import message_preprocessor

  # 关闭命令test, 仅对当前消息生效
  @message_preprocessor
  async def processor(bot: NoneBot, event: CQEvent, plugin_manager: PluginManager):
      plugin_manager.cmd_manager.switch_command(("test", ), state=False)
  ```

### _class_ `CommandSession`

继承自 `BaseSession` 类，表示命令 Session。

#### _readonly property_ `state` <Badge text="1.2.0+"/>

- **类型:** `State_T`

- **说明:**

  命令会话的状态数据（包括已获得的所有参数）。

  属性本身只读，但属性中的内容可读写。

- **用法:**

  ```python
  if not session.state.get('initialized'):
      # ... 初始化工作
      session.state['initialized'] = True
  ```

  在命令处理函数的开头进行**每次命令调用只应该执行一次的初始化操作**。

#### _readonly property_ `is_first_run`

- **类型:** `bool`

- **说明:**

  命令会话是否第一次运行。

#### `current_key`

- **类型:** `str | None`

- **说明:**

  命令会话当前正在询问用户的参数的键（或称参数的名字）。第一次运行会话时，该属性为 `None`。

#### `current_arg`

- **类型:** `str`

- **说明:**

  命令会话当前参数。实际上是 酷 Q 收到的消息去掉命令名的剩下部分，因此可能存在 CQ 码。

#### _readonly property_ `current_arg_text`

- **类型:** `str`

- **说明:**

  `current_arg` 属性的纯文本部分（不包含 CQ 码），各部分使用空格连接。

#### _readonly property_ `current_arg_images`

- **类型:** `list[str]`

- **说明:**

  `current_arg` 属性中所有图片的 URL 的列表，如果参数中没有图片，则为 `[]`。

#### _readonly property_ `argv`

- **类型:** `list[str]`

- **说明:**

  命令参数列表，类似于 `sys.argv`，本质上是 `session.state.get('argv', [])`，**需要搭配 `on_command(..., shell_like=True)` 使用**。

- **用法:**

  ```python
  @on_command('some_cmd', shell_like=True)
  async def _(session: CommandSession):
      argv = session.argv
  ```

#### `get(key, *, prompt=None, arg_filters=None, **kwargs)`

- **说明:**

  从 `state` 属性获取参数，如果参数不存在，则暂停当前会话，向用户发送提示，并等待用户的新一轮交互。

  如果需要暂停当前会话，则命令处理器中，此函数调用之后的语句将不会被执行（除非捕获了此函数抛出的特殊异常）。

  注意，一旦传入 `arg_filters` 参数（参数过滤器），则等用户再次输入时，_command_func._`args_parser` 所注册的参数解析函数将不会被运行，而会在对 `current_arg` 依次运行过滤器之后直接将其放入 `state` 属性中。

  :::tip
  推荐使用下面的 `aget` 方法。
  :::

- **参数:**

  - `key: Any`: 参数的键
  - `prompt: Message_T | None`: 提示的消息内容
  - `arg_filters: list[Filter_T] | None` <Badge text="1.2.0+"/>: 用于处理和验证用户输入的参数的过滤器
  - `**kwargs: Any`: 其它传入 `BaseSession.send()` 的命名参数

- **返回:**

  - `Any`: 参数的值

- **用法:**

  ```python
  location = session.get('location', prompt='请输入要查询的地区')
  ```

  获取位置信息，如果当前还不知道，则询问用户。

  ```python
  from nonebot.command.argfilter import extractors, validators

  time = session.get(
      'time', prompt='你需要我在什么时间提醒你呢？',
      arg_filters=[
          extractors.extract_text,  # 取纯文本部分
          controllers.handle_cancellation(session),  # 处理用户可能的取消指令
          str.strip,  # 去掉两边空白字符
          # 正则匹配输入格式
          validators.match_regex(r'^\d{4}-\d{2}-\d{2}$', '格式不对啦，请重新输入')
      ]
  )
  ```

  获取时间信息，如果当前还不知道，则询问用户，等待用户输入之后，会依次运行 `arg_filters` 参数中的过滤器，以确保参数内容和格式符合要求。

#### _coroutine_ `aget(key=..., *, prompt=None, arg_filters=None, force_update=..., **kwargs)` <Badge text="v1.8.0+"/>

- **说明:**

  从 `state` 属性获取参数，如果参数不存在，则异步地暂停当前会话，向用户发送提示，并等待用户的进一步交互。

  当用户再次输入时，不会重新运行命令处理器，而是回到此函数调用之处继续执行。

  注意，一旦传入 `arg_filters` 参数（参数过滤器），则等用户再次输入时，_command_func._`args_parser` 所注册的参数解析函数将不会被运行，而会在对 `current_arg` 依次运行过滤器之后直接将其放入 `state` 属性中。

- **参数:**

  - `key: Any`: 参数的键，若不传入则使用默认键值
  - `prompt: Message_T | None`: 提示的消息内容
  - `arg_filters: list[Filter_T] | None`: 用于处理和验证用户输入的参数的过滤器
  - `force_update: bool`: 是否强制获取用户新的输入，若是，则会忽略已有的当前参数，若 `key` 不传入则为真，否则默认为假
  - `**kwargs: Any`: 其它传入 `BaseSession.send()` 的命名参数

- **返回:**

  - `Any`: 参数的值

- **用法:**

  ```python
  from nonebot.command.argfilter import extractors, validators

  note = await session.aget(
      'note', prompt='你需要我提醒你什么呢',
      arg_filters=[
          extractors.extract_text,  # 取纯文本部分
          controllers.handle_cancellation(session),  # 处理用户可能的取消指令
          str.strip  # 去掉两边空白字符
      ]
  )

  time = await session.aget(
      'time', prompt='你需要我在什么时间提醒你呢？',
      arg_filters=[
          extractors.extract_text,  # 取纯文本部分
          controllers.handle_cancellation(session),  # 处理用户可能的取消指令
          str.strip,  # 去掉两边空白字符
          # 正则匹配输入格式
          validators.match_regex(r'^\d{4}-\d{2}-\d{2}$', '格式不对啦，请重新输入')
      ]
  )
  ```

  连续获取多个参数，如果当前还不知道，则询问用户，等待用户输入之后，会依次运行 `arg_filters` 参数中的过滤器，以确保参数内容和格式符合要求。

#### `pause(message=None, **kwargs)`

- **说明:**

  暂停当前命令会话，并发送消息。此函数调用之后的语句将不会被执行（除非捕获了此函数抛出的特殊异常）。

  :::tip
  推荐使用下面的 `apause` 方法。
  :::

- **参数:**

  - `message: Message_T | None`: 要发送的消息，若不传入则不发送
  - `**kwargs: Any`: 其它传入 `BaseSession.send()` 的命名参数

- **用法:**

  ```python
  if session.is_first_run:
      session.pause('请发送要处理的图片，发送 done 结束')
  if session.current_arg_text.strip() == 'done':
      session.finish('处理完成')
  process_images(session.current_arg_images)
  session.pause('请继续发送要处理的图片，发送 done 结束')
  ```

  需要连续接收用户输入，并且过程中不需要改变 `current_key` 时，使用此函数暂停会话。

#### _coroutine_ `apause(message=None, **kwargs)` <Badge text="v1.8.0+"/>

- **说明:**

  异步地暂停当前命令会话，并发送消息。

  当用户再次输入时，不会重新运行命令处理器，而是回到此函数调用之处继续执行。

- **参数:**

  - `message: Message_T | None`: 要发送的消息，若不传入则不发送
  - `**kwargs: Any`: 其它传入 `BaseSession.send()` 的命名参数

- **用法:**

  ```python
  await session.apause('请发送要处理的图片，发送 done 结束')
  while True:
      if session.current_arg_text.strip() == 'done':
          session.finish('处理完成')
      process_images(session.current_arg_images)
      await session.apause('请继续发送要处理的图片，发送 done 结束')
  ```

  需要连续接收用户输入，并且过程中不需要改变 `current_key` 时，使用此函数暂停会话。

#### `finish(message=None, **kwargs)`

- **说明:**

  结束当前命令会话，并发送消息。此函数调用之后的语句将不会被执行（除非捕获了此函数抛出的特殊异常）。

  调用此函数后，命令将被视为已经完成，当前命令会话将被移除。

- **参数:**

  - `message: Message_T | None`: 要发送的消息，若不传入则不发送
  - `**kwargs: Any`: 其它传入 `BaseSession.send()` 的命名参数

- **用法:**

  ```python
  session.finish('感谢您的使用～')
  ```

#### `switch(new_message)`

- **说明:**

  结束当前会话，改变当前消息事件中的消息内容，然后重新处理消息事件。

  此函数可用于从一个命令中跳出，将用户输入的剩余部分作为新的消息来处理，例如可实现以下对话：

  ```
  用户：帮我查下天气
  Bot：你要查询哪里的天气呢？
  用户：算了，帮我查下今天下午南京到上海的火车票吧
  Bot：今天下午南京到上海的火车票有如下班次：blahblahblah
  ```

  这里进行到第三行时，命令期待的是一个地点，但实际发现消息的开头是「算了」，于是调用 `switch('帮我查下今天下午南京到上海的火车票吧')`，结束天气命令，将剩下来的内容作为新的消息来处理（触发火车票插件的自然语言处理器，进而调用火车票查询命令）。

- **参数:**

  - `new_message: Message_T`: 要覆盖消息事件的新消息内容

- **用法:**

  ```python
  @my_cmd.args_parser
  async def _(session: CommandSession)
      if not session.is_first_run and session.current_arg.startswith('算了，'):
          session.switch(session.current_arg[len('算了，'):])
  ```

  使用「算了」来取消当前命令，转而进入新的消息处理流程。这个例子比较简单，实际应用中可以使用更复杂的 NLP 技术来判断。

### _coroutine_ `call_command(bot, event, name, *, current_arg='', args=None, check_perm=True, disable_interaction=False)`

- **说明:**

  从内部直接调用命令。可用于在一个插件中直接调用另一个插件的命令。

- **参数:**

  - `bot: NoneBot`: NoneBot 对象
  - `event: aiocqhttp.Event`: 事件对象
  - `name: str | CommandName_T`: 要调用的命令名
  - `current_arg: str`: 命令会话的当前输入参数
  - `args: CommandArgs_T | None`: 命令会话的（初始）参数（将会被并入命令会话的 `state` 属性）
  - `check_perm: bool`: 是否检查命令的权限，若否，则即使当前事件上下文并没有权限调用这里指定的命令，也仍然会调用成功
  - `disable_interaction: bool`: 是否禁用交互功能，若是，则该命令的会话不会覆盖任何当前已存在的命令会话，新创建的会话也不会保留

- **返回:**

  - `bool`: 命令是否调用成功

- **用法:**

  ```python
  await call_command(bot, event, 'say', current_arg='[CQ:face,id=14]', check_perm=False)
  ```

  从内部调用 `say` 命令，且不检查权限。

### `kill_current_session(event)`

- **说明:**

  强行移除当前已存在的任何命令会话，即使它正在运行。该函数可用于强制移除执行时间超过预期的命令，以保证新的消息不会被拒绝服务。

- **参数:**

  - `event: aiocqhttp.Event`: 事件对象

- **返回:**

  - `None`

- **用法:**

  ```python
  @on_command('kill', privileged=True)
  async def _(session: CommandSession):
      kill_current_session(session.event)
  ```

  在特权命令 `kill` 中强行移除当前正在运行的会话。

## `nonebot.command.argfilter` 模块 <Badge text="1.2.0+"/>

本模块主要用于命令参数过滤相关的功能。

命令参数过滤器主要有下面几种：

- 提取器，从用户输入的原始参数内容中提取需要的内容，`extractors` 子模块中提供了一些常用提取器
- 修剪器，将用户输入的原始参数内容进行适当修剪，例如 `str.strip` 可以去掉两遍的空白字符
- 验证器，验证参数的格式、长度等是否符合要求，`validators` 子模块中提供了一些常用验证器
- 转换器，将参数进行类型或格式上的转换，例如 `int` 可以将字符串转换成整数，`converters` 子模块中提供了一些常用转换器
- 控制器，根据用户输入或当前会话状态对会话进行相关控制，例如当用户发送 `算了` 时停止当前会话，`controllers` 子模块中提供了一些常用控制器

### _class_ `ValidateError`

用于表示验证失败的异常类。

#### `message`

- **类型:** `Message_T | None`

- **说明:**

  验证失败时要发送的错误提示消息。如果为 `None`，则使用配置中的 `DEFAULT_VALIDATION_FAILURE_EXPRESSION`。

## `nonebot.command.argfilter.extractors` 模块 <Badge text="1.2.0+"/>

提供几种常用的提取器。

### `extract_text`

- **说明:**

  提取消息中的纯文本部分（使用空格合并纯文本消息段）。

- **输入类型:** `Message_T`

- **输出类型:** `str`

### `extract_image_urls`

- **说明:**

  提取消息中的图片 URL 列表。

- **输入类型:** `Message_T`

- **输出类型:** `list[str]`

### `extract_numbers`

- **说明:**

  提取消息中的所有数字（浮点数）。

- **输入类型:** `Message_T`

- **输出类型:** `list[float]`

## `nonebot.command.argfilter.validators` 模块 <Badge text="1.2.0+"/>

提供几种常用的验证器。

这些验证器的工厂函数全都接受可选参数 `message: Message_T | None`，用于在验证失败时向用户发送错误提示。使用这些的验证器时，必须先调用验证器的工厂函数，其返回结果才是真正的验证器，例如：

```python
session.get('arg1', prompt='请输入 arg1：',
            arg_filters=[extract_text， not_empty('输入不能为空')])
```

注意 `extract_text` 和 `not_empty` 使用上的区别。

### `not_empty(message=None)`

- **说明:**

  验证输入不为空。

- **输入类型:** `Any`

- **输出类型:** `Any`

### `fit_size(min_length=0, max_length=None, message=None)`

- **说明:**

  验证输入的长度（大小）在 `min_length` 到 `max_length` 之间（包括两者）。

- **参数:**

  - `min_length: int`: 最小长度
  - `max_length: int | None`: 最大长度

- **输入类型:** `Sized`

- **输出类型:** `Sized`

### `match_regex(pattern, message=None, *, flags=0, fullmatch=False)`

- **说明:**

  验证输入是否匹配正则表达式。

- **参数:**

  - `pattern: str`: 正则表达式
  - `flags`: 传入 `re.compile()` 的标志
  - `fullmatch: bool`: 是否使用完全匹配（`re.fullmatch()`）

- **输入类型:** `str`

- **输出类型:** `str`

### `ensure_true(bool_func, message=None)`

- **说明:**

  验证输入是否能使给定布尔函数返回 `True`。

- **参数:**

  - `bool_func: (Any) -> bool`: 接受输入、返回布尔值的函数

- **输入类型:** `Any`

- **输出类型:** `Any`

### `between_inclusive(start=None, end=None, message=None)`

- **说明:**

  验证输入是否在 `start` 到 `end` 之间（包括两者）。

- **参数:**

  - `start`: 范围开始
  - `end`: 范围结束

- **输入类型:** `Comparable`

- **输出类型:** `Comparable`

## `nonebot.command.argfilter.converters` 模块 <Badge text="1.2.0+"/>

提供几种常用的转换器。

### `simple_chinese_to_bool`

- **说明:**

  将中文（`好`、`不行` 等）转换成布尔值。

- **输入类型:** `str`

- **输出类型:** `bool | None`

### `split_nonempty_lines`

- **说明:**

  按行切割文本，并忽略所有空行。

- **输入类型:** `str`

- **输出类型:** `list[str]`

### `split_nonempty_stripped_lines`

- **说明:**

  按行切割文本，并对每一行进行 `str.strip`，再忽略所有空行。

- **输入类型:** `str`

- **输出类型:** `list[str]`

## `nonebot.command.argfilter.controllers` 模块 <Badge text="1.3.0+"/>

提供几种常用的控制器。

这些验证器通常需要提供一些参数进行一次调用，返回的结果才是真正的验证器，其中的技巧在于通过闭包使要控制的对象能够被内部函数访问。

### `handle_cancellation(session)`

- **说明:**

  在用户发送 `算了`、`不用了`、`取消吧`、`停` 之类的话的时候，结束当前传入的命令会话（调用 `session.finish()`），并发送配置项 `SESSION_CANCEL_EXPRESSION` 所填的内容。

  如果不是上述取消指令，则将输入原样输出。

- **参数:**

  - `session: CommandSession`: 要控制的命令会话

- **输入类型:** `Any`

- **输出类型:** `Any`

## `nonebot.natural_language` 模块

### _decorator_ `on_natural_language(keywords=None, *, permission=EVERYBODY, only_to_me=True, only_short_message=True, allow_empty_message=False)` <Badge text="1.6.0-" type="error" />

- **说明:**

  将函数装饰为自然语言处理器。

- **参数:**

  - `keywords: (Iterable[str] | str) | None`: 要响应的关键词，若传入 `None`，则响应所有消息
  - `permission: int`: 自然语言处理器所需要的权限，不满足权限的用户将无法触发该处理器
  - `only_to_me: bool`: 是否只响应确定是在和「我」（机器人）说话的消息（在开头或结尾 @ 了机器人，或在开头称呼了机器人昵称）
  - `only_short_message: bool`: 是否只响应短消息
  - `allow_empty_message: bool`: 是否响应内容为空的消息（只有 @ 或机器人昵称）

- **要求:**

  被装饰函数必须是一个 async 函数，且必须接收且仅接收一个位置参数，类型为 `NLPSession`，即形如：

  ```python
  async def func(session: NLPSession):
      pass
  ```

- **用法:**

  ```python
  @on_natural_language({'天气'}, only_to_me=False)
  async def _(session: NLPSession):
      return IntentCommand('weather', 100.0)
  ```

  响应所有带有「天气」关键词的消息，当做 `weather` 命令处理。

### _class_ `NLPSession`

继承自 `BaseSession` 类，表示自然语言处理 Session。

#### `msg`

- **类型:** `str`

- **说明:**

  以字符串形式表示的消息内容，已去除开头的 @ 和机器人称呼，可能存在 CQ 码。

#### `msg_text`

- **类型:** `str`

- **说明:**

  消息内容的纯文本部分，已去除所有 CQ 码／非 `text` 类型的消息段。各纯文本消息段之间使用空格连接。

#### `msg_images`

- **类型:** `list[str]`

- **说明:**

  消息内容中所有图片的 URL 的列表，如果消息中没有图片，则为 `[]`。

### _class_ `IntentCommand` <Badge text="1.2.0+"/>

用于表示自然语言处理之后得到的意图命令，是一个 namedtuple，由自然语言处理器返回。

#### `confidence`

- **类型:** `float`

- **说明:**

  意图的置信度，即表示对当前推测的用户意图有多大把握。

#### `name`

- **类型:** `str | CommandName_T`

- **说明:**

  命令的名字。

#### `args`

- **类型:** `CommandArgs_T | None`

- **说明:**

  命令的（初始）参数。

#### `current_arg`

- **类型:** `str | None`

- **说明:**

  命令的当前输入参数。

#### `__init__(confidence, name, args=None, current_arg=None)`

- **说明:**

  初始化 `IntentCommand` 对象，参数即为上面的几个属性。

## `nonebot.notice_request` 模块

### _decorator_ `on_notice(*events)` <Badge text="1.6.0-" type="error" />

- **说明:**

  将函数装饰为通知处理器。

- **参数:**

  - `*events: str`: 要处理的通知类型（`notice_type`），若不传入，则处理所有通知

- **要求:**

  被装饰函数必须是一个 async 函数，且必须接收且仅接收一个位置参数，类型为 `NoticeSession`，即形如：

  ```python
  async def func(session: NoticeSession):
      pass
  ```

- **用法:**

  ```python
  @on_notice
  async def _(session: NoticeSession):
      logger.info('有新的通知事件：%s', session.event)

  @on_notice('group_increase')
  async def _(session: NoticeSession):
      await session.send('欢迎新朋友～')
  ```

  收到所有通知时打日志，收到新成员进群通知时除了打日志还发送欢迎信息。

### _decorator_ `on_request(*events)` <Badge text="1.6.0-" type="error" />

- **说明:**

  将函数装饰为请求处理器。

- **参数:**

  - `*events: str`: 要处理的请求类型（`request_type`），若不传入，则处理所有请求

- **要求:**

  被装饰函数必须是一个 async 函数，且必须接收且仅接收一个位置参数，类型为 `RequestSession`，即形如：

  ```python
  async def func(session: RequestSession):
      pass
  ```

- **用法:**

  ```python
  @on_request
  async def _(session: RequestSession):
      logger.info('有新的请求事件：%s', session.event)

  @on_request('group')
  async def _(session: RequestSession):
      await session.approve()
  ```

  收到所有请求时打日志，收到群请求时除了打日志还同意请求。

### _class_ `NoticeSession`

继承自 `BaseSession` 类，表示通知类事件的 Session。

### _class_ `RequestSession`

继承自 `BaseSession` 类，表示请求类事件的 Session。

#### _coroutine_ `approve(remark='')`

- **说明:**

  同意当前请求。

- **参数:**

  - `remark: str`: 好友备注，只在好友请求时有效

- **返回:**

  - `None`

- **异常:**

  - `CQHttpError`: 发送失败时抛出，实际由 [aiocqhttp] 抛出，等价于 `aiocqhttp.Error`

- **用法:**

  ```python
  await session.approve()
  ```

#### _coroutine_ `reject(reason='')`

- **说明:**

  拒绝当前请求。

- **参数:**

  - `reason: str`: 拒绝理由，只在群请求时有效

- **返回:**

  - `None`

- **异常:**

  - `CQHttpError`: 发送失败时抛出，实际由 [aiocqhttp] 抛出，等价于 `aiocqhttp.Error`

- **用法:**

  ```python
  await session.reject()
  ```

## `nonebot.session` 模块

### _class_ `BaseSession`

基础 session 类，`CommandSession` 等均继承自此类。

#### `bot`

- **类型:** `NoneBot`

- **说明:**

  Session 对应的 NoneBot 对象。

- **用法:**

  ```python
  await session.bot.send('hello')
  ```

  在当前 Session 对应的上下文中发送 `hello`。

#### `event` <Badge text="1.5.0+"/>

- **类型:** `aiocqhttp.Event`

- **说明:**

  CQHTTP 上报的事件数据对象，具体请参考 [`aiocqhttp.Event`](https://aiocqhttp.nonebot.dev/module/aiocqhttp/index.html#aiocqhttp.Event) 和 [事件上报](https://cqhttp.cc/docs/#/Post)。

- **用法:**

  ```python
  user_id = session.event['user_id']
  group_id = session.event.group_id
  ```

  获取当前事件的 `user_id` 和 `group_id` 字段。

#### `ctx` <Badge text="1.5.0-" type="error"/>

- **类型:** `aiocqhttp.Event`

- **说明:**

  CQHTTP 上报的事件数据对象，或称事件上下文，具体请参考 [事件上报](https://cqhttp.cc/docs/#/Post)。

- **用法:**

  ```python
  user_id = session.ctx['user_id']
  ```

  获取当前事件的 `user_id` 字段。

#### _readonly property_ `self_id` <Badge text="1.1.0+"/>

- **类型:** `int`

- **说明:**

  当前 session 对应的 QQ 机器人账号，在多个机器人账号使用同一个 NoneBot 后端时可用于区分当前收到消息或事件的是哪一个机器人。

  等价于 `session.event.self_id`。

- **用法:**

  ```python
  await bot.send_private_msg(self_id=session.self_id, user_id=12345678, message='Hello')
  ```

#### _coroutine_ `send(message, *, at_sender=False, ensure_private=False, ignore_failure=True, **kwargs)`

- **说明:**

  发送消息到 Session 对应的上下文中。

- **参数:**

  - `message: Message_T`: 要发送的消息内容
  - `at_sender: bool`: 是否 @ 发送者，对私聊不起作用
  - `ensure_private: bool`: 确保消息发送到私聊，对于群组和讨论组消息上下文，会私聊发送者
  - `ignore_failure: bool`: 发送失败时忽略 `CQHttpError` 异常
  - `**kwargs: Any`: 其它传入 `CQHttp.send()` 的命名参数

- **返回:**

  - `Any` <Badge text="1.1.0+"/>: 返回 CQHTTP 插件发送消息接口的调用返回值，具体见 aiocqhttp 的 [API 调用](https://aiocqhttp.nonebot.dev/#/what-happened#api-%E8%B0%83%E7%94%A8)

- **异常:**

  - `CQHttpError`: 发送失败时抛出，实际由 [aiocqhttp] 抛出，等价于 `aiocqhttp.Error`

- **用法:**

  ```python
  await session.send('hello')
  ```

  在当前 Session 对应的上下文中发送 `hello`。

## `nonebot.permission` 模块

NoneBot 支持为命令和自然语言处理器设置触发条件，此条件为一个类型为 `PermissionPolicy_T` 的可调用对象：

```python
# 同步：返回值恒为假，即表示所有消息和发送者都没有权限
disabled: PermissionPolicy_T = lambda sender: False

# 同步：当消息是群聊，且发送者既不是管理员也不是群主时给予权限
def normal_group_member(sender: SenderRoles):
    return sender.is_groupchat and not sender.is_admin and not sender.is_owner

# 异步：在检查器中查询数据库再根据返回值决定是否给予权限
async def db_check(sender: SenderRoles):
    query = await db.execute('if exists (select * from list where user=?) 1 else 0', (sender.event.user_id,))
    return query[0] != 0
```

在实际使用时应当避免挂起太久的异步操作。在定义了这些条件后，可作为 `permission` 参数传递给相关的装饰器：

```python
permit_group = { 768887710 }
banned_people = { 10000, 10001 }
def foo(sender: SenderRoles):
    return sender.is_groupchat and sender.from_group(permit_group) \
    and not sender.sendby(banned_people)

@on_natural_language({'天气'}, only_to_me=False, permission=(foo, db_check))                        # 需要同时满足 foo 和 db_check
                                                # permission=aggregate_policy((foo, db_check))      # 需要同时满足 foo 和 db_check
                                                # permission=aggregate_policy((foo, db_check), any) # 只需满足一个
async def _(session: NLPSession):
    return IntentCommand('weather', 100.0)
```

### _class_ `SenderRoles` <Badge text="1.9.0+"/>

封装了原生的 `CQEvent` 便于权限检查。此类的实例一般会传入 `PermissionPolicy_T` 作为参数。

#### `bot`

- **类型:** `NoneBot`

#### `event`

- **类型:** `CQEvent`

#### `sender`

- **类型:** `dict[str, Any] | None`

- **说明:**

  只有消息是群消息的时候才会有这个属性，其内容是 `/get_group_member_info` API 调用的返回值。

#### _staticmethod_ _coroutine_ `create(bot, event)`

- **说明:**

  构造 `SenderRoles`。

- **参数:**

  - `bot: NoneBot`: 接收事件的 NoneBot 对象
  - `event: CQEvent`: 上报事件

- **返回:**

  - `SenderRoles`

- **用法:**

  ```python
  sender = await SenderRoles.create(session.bot, session.event)
  if sender.is_groupchat:
    if sender.is_owner:
        await process_owner(session)
    elif sender.is_admin:
        await process_admin(session)
    else:
        await process_member(session)
  ```

  根据发送者的身份决定相应命令处理方式。

#### _readonly property_ `is_superuser`

- **类型:** `bool`

- **说明:**

  发送者是配置文件中设置的超级用户。

#### _readonly property_ `is_groupchat`

- **类型:** `bool`

- **说明:**

  消息是群聊消息。

#### _readonly property_ `is_anonymous`

- **类型:** `bool`

- **说明:**

  消息是匿名消息。

#### _readonly property_ `is_admin`

- **类型:** `bool`

- **说明:**

  发送者是群管理员。

#### _readonly property_ `is_owner`

- **类型:** `bool`

- **说明:**

  发送者是群主。

#### _readonly property_ `is_privatechat`

- **类型:** `bool`

- **说明:**

  消息是私聊消息。

#### _readonly property_ `is_private_friend`

- **类型:** `bool`

- **说明:**

  消息是好友私聊消息。

#### _readonly property_ `is_private_group`

- **类型:** `bool`

- **说明:**

  消息是群私聊消息。

#### _readonly property_ `is_private_discuss`

- **类型:** `bool`

- **说明:**

  消息是讨论组私聊消息。

#### _readonly property_ `is_discusschat`

- **类型:** `bool`

- **说明:**

  消息是讨论组消息。

#### `from_group(self, group_id)`

- **说明:**

  表示发送者是否来自于群 `group_id`。

- **参数:**

  - `group_id: int | Container[int]`: 群号码，可以为多个群号。

- **返回:**

  `bool`

#### `sent_by(self, sender_id)`

- **说明:**

  表示发送者 QQ 号是否是 `sender_id`。

- **参数:**

  - `sender_id: int | Container[int]`: 发送者 QQ 号，可以是多个。

- **返回:**

  `bool`

### _coroutine_ `check_permission(bot, event, policy)`

- **说明:**

  检查用户是否具有所要求的权限。

  一般用户应该没有必要使用该函数。

- **参数:**

  - `bot: NoneBot`: NoneBot 对象
  - `event: aiocqhttp.Event`: 消息事件对象
  - `policy: PermissionPolicy_T` <Badge text="1.9.0+"/>: 返回布尔值的权限检查策略

- **返回:**

  - `bool`: 消息事件所对应的上下文是否具有所要求的权限

- **用法:**

  ```python
  has_perm = await check_permission(bot, event, normal_group_member)
  ```

### `aggregate_policy(policies, aggregator=all)` <Badge text="1.9.0+"/>

- **说明:**

  在默认参数下，将多个权限检查策略函数使用 AND 操作符连接并返回单个权限检查策略。在实现中对这几个策略使用内置 `all` 函数，会优先执行同步函数而且尽可能在同步模式的情况下短路。

  在新的策略下，只有事件满足了 `policies` 中所有的原策略，才会返回 `True`。

  `aggregator` 参数也可以设置为其他函数，例如 `any`：在此情况下会使用 `OR` 操作符连接。

  如果参数中所有的策略都是同步的，则返回值是同步的，否则返回值是异步函数。

- **参数:**

  - `policies: Iterable[PermissionPolicy_T]`: 要合并的权限检查策略
  - `aggregator: (Iterable[object]) -> bool`: 用于合并策略的函数

- **返回:**

  - `PermissionPolicy_T`: 新的权限检查策略

- **用法:**

  ```python
  # 以下两种方式在效果上等同
  policy1 = lambda sender: sender.is_groupchat and sender.from_group(123456789)

  policy2 = aggregate_policy(lambda sender: sender.is_groupchat,
                             lambda sender: sender.from_group(123456789))
  ```

### 权限声明常量

NoneBot 在 1.9.0 后改变了声明权限的风格。为了保持向前兼容，尽管不建议使用，如果你的代码仍包含以下常量，则无需改动它们仍将工作：

- `PRIVATE_FRIEND`: 好友私聊
- `PRIVATE_GROUP`: 群临时私聊
- `PRIVATE_DISCUSS`: 讨论组临时私聊
- `PRIVATE_OTHER`: 其它私聊
- `PRIVATE`: 任何私聊
- `DISCUSS`: 讨论组
- `GROUP_MEMBER`: 群成员
- `GROUP_ADMIN`: 群管理员
- `GROUP_OWNER`: 群主
- `GROUP`: 任何群成员
- `SUPERUSER`: 超级用户
- `EVERYBODY`: 任何人

用于权限声明的常量可通过 `|` 合并，在命令或自然语言处理器装饰器的 `permission` 参数中传入，表示允许触发相应命令或自然语言处理器的用户类型。

例如下面的代码中，只有私聊和群管理员可以访问 `hello` 命令：

```python
@nonebot.on_command('hello', permission=PRIVATE | GROUP_ADMIN)
async def _(session):
    pass
```

需要注意的是，当一个用户是「群管理员」时，ta 同时也是「群成员」；当 ta 是「群主」时，ta 同时也是「群管理员」和「群成员」。

在 1.9.0 后，这些常量的类型从 `int` 改变为了 `PermissionPolicy_T`，所以如果你之前包含了它们的 type hints，或用了不寻常的方法来获取它们的值，则可能会导致错误。

## `nonebot.log` 模块

### `logger`

- **类型:** `logging.Logger`

- **说明:**

  NoneBot 全局的 logger。

- **用法:**

  ```python
  logger.debug('Some log message here')
  ```

## `nonebot.helpers` 模块

### `context_id(event, *, mode='default', use_hash=False)`

- **说明:**

  获取事件对应的上下文的唯一 ID。

- **参数:**

  - `event: aiocqhttp.Event`: 事件对象
  - `mode: str`: ID 的计算模式
    - `'default'`: 默认模式，任何一个上下文都有其唯一 ID
    - `'group'`: 群组模式，同一个群组或讨论组的上下文（即使是不同用户）具有相同 ID
    - `'user'`: 用户模式，同一个用户的上下文（即使在不同群组）具有相同 ID
  - `use_hash: bool`: 是否将计算出的 ID 使用 MD5 进行哈希

- **返回:**

  - `str`: 事件对应的上下文的唯一 ID

- **用法:**

  ```python
  ctx_id = context_id(session.event, use_hash=True)
  ```

  获取当前 Session 的事件对应的上下文的唯一 ID，并进行 MD5 哈希，得到的结果可用于图灵机器人等 API 的调用。

### _coroutine_ `send(bot, event, message, *, ensure_private=False, ignore_failure=True, **kwargs)`

- **说明:**

  发送消息到指定事件的上下文中。

- **参数:**

  - `bot: NoneBot`: NoneBot 对象
  - `event: aiocqhttp.Event`: 事件对象
  - `message: Message_T`: 要发送的消息内容
  - `ensure_private: bool`: 确保消息发送到私聊，对于群组和讨论组消息上下文，会私聊发送者
  - `ignore_failure: bool`: 发送失败时忽略 `CQHttpError` 异常
  - `**kwargs: Any`: 其它传入 `CQHttp.send()` 的命名参数

- **返回:**

  - `Any` <Badge text="1.1.0+"/>: 返回 CQHTTP 插件发送消息接口的调用返回值，具体见 aiocqhttp 的 [API 调用](https://aiocqhttp.nonebot.dev/#/what-happened#api-%E8%B0%83%E7%94%A8)

- **异常:**

  - `CQHttpError`: 发送失败时抛出，实际由 [aiocqhttp] 抛出，等价于 `aiocqhttp.Error`

- **用法:**

  ```python
  await send(bot, event, 'hello')
  ```

### _coroutine_ `send_to_superusers(bot, message, **kwargs)` <Badge text="1.7.0+"/>

- **说明:**

  发送私聊消息到全体超级用户（即配置下的 `SUPERUSERS`）。

- **参数:**

  - `bot: NoneBot`: NoneBot 对象
  - `message: Message_T`: 要发送的消息内容
  - `**kwargs: Any`: 其它传入 `bot.send_private_msg()` 的命名参数

- **返回:**

  - `None`

- **异常:**

  - `CQHttpError`: 发送失败时抛出，实际由 [aiocqhttp] 抛出，等价于 `aiocqhttp.Error`

- **用法:**

  ```python
  await send_to_superusers(bot, f'被群 {event.group_id} 踢出了')
  ```

### `render_expression(expr, *args, escape_args=True, **kwargs)`

- **说明:**

  渲染 Expression。

- **参数:**

  - `expr: Expression_T`: 要渲染的 Expression，对于 Expression 的三种类型：`str`、`Sequence[str]`、`(*Any, **Any) -> str`，行为分别是：
    - `str`：以 `*args`、`**kwargs` 为参数，使用 `str.format()` 进行格式化
    - `Sequence[str]`：随机选择其中之一，进行上面 `str` 的操作
    - `(*Any, **Any) -> str`：以 `*args`、`**kwargs` 为参数，调用该可调用对象/函数，对返回的字符串进行上面 `str` 的操作
  - `escape_args: bool`: 是否对渲染参数进行转义
  - `*args: Any`: 渲染参数
  - `**kwargs: Any`: 渲染参数

- **返回:**

  - `str`: 渲染出的消息字符串

- **用法:**

  ```python
  msg1 = render_expression(
      ['你好，{username}！', '欢迎，{username}～'],
      username=username
  )
  msg2 = render_expression('你所查询的城市是{}', city)
  ```

## `nonebot.argparse` 模块

### _class_ `ArgumentParser`

继承自 `argparse.ArgumentParser` 类，修改部分函数实现使其适用于命令型聊天机器人。

此类可用于命令参数的解析。基本用法和 Python 内置的 `argparse.ArgumentParser` 类一致，下面主要列出与 Python 原生含义和行为不同的属性和方法。

- **用法:**

  ```python
  USAGE = r"""
  创建计划任务

  使用方法：
  XXXXXX
  """.strip()

  @on_command('schedule', shell_like=True)
  async def _(session: CommandSession):
      parser = ArgumentParser(session=session, usage=USAGE)
      parser.add_argument('-S', '--second')
      parser.add_argument('-M', '--minute')
      parser.add_argument('-H', '--hour')
      parser.add_argument('-d', '--day')
      parser.add_argument('-m', '--month')
      parser.add_argument('-w', '--day-of-week')
      parser.add_argument('-f', '--force', action='store_true', default=False)
      parser.add_argument('-v', '--verbose', action='store_true', default=False)
      parser.add_argument('--name', required=True)
      parser.add_argument('commands', nargs='+')

      args = parser.parse_args(session.argv)
      name = args.name
      # ...
  ```

#### `__init__(session=None, usage=None, **kwargs)`

- **说明:**

  初始化 `ArgumentParser` 对象。

- **参数:**

  - `session: CommandSession`: 当前需要解析参数的命令会话，用于解析失败或遇到 `--help` 时发送提示消息
  - `usage: str`: 命令的使用帮助，在参数为空或遇到 `--help` 时发送
  - `**kwargs: Any`: 和 Python `argparse.ArgumentParser` 类一致

#### `parse_args(args=None, namespace=None)`

- **说明:**

  解析参数。

  Python 原生的「打印到控制台」行为变为「发送消息到用户」，「退出程序」变为「结束当前命令会话」。

- **参数:**

  和 Python `argparse.ArgumentParser` 类一致。

- **异常:**

  无。

## `nonebot.sched` 模块

### _class_ `Scheduler`

继承自 `apscheduler.schedulers.asyncio.AsyncIOScheduler` 类，功能不变。

当 Python 环境中没有安装 APScheduler 包时，此类不存在，`Scheduler` 为 `None`。

## `nonebot.experimental` 模块 <Badge text="v1.8.0+"/>

实验性功能模块提供了和 NoneBot 原有特性略有重合但功能更灵活的 API。此模块中的内容可能会再未来版本中随时修改，合并，并且可能缺失注释。在使用前，请仔细阅读文档和开发日志以避免因 API 修改带来的麻烦。

## `nonebot.experimental.permission` 模块 <Badge text="v1.8.0+"/>

### `simple_allow_list(*, user_ids=... , group_ids=..., reverse=False)`

- **说明:**

  产生一个对应着白名单的权限检查策略。新的权限检查策略只有在发送者的 QQ 号来自于 `user_ids` 或者群组属于 `group_ids` 时才会返回 `True`。

  推荐使用者查看此函数的实现并尝试书写自己的权限检查器。

- **参数:**

  - `user_ids: Container[int]` <Badge text="1.8.2+"/>: 要加入白名单的 QQ 号们，默认为空
  - `group_ids: Container[int]` <Badge text="1.8.2+"/>: 要加入白名单的群号们，默认为空
  - `reverse: bool`: 如果为真，则返回值变为黑名单

- **返回:**

  - `PermissionPolicy_T`: 新的权限检查策略

- **用法:**

  ```python
  bans_list = simple_allow_list(group_ids={ 123456789, 987654321 }, reverse=True)
  # bans_list(987654321) -> False
  # bans_list(987654322) -> True
  @nonebot.on_command('签到', permission=bans_list)
  async def _(session: CommandSession):
      # 只有不是这两个群的时候才会执行
      ...
  ```

### `simple_time_range(begin_time, end_time, reverse=False, tz_info=None)`

- **说明:**

  产生一个对应着时间白名单的权限检查策略。新的权限检查策略只有在当前时间在 `begin_time` 和 `end_time` 之间时才会返回 `True`。

- **参数:**

  - `begin_time: datetime.time`: 起始时间
  - `end_time: datetime.time`: 结束时间
  - `reverse: bool`: 如果为真，则返回值变为黑名单
  - `tz_info: Any`: 传入 `datetime.datetime.now()` 的时区参数

- **返回:**

  - `PermissionPolicy_T`: 新的权限检查策略

## `nonebot.experimental.plugin` 模块 <Badge text="v1.8.0+"/>

为了保持向前的兼容，在 1.9.0 后此模块仅导出与主包完全相同的 `on_command` 和 `on_natural_language` 两个函数。会在未来版本中移除。

<!-- 链接 -->

[aiocqhttp]: https://github.com/nonebot/aiocqhttp/
