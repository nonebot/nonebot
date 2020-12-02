from typing import Union, Callable

from nonebot.plugin import on_command
from nonebot.typing import CommandHandler_T, CommandName_T


class CommandGroup:
    """
    Group a set of commands with same name prefix.
    """

    __slots__ = ('basename', 'base_kwargs')

    def __init__(self, name: Union[str, CommandName_T], **kwargs):
        if 'aliases' in kwargs or 'patterns' in kwargs:
            raise ValueError('aliases or patterns should not be used as base kwargs for group')
        self.basename = (name,) if isinstance(name, str) else name
        self.base_kwargs = kwargs

    def command(self, name: Union[str, CommandName_T],
                **kwargs) -> Callable[[CommandHandler_T], CommandHandler_T]:
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

        final_kwargs = { **self.base_kwargs, **kwargs }
        return on_command(name, **final_kwargs)
