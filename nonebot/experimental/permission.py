from datetime import datetime, time
from typing import Any, Container

from nonebot.permission import SenderRoles
from nonebot.typing import PermissionPolicy_T


def simple_allow_list(*, user_ids: Container[int] = ...,
                      group_ids: Container[int] = ...,
                      reverse: bool = False) -> PermissionPolicy_T:
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
                      tz_info: Any = None) -> PermissionPolicy_T:
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
    'simple_allow_list',
    'simple_time_range'
]
