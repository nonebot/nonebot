from typing import Optional, Union, Callable, Iterable

from nonebot.plugin import on_command
from nonebot.typing import CommandHandler_T, CommandName_T


class CommandGroup:
    """
    Group a set of commands with same name prefix.
    """

    __slots__ = ('basename', 'permission', 'only_to_me',
                 'privileged', 'shell_like')

    def __init__(self, name: Union[str, CommandName_T], *,
                 permission: Optional[int] = None,
                 only_to_me: Optional[bool] = None,
                 privileged: Optional[bool] = None,
                 shell_like: Optional[bool] = None) -> None:
        self.basename = (name,) if isinstance(name, str) else name
        self.permission = permission
        self.only_to_me = only_to_me
        self.privileged = privileged
        self.shell_like = shell_like

    def command(self, name: Union[str, CommandName_T], *,
                aliases: Optional[Union[Iterable[str], str]] = None,
                permission: Optional[int] = None,
                only_to_me: Optional[bool] = None,
                privileged: Optional[bool] = None,
                shell_like: Optional[bool] = None
                ) -> Callable[[CommandHandler_T], CommandHandler_T]:
        """
        Decorator to register a function as a command. Its has the same usage as
        `on_command`.

        :param kwargs: keyword arguments will be passed to `on_command`. For each
                       argument in the signature of this method here, if it is not
                       present when calling, default value for the command group is
                       used (e.g. `self.permission`). If that value is also not set,
                       default value for `on_command` is used.
        """
        sub_name = (name,) if isinstance(name, str) else name
        name = self.basename + sub_name

        kwargs_tup = (
            ('name', name),
            ('aliases', aliases),
            ('permission', permission if permission is not None else self.permission),
            ('only_to_me', only_to_me if only_to_me is not None else self.only_to_me),
            ('privileged', privileged if privileged is not None else self.privileged),
            ('shell_like', shell_like if shell_like is not None else self.shell_like)
        )
        kwargs = { k: v for k, v in kwargs_tup if v is not None }

        return on_command(**kwargs)


__all__ = [
    'CommandGroup',
]
