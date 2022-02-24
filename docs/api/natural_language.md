# nonebot.natural_language

## _class_ `NLPSession(bot, event, msg)`

- **说明**

  继承自 `BaseSession` 类，表示自然语言处理 Session。

- **参数**

  - `bot` ([NoneBot](./index.md#class-nonebot-config-object-none))

  - `event` (aiocqhttp.event.Event)

  - `msg` (str)

### _instance-var_ `msg`

- **类型:** str

- **说明:** 以字符串形式表示的消息内容，已去除开头的 @ 和机器人称呼，可能存在 CQ 码。

### _instance-var_ `msg_images`

- **类型:** list[str]

- **说明:** 消息内容中所有图片的 URL 的列表，如果消息中没有图片，则为 `[]`。

### _instance-var_ `msg_text`

- **类型:** str

- **说明:** 消息内容的纯文本部分，已去除所有 CQ 码/非 `text` 类型的消息段。各纯文本消息段之间使用空格连接。

## _class_ `IntentCommand(confidence, name, args=None, current_arg='')` <Badge text="1.2.0+"/>

- **说明**

  用于表示自然语言处理之后得到的意图命令，是一个 `NamedTuple`，由自然语言处理器返回。

- **参数**

  - `confidence` (float)

  - `name` (str | [CommandName_T](./typing.md#var-commandname-t))

  - `args` ([CommandArgs_T](./typing.md#var-commandargs-t))

  - `current_arg` (str)

### _instance-var_ `args`

- **类型:** [CommandArgs_T](./typing.md#var-commandargs-t)

- **说明:** 命令的（初始）参数。

### _instance-var_ `confidence`

- **类型:** float

- **说明:** 意图的置信度，即表示对当前推测的用户意图有多大把握。

### _instance-var_ `current_arg`

- **类型:** str

- **说明:** 命令的当前输入参数。

### _instance-var_ `name`

- **类型:** str | [CommandName_T](./typing.md#var-commandname-t)

- **说明:** 命令的名字。