"""
This module replicates the standard permission module already defined
in Nonebot. This, yet another implementation, is experimental and may
be easier or harder to use than the standard one.
"""

import asyncio
from datetime import datetime, time
from typing import Any, Awaitable, Callable, Container, Dict, Iterable, NamedTuple, Optional, Union, List

from aiocache.decorators import cached
from aiocqhttp.event import Event as CQEvent
from nonebot import NoneBot
from nonebot.exceptions import CQHttpError


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


# AS OF this commit: same as original _get_member_info()
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
                           policy: 'RoleCheckPolicy') -> bool:
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


# Polices are the functions that triggers when events arrive. They return
# booleans to determine whether to proceed with the commands. Here we give
# its definition, and some example implementations.


RoleCheckPolicy = Callable[[SenderRoles], Union[bool, Awaitable[bool]]]


def aggregate_policy(
    policies: Iterable[RoleCheckPolicy],
    aggregator: Callable[[Iterable[object]], bool] = all
) -> RoleCheckPolicy:
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
    syncs = []  # type: List[Callable[[SenderRoles], bool]]
    asyncs = []  # type: List[Callable[[SenderRoles], Awaitable[bool]]]
    for f in policies:
        if asyncio.iscoroutinefunction(f) or (
            asyncio.iscoroutinefunction(f.__call__)):
            # pyright cannot narrow down types
            asyncs.append(f)  # type: ignore
        else:
            syncs.append(f)  # type: ignore

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


def simple_allow_list(*, user_ids: Container[int] = ...,
                      group_ids: Container[int] = ...,
                      reverse: bool = False) -> RoleCheckPolicy:
    """
    Creates a policy that only allows senders from these users or groups.
    The returned function is stateless.

    ctrl+mouse to this function to see how to write a complex policy.

    :param user_ids: set of user ids to allow
    :param group_ids: set of group ids to allow
    :param reverse: if this is true, then bans the aforementioned
                    senders instead (policy becomes blocklist)
    :return: new policy
    """
    user_ids = user_ids if user_ids is not ... else set()
    group_ids = group_ids if group_ids is not ... else set()

    def checker(sender: SenderRoles) -> bool:
        is_in = sender.sent_by(user_ids) or sender.from_group(group_ids)
        return not is_in if reverse else is_in

    return checker


def simple_time_range(begin_time: time, end_time: time,
                      reverse: bool = False,
                      tz_info: Any = None) -> RoleCheckPolicy:
    """
    Creates a policy that only allows commands to be activated between
    begin_time and end_time. Uses builtin datetime.datetime module.
    The returned function is stateless.

    :param begin_time: starting time and
    :param end_time: ending time to allow users
    :param reverse: if this is true, then bans the aforementioned
                    time ranges instead
    :param tz_info: argument to pass to datetime.now()
    :return: new policy
    """
    # source: https://stackoverflow.com/questions/10048249/how-do-i-determine-if-current-time-is-within-a-specified-range-using-pythons-da
    def checker(_: Any) -> bool:
        now = datetime.now(tz_info).time()
        if begin_time < end_time:
            is_in = now >= begin_time and now <= end_time
        else:
            is_in = now >= begin_time or now <= end_time
        return not is_in if reverse else is_in

    return checker


__all__ = [
    'SenderRoles',
    'check_permission',
    'RoleCheckPolicy',
    'aggregate_policy',
    'simple_allow_list',
    'simple_time_range'
]
