"""
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
    return sender.is_groupchat and sender.from_group(permit_group) \
    and not sender.sendby(banned_people)

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

在 1.9.0 后，这些常量的类型从 `int` 改变为了 {ref}`nonebot.typing.PermissionPolicy_T`，所以如果你之前包含了它们的 type hints，或用了不寻常的方法来获取它们的值，则可能会导致错误。

</details>
"""
import asyncio
from typing import Any, Awaitable, Callable, Container, Dict, Iterable, NamedTuple, Optional, Union, List

from aiocache.decorators import cached
from aiocqhttp.event import Event as CQEvent

from nonebot import NoneBot
from nonebot.exceptions import CQHttpError
from nonebot.helpers import separate_async_funcs
from nonebot.typing import PermissionPolicy_T


class SenderRoles(NamedTuple):
    """
    封装了原生的 `CQEvent` 便于权限检查。此类的实例一般会传入 `PermissionPolicy_T` 作为参数。

    版本: 1.9.0+
    """

    bot: NoneBot
    """{kind}`instance-var` 机器人对象。"""
    event: CQEvent
    """{kind}`instance-var` 事件。"""
    sender: Optional[Dict[str, Any]]
    """{kind}`instance-var` 只有消息是群消息的时候才会有这个属性，其内容是 `/get_group_member_info` API 调用的返回值。"""

    @staticmethod
    async def create(bot: NoneBot, event: CQEvent) -> 'SenderRoles':
        """
        构造 `SenderRoles`。

        参数:
            bot: 接收事件的 NoneBot 对象
            event: 上报事件

        用法:
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
        """
        # same approach as vanilla permission checker
        sender_info = await _get_member_info(bot, event.self_id,
            event.group_id, event.user_id) \
            if event.get('message_type') == 'group' else None
        return SenderRoles(bot, event, sender_info)

    # builtin components:

    @property
    def is_superuser(self) -> bool:
        """发送者是配置文件中设置的超级用户。"""
        return self.event.user_id in self.bot.config.SUPERUSERS

    @property
    def is_groupchat(self) -> bool:
        """消息是群聊消息。"""
        return self.event.get('message_type') == 'group'

    @property
    def is_anonymous(self) -> bool:
        """消息是匿名消息。"""
        return self.event.sub_type == 'anonymous'

    @property
    def is_admin(self) -> bool:
        """发送者是群管理员。"""
        return self.sender is not None and self.sender.get('role') == 'admin'

    @property
    def is_owner(self) -> bool:
        """发送者是群主。"""
        return self.sender is not None and self.sender.get('role') == 'owner'

    @property
    def is_privatechat(self) -> bool:
        """消息是私聊消息。"""
        return self.event.get('message_type') == 'private'

    @property
    def is_private_friend(self) -> bool:
        """消息是好友私聊消息。"""
        return self.is_privatechat and self.event.sub_type == 'friend'

    @property
    def is_private_group(self) -> bool:
        """消息是群私聊消息。"""
        return self.is_privatechat and self.event.sub_type == 'group'

    @property
    def is_private_discuss(self) -> bool:
        """消息是讨论组私聊消息。"""
        return self.is_privatechat and self.event.sub_type == 'discuss'

    @property
    def is_discusschat(self) -> bool:
        """消息是讨论组消息。"""
        return self.event.get('message_type') == 'discuss'

    def from_group(self, group_id: Union[int, Container[int]]) -> bool:
        """
        表示发送者是否来自于群 `group_id`。

        参数:
            group_id: 群号码，可以为多个群号。
        """
        if isinstance(group_id, int):
            return self.event.group_id == group_id
        return self.event.group_id in group_id

    def sent_by(self, sender_id: Union[int, Container[int]]) -> bool:
        """
        表示发送者 QQ 号是否是 `sender_id`。

        参数:
            sender_id: 表示发送者 QQ 号是否是 `sender_id`。
        """
        if isinstance(sender_id, int):
            return self.event.user_id == sender_id
        return self.event.user_id in sender_id


@cached(ttl=2 * 60)
async def _get_member_info(bot: NoneBot,
                           self_id: int,
                           group_id: int,
                           user_id: int) -> Optional[Dict[str, Any]]:
    try:
        return await bot.get_group_member_info(
                    self_id=self_id,
                    group_id=group_id,
                    user_id=user_id,
                    no_cache=True)
    except CQHttpError:
        return None


async def check_permission(bot: NoneBot, event: CQEvent,
                           policy: PermissionPolicy_T) -> bool:
    """
    检查用户是否具有所要求的权限。

    一般用户应该没有必要使用该函数。

    参数:
        bot: NoneBot 对象
        event: 消息事件对象
        policy (nonebot.typing.PermissionPolicy_T) {version}`1.9.0+`: 返回布尔值的权限检查策略

    返回:
        bool: 消息事件所对应的上下文是否具有所要求的权限

    用法:
        ```python
        has_perm = await check_permission(bot, event, normal_group_member)
        ```
    """
    sender_roles = await SenderRoles.create(bot, event)
    res = policy(sender_roles)
    if isinstance(res, Awaitable):
        return await res
    return res


def aggregate_policy(
    policies: Iterable[PermissionPolicy_T],
    aggregator: Callable[[Iterable[object]], bool] = all
) -> PermissionPolicy_T:
    """
    在默认参数下，将多个权限检查策略函数使用 AND 操作符连接并返回单个权限检查策略。在实现中对这几个策略使用内置 `all` 函数，会优先执行同步函数而且尽可能在同步模式的情况下短路。

    在新的策略下，只有事件满足了 `policies` 中所有的原策略，才会返回 `True`。

    `aggregator` 参数也可以设置为其他函数，例如 `any`: 在此情况下会使用 `OR` 操作符连接。

    如果参数中所有的策略都是同步的，则返回值是同步的，否则返回值是异步函数。

    版本: 1.9.0+

    参数:
        policies: 要合并的权限检查策略
        aggregator: 用于合并策略的函数

    返回:
        PermissionPolicy_T: 新的权限检查策略

    用法:
        ```python
        # 以下两种方式在效果上等同
        policy1 = lambda sender: sender.is_groupchat and sender.from_group(123456789)

        policy2 = aggregate_policy(lambda sender: sender.is_groupchat,
                                   lambda sender: sender.from_group(123456789))
        ```
    """
    syncs: List[Callable[[SenderRoles], bool]]
    asyncs: List[Callable[[SenderRoles], Awaitable[bool]]]
    syncs, asyncs = separate_async_funcs(policies)

    def checker_sync(sender: SenderRoles) -> bool:
        return aggregator(f(sender) for f in syncs)

    if len(asyncs) == 0:
        return checker_sync

    async def checker_async(sender: SenderRoles) -> bool:
        if not checker_sync(sender):
            return False
        # no short circuiting currently :-(
        coros = [f(sender) for f in asyncs]
        return aggregator(await asyncio.gather(*coros))

    return checker_async


# legacy interfaces

class _LegacyPermissionConstant:
    """INTERNAL API"""

    def __init__(self, policy: Callable[[SenderRoles], bool]):
        # skip aggregate_policy as legacy permissions are sync checks
        self._policy = policy

    def __call__(self, sender: SenderRoles):
        return self._policy(sender)

    def __and__(self, other: '_LegacyPermissionConstant') -> '_LegacyPermissionConstant':
        return _LegacyPermissionConstant(lambda s: self._policy(s) and other._policy(s))

    def __or__(self, other: '_LegacyPermissionConstant') -> '_LegacyPermissionConstant':
        return _LegacyPermissionConstant(lambda s: self._policy(s) or other._policy(s))


PRIVATE_FRIEND = _LegacyPermissionConstant(lambda s: s.is_private_friend)
PRIVATE_GROUP = _LegacyPermissionConstant(lambda s: s.is_private_group)
PRIVATE_DISCUSS = _LegacyPermissionConstant(lambda s: s.is_private_discuss)
PRIVATE_OTHER = _LegacyPermissionConstant(lambda s: s.is_privatechat and s.event.sub_type == 'other')
PRIVATE = _LegacyPermissionConstant(lambda s: s.is_privatechat)
DISCUSS = _LegacyPermissionConstant(lambda s: s.is_discusschat)
GROUP_MEMBER = _LegacyPermissionConstant(lambda s: s.is_groupchat and not s.is_anonymous)
GROUP_ADMIN = _LegacyPermissionConstant(lambda s: s.is_groupchat and s.is_admin)
GROUP_OWNER = _LegacyPermissionConstant(lambda s: s.is_groupchat and s.is_owner)
GROUP = _LegacyPermissionConstant(lambda s: s.is_groupchat)
SUPERUSER = _LegacyPermissionConstant(lambda s: s.is_superuser)
EVERYBODY = _LegacyPermissionConstant(lambda _: True)


__all__ = [
    'SenderRoles',
    'check_permission',
    'aggregate_policy',
    'check_permission',
    'PRIVATE_FRIEND',
    'PRIVATE_GROUP',
    'PRIVATE_DISCUSS',
    'PRIVATE_OTHER',
    'PRIVATE',
    'DISCUSS',
    'GROUP_MEMBER',
    'GROUP_ADMIN',
    'GROUP_OWNER',
    'GROUP',
    'SUPERUSER',
    'EVERYBODY',
]
