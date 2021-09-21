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
    A high level agent object to assess a message sender's permissions
    such as message type, sender's group role, etc. If any groups are
    involved, such as group messages and direct private messages from
    a group member, that group number is consistent across all methods
    """

    bot: NoneBot
    event: CQEvent
    sender: Optional[Dict[str, Any]]

    @staticmethod
    async def create(bot: NoneBot, event: CQEvent) -> 'SenderRoles':
        """constructor to create a SenderRoles object from an event"""
        # same approach as vanilla permission checker
        sender_info = await _get_member_info(bot, event.self_id,
            event.group_id, event.user_id) \
            if event.get('message_type') == 'group' else None
        return SenderRoles(bot, event, sender_info)

    # builtin components:

    @property
    def is_superuser(self) -> bool:
        return self.event.user_id in self.bot.config.SUPERUSERS

    @property
    def is_groupchat(self) -> bool:
        return self.event.get('message_type') == 'group'

    @property
    def is_anonymous(self) -> bool:
        return self.event.sub_type == 'anonymous'

    @property
    def is_admin(self) -> bool:
        return self.sender is not None and self.sender.get('role') == 'admin'

    @property
    def is_owner(self) -> bool:
        return self.sender is not None and self.sender.get('role') == 'owner'

    @property
    def is_privatechat(self) -> bool:
        return self.event.get('message_type') == 'private'

    @property
    def is_private_friend(self) -> bool:
        return self.is_privatechat and self.event.sub_type == 'friend'

    @property
    def is_private_group(self) -> bool:
        return self.is_privatechat and self.event.sub_type == 'group'

    @property
    def is_private_discuss(self) -> bool:
        return self.is_privatechat and self.event.sub_type == 'discuss'

    @property
    def is_discusschat(self) -> bool:
        return self.event.get('message_type') == 'discuss'

    def from_group(self, group_id: Union[int, Container[int]]) -> bool:
        """returns True if the sender belongs to these groups (group_ids)"""
        if isinstance(group_id, int):
            return self.event.group_id == group_id
        return self.event.group_id in group_id

    def sent_by(self, sender_id: Union[int, Container[int]]) -> bool:
        """returns True if the sender is one of these people (sender_ids)"""
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
    Check whether the message sender has permission required defined
    by the policy

    :param bot: NoneBot instance
    :param event: message event
    :param policy: the policy that returns boolean
    :return: the context has the permission
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
    Merge several role checkers into one using the AND operator (if `aggregator`
    is builtin function `all` - by default). if all given policies are sync,
    the merged one is sync, otherwise it is async. This is useful to concatenate
    policies like applying [blocklist, groupchat, ...] altogether.

    async functions are slow maybe. use with caution.

    The `aggregator` parameter is recommended to be the bultin functions such as
    `all` (performing AND operations on each checkers), or `any` (performing OR
    operations) because they short circuit. However it is possible to define more
    complex aggregators.

    Be aware that the order of checkers being called is not specified.

    :param policies: list of policies
    :param aggregator: the function used to combine the results of each separate
                       checkers as items consumed in iterators.
    :return: new policy
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
