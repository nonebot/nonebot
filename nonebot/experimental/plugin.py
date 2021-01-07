"""
This module replicates the standard  modules already defined
in Nonebot. This, yet another implementation, is experimental and may
be easier or harder to use than the standard one.
"""

from datetime import timedelta
from functools import partial
from typing import Callable, Iterable, Optional, Type, Union, overload

from nonebot.command import CommandSession
from nonebot.experimental.permission import (RoleCheckPolicy, aggregate_policy,
                                             check_permission)
from nonebot.plugin import on_command_custom, on_natural_language_custom
from nonebot.typing import CommandHandler_T, CommandName_T, Patterns_T, NLPHandler_T


def on_command(
    name: Union[str, CommandName_T],
    *,
    aliases: Union[Iterable[str], str] = (),
    patterns: Patterns_T = (),
    permission: Union[RoleCheckPolicy, Iterable[RoleCheckPolicy]] = lambda _: True,
    only_to_me: bool = True,
    privileged: bool = False,
    shell_like: bool = False,
    expire_timeout: Optional[timedelta] = ...,
    run_timeout: Optional[timedelta] = ...,
    session_class: Optional[Type[CommandSession]] = None
) -> Callable[[CommandHandler_T], CommandHandler_T]:
    """
    Decorator to register a function as a command.

    This function's description is consistent with nonebot.plugin.on_command.
    """
    if isinstance(permission, Iterable):
        permission = aggregate_policy(permission)
    perm_checker = partial(check_permission, policy=permission)
    return on_command_custom(name, aliases=aliases, patterns=patterns,
                             only_to_me=only_to_me, privileged=privileged,
                             shell_like=shell_like, perm_checker=perm_checker,
                             expire_timeout=expire_timeout, run_timeout=run_timeout,
                             session_class=session_class)


@overload
def on_natural_language(func: NLPHandler_T) -> NLPHandler_T:
    """
    Decorator to register a function as a natural language processor with
    default kwargs.
    """


@overload
def on_natural_language(
    keywords: Optional[Union[Iterable[str], str]] = ...,
    *,
    permission: Union[RoleCheckPolicy, Iterable[RoleCheckPolicy]] = ...,
    only_to_me: bool = ...,
    only_short_message: bool = ...,
    allow_empty_message: bool = ...
) -> Callable[[NLPHandler_T], NLPHandler_T]:
    """
    Decorator to register a function as a natural language processor.

    This function's description is consistent with nonebot.plugin.on_natural_language,
    except permission, where you pass a function instead of an int.
    """


def on_natural_language(
    keywords: Union[Optional[Iterable[str]], str, NLPHandler_T] = None,
    *,
    permission: Union[RoleCheckPolicy, Iterable[RoleCheckPolicy]] = lambda _: True,
    only_to_me: bool = True,
    only_short_message: bool = True,
    allow_empty_message: bool = False
):
    """
    Implementation of on_natural_language overloads.
    """
    if isinstance(permission, Iterable):
        permission = aggregate_policy(permission)
    perm_checker = partial(check_permission, policy=permission)
    return on_natural_language_custom(keywords, only_to_me=only_to_me,
                                      only_short_message=only_short_message,
                                      allow_empty_message=allow_empty_message,
                                      perm_checker=perm_checker)


# command groups not implemented yet

__all__ = [
    'on_command',
    'on_natural_language'
]
