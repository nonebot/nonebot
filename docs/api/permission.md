# nonebot.permission

NoneBot 支持为命令和自然语言处理器设置触发条件，此条件为一个类型为 `PermissionPolicy_T` 的可调用对象:

```python
# 同步: 返回值恒为假，即表示所有消息和发送者都没有权限
disabled: PermissionPolicy_T = lambda sender: False

# 同步: 当消息是群聊，且发送者既不是管理员也不是群主时给予权限
def normal_group_member(sender: SenderRoles):
    return sender.is_groupchat and not sender.is_admin and not sender.is_owner

# 异步: 在检查器中查询数据库再根据返回值决定是否给予权限
async def db_check(sender: SenderRoles):
    query = await db.execute('if exists (select * from list where user=?) 1 else 0', (sender.event.user_id,))
    return query[0] != 0
```

在实际使用时应当避免挂起太久的异步操作。在定义了这些条件后，可作为 `permission` 参数传递给相关的装饰器:

```python
permit_group = { 768887710 }
banned_people = { 10000, 10001 }
def foo(sender: SenderRoles):
    return sender.is_groupchat and sender.from_group(permit_group)     and not sender.sendby(banned_people)

@on_natural_language({'天气'}, only_to_me=False, permission=(foo, db_check))                        # 需要同时满足 foo 和 db_check
                                                # permission=aggregate_policy((foo, db_check))      # 需要同时满足 foo 和 db_check
                                                # permission=aggregate_policy((foo, db_check), any) # 只需满足一个
async def _(session: NLPSession):
    return IntentCommand('weather', 100.0)
```

## 权限声明常量
<br />
<details>
<summary>适用于 1.9.0 之前的版本。点此展开</summary>

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

在 1.9.0 后，这些常量的类型从 `int` 改变为了 [PermissionPolicy_T](./typing.md#var-permissionpolicy-t)，所以如果你之前包含了它们的 type hints，或用了不寻常的方法来获取它们的值，则可能会导致错误。

</details>

## _class_ `SenderRoles(bot, event, sender)` <Badge text="1.9.0+"/>

- **说明**

  封装了原生的 `CQEvent` 便于权限检查。此类的实例一般会传入 `PermissionPolicy_T` 作为参数。

- **参数**

  - `bot` ([NoneBot](./index.md#class-nonebot-config-object-none))

  - `event` (aiocqhttp.event.Event)

  - `sender` (dict[str, Any] | None)

### _class-var_ `bot`

- **类型:** nonebot.NoneBot

- **说明:** 机器人对象。

### _class-var_ `event`

- **类型:** aiocqhttp.event.Event

- **说明:** 事件。

### _property_ `is_admin`

- **类型:** bool

- **说明:** 发送者是群管理员。

### _property_ `is_anonymous`

- **类型:** bool

- **说明:** 消息是匿名消息。

### _property_ `is_discusschat`

- **类型:** bool

- **说明:** 消息是讨论组消息。

### _property_ `is_groupchat`

- **类型:** bool

- **说明:** 消息是群聊消息。

### _property_ `is_owner`

- **类型:** bool

- **说明:** 发送者是群主。

### _property_ `is_private_discuss`

- **类型:** bool

- **说明:** 消息是讨论组私聊消息。

### _property_ `is_private_friend`

- **类型:** bool

- **说明:** 消息是好友私聊消息。

### _property_ `is_private_group`

- **类型:** bool

- **说明:** 消息是群私聊消息。

### _property_ `is_privatechat`

- **类型:** bool

- **说明:** 消息是私聊消息。

### _property_ `is_superuser`

- **类型:** bool

- **说明:** 发送者是配置文件中设置的超级用户。

### _class-var_ `sender`

- **类型:** dict[str, Any] | None

- **说明:** 只有消息是群消息的时候才会有这个属性，其内容是 `/get_group_member_info` API 调用的返回值。

### _async staticmethod_ `create(bot, event)`

- **说明**

  构造 `SenderRoles`。

- **参数**

  - `bot` ([NoneBot](./index.md#class-nonebot-config-object-none)): 接收事件的 NoneBot 对象

  - `event` (aiocqhttp.event.Event): 上报事件

- **返回**

  - SenderRoles

- **用法**

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

### _method_ `from_group(self, group_id)`

- **说明**

  表示发送者是否来自于群 `group_id`。

- **参数**

  - `group_id` (int | Container[int]): 群号码，可以为多个群号。

- **返回**

  - bool

### _method_ `sent_by(self, sender_id)`

- **说明**

  表示发送者 QQ 号是否是 `sender_id`。

- **参数**

  - `sender_id` (int | Container[int]): 表示发送者 QQ 号是否是 `sender_id`。

- **返回**

  - bool

## _async def_ `check_permission(bot, event, policy)`

- **说明**

  检查用户是否具有所要求的权限。

  一般用户应该没有必要使用该函数。

- **参数**

  - `bot` ([NoneBot](./index.md#class-nonebot-config-object-none)): NoneBot 对象

  - `event` (aiocqhttp.event.Event): 消息事件对象

  - `policy` ((SenderRoles) -> bool | (SenderRoles) -> Awaitable[bool]) <Badge text="1.9.0+"/>: 返回布尔值的权限检查策略

- **返回**

  - bool: 消息事件所对应的上下文是否具有所要求的权限

- **用法**

  ```python
  has_perm = await check_permission(bot, event, normal_group_member)
  ```

## _def_ `aggregate_policy(policies, aggregator=<built-in function all>)` <Badge text="1.9.0+"/>

- **说明**

  在默认参数下，将多个权限检查策略函数使用 AND 操作符连接并返回单个权限检查策略。在实现中对这几个策略使用内置 `all` 函数，会优先执行同步函数而且尽可能在同步模式的情况下短路。

  在新的策略下，只有事件满足了 `policies` 中所有的原策略，才会返回 `True`。

  `aggregator` 参数也可以设置为其他函数，例如 `any`: 在此情况下会使用 `OR` 操作符连接。

  如果参数中所有的策略都是同步的，则返回值是同步的，否则返回值是异步函数。

- **参数**

  - `policies` (Iterable[(SenderRoles) -> bool | (SenderRoles) -> Awaitable[bool]]): 要合并的权限检查策略

  - `aggregator` ((Iterable[object]) -> bool): 用于合并策略的函数

- **返回**

  - PermissionPolicy_T: 新的权限检查策略

- **用法**

  ```python
  # 以下两种方式在效果上等同
  policy1 = lambda sender: sender.is_groupchat and sender.from_group(123456789)

  policy2 = aggregate_policy(lambda sender: sender.is_groupchat,
                             lambda sender: sender.from_group(123456789))
  ```