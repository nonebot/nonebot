# nonebot.command.group

## _class_ `CommandGroup(name, *, permission=..., only_to_me=..., privileged=..., shell_like=..., expire_timeout=..., run_timeout=..., session_class=...)`

- **说明**

  命令组，用于声明一组有相同名称前缀的命令。

  **注:** 在 1.8.1 之前，此类文档与实际表现不一致 ([issue 242](https://github.com/nonebot/nonebot/issues/242))。

- **参数**

  - `name` (str | [CommandName_T](../typing.md#var-commandname-t)): 命令名前缀，若传入字符串，则会自动转换成元组

  - `permission` ([PermissionPolicy_T](../typing.md#var-permissionpolicy-t) | Iterable[[PermissionPolicy_T](../typing.md#var-permissionpolicy-t)]) <Badge text="1.9.0+"/>: 对应 `permission` 属性

  - `only_to_me` (bool): 对应 `only_to_me` 属性

  - `privileged` (bool): 对应 `privileged` 属性

  - `shell_like` (bool): 对应 `shell_like` 属性

  - `expire_timeout` (datetime.timedelta | None) <Badge text="1.8.2+"/>: 对应 `expire_timeout` 属性

  - `run_timeout` (datetime.timedelta | None) <Badge text="1.8.2+"/>: 对应 `expire_timeout` 属性

  - `session_class` (Type[[CommandSession](./index.md#class-commandsession-bot-event-cmd-current-arg-args-none)] | None) <Badge text="1.8.1+"/>: 对应 `session_class` 属性

### _instance-var_ `basename`

- **类型:** tuple[str]

- **说明:** 命令名前缀。

### _instance-var_ `base_kwargs`

- **类型:** dict[str, Any]

- **说明:** 此对象初始化时传递的 `permission`, `only_to_me`, `privileged`, `shell_like`, `expire_timeout`, `run_timeout`, `session_class`。如果没有传递，则此字典也不存在相应键值。

### _method_ `command(self, name, *, aliases=..., patterns=..., permission=..., only_to_me=..., privileged=..., shell_like=..., expire_timeout=..., run_timeout=..., session_class=...)`

- **说明**

  将函数装饰为命令组中的命令处理器。使用方法和 `on_command` 装饰器完全相同。

- **参数**

  - `name` (str | [CommandName_T](../typing.md#var-commandname-t)): 命令名，注册命令处理器时会加上命令组的前缀

  - `aliases` (Iterable[str] | str): 和 `on_command` 装饰器含义相同，若不传入则使用命令组默认值，若命令组没有默认值时，则使用 `on_command` 装饰器的默认值

  - `patterns` ([Patterns_T](../typing.md#var-patterns-t)) <Badge text="1.8.1+"/>: 同上

  - `permission` ([PermissionPolicy_T](../typing.md#var-permissionpolicy-t) | Iterable[[PermissionPolicy_T](../typing.md#var-permissionpolicy-t)]) <Badge text="1.9.0+"/>: 同上

  - `only_to_me` (bool): 同上

  - `privileged` (bool): 同上

  - `shell_like` (bool): 同上

  - `expire_timeout` (datetime.timedelta | None) <Badge text="1.8.2+"/>: 同上

  - `run_timeout` (datetime.timedelta | None) <Badge text="1.8.2+"/>: 同上

  - `session_class` (Type[[CommandSession](./index.md#class-commandsession-bot-event-cmd-current-arg-args-none)] | None) <Badge text="1.8.1+"/>: 同上

- **返回**

  - ([CommandHandler_T](../typing.md#var-commandhandler-t)) -> [CommandHandler_T](../typing.md#var-commandhandler-t): 装饰器闭包

- **用法**

  ```python
  sched = CommandGroup('scheduler')

  @sched.command('add', permission=PRIVATE)
  async def _(session: CommandSession):
      pass
  ```

  注册 `('scheduler', 'add')` 命令。