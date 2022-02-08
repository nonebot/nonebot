# nonebot.plugin <Badge text="1.1.0+"/>

## _class_ `Plugin(module, name=None, usage=None, userdata=None, commands=..., nl_processors=..., event_handlers=..., msg_preprocessors=..., lifetime_hooks=...)`

- **说明**

  用于包装已加载的插件模块的类。

- **参数**

  - `module` (module)

  - `name` (str | None)

  - `usage` (Any | None)

  - `userdata` (Any | None)

  - `commands` (set[nonebot.command.Command])

  - `nl_processors` (set[nonebot.natural_language.NLProcessor])

  - `event_handlers` (set[nonebot.notice_request.EventHandler])

  - `msg_preprocessors` (set[MessagePreprocessor])

  - `lifetime_hooks` (list[nonebot.plugin.LifetimeHook])

### _instance-var_ `commands` <Badge text="1.6.0+"/>

- **类型:** 

- **说明:** 插件包含的命令，通过 `on_command` 装饰器注册。

### _instance-var_ `event_handlers` <Badge text="1.6.0+"/>

- **类型:** 

- **说明:** 插件包含的事件处理器（包含通知、请求），通过 `on_notice` 以及 `on_request` 装饰器注册。

### _instance-var_ `lifetime_hooks` <Badge text="1.9.0+"/>

- **类型:** 

- **说明:** 插件包含的生命周期事件回调，通过 `on_plugin` 装饰器注册。

### _instance-var_ `module`

- **类型:** 

- **说明:** 已加载的插件模块（importlib 导入的 Python 模块）。

### _instance-var_ `msg_preprocessors` <Badge text="1.9.0+"/>

- **类型:** 

- **说明:** 插件包含的消息预处理器，通过 `message_preprocessor` 装饰器注册。

### _instance-var_ `name`

- **类型:** 

- **说明:** 插件名称，从插件模块的 `__plugin_name__` 特殊变量获得，如果没有此变量，则为 `None`。

### _instance-var_ `nl_processors` <Badge text="1.6.0+"/>

- **类型:** 

- **说明:** 插件包含的自然语言处理器，通过 `on_natural_language` 装饰器注册。

### _instance-var_ `usage`

- **类型:** 

- **说明:** 插件使用方法，从插件模块的 `__plugin_usage__` 特殊变量获得，如果没有此变量，则为 `None`。

### _instance-var_ `userdata` <Badge text="1.9.0+"/>

- **类型:** 

- **说明:** 插件作者可由此变量向外部暴露其他信息，从插件模块的 `__plugin_userdata__` 特殊变量获得，如果没有此变量，则为 `None`。

### _method_ `__await__(self)` <Badge text="1.9.0+"/>

- **说明**

  当使用 `load_plugin`, `unload_plugin`, `reload_plugin` 时，其返回的 `Plugin` 对象可以（非必需）被 await 来等待其异步加载、卸载完成。详情请见这些函数的文档。

- **返回**

  - Generator[NoneType, NoneType, Plugin | None]

## _class_ `PluginManager()` <Badge text="1.6.0+"/>

- **说明**

  插件管理器: 用于管理插件的加载以及插件中命令、自然语言处理器、事件处理器的开关。

### _instance-var_ `cmd_manager`

- **类型:** 

- **说明:** 命令管理器实例。

### _instance-var_ `nlp_manager`

- **类型:** 

- **说明:** 自然语言管理器实例。

### _classmethod_ `add_plugin(cls, module_path, plugin)`

- **说明**

  注册一个 `Plugin` 对象。

- **参数**

  - `module_path` (str): 模块路径

  - `plugin` ([Plugin](#class-plugin-module-name-none-usage-none-userdata-none-commands-nl-processors-event-handlers-msg-preprocessors-lifetime-hooks)): Plugin 对象

- **返回**

  - None

- **用法**

  ```python
  plugin = Plugin(module, name, usage, commands, nl_processors, event_handlers)
  PluginManager.add_plugin("path.to.plugin", plugin)
  ```

### _classmethod_ `get_plugin(cls, module_path)`

- **说明**

  获取一个已经注册的 `Plugin` 对象。

- **参数**

  - `module_path` (str): 模块路径

- **返回**

  - Plugin | None: Plugin 对象

- **用法**

  ```python
  plugin = PluginManager.get_plugin("path.to.plugin")
  ```

### _classmethod_ `remove_plugin(cls, module_path)`

- **说明**

  删除 Plugin 中的所有命令、自然语言处理器、事件处理器并从插件管理器移除 Plugin 对象。在 1.9.0 后，也会移除消息预处理器。

  :::danger
  这个方法实际并没有完全移除定义 Plugin 的模块。仅是移除其所注册的处理器。
  :::

- **参数**

  - `module_path` (str): 模块路径

- **返回**

  - bool: 是否移除了插件

### _method_ `switch_command(self, module_path, state=None)`

- **说明**

  根据 `state` 修改 plugin 中 commands 的状态。仅对当前消息有效。

- **参数**

  - `module_path` (str): 模块路径

  - `state` (bool | None)

    - `None(default)`: 切换状态，即 开 -> 关、关 -> 开
    - `bool`: 切换至指定状态，`True` -> 开、`False` -> 关

- **返回**

  - None

- **用法**

  ```python
  from nonebot import message_preprocessor

  # 关闭插件 path.to.plugin 中所有命令, 仅对当前消息生效
  @message_preprocessor
  async def processor(bot: NoneBot, event: CQEvent, plugin_manager: PluginManager):
      plugin_manager.switch_command("path.to.plugin", state=False)
  ```

### _classmethod_ `switch_command_global(cls, module_path, state=None)`

- **说明**

  根据 `state` 更改 plugin 中 commands 的全局状态。

- **参数**

  - `module_path` (str): 模块路径

  - `state` (bool | None)

    - `None(default)`: 切换状态，即 开 -> 关、关 -> 开
    - `bool`: 切换至指定状态，`True` -> 开、`False` -> 关

- **返回**

  - None

- **用法**

  ```python
  # 全局关闭插件 path.to.plugin 中所有命令, 对所有消息生效
  PluginManager.switch_command_global("path.to.plugin", state=False)
  ```

### _classmethod_ `switch_eventhandler_global(cls, module_path, state=None)`

- **说明**

  根据 `state` 更改 plugin 中 event handlers 的全局状态。

- **参数**

  - `module_path` (str): 模块路径

  - `state` (bool | None)

    - `None(default)`: 切换状态，即 开 -> 关、关 -> 开
    - `bool`: 切换至指定状态，`True` -> 开、`False` -> 关

- **返回**

  - None

- **用法**

  ```python
  # 全局关闭插件 path.to.plugin 中所有事件处理器, 对所有消息生效
  PluginManager.switch_eventhandler_global("path.to.plugin", state=False)
  ```

### _classmethod_ `switch_messagepreprocessor_global(cls, module_path, state=None)` <Badge text="1.9.0+"/>

- **说明**

  根据 `state` 更改 plugin 中 message preprocessors 的全局状态。

- **参数**

  - `module_path` (str): 模块路径

  - `state` (bool | None)

    - `None(default)`: 切换状态，即 开 -> 关、关 -> 开
    - `bool`: 切换至指定状态，`True` -> 开、`False` -> 关

- **返回**

  - None

- **用法**

  ```python
  # 全局关闭插件 path.to.plugin 中所有消息预处理器, 对所有消息生效
  PluginManager.switch_messagepreprocessor_global("path.to.plugin", state=False)
  ```

### _method_ `switch_nlprocessor(self, module_path, state=None)`

- **说明**

  根据 `state` 修改 plugin 中 nl_processors 的状态。仅对当前消息有效。

- **参数**

  - `module_path` (str): 模块路径

  - `state` (bool | None)

    - `None(default)`: 切换状态，即 开 -> 关、关 -> 开
    - `bool`: 切换至指定状态，`True` -> 开、`False` -> 关

- **返回**

  - None

- **用法**

  ```python
  from nonebot import message_preprocessor

  # 关闭插件 path.to.plugin 中所有自然语言处理器, 仅对当前消息生效
  @message_preprocessor
  async def processor(bot: NoneBot, event: CQEvent, plugin_manager: PluginManager):
      plugin_manager.switch_nlprocessor("path.to.plugin", state=False)
  ```

### _classmethod_ `switch_nlprocessor_global(cls, module_path, state=None)`

- **说明**

  根据 `state` 更改 plugin 中 nl_processors 的全局状态。

- **参数**

  - `module_path` (str): 模块路径

  - `state` (bool | None)

    - `None(default)`: 切换状态，即 开 -> 关、关 -> 开
    - `bool`: 切换至指定状态，`True` -> 开、`False` -> 关

- **返回**

  - None

- **用法**

  ```python
  from nonebot import message_preprocessor

  # 全局关闭插件 path.to.plugin 中所有自然语言处理器, 对所有消息生效
  PluginManager.switch_nlprocessor_global("path.to.plugin", state=False)

  @message_preprocessor
  async def processor(bot: NoneBot, event: CQEvent, plugin_manager: PluginManager):
      plugin_manager.switch_nlprocessor_global("path.to.plugin", state=False)
  ```

### _method_ `switch_plugin(self, module_path, state=None)`

- **说明**

  根据 `state` 修改 plugin 中的 commands 和 nlprocessors 状态。仅对当前消息有效。

- **参数**

  - `module_path` (str): 模块路径

  - `state` (bool | None)

    - `None(default)`: 切换状态，即 开 -> 关、关 -> 开
    - `bool`: 切换至指定状态，`True` -> 开、`False` -> 关

- **返回**

  - None

- **用法**

  ```python
  from nonebot import message_preprocessor

  # 关闭插件 path.to.plugin , 仅对当前消息生效
  @message_preprocessor
  async def processor(bot: NoneBot, event: CQEvent, plugin_manager: PluginManager):
      plugin_manager.switch_plugin("path.to.plugin", state=False)
  ```

### _classmethod_ `switch_plugin_global(cls, module_path, state=None)`

- **说明**

  根据 `state` 更改 plugin 中 commands, nl_processors, event_handlers 的全局状态。在 1.9.0 后，msg_preprocessors 的状态也会被更改。

  :::warning
  更改插件状态并不会影响插件内 scheduler 等其他全局副作用状态
  :::

- **参数**

  - `module_path` (str): 模块路径

  - `state` (bool | None)

    - `None(default)`: 切换状态，即 开 -> 关、关 -> 开
    - `bool`: 切换至指定状态，`True` -> 开、`False` -> 关

- **返回**

  - None

- **用法**

  ```python
  # 全局关闭插件 path.to.plugin , 对所有消息生效
  PluginManager.switch_plugin_global("path.to.plugin", state=False)
  ```

## _def_ `load_plugin(module_path, no_fast=False)`

- **说明**

  加载插件（等价于导入模块）。

  此函数会调用插件中由 `on_plugin('loading')` 装饰器注册的函数（下称 「加载回调」），之后再添加插件中注册的处理器（如命令等）。

- **参数**

  - `module_path` (str): 模块路径

  - `no_fast` (bool) <Badge text="1.9.1+"/>: 若此参数为 `True`，则无视 `unload_plugin` 中的 `fast` 选项而强制重新导入模块

- **返回** <Badge text="1.6.0+"/>

  - Plugin | None: 加载后生成的 `Plugin` 对象。根据插件组成不同，返回值包含如下情况:

    - 插件没有定义加载回调，或只定义了同步的加载回调（此为 1.9.0 前的唯一情况）: 此函数会执行回调，在加载完毕后返回新的插件对象，其可以被 await，行为为直接返回插件本身（也就是可以不 await）。如果发生异常，则返回 `None`
    - 插件定义了异步加载回调，但 `load_plugin` 是在 NoneBot 启动前调用的: 此函数会阻塞地运行异步函数，其余表现和上一致
    - 插件定义了异步加载回调，但 `load_plugin` 是在异步的情况下调用的（比如在 NoneBot 运行的事件循环中）: 此函数会先执行部分同步的加载回调
        - 如果成功，返回一个插件对象。返回值可以被 await，行为为等待剩余的异步加载完毕然后返回插件本身，或如果在 await 中发生了错误，返回 `None`
        - 如果失败，返回 `None`

- **用法**

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

## _def_ `unload_plugin(module_path, fast=False)` <Badge text="1.9.0+"/>

- **说明**

  卸载插件，即移除插件的 commands, nlprocessors, event handlers 和 message preprocessors，运行由 `on_plugin('unloaded')` 注册的函数（下称 「卸载回调」），并将已导入的模块移除。

  :::danger
  该函数为强制卸载，如果使用不当，可能导致不可预测的错误！（如引用已经被移除的模块变量）

  此函数不会回滚已导入模块中产生过的其他副作用（比如已计划的任务，aiocqhttp 中注册的处理器等）。
  :::

- **参数**

  - `module_path` (str): 模块路径

  - `fast` (bool) <Badge text="1.9.1+"/>: 若此参数为 `True`，则卸载时将不会移除已导入的模块。当未来的 `load_plugin` 调用将加载相同的插件时，将不会重新导入相应模块而是复用。

- **返回**

  - Plugin | None: 执行卸载后遗留的 `Plugin` 对象，或 `None` 如果插件不存在。根据插件组成不同，`Plugin` 返回值包含如下情况:

    - 插件没有定义卸载回调，或只定义了同步的卸载回调：此函数会卸载处理器并执行回调，在卸载完毕后返回遗留的插件对象，其可以被 await，行为为直接返回此插件本身（也就是可以不 await）。
    - 插件定义了异步卸载回调，但 `unload_plugin` 是在 NoneBot 启动前调用的：此函数会阻塞地运行异步函数，其余表现和上一致
    - 插件定义了异步卸载回调，但 `unload_plugin` 是在异步的情况下调用的（比如在 NoneBot 运行的事件循环中）：此函数会卸载处理器并执行部分同步的卸载回调，返回遗留的插件对象。此对象可以被 await，行为为等待剩余的异步卸载回调执行完毕然后返回此插件本身。
    - 在此之后此返回值将不再有用

- **用法**

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

## _def_ `reload_plugin(module_path, fast=False)` <Badge text="1.6.0+"/>

- **说明**

  重载插件，也就是先 `unload_plugin`，再 `load_plugin`，期间等待相应回调执行完毕。

  :::danger
  该函数为强制重载，如果使用不当，可能导致不可预测的错误！
  :::

- **参数**

  - `module_path` (str): 模块路径

  - `fast` (bool) <Badge text="1.9.1+"/>: 若此参数为 `True`，则卸载时将不会移除已导入的模块，加载时将不会重新导入相应模块而是复用。

    :::tip
    在 1.9.1 后，建议使用 `fast=True`。此参数的默认值 `False` 是由于历史原因。
    :::

- **返回**

  - Plugin | None: 重载后生成的 Plugin 对象。根据插件组成不同，返回值包含如下情况:

    - 插件没有定义或只定义了同步的加载/卸载回调（此为 1.9.0 前的唯一情况）: 此函数会执行两个步骤的回调，在重载完毕后返回新的插件对象，其可以被 await，行为为直接返回插件本身（也就是可以不 await）。如果发生异常，则返回 `None`
    - 插件定义了异步的回调，但 `reload_plugin` 是在 NoneBot 启动前调用的: 此函数会阻塞地运行异步函数，其余表现和上一致
    - 插件定义了异步的回调，但 `reload_plugin` 是在异步的情况下调用的（比如在 NoneBot 运行的事件循环中）: 此函数会卸载处理器并执行部分同步的卸载回调，返回遗留的插件对象。返回值可以被 await，行为为等待剩余的异步卸载完毕并且加载新插件完毕后然后返回新的插件对象，或如果在 await 中发生了错误，返回 `None`

- **用法**

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

## _def_ `load_plugins(plugin_dir, module_prefix, no_fast=False)`

- **说明**

  查找指定路径（相对或绝对）中的非隐藏模块（隐藏模块名字以 `_` 开头）并通过指定的模块前缀导入。其返回值的表现与 `load_plugin` 一致。

- **参数**

  - `plugin_dir` (str): 插件目录

  - `module_prefix` (str): 模块前缀

  - `no_fast` (bool) <Badge text="1.9.1+"/>: 若此参数为 `True`，则无视 `unload_plugin` 中的 `fast` 选项而强制重新导入模块

- **返回** <Badge text="1.6.0+"/>

  - set[Plugin]: 加载成功的 Plugin 对象

- **用法**

  ```python
  nonebot.plugin.load_plugins(path.join(path.dirname(__file__), 'plugins'), 'plugins')
  ```

  加载 `plugins` 目录下的插件。

## _def_ `load_builtin_plugins()`

- **说明**

  加载内置插件。

- **返回** <Badge text="1.6.0+"/>

  - set[Plugin]: 加载成功的 Plugin 对象

- **用法**

  ```python
  nonebot.plugin.load_builtin_plugins()
  ```

## _def_ `get_loaded_plugins()`

- **说明**

  获取已经加载的插件集合。

- **返回**

  - set[Plugin]: 已加载的插件集合

- **用法**

  ```python
  plugins = nonebot.plugin.get_loaded_plugins()
  await session.send('我现在支持以下功能：\n\n' +
                      '\n'.join(map(lambda p: p.name, filter(lambda p: p.name, plugins))))
  ```

## _def_ `on_plugin(timing)` <Badge text="1.9.0+"/>

- **说明**

  将函数设置为插件生命周期的回调函数。注册的加载回调会在调用 `load_plugin` 时被调用，注册的卸载回调会在调用 `unload_plugin` 时被调用。

- **要求**

  被装饰函数可为同步或异步（async def）函数，必须不接受参数，其返回值会被忽略:

  ```python
  def func():
      pass

  async def func():
      pass
  ```

  被 `on_plugin('unloaded')` 装饰的函数必须不能抛出 `Exception`，否则卸载时的行为将不能保证。

- **参数**

  - `timing` (str): `"loading"` 表示注册加载回调，`"unloaded"` 表示注册卸载回调

- **返回**

  - (() -> Any | () -> Awaitable[Any]) -> () -> Any | () -> Awaitable[Any]

- **用法**

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

## _def_ `on_command(name, *, aliases=(), patterns=(), permission=..., only_to_me=True, privileged=False, shell_like=False, expire_timeout=..., run_timeout=..., session_class=None)` <Badge text="1.6.0+"/>

- **说明**

  将函数装饰为命令处理器 `CommandHandler_T` 。

  被装饰的函数将会获得一个 `args_parser` 属性，是一个装饰器，下面会有详细说明。

- **要求**

  被装饰函数必须是一个 async 函数，且必须接收且仅接收一个位置参数，类型为 `CommandSession`，即形如:

  ```python
  async def func(session: CommandSession):
      pass
  ```

- **参数**

  - `name` (str | tuple[str, ...]): 命令名，如果传入的是字符串则会自动转为元组

  - `aliases` (Iterable[str] | str): 命令别名

  - `patterns` (Iterable[str] | str | Iterable[Pattern[str]] | Pattern[str]) <Badge text="1.7.0+"/>: 正则匹配，可以传入正则表达式或正则表达式组，来对整条命令进行匹配

    :::warning 注意
    滥用正则表达式可能会引发性能问题，请优先使用普通命令。另外一点需要注意的是，由正则表达式匹配到的匹配到的命令，`session` 中的 `current_arg` 会是整个命令，而不会删除匹配到的内容，以满足一些特殊需求。
    :::

  - `permission` ((SenderRoles) -> bool | (SenderRoles) -> Awaitable[bool] | Iterable[(SenderRoles) -> bool | (SenderRoles) -> Awaitable[bool]]) <Badge text="1.9.0+"/>: 命令所需要的权限，不满足权限的用户将无法触发该命令。若提供了多个，则默认使用 `aggregate_policy` 和其默认参数组合。如果不传入该参数（即为默认的 `...`），则使用配置项中的 `DEFAULT_COMMAND_PERMISSION`

  - `only_to_me` (bool): 是否只响应确定是在和「我」（机器人）说话的命令（在开头或结尾 @ 了机器人，或在开头称呼了机器人昵称）

  - `privileged` (bool): 是否特权命令，若是，则无论当前是否有命令会话正在运行，都会运行该命令，但运行不会覆盖已有会话，也不会保留新创建的会话

  - `shell_like` (bool): 是否使用类 shell 语法，若是，则会自动使用 `shlex` 模块进行分割（无需手动编写参数解析器），分割后的参数列表放入 `session.args['argv']`

  - `expire_timeout` (datetime.timedelta | None) <Badge text="1.8.2+"/>: 命令过期时间。如果不传入该参数（即为默认的 `...`），则使用配置项中的 `SESSION_EXPIRE_TIMEOUT`，如果提供则使用提供的值。

  - `run_timeout` (datetime.timedelta | None) <Badge text="1.8.2+"/>: 命令会话的运行超时时长。如果不传入该参数（即为默认的 `...`），则使用配置项中的 `SESSION_RUN_TIMEOUT`，如果提供则使用提供的值。

  - `session_class` (Type[[CommandSession](./command/index.md#class-commandsession-bot-event-cmd-current-arg-args-none)] | None) <Badge text="1.7.0+"/>: 自定义 `CommandSession` 子类，若传入此参数，则命令处理函数的参数 `session` 类型为 `session_class`

- **返回**

  - ((CommandSession) -> Awaitable[Any]) -> (CommandSession) -> Awaitable[Any]

- **用法**

  ```python
  @on_command('echo', aliases=('复读',), permission=lambda sender: sender.is_superuser)
  async def _(session: CommandSession):
      await session.send(session.current_arg)
  ```

  一个仅对超级用户生效的复读命令。

- **属性**

  - `args_parser`

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

## _def_ `on_natural_language(keywords=None, *, permission=..., only_to_me=True, only_short_message=True, allow_empty_message=False)` <Badge text="1.6.0+"/>

- **说明**

  将函数装饰为自然语言处理器。

- **要求**

  被装饰函数必须是一个 async 函数，且必须接收且仅接收一个位置参数，类型为 `NLPSession`，即形如:

  ```python
  async def func(session: NLPSession):
      pass
  ```

- **重载**

  **1.** `(__func)`

  - **参数**

    - `__func` ((NLPSession) -> Awaitable[IntentCommand | None]): 待装饰函数

  - **返回**

    - NLPHandler_T: 被装饰函数

  **2.** `(keywords=..., *, permission=..., only_to_me=..., only_short_message=..., allow_empty_message=...)`

  - **参数**

    - `keywords` (Iterable[str] | str | NoneType): 要响应的关键词，若传入 `None`，则响应所有消息

    - `permission` ((SenderRoles) -> bool | (SenderRoles) -> Awaitable[bool] | Iterable[(SenderRoles) -> bool | (SenderRoles) -> Awaitable[bool]]) <Badge text="1.9.0+"/>: 自然语言处理器所需要的权限，不满足权限的用户将无法触发该处理器。若提供了多个，则默认使用 `aggregate_policy` 和其默认参数组合。如果不传入该参数（即为默认的 `...`），则使用配置项中的 `DEFAULT_NLP_PERMISSION`

    - `only_to_me` (bool): 是否只响应确定是在和「我」（机器人）说话的消息（在开头或结尾 @ 了机器人，或在开头称呼了机器人昵称）

    - `only_short_message` (bool): 是否只响应短消息

    - `allow_empty_message` (bool): 是否响应内容为空的消息（只有 @ 或机器人昵称）

  - **返回**

    - ((NLPSession) -> Awaitable[IntentCommand | None]) -> (NLPSession) -> Awaitable[IntentCommand | None]

- **用法**

  ```python
  @on_natural_language({'天气'}, only_to_me=False)
  async def _(session: NLPSession):
      return IntentCommand('weather', 100.0)
  ```

  响应所有带有「天气」关键词的消息，当做 `weather` 命令处理。

  如果有多个自然语言处理器同时处理了一条消息，则置信度最高的 `IntentCommand` 会被选择。处理器可以返回 `None`，表示不把消息当作任何命令处理。

## _def_ `on_notice(arg=None, *events)` <Badge text="1.6.0+"/>

- **说明**

  将函数装饰为通知处理器。

- **要求**

  被装饰函数必须是一个 async 函数，且必须接收且仅接收一个位置参数，类型为 `NoticeSession`，即形如:

  ```python
  async def func(session: NoticeSession):
      pass
  ```

- **重载**

  **1.** `(__func)`

  - **参数**

    - `__func` ((NoticeSession) -> Awaitable[Any])

  - **返回**

    - (NoticeSession) -> Awaitable[Any]

  **2.** `(*events)`

  - **参数**

    - `*events` (str): 要处理的通知类型（`notice_type`），若不传入，则处理所有通知

  - **返回**

    - ((NoticeSession) -> Awaitable[Any]) -> (NoticeSession) -> Awaitable[Any]

- **用法**

  ```python
  @on_notice
  async def _(session: NoticeSession):
      logger.info('有新的通知事件：%s', session.event)

  @on_notice('group_increase')
  async def _(session: NoticeSession):
      await session.send('欢迎新朋友～')
  ```

  收到所有通知时打日志，收到新成员进群通知时除了打日志还发送欢迎信息。

## _def_ `on_request(arg=None, *events)` <Badge text="1.6.0+"/>

- **说明**

  将函数装饰为请求处理器。

- **要求**

  被装饰函数必须是一个 async 函数，且必须接收且仅接收一个位置参数，类型为 `RequestSession`，即形如:

  ```python
  async def func(session: RequestSession):
      pass
  ```

- **重载**

  **1.** `(__func)`

  - **参数**

    - `__func` ((RequestSession) -> Awaitable[Any])

  - **返回**

    - (RequestSession) -> Awaitable[Any]

  **2.** `(*events)`

  - **参数**

    - `*events` (str): 要处理的请求类型（`request_type`），若不传入，则处理所有请求

  - **返回**

    - ((RequestSession) -> Awaitable[Any]) -> (RequestSession) -> Awaitable[Any]

- **用法**

  ```python
  @on_request
  async def _(session: RequestSession):
      logger.info('有新的请求事件：%s', session.event)

  @on_request('group')
  async def _(session: RequestSession):
      await session.approve()
  ```

  收到所有请求时打日志，收到群请求时除了打日志还同意请求。