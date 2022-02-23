# nonebot.default_config

默认配置。

任何自定义配置都必须从此模块导入所有内容，然后设置自定义值来覆盖默认值。

例如:

```python
from nonebot.default_config import *

HOST = '0.0.0.0'
PORT = 8080
SUPERUSERS = {12345678}
COMMAND_START = {'', '/', '!', '／', '！'}
```

## _var_ `API_ROOT`

- **类型:** str

- **说明**

  CQHTTP 插件的 HTTP 接口地址，如果不使用 HTTP 通信，则无需设置。

  **默认值:** `''`

- **用法**

  ```python
  API_ROOT = 'http://127.0.0.1:5700'
  ```

  告诉 NoneBot CQHTTP 插件的 HTTP 服务运行在 `http://127.0.0.1:5700`。

## _var_ `ACCESS_TOKEN`

- **类型:** str

- **说明**

  需要和 CQHTTP 插件的配置中的 `access_token` 相同。

  **默认值:** `''`

## _var_ `SECRET`

- **类型:** str

- **说明**

  需要和 CQHTTP 插件的配置中的 `secret` 相同。

  **默认值:** `''`

## _var_ `HOST`

- **类型:** str

- **说明**

  NoneBot 的 HTTP 和 WebSocket 服务端监听的 IP／主机名。

  **默认值:** `'127.0.0.1'`

- **用法**

  ```python
  HOST = '0.0.0.0'
  ```

  监听服务器的所有 IP。

## _var_ `PORT`

- **类型:** int

- **说明**

  NoneBot 的 HTTP 和 WebSocket 服务端监听的端口。

  **默认值:** `8080`

- **用法**

  ```python
  PORT = 9876
  ```

  监听 9876 端口。

## _var_ `DEBUG`

- **类型:** bool

- **说明**

  是否以调试模式运行，生产环境需要设置为 `False` 以提高性能。

  **默认值:** `True`

- **用法**

  ```python
  DEBUG = False
  ```

  不使用调试模式运行。

## _var_ `SUPERUSERS`

- **类型:** Collection[int] <Badge text="1.7.0+"/>

- **说明**

  超级用户的 QQ 号，用于命令的权限检查。

  **默认值:** `set()`

- **用法**

  ```python
  SUPERUSERS = {12345678, 87654321}
  ```

  设置 `12345678` 和 `87654321` 为超级用户。

## _var_ `NICKNAME`

- **类型:** str | Iterable[str]

- **说明**

  机器人的昵称，用于辨别用户是否在和机器人说话。

  **默认值:** `''`

- **用法**

  ```python
  NICKNAME = {'奶茶', '小奶茶'}
  ```

  用户可以通过「奶茶」或「小奶茶」来呼唤机器人。

## _var_ `COMMAND_START`

- **类型:** Iterable[str | Pattern]

- **说明**

  命令的起始标记，用于判断一条消息是不是命令。

  **默认值:** `{'/', '!', '／', '！'}`

- **用法**

  ```python
  COMMAND_START = {'', '/', '!'}
  ```

  允许使用 `/`、`!` 作为命令起始符，或不用发送起始符。

## _var_ `COMMAND_SEP`

- **类型:** Iterable[str | Pattern]

- **说明**

  命令的分隔标记，用于将文本形式的命令切分为元组（实际的命令名）。

  **默认值:** `{'/', '.'}`

- **用法**

  ```python
  COMMAND_SEP = {'.'}
  ```

  将 `note.add` 这样的命令解析为 `('note', 'add')`。

## _var_ `DEFAULT_COMMAND_PERMISSION` <Badge text="1.9.0+"/>

- **类型:** (SenderRoles) -> bool | (SenderRoles) -> Awaitable[bool]

- **说明**

  命令处理器的缺省权限。默认为允许所有用户触发。

  **默认值:** `lambda _: True`

- **用法**

  ```python
  DEFAULT_COMMAND_PERMISSION = lambda s: s.is_superuser
  ```

  调用 `on_command` 而不提供 `permission` 参数时，命令仅能被超级用户触发。

## _var_ `DEFAULT_NLP_PERMISSION` <Badge text="1.9.0+"/>

- **类型:** (SenderRoles) -> bool | (SenderRoles) -> Awaitable[bool]

- **说明**

  自然语言处理器的缺省权限。默认为允许所有用户触发。

  **默认值:** `lambda _: True`

## _var_ `SESSION_EXPIRE_TIMEOUT`

- **类型:** datetime.timedelta | None

- **说明**

  命令会话的过期超时时长，超时后会话将被移除。`None` 表示不超时。

  **默认值:** `datetime.timedelta(minutes=5)`

- **用法**

  ```python
  from datetime import timedelta
  SESSION_EXPIRE_TIMEOUT = timedelta(minutes=2)
  ```

  设置过期超时为 2 分钟，即用户 2 分钟不发消息后，会话将被关闭。

## _var_ `SESSION_RUN_TIMEOUT`

- **类型:** datetime.timedelta | None

- **说明**

  命令会话的运行超时时长，超时后会话将被移除，命令处理函数会被异常所中断。此时用户可以调用新的命令，开启新的会话。`None` 表示不超时。

  **默认值:** `None`

- **用法**

  ```python
  from datetime import timedelta
  SESSION_RUN_TIMEOUT = timedelta(seconds=10)
  ```

  设置运行超时为 10 秒，即命令会话运行达到 10 秒，NoneBot 将认为它已经结束。

## _var_ `SESSION_RUNNING_EXPRESSION`

- **类型:** str | Sequence[str] | (*Any, **Any) -> str

- **说明**

  当有命令会话正在运行时，给用户新消息的回复。

  **默认值:** `'您有命令正在执行，请稍后再试'`

- **用法**

  ```python
  SESSION_RUNNING_EXPRESSION = ''
  ```

  设置为空，表示当有命令会话正在运行时，不回复用户的新消息。

## _var_ `SHORT_MESSAGE_MAX_LENGTH`

- **类型:** int

- **说明**

  短消息的最大长度。默认情况下（`only_short_message` 为 `True`），自然语言处理器只会响应消息中纯文本部分的长度总和小于等于此值的消息。

  **默认值:** `50`

- **用法**

  ```python
  SHORT_MESSAGE_MAX_LENGTH = 100
  ```

  设置最大长度为 100。

## _var_ `DEFAULT_VALIDATION_FAILURE_EXPRESSION` <Badge text="1.2.0+"/>

- **类型:** str | Sequence[str] | (*Any, **Any) -> str

- **说明**

  命令参数验证失败（验证器抛出 `ValidateError` 异常）、且验证器没有指定错误信息时，默认向用户发送的错误提示。

  **默认值:** `'您的输入不符合要求，请重新输入'`

- **用法**

  ```python
  DEFAULT_VALIDATION_FAILURE_EXPRESSION = '你发送的内容格式不太对呢，请检查一下再发送哦～'
  ```

  设置更亲切的默认错误提示。

## _var_ `MAX_VALIDATION_FAILURES` <Badge text="1.3.0+"/>

- **类型:** int

- **说明**

  命令参数验证允许的最大失败次数，用户输入错误达到这个次数之后，将会提示用户输入错误太多次，并结束命令会话。

  设置为 `0` 将不会检查验证失败次数。

  **默认值:** `3`

## _var_ `TOO_MANY_VALIDATION_FAILURES_EXPRESSION` <Badge text="1.3.0+"/>

- **类型:** str | Sequence[str] | (*Any, **Any) -> str

- **说明**

  命令参数验证失败达到 `MAX_VALIDATION_FAILURES` 次之后，向用户发送的提示。

  **默认值:** `'您输入错误太多次啦，如需重试，请重新触发本功能'`

- **用法**

  ```python
  TOO_MANY_VALIDATION_FAILURES_EXPRESSION = (
      '你输错太多次啦，需要的时候再叫我吧',
      '你输错太多次了，建议先看看使用帮助哦～',
  )
  ```

## _var_ `SESSION_CANCEL_EXPRESSION` <Badge text="1.3.0+"/>

- **类型:** str | Sequence[str] | (*Any, **Any) -> str

- **说明**

  `nonebot.command.argfilter.controllers.handle_cancellation()` 控制器在用户发送了 `算了`、`取消` 等取消指令后，结束当前命令会话时，向用户发送的提示。

  **默认值:** `'好的'`

- **用法**

  ```python
  SESSION_CANCEL_EXPRESSION = (
      '好的',
      '好的吧',
      '好吧，那奶茶就不打扰啦',
      '那奶茶先不打扰小主人啦',
  )
  ```

## _var_ `APSCHEDULER_CONFIG`

- **类型:** dict[str, Any]

- **说明**

  APScheduler 的配置对象，见 [Configuring the scheduler](https://apscheduler.readthedocs.io/en/latest/userguide.html#configuring-the-scheduler)。

  **默认值:** `{'apscheduler.timezone': 'Asia/Shanghai'}`