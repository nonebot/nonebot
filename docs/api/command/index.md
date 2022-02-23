# nonebot.command

快捷导入:

- `CommandGroup` -> [CommandGroup](./group.md#class-commandgroup-name-permission-only-to-me-privileged-shell-like-expire-timeout-run-timeout-session-class)

## _class_ `CommandManager()` <Badge text="1.6.0+"/>

- **说明**

  全局命令管理器。

### _instance-var_ `commands`

- **类型:** Dict[CommandName_T, Command]

- **说明:** 命令字典。

### _instance-var_ `aliases`

- **类型:** Dict[str, Command]

- **说明:** 命令别名字典。

### _instance-var_ `switches`

- **类型:** Dict[Command, bool]

- **说明:** 命令开关状态字典。

### _instance-var_ `patterns` <Badge text="1.7.0+"/>

- **类型:** Dict[Pattern[str], Command]

- **说明:** 命令正则匹配字典。

### _classmethod_ `add_aliases(cls, aliases, cmd)`

- **说明**

  为 `Command` 添加命令别名。

- **参数**

  - `aliases` (Iterable[str] | str): 命令别名列表

  - `cmd` (nonebot.command.Command)

- **返回**

  - None

- **用法**

  ```python
  cmd = Command(name, func, permission, only_to_me, privileged)
  CommandManager.add_aliases({"别名", "test"}, cmd)
  ```

### _classmethod_ `add_command(cls, cmd_name, cmd)`

- **说明**

  注册一个 `Command` 对象。

- **参数**

  - `cmd_name` (tuple[str, ...]): 命令名称

  - `cmd` (nonebot.command.Command): 命令对象

- **返回**

  - None

- **用法**

  ```python
  cmd = Command(name, func, permission, only_to_me, privileged)
  CommandManager.add_command(name, cmd)
  ```

### _classmethod_ `reload_command(cls, cmd_name, cmd)`

- **说明**

  更新一个已存在的命令。

- **参数**

  - `cmd_name` (tuple[str, ...]): 命令名词

  - `cmd` (nonebot.command.Command): 命令对象

- **返回**

  - None

- **用法**

  ```python
  cmd = Command(name, func, permission, only_to_me, privileged)
  CommandManager.reload_command(name, cmd)
  ```

### _classmethod_ `remove_command(cls, cmd_name)`

- **说明**

  移除一个已存在的命令。

- **参数**

  - `cmd_name` (tuple[str, ...]): 命令名称

- **返回**

  - bool: 是否成功移除命令

- **用法**

  ```python
  CommandManager.remove_command(("test", ))
  ```

### _method_ `switch_command(self, cmd_name, state=None)`

- **说明**

  根据 `state` 更改 command 的状态。仅对当前消息有效。

- **参数**

  - `cmd_name` (tuple[str, ...]): 命令名称

  - `state` (bool | None)

    - `None(default)`: 切换状态，即 开 -> 关、关 -> 开
    - `bool`: 切换至指定状态，`True` -> 开、`False` -> 关

- **返回**

  - None

- **用法**

  ```python
  from nonebot import message_preprocessor

  # 关闭命令test, 仅对当前消息生效
  @message_preprocessor
  async def processor(bot: NoneBot, event: CQEvent, plugin_manager: PluginManager):
      plugin_manager.cmd_manager.switch_command(("test", ), state=False)
  ```

### _classmethod_ `switch_command_global(cls, cmd_name, state=None)`

- **说明**

  根据 `state` 更改 command 的全局状态。

- **参数**

  - `cmd_name` (tuple[str, ...]): 命令名称

  - `state` (bool | None)

    - `None(default)`: 切换状态，即 开 -> 关、关 -> 开
    - `bool`: 切换至指定状态，`True` -> 开、`False` -> 关

- **返回**

  - None

- **用法**

  ```python
  from nonebot import message_preprocessor

  # 全局关闭命令test, 对所有消息生效
  CommandManager.switch_command_global(("test", ), state=False)

  @message_preprocessor
  async def processor(bot: NoneBot, event: CQEvent, plugin_manager: PluginManager):
      plugin_manager.cmd_manager.switch_command_global(("test", ), state=False)
  ```

## _class_ `CommandSession(bot, event, cmd, *, current_arg='', args=None)`

- **说明**

  继承自 `BaseSession` 类，表示命令 Session。

- **参数**

  - `bot` ([NoneBot](../index.md#class-nonebot-config-object-none))

  - `event` (aiocqhttp.event.Event)

  - `cmd` (nonebot.command.Command)

  - `current_arg` (str | None)

  - `args` (dict[str, Any] | None)

### _property_ `argv`

- **类型:** list[str]

- **说明:** 命令参数列表，类似于 `sys.argv`，本质上是 `session.state.get('argv', [])`，**需要搭配 `on_command(..., shell_like=True)` 使用**。

- **用法**

  ```python
  @on_command('some_cmd', shell_like=True)
  async def _(session: CommandSession):
      argv = session.argv
  ```

### _instance-var_ `current_arg`

- **类型:** Optional[str]

- **说明:** 命令会话当前参数。实际上是 酷 Q 收到的消息去掉命令名的剩下部分，因此可能存在 CQ 码。

### _property_ `current_arg_images`

- **类型:** list[str]

- **说明:** `current_arg` 属性中所有图片的 URL 的列表，如果参数中没有图片，则为 `[]`。

### _property_ `current_arg_text`

- **类型:** str

- **说明:** `current_arg` 属性的纯文本部分（不包含 CQ 码），各部分使用空格连接。

### _instance-var_ `current_key`

- **类型:** Optional[str]

- **说明:** 命令会话当前正在询问用户的参数的键（或称参数的名字）。第一次运行会话时，该属性为 `None`。

### _property_ `is_first_run`

- **类型:** bool

- **说明:** 命令会话是否第一次运行。

### _property_ `state` <Badge text="1.2.0+"/>

- **类型:** dict[str, Any]

- **说明**

  命令会话的状态数据（包括已获得的所有参数）。

  属性本身只读，但属性中的内容可读写。

- **用法**

  ```python
  if not session.state.get('initialized'):
      # ... 初始化工作
      session.state['initialized'] = True
  ```

  在命令处理函数的开头进行**每次命令调用只应该执行一次的初始化操作**。

### _async method_ `aget(self, key=..., *, prompt=None, arg_filters=None, force_update=..., **kwargs)` <Badge text="1.8.0+"/>

- **说明**

  从 `state` 属性获取参数，如果参数不存在，则异步地暂停当前会话，向用户发送提示，并等待用户的进一步交互。

  当用户再次输入时，不会重新运行命令处理器，而是回到此函数调用之处继续执行。

  注意，一旦传入 `arg_filters` 参数（参数过滤器），则等用户再次输入时，_command_func._`args_parser` 所注册的参数解析函数将不会被运行，而会在对 `current_arg` 依次运行过滤器之后直接将其放入 `state` 属性中。

- **参数**

  - `key` (str): 参数的键，若不传入则使用默认键值

  - `prompt` (str | dict[str, Any] | list[dict[str, Any]] | NoneType): 提示的消息内容

  - `arg_filters` (list[(Any) -> Any | Awaitable[Any]] | None): 用于处理和验证用户输入的参数的过滤器

  - `force_update` (bool): 是否强制获取用户新的输入，若是，则会忽略已有的当前参数，若 `key` 不传入则为真，否则默认为假

  - `**kwargs`: 其它传入 `BaseSession.send()` 的命名参数

- **返回**

  - Any: 参数的值

- **用法**

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

### _async method_ `apause(self, message=None, **kwargs)` <Badge text="1.8.0+"/>

- **说明**

  异步地暂停当前命令会话，并发送消息。

  当用户再次输入时，不会重新运行命令处理器，而是回到此函数调用之处继续执行。

- **参数**

  - `message` (str | dict[str, Any] | list[dict[str, Any]] | NoneType): 要发送的消息，若不传入则不发送

  - `**kwargs`: 其它传入 `BaseSession.send()` 的命名参数

- **返回**

  - None

- **用法**

  ```python
  await session.apause('请发送要处理的图片，发送 done 结束')
  while True:
      if session.current_arg_text.strip() == 'done':
          session.finish('处理完成')
      process_images(session.current_arg_images)
      await session.apause('请继续发送要处理的图片，发送 done 结束')
  ```

  需要连续接收用户输入，并且过程中不需要改变 `current_key` 时，使用此函数暂停会话。

### _method_ `finish(self, message=None, **kwargs)`

- **说明**

  结束当前命令会话，并发送消息。此函数调用之后的语句将不会被执行（除非捕获了此函数抛出的特殊异常）。

  调用此函数后，命令将被视为已经完成，当前命令会话将被移除。

- **参数**

  - `message` (str | dict[str, Any] | list[dict[str, Any]] | NoneType): 要发送的消息，若不传入则不发送

  - `**kwargs`: 其它传入 `BaseSession.send()` 的命名参数

- **返回**

  - NoReturn

- **用法**

  ```python
  session.finish('感谢您的使用～')
  ```

### _method_ `get(self, key, *, prompt=None, arg_filters=None, **kwargs)`

- **说明**

  从 `state` 属性获取参数，如果参数不存在，则暂停当前会话，向用户发送提示，并等待用户的新一轮交互。

  如果需要暂停当前会话，则命令处理器中，此函数调用之后的语句将不会被执行（除非捕获了此函数抛出的特殊异常）。

  注意，一旦传入 `arg_filters` 参数（参数过滤器），则等用户再次输入时，_command_func._`args_parser` 所注册的参数解析函数将不会被运行，而会在对 `current_arg` 依次运行过滤器之后直接将其放入 `state` 属性中。

  :::tip
  推荐使用下面的 `aget` 方法。
  :::

- **参数**

  - `key` (str): 参数的键

  - `prompt` (str | dict[str, Any] | list[dict[str, Any]] | NoneType): 提示的消息内容

  - `arg_filters` (list[(Any) -> Any | Awaitable[Any]] | None) <Badge text="1.2.0+"/>: 用于处理和验证用户输入的参数的过滤器

  - `**kwargs`: 其它传入 `BaseSession.send()` 的命名参数

- **返回**

  - Any: 参数的值

- **用法**

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

### _method_ `pause(self, message=None, **kwargs)`

- **说明**

  暂停当前命令会话，并发送消息。此函数调用之后的语句将不会被执行（除非捕获了此函数抛出的特殊异常）。

  :::tip
  推荐使用下面的 `apause` 方法。
  :::

- **参数**

  - `message` (str | dict[str, Any] | list[dict[str, Any]] | NoneType): 要发送的消息，若不传入则不发送

  - `**kwargs`: 其它传入 `BaseSession.send()` 的命名参数

- **返回**

  - NoReturn

- **用法**

  ```python
  if session.is_first_run:
      session.pause('请发送要处理的图片，发送 done 结束')
  if session.current_arg_text.strip() == 'done':
      session.finish('处理完成')
  process_images(session.current_arg_images)
  session.pause('请继续发送要处理的图片，发送 done 结束')
  ```

  需要连续接收用户输入，并且过程中不需要改变 `current_key` 时，使用此函数暂停会话。

### _method_ `switch(self, new_message)`

- **说明**

  结束当前会话，改变当前消息事件中的消息内容，然后重新处理消息事件。

  此函数可用于从一个命令中跳出，将用户输入的剩余部分作为新的消息来处理，例如可实现以下对话:

  ```
  用户: 帮我查下天气
  Bot: 你要查询哪里的天气呢？
  用户: 算了，帮我查下今天下午南京到上海的火车票吧
  Bot: 今天下午南京到上海的火车票有如下班次: blahblahblah
  ```

  这里进行到第三行时，命令期待的是一个地点，但实际发现消息的开头是「算了」，于是调用 `switch('帮我查下今天下午南京到上海的火车票吧')`，结束天气命令，将剩下来的内容作为新的消息来处理（触发火车票插件的自然语言处理器，进而调用火车票查询命令）。

- **参数**

  - `new_message` (str | dict[str, Any] | list[dict[str, Any]]): 要覆盖消息事件的新消息内容

- **返回**

  - NoReturn

- **用法**

  ```python
  @my_cmd.args_parser
  async def _(session: CommandSession)
      if not session.is_first_run and session.current_arg.startswith('算了，'):
          session.switch(session.current_arg[len('算了，'):])
  ```

  使用「算了」来取消当前命令，转而进入新的消息处理流程。这个例子比较简单，实际应用中可以使用更复杂的 NLP 技术来判断。

## _async def_ `call_command(bot, event, name, *, current_arg='', args=None, check_perm=True, disable_interaction=False)`

- **说明**

  从内部直接调用命令。可用于在一个插件中直接调用另一个插件的命令。

- **参数**

  - `bot` ([NoneBot](../index.md#class-nonebot-config-object-none)): NoneBot 对象

  - `event` (aiocqhttp.event.Event): 事件对象

  - `name` (str | tuple[str, ...]): 要调用的命令名

  - `current_arg` (str): 命令会话的当前输入参数

  - `args` (dict[str, Any] | None): 命令会话的（初始）参数（将会被并入命令会话的 `state` 属性）

  - `check_perm` (bool): 是否检查命令的权限，若否，则即使当前事件上下文并没有权限调用这里指定的命令，也仍然会调用成功

  - `disable_interaction` (bool): 是否禁用交互功能，若是，则该命令的会话不会覆盖任何当前已存在的命令会话，新创建的会话也不会保留

- **返回**

  - bool: 命令是否调用成功

- **用法**

  ```python
  await call_command(bot, event, 'say', current_arg='[CQ:face,id=14]', check_perm=False)
  ```

  从内部调用 `say` 命令，且不检查权限。

## _def_ `kill_current_session(event)`

- **说明**

  强行移除当前已存在的任何命令会话，即使它正在运行。该函数可用于强制移除执行时间超过预期的命令，以保证新的消息不会被拒绝服务。

- **参数**

  - `event` (aiocqhttp.event.Event): 事件对象

- **返回**

  - None

- **用法**

  ```python
  @on_command('kill', privileged=True)
  async def _(session: CommandSession):
      kill_current_session(session.event)
  ```

  在特权命令 `kill` 中强行移除当前正在运行的会话。