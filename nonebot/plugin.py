"""
版本: 1.1.0+
"""
import asyncio
import os
import re
import sys
import shlex
import warnings
import importlib
import contextlib
from datetime import timedelta
from types import ModuleType
from typing import TYPE_CHECKING, Any, Awaitable, Generator, List, Set, Dict, Tuple, TypeVar, Union, Optional, Iterable, Callable, Type, overload

from .log import logger
from nonebot import permission as perm
from .command import Command, CommandManager, CommandSession
from .notice_request import EventHandler, EventManager
from .natural_language import NLProcessor, NLPManager
from .helpers import separate_async_funcs
from .typing import CommandName_T, CommandHandler_T, NLPHandler_T, NoticeHandler_T, Patterns_T, PermissionPolicy_T, PluginLifetimeHook_T, RequestHandler_T

if TYPE_CHECKING:
    from .message import MessagePreprocessor


class LifetimeHook:
    """INTERNAL_API"""
    __slots__ = ('func', 'timing')

    def __init__(self, func: PluginLifetimeHook_T, timing: str):
        if timing not in ('loading', 'unloaded'):
            raise ValueError(f'Invalid timing "{timing}"')
        self.func = func
        self.timing = timing


class Plugin:
    """用于包装已加载的插件模块的类。"""
    __slots__ = ('module', 'name', 'usage', 'userdata', 'commands', 'nl_processors',
                 'event_handlers', 'msg_preprocessors', 'lifetime_hooks',
                 '_load_future', '_command_args')

    def __init__(self,
                 module: ModuleType,
                 name: Optional[str] = None,
                 usage: Optional[Any] = None,
                 userdata: Optional[Any] = None,
                 commands: Set[Command] = ...,
                 nl_processors: Set[NLProcessor] = ...,
                 event_handlers: Set[EventHandler] = ...,
                 msg_preprocessors: Set['MessagePreprocessor'] = ...,
                 lifetime_hooks: List[LifetimeHook] = ...):
        """Creates a plugin with no name, no usage, and no handlers."""

        self.module = module
        """已加载的插件模块（importlib 导入的 Python 模块）。"""
        self.name = name
        """插件名称，从插件模块的 `__plugin_name__` 特殊变量获得，如果没有此变量，则为 `None`。"""
        self.usage = usage
        """插件使用方法，从插件模块的 `__plugin_usage__` 特殊变量获得，如果没有此变量，则为 `None`。"""
        self.userdata = userdata
        """
        插件作者可由此变量向外部暴露其他信息，从插件模块的 `__plugin_userdata__` 特殊变量获得，如果没有此变量，则为 `None`。
        版本: 1.9.0+
        """
        self.commands: Set[Command] = \
            commands if commands is not ... else set()
        """
        插件包含的命令，通过 `on_command` 装饰器注册。
        版本: 1.6.0+
        """
        self.nl_processors: Set[NLProcessor] = \
            nl_processors if nl_processors is not ... else set()
        """
        插件包含的自然语言处理器，通过 `on_natural_language` 装饰器注册。
        版本: 1.6.0+
        """
        self.event_handlers: Set[EventHandler] = \
            event_handlers if event_handlers is not ... else set()
        """
        插件包含的事件处理器（包含通知、请求），通过 `on_notice` 以及 `on_request` 装饰器注册。
        版本: 1.6.0+
        """
        self.msg_preprocessors: Set['MessagePreprocessor'] = \
            msg_preprocessors if msg_preprocessors is not ... else set()
        """
        插件包含的消息预处理器，通过 `message_preprocessor` 装饰器注册。
        版本: 1.9.0+
        """
        self.lifetime_hooks: List[LifetimeHook] = \
            lifetime_hooks if lifetime_hooks is not ... else []
        """
        插件包含的生命周期事件回调，通过 `on_plugin` 装饰器注册。
        版本: 1.9.0+
        """

        self._load_future: Optional[asyncio.Future] = None
        # backward compat without touching self.commands
        self._command_args: Dict[
            Command, Tuple[Union[Iterable[str], str], Patterns_T]] = {}

    def __await__(self) -> Generator[None, None, Union['Plugin', None]]:
        """
        当使用 `load_plugin`, `unload_plugin`, `reload_plugin` 时，其返回的 `Plugin` 对象可以（非必需）被 await 来等待其异步加载、卸载完成。详情请见这些函数的文档。

        版本: 1.9.0+
        """
        if self._load_future is not None:
            try:
                result = yield from self._load_future.__await__()
                # if we are awaiting non-fast reload, self is stale plugin
                # a reload call will return a new Plugin if successful
                if result is not None:
                    return (yield from result.__await__())
                return self
            except Exception:
                return None
            finally:
                self._load_future = None
        return self

    def __del__(self):
        # surpress unretrieved future exception warning
        if self._load_future is not None:
            self._load_future.cancel()

    def _new_load_future(self) -> asyncio.Future:
        if self._load_future is not None and not self._load_future.done():
            self._load_future.set_exception(asyncio.CancelledError())
        self._load_future = asyncio.get_event_loop().create_future()
        return self._load_future

    class GlobalTemp:
        """INTERNAL API"""

        # command, aliases, pattern
        commands: List[Tuple[Command, Union[Iterable[str], str], Patterns_T]] = []
        nl_processors: Set[NLProcessor] = set()
        event_handlers: Set[EventHandler] = set()
        msg_preprocessors: Set['MessagePreprocessor'] = set()
        lifetime_hooks: List[LifetimeHook] = []
        now_within_plugin: bool = False

        @classmethod
        @contextlib.contextmanager
        def enter_plugin(cls):
            try:
                cls.clear()
                cls.now_within_plugin = True
                yield
            finally:
                cls.now_within_plugin = False

        @classmethod
        def clear(cls):
            cls.commands.clear()
            cls.nl_processors.clear()
            cls.event_handlers.clear()
            cls.msg_preprocessors.clear()
            cls.lifetime_hooks.clear()

        @classmethod
        def make_plugin(cls, module: ModuleType):
            p = Plugin(module=module,
                       name=getattr(module, '__plugin_name__', None),
                       usage=getattr(module, '__plugin_usage__', None),
                       userdata=getattr(module, '__plugin_userdata__', None),
                       commands={cmd[0] for cmd in cls.commands},
                       nl_processors={*cls.nl_processors},
                       event_handlers={*cls.event_handlers},
                       msg_preprocessors={*cls.msg_preprocessors},
                       lifetime_hooks=[*cls.lifetime_hooks])
            # backward compat
            if cls.commands:
                p._command_args = {cmd[0]: (cmd[1], cmd[2]) for cmd in cls.commands}
            return p


class PluginManager:
    """
    插件管理器: 用于管理插件的加载以及插件中命令、自然语言处理器、事件处理器的开关。

    版本: 1.6.0+
    """
    # current loaded plugins
    _plugins: Dict[str, Plugin] = {}
    # plugins that are unloaded with option 'fast'
    _unloaded_plugins_fast: Dict[str, Plugin] = {}

    def __init__(self):
        self.cmd_manager = CommandManager()
        """命令管理器实例。"""
        self.nlp_manager = NLPManager()
        """自然语言管理器实例。"""

    @classmethod
    def add_plugin(cls, module_path: str, plugin: Plugin) -> None:
        """
        注册一个 `Plugin` 对象。

        参数:
            module_path: 模块路径
            plugin: Plugin 对象

        用法:
            ```python
            plugin = Plugin(module, name, usage, commands, nl_processors, event_handlers)
            PluginManager.add_plugin("path.to.plugin", plugin)
            ```
        """
        if module_path in cls._plugins:
            warnings.warn(f"Plugin {module_path} already exists")
            return
        cls._plugins[module_path] = plugin

    @classmethod
    def get_plugin(cls, module_path: str) -> Optional[Plugin]:
        """
        获取一个已经注册的 `Plugin` 对象。

        参数:
            module_path: 模块路径

        返回:
            Optional[Plugin]: Plugin 对象

        用法:
            ```python
            plugin = PluginManager.get_plugin("path.to.plugin")
            ```
        """
        return cls._plugins.get(module_path, None)

    @classmethod
    def remove_plugin(cls, module_path: str) -> bool:
        """
        删除 Plugin 中的所有命令、自然语言处理器、事件处理器并从插件管理器移除 Plugin 对象。在 1.9.0 后，也会移除消息预处理器。

        :::danger
        这个方法实际并没有完全移除定义 Plugin 的模块。仅是移除其所注册的处理器。
        :::

        参数:
            module_path: 模块路径

        返回:
            bool: 是否移除了插件
        """
        plugin = cls.get_plugin(module_path)
        if not plugin:
            warnings.warn(f"Plugin {module_path} not exists")
            return False
        for command in plugin.commands:
            CommandManager.remove_command(command.name)
        for nl_processor in plugin.nl_processors:
            NLPManager.remove_nl_processor(nl_processor)
        for event_handler in plugin.event_handlers:
            EventManager.remove_event_handler(event_handler)
        from .message import MessagePreprocessorManager  # avoid import cycles
        for msg_preprocessor in plugin.msg_preprocessors:
            MessagePreprocessorManager.remove_message_preprocessor(msg_preprocessor)
        del cls._plugins[module_path]
        return True

    @classmethod
    def switch_plugin_global(cls,
                             module_path: str,
                             state: Optional[bool] = None) -> None:
        """
        根据 `state` 更改 plugin 中 commands, nl_processors, event_handlers 的全局状态。在 1.9.0 后，msg_preprocessors 的状态也会被更改。

        :::warning
        更改插件状态并不会影响插件内 scheduler 等其他全局副作用状态
        :::

        参数:
            module_path: 模块路径
            state:
                - `None(default)`: 切换状态，即 开 -> 关、关 -> 开
                - `bool`: 切换至指定状态，`True` -> 开、`False` -> 关

        用法:
            ```python
            # 全局关闭插件 path.to.plugin , 对所有消息生效
            PluginManager.switch_plugin_global("path.to.plugin", state=False)
            ```
        """
        plugin = cls.get_plugin(module_path)
        if not plugin:
            warnings.warn(f"Plugin {module_path} not found")
            return
        for command in plugin.commands:
            CommandManager.switch_command_global(command.name, state)
        for nl_processor in plugin.nl_processors:
            NLPManager.switch_nlprocessor_global(nl_processor, state)
        for event_handler in plugin.event_handlers:
            EventManager.switch_event_handler_global(event_handler, state)
        from .message import MessagePreprocessorManager  # avoid import cycles
        for msg_preprocessor in plugin.msg_preprocessors:
            MessagePreprocessorManager.switch_message_preprocessor_global(msg_preprocessor, state)

    @classmethod
    def switch_command_global(cls,
                              module_path: str,
                              state: Optional[bool] = None) -> None:
        """
        根据 `state` 更改 plugin 中 commands 的全局状态。

        参数:
            module_path: 模块路径
            state:
                - `None(default)`: 切换状态，即 开 -> 关、关 -> 开
                - `bool`: 切换至指定状态，`True` -> 开、`False` -> 关

        用法:
            ```python
            # 全局关闭插件 path.to.plugin 中所有命令, 对所有消息生效
            PluginManager.switch_command_global("path.to.plugin", state=False)
            ```
        """
        plugin = cls.get_plugin(module_path)
        if not plugin:
            warnings.warn(f"Plugin {module_path} not found")
            return
        for command in plugin.commands:
            CommandManager.switch_command_global(command.name, state)

    @classmethod
    def switch_nlprocessor_global(cls,
                                  module_path: str,
                                  state: Optional[bool] = None) -> None:
        """
        根据 `state` 更改 plugin 中 nl_processors 的全局状态。

        参数:
            module_path: 模块路径
            state:
                - `None(default)`: 切换状态，即 开 -> 关、关 -> 开
                - `bool`: 切换至指定状态，`True` -> 开、`False` -> 关

        用法:
            ```python
            from nonebot import message_preprocessor

            # 全局关闭插件 path.to.plugin 中所有自然语言处理器, 对所有消息生效
            PluginManager.switch_nlprocessor_global("path.to.plugin", state=False)

            @message_preprocessor
            async def processor(bot: NoneBot, event: CQEvent, plugin_manager: PluginManager):
                plugin_manager.switch_nlprocessor_global("path.to.plugin", state=False)
            ```
        """
        plugin = cls.get_plugin(module_path)
        if not plugin:
            warnings.warn(f"Plugin {module_path} not found")
            return
        for processor in plugin.nl_processors:
            NLPManager.switch_nlprocessor_global(processor, state)

    @classmethod
    def switch_eventhandler_global(cls,
                                   module_path: str,
                                   state: Optional[bool] = None) -> None:
        """
        根据 `state` 更改 plugin 中 event handlers 的全局状态。

        参数:
            module_path: 模块路径
            state:
                - `None(default)`: 切换状态，即 开 -> 关、关 -> 开
                - `bool`: 切换至指定状态，`True` -> 开、`False` -> 关

        用法:
            ```python
            # 全局关闭插件 path.to.plugin 中所有事件处理器, 对所有消息生效
            PluginManager.switch_eventhandler_global("path.to.plugin", state=False)
            ```
        """
        plugin = cls.get_plugin(module_path)
        if not plugin:
            warnings.warn(f"Plugin {module_path} not found")
            return
        for event_handler in plugin.event_handlers:
            EventManager.switch_event_handler_global(event_handler, state)

    @classmethod
    def switch_messagepreprocessor_global(cls,
                                          module_path: str,
                                          state: Optional[bool] = None) -> None:
        """
        根据 `state` 更改 plugin 中 message preprocessors 的全局状态。

        版本: 1.9.0+

        参数:
            module_path: 模块路径
            state:
                - `None(default)`: 切换状态，即 开 -> 关、关 -> 开
                - `bool`: 切换至指定状态，`True` -> 开、`False` -> 关

        用法:
            ```python
            # 全局关闭插件 path.to.plugin 中所有消息预处理器, 对所有消息生效
            PluginManager.switch_messagepreprocessor_global("path.to.plugin", state=False)
            ```
        """
        plugin = cls.get_plugin(module_path)
        if not plugin:
            warnings.warn(f"Plugin {module_path} not found")
            return
        from .message import MessagePreprocessorManager  # avoid import cycles
        for msg_preprocessor in plugin.msg_preprocessors:
            MessagePreprocessorManager.switch_message_preprocessor_global(msg_preprocessor, state)

    def switch_plugin(self,
                      module_path: str,
                      state: Optional[bool] = None) -> None:
        """
        根据 `state` 修改 plugin 中的 commands 和 nlprocessors 状态。仅对当前消息有效。

        参数:
            module_path: 模块路径
            state:
                - `None(default)`: 切换状态，即 开 -> 关、关 -> 开
                - `bool`: 切换至指定状态，`True` -> 开、`False` -> 关

        用法:
            ```python
            from nonebot import message_preprocessor

            # 关闭插件 path.to.plugin , 仅对当前消息生效
            @message_preprocessor
            async def processor(bot: NoneBot, event: CQEvent, plugin_manager: PluginManager):
                plugin_manager.switch_plugin("path.to.plugin", state=False)
            ```
        """
        plugin = self.get_plugin(module_path)
        if not plugin:
            warnings.warn(f"Plugin {module_path} not found")
            return
        for command in plugin.commands:
            self.cmd_manager.switch_command(command.name, state)
        for nl_processor in plugin.nl_processors:
            self.nlp_manager.switch_nlprocessor(nl_processor, state)

    def switch_command(self,
                       module_path: str,
                       state: Optional[bool] = None) -> None:
        """
        根据 `state` 修改 plugin 中 commands 的状态。仅对当前消息有效。

        参数:
            module_path: 模块路径
            state:
                - `None(default)`: 切换状态，即 开 -> 关、关 -> 开
                - `bool`: 切换至指定状态，`True` -> 开、`False` -> 关

        用法:
            ```python
            from nonebot import message_preprocessor

            # 关闭插件 path.to.plugin 中所有命令, 仅对当前消息生效
            @message_preprocessor
            async def processor(bot: NoneBot, event: CQEvent, plugin_manager: PluginManager):
                plugin_manager.switch_command("path.to.plugin", state=False)
            ```
        """
        plugin = self.get_plugin(module_path)
        if not plugin:
            warnings.warn(f"Plugin {module_path} not found")
            return
        for command in plugin.commands:
            self.cmd_manager.switch_command(command.name, state)

    def switch_nlprocessor(self,
                           module_path: str,
                           state: Optional[bool] = None) -> None:
        """
        根据 `state` 修改 plugin 中 nl_processors 的状态。仅对当前消息有效。

        参数:
            module_path: 模块路径
            state:
                - `None(default)`: 切换状态，即 开 -> 关、关 -> 开
                - `bool`: 切换至指定状态，`True` -> 开、`False` -> 关

        用法:
            ```python
            from nonebot import message_preprocessor

            # 关闭插件 path.to.plugin 中所有自然语言处理器, 仅对当前消息生效
            @message_preprocessor
            async def processor(bot: NoneBot, event: CQEvent, plugin_manager: PluginManager):
                plugin_manager.switch_nlprocessor("path.to.plugin", state=False)
            ```
        """
        plugin = self.get_plugin(module_path)
        if not plugin:
            warnings.warn(f"Plugin {module_path} not found")
            return
        for processor in plugin.nl_processors:
            self.nlp_manager.switch_nlprocessor(processor, state)


def _add_handlers_to_managers(plugin: Plugin) -> None:
    for cmd in plugin.commands:
        CommandManager.add_command(cmd.name, cmd)
        args = plugin._command_args[cmd]
        CommandManager.add_aliases(args[0], cmd)
        CommandManager.add_patterns(args[1], cmd)
    for processor in plugin.nl_processors:
        NLPManager.add_nl_processor(processor)
    for handler in plugin.event_handlers:
        EventManager.add_event_handler(handler)
    from .message import MessagePreprocessorManager  # avoid import cycles
    for mp in plugin.msg_preprocessors:
        MessagePreprocessorManager.add_message_preprocessor(mp)


def _run_async_func_by_environ(func: Callable[..., Awaitable[Any]]) -> None:
    """
    run an async func depending on whether we are currently in a running
    event loop (inside a another async function)
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:  # There is no current event loop..
        loop = None
    if loop and loop.is_running():
        loop.create_task(func())
    else:
        # not using asyncio.run() because it can be called only once (ideally)
        asyncio.get_event_loop().run_until_complete(func())


def _clean_up_module(module_path: str):
    to_del = [n for n in sys.modules.keys() if n.startswith(module_path)
        and (len(n) == len(module_path)
            or (len(n) > len(module_path) and n[len(module_path)] == '.'))]
    for name in to_del:
        del sys.modules[name]


def _load_plugin(module_path: str,
                 act: str,
                 no_fast: bool,
                 keep_future: bool) -> Optional[Plugin]:
    if PluginManager.get_plugin(module_path) is not None:
        warnings.warn(f"Plugin {module_path} already exists")
        return

    if no_fast and module_path in PluginManager._unloaded_plugins_fast:
        _clean_up_module(module_path)
        del PluginManager._unloaded_plugins_fast[module_path]

    imported = False
    try:
        if module_path in PluginManager._unloaded_plugins_fast:
            plugin = PluginManager._unloaded_plugins_fast[module_path]
        else:
            with Plugin.GlobalTemp.enter_plugin():
                module = importlib.import_module(module_path)
            imported = True
            plugin = Plugin.GlobalTemp.make_plugin(module)

        sync_loaders, async_loaders = separate_async_funcs(
            f.func for f in plugin.lifetime_hooks if f.timing == 'loading'
        )
        for f in sync_loaders:
            f()

        def after_cbs():
            _add_handlers_to_managers(plugin)
            PluginManager.add_plugin(module_path, plugin)
            if module_path in PluginManager._unloaded_plugins_fast:
                del PluginManager._unloaded_plugins_fast[module_path]
            logger.info(f'Succeeded to {act} "{module_path}"')

        if not async_loaders:
            # at this point, GlobalTemp and plugin object ^ have same contents
            after_cbs()
            return plugin
        # continue the async loading after this functions returns
        fut = plugin._load_future if keep_future and plugin._load_future is not None \
            else plugin._new_load_future()

        async def new_loader():
            try:
                for f in async_loaders:
                    await f()
                # but not necessarily here
                after_cbs()
                fut.set_result(None)
            except Exception as e:
                if imported:
                    _clean_up_module(module_path)
                fut.set_exception(e)
                logger.error(f'Failed to run loading hooks when {act}ing '
                             f'"{module_path}" asynchronously, error: {e}')
                logger.exception(e)

        _run_async_func_by_environ(new_loader)
        return plugin
    except Exception as e:
        if imported:
            _clean_up_module(module_path)
        logger.error(f'Failed to {act} "{module_path}", error: {e}')
        logger.exception(e)
        return None


def load_plugin(module_path: str, no_fast: bool = False) -> Optional[Plugin]:
    """
    加载插件（等价于导入模块）。

    此函数会调用插件中由 `on_plugin('loading')` 装饰器注册的函数（下称 「加载回调」），之后再添加插件中注册的处理器（如命令等）。

    参数:
        module_path: 模块路径
        no_fast {version}`1.9.1+`: 若此参数为 `True`，则无视 `unload_plugin` 中的 `fast` 选项而强制重新导入模块

    返回 (1.6.0+):
        Optional[Plugin]: 加载后生成的 `Plugin` 对象。根据插件组成不同，返回值包含如下情况:
            - 插件没有定义加载回调，或只定义了同步的加载回调（此为 1.9.0 前的唯一情况）: 此函数会执行回调，在加载完毕后返回新的插件对象，其可以被 await，行为为直接返回插件本身（也就是可以不 await）。如果发生异常，则返回 `None`
            - 插件定义了异步加载回调，但 `load_plugin` 是在 NoneBot 启动前调用的: 此函数会阻塞地运行异步函数，其余表现和上一致
            - 插件定义了异步加载回调，但 `load_plugin` 是在异步的情况下调用的（比如在 NoneBot 运行的事件循环中）: 此函数会先执行部分同步的加载回调
                - 如果成功，返回一个插件对象。返回值可以被 await，行为为等待剩余的异步加载完毕然后返回插件本身，或如果在 await 中发生了错误，返回 `None`
                - 如果失败，返回 `None`

    用法:
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
    """
    return _load_plugin(module_path, 'import and load', no_fast, False)


def _unload_plugin(module_path: str,
                   fast: bool,
                   kont: Optional[Callable[[], Any]]) -> Optional[Plugin]:
    plugin = PluginManager.get_plugin(module_path)
    if not PluginManager.remove_plugin(module_path) or plugin is None:
        # second condition is useless. just pass type check
        return None

    sync_unloaders, async_unloaders = separate_async_funcs(
        f.func for f in plugin.lifetime_hooks if f.timing == 'unloaded'
    )

    # docs say behavior is undefined if unloaders raise, but the case is still
    # handled like this under the hood
    error = False

    try:
        for f in sync_unloaders:
            f()
    except Exception as e:
        error = True
        logger.error(f'Failed to run unloading hooks when unloading '
                     f'"{module_path}", error: {e}. Remaining hooks are not continued.')
        logger.exception(e)

    def after_cbs():
        if fast:
            # plugin is not None
            PluginManager._unloaded_plugins_fast[module_path] = plugin  # type: ignore
        else:
            _clean_up_module(module_path)
        if error:
            logger.info(f'Unloaded "{module_path}" with error')
        else:
            logger.info(f'Succeeded to unload "{module_path}"')

    if not async_unloaders:
        after_cbs()
        if kont is not None:
            return kont()
        return plugin  # this is not None
    # continue the async unloading after this functions returns
    fut = plugin._new_load_future()

    async def new_unloader():
        try:
            for f in async_unloaders:
                await f()
        except Exception as e:
            nonlocal error
            error = True
            logger.error(f'Failed to run unloading hooks when unloading '
                         f'"{module_path}" asynchronously, error: {e}.'
                         'Remaining hooks are not continued.')
            logger.exception(e)
        after_cbs()
        fut_result = kont() if kont is not None else None
        # if reloading and fast, the newly loaded identical plugin will overrule the
        # existing future, and one should not set result here
        if kont is None or not fast:
            fut.set_result(fut_result)

    _run_async_func_by_environ(new_unloader)
    return plugin


def unload_plugin(module_path: str, fast: bool = False) -> Optional[Plugin]:
    """
    卸载插件，即移除插件的 commands, nlprocessors, event handlers 和 message preprocessors，运行由 `on_plugin('unloaded')` 注册的函数（下称 「卸载回调」），并将已导入的模块移除。

    :::danger
    该函数为强制卸载，如果使用不当，可能导致不可预测的错误！（如引用已经被移除的模块变量）

    此函数不会回滚已导入模块中产生过的其他副作用（比如已计划的任务，aiocqhttp 中注册的处理器等）。
    :::

    版本: 1.9.0+

    参数:
        module_path: 模块路径
        fast {version}`1.9.1+`: 若此参数为 `True`，则卸载时将不会移除已导入的模块。当未来的 `load_plugin` 调用将加载相同的插件时，将不会重新导入相应模块而是复用。

    返回:
        Optional[Plugin]: 执行卸载后遗留的 `Plugin` 对象，或 `None` 如果插件不存在。根据插件组成不同，`Plugin` 返回值包含如下情况:
            - 插件没有定义卸载回调，或只定义了同步的卸载回调：此函数会卸载处理器并执行回调，在卸载完毕后返回遗留的插件对象，其可以被 await，行为为直接返回此插件本身（也就是可以不 await）。
            - 插件定义了异步卸载回调，但 `unload_plugin` 是在 NoneBot 启动前调用的：此函数会阻塞地运行异步函数，其余表现和上一致
            - 插件定义了异步卸载回调，但 `unload_plugin` 是在异步的情况下调用的（比如在 NoneBot 运行的事件循环中）：此函数会卸载处理器并执行部分同步的卸载回调，返回遗留的插件对象。此对象可以被 await，行为为等待剩余的异步卸载回调执行完毕然后返回此插件本身。
            - 在此之后此返回值将不再有用

    用法:
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
    """
    return _unload_plugin(module_path, fast, None)


def reload_plugin(module_path: str, fast: bool = False) -> Optional[Plugin]:
    """
    重载插件，也就是先 `unload_plugin`，再 `load_plugin`，期间等待相应回调执行完毕。

    :::danger
    该函数为强制重载，如果使用不当，可能导致不可预测的错误！
    :::

    版本: 1.6.0+

    参数:
        module_path: 模块路径
        fast {version}`1.9.1+`: 若此参数为 `True`，则卸载时将不会移除已导入的模块，加载时将不会重新导入相应模块而是复用。
            :::tip
            在 1.9.1 后，建议使用 `fast=True`。此参数的默认值 `False` 是由于历史原因。
            :::

    返回:
        Optional[Plugin]: 重载后生成的 Plugin 对象。根据插件组成不同，返回值包含如下情况:
            - 插件没有定义或只定义了同步的加载/卸载回调（此为 1.9.0 前的唯一情况）: 此函数会执行两个步骤的回调，在重载完毕后返回新的插件对象，其可以被 await，行为为直接返回插件本身（也就是可以不 await）。如果发生异常，则返回 `None`
            - 插件定义了异步的回调，但 `reload_plugin` 是在 NoneBot 启动前调用的: 此函数会阻塞地运行异步函数，其余表现和上一致
            - 插件定义了异步的回调，但 `reload_plugin` 是在异步的情况下调用的（比如在 NoneBot 运行的事件循环中）: 此函数会卸载处理器并执行部分同步的卸载回调，返回遗留的插件对象。返回值可以被 await，行为为等待剩余的异步卸载完毕并且加载新插件完毕后然后返回新的插件对象，或如果在 await 中发生了错误，返回 `None`

    用法:
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
    """
    # NOTE: consider importlib.reload()
    return _unload_plugin(module_path, fast,
        lambda: _load_plugin(module_path, 'reload', False, fast))


def load_plugins(plugin_dir: str,
                 module_prefix: str,
                 no_fast: bool = False) -> Set[Plugin]:
    """
    查找指定路径（相对或绝对）中的非隐藏模块（隐藏模块名字以 `_` 开头）并通过指定的模块前缀导入。其返回值的表现与 `load_plugin` 一致。

    参数:
        plugin_dir: 插件目录
        module_prefix: 模块前缀
        no_fast {version}`1.9.1+`: 若此参数为 `True`，则无视 `unload_plugin` 中的 `fast` 选项而强制重新导入模块

    返回 (1.6.0+):
        Set[Plugin]: 加载成功的 Plugin 对象

    用法:
        ```python
        nonebot.plugin.load_plugins(path.join(path.dirname(__file__), 'plugins'), 'plugins')
        ```

        加载 `plugins` 目录下的插件。
    """

    count = set()
    for name in os.listdir(plugin_dir):
        path = os.path.join(plugin_dir, name)
        if os.path.isfile(path) and \
                (name.startswith('_') or not name.endswith('.py')):
            continue
        if os.path.isdir(path) and \
                (name.startswith('_') or not os.path.exists(
                    os.path.join(path, '__init__.py'))):
            continue

        m = re.match(r'([_A-Z0-9a-z]+)(.py)?', name)
        if not m:
            continue

        result = load_plugin(f'{module_prefix}.{m.group(1)}', no_fast)
        if result:
            count.add(result)
    return count


def load_builtin_plugins() -> Set[Plugin]:
    """
    加载内置插件。

    返回 (1.6.0+):
        Set[Plugin]: 加载成功的 Plugin 对象

    用法:
        ```python
        nonebot.plugin.load_builtin_plugins()
        ```
    """
    plugin_dir = os.path.join(os.path.dirname(__file__), 'plugins')
    return load_plugins(plugin_dir, 'nonebot.plugins')


def get_loaded_plugins() -> Set[Plugin]:
    """
    获取已经加载的插件集合。

    返回:
        Set[Plugin]: 已加载的插件集合

    用法:
        ```python
        plugins = nonebot.plugin.get_loaded_plugins()
        await session.send('我现在支持以下功能：\\n\\n' +
                            '\\n'.join(map(lambda p: p.name, filter(lambda p: p.name, plugins))))
        ```
    """
    return set(PluginManager._plugins.values())


def on_plugin(timing: str) -> Callable[[PluginLifetimeHook_T], PluginLifetimeHook_T]:
    """
    将函数设置为插件生命周期的回调函数。注册的加载回调会在调用 `load_plugin` 时被调用，注册的卸载回调会在调用 `unload_plugin` 时被调用。

    版本: 1.9.0+

    要求:
        被装饰函数可为同步或异步（async def）函数，必须不接受参数，其返回值会被忽略:

        ```python
        def func():
            pass

        async def func():
            pass
        ```

        被 `on_plugin('unloaded')` 装饰的函数必须不能抛出 `Exception`，否则卸载时的行为将不能保证。

    参数:
        timing: `"loading"` 表示注册加载回调，`"unloaded"` 表示注册卸载回调

    用法:
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
    """
    def deco(func: PluginLifetimeHook_T):
        if Plugin.GlobalTemp.now_within_plugin:
            hk = LifetimeHook(func, timing)
            Plugin.GlobalTemp.lifetime_hooks.append(hk)
        else:
            raise RuntimeError('Cannot register a lifetime hook outside a plugin')
        return func

    return deco


def on_command(
    name: Union[str, CommandName_T],
    *,
    aliases: Union[Iterable[str], str] = (),
    patterns: Patterns_T = (),
    permission: Union[PermissionPolicy_T, Iterable[PermissionPolicy_T]] = ...,
    only_to_me: bool = True,
    privileged: bool = False,
    shell_like: bool = False,
    expire_timeout: Optional[timedelta] = ...,
    run_timeout: Optional[timedelta] = ...,
    session_class: Optional[Type[CommandSession]] = None
) -> Callable[[CommandHandler_T], CommandHandler_T]:
    """
    将函数装饰为命令处理器 `CommandHandler_T` 。

    被装饰的函数将会获得一个 `args_parser` 属性，是一个装饰器，下面会有详细说明。

    版本: 1.6.0+

    要求:
        被装饰函数必须是一个 async 函数，且必须接收且仅接收一个位置参数，类型为 `CommandSession`，即形如:

        ```python
        async def func(session: CommandSession):
            pass
        ```

    参数:
        name: 命令名，如果传入的是字符串则会自动转为元组
        aliases: 命令别名
        patterns {version}`1.7.0+`: 正则匹配，可以传入正则表达式或正则表达式组，来对整条命令进行匹配
            :::warning 注意
            滥用正则表达式可能会引发性能问题，请优先使用普通命令。另外一点需要注意的是，由正则表达式匹配到的匹配到的命令，`session` 中的 `current_arg` 会是整个命令，而不会删除匹配到的内容，以满足一些特殊需求。
            :::
        permission {version}`1.9.0+`: 命令所需要的权限，不满足权限的用户将无法触发该命令。若提供了多个，则默认使用 `aggregate_policy` 和其默认参数组合。如果不传入该参数（即为默认的 `...`），则使用配置项中的 `DEFAULT_COMMAND_PERMISSION`
        only_to_me: 是否只响应确定是在和「我」（机器人）说话的命令（在开头或结尾 @ 了机器人，或在开头称呼了机器人昵称）
        privileged: 是否特权命令，若是，则无论当前是否有命令会话正在运行，都会运行该命令，但运行不会覆盖已有会话，也不会保留新创建的会话
        shell_like: 是否使用类 shell 语法，若是，则会自动使用 `shlex` 模块进行分割（无需手动编写参数解析器），分割后的参数列表放入 `session.args['argv']`
        expire_timeout {version}`1.8.2+`: 命令过期时间。如果不传入该参数（即为默认的 `...`），则使用配置项中的 `SESSION_EXPIRE_TIMEOUT`，如果提供则使用提供的值。
        run_timeout {version}`1.8.2+`: 命令会话的运行超时时长。如果不传入该参数（即为默认的 `...`），则使用配置项中的 `SESSION_RUN_TIMEOUT`，如果提供则使用提供的值。
        session_class {version}`1.7.0+`: 自定义 `CommandSession` 子类，若传入此参数，则命令处理函数的参数 `session` 类型为 `session_class`

    用法:
        ```python
        @on_command('echo', aliases=('复读',), permission=lambda sender: sender.is_superuser)
        async def _(session: CommandSession):
            await session.send(session.current_arg)
        ```

        一个仅对超级用户生效的复读命令。

    属性:
        args_parser:
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
    """
    real_permission = perm.aggregate_policy(permission) \
        if isinstance(permission, Iterable) else permission

    def deco(func: CommandHandler_T) -> CommandHandler_T:
        if not isinstance(name, (str, tuple)):
            raise TypeError('the name of a command must be a str or tuple')
        if not name:
            raise ValueError('the name of a command must not be empty')
        if session_class is not None and not issubclass(session_class,
                                                        CommandSession):
            raise TypeError(
                'session_class must be a subclass of CommandSession')

        cmd_name = (name,) if isinstance(name, str) else name

        cmd = Command(name=cmd_name,
                      func=func,
                      only_to_me=only_to_me,
                      privileged=privileged,
                      permission=real_permission,
                      expire_timeout=expire_timeout,
                      run_timeout=run_timeout,
                      session_class=session_class)

        if shell_like:

            async def shell_like_args_parser(session: CommandSession):
                session.state['argv'] = shlex.split(session.current_arg) if \
                    session.current_arg else []

            cmd.args_parser_func = shell_like_args_parser

        if Plugin.GlobalTemp.now_within_plugin:
            Plugin.GlobalTemp.commands.append((cmd, aliases, patterns))
        else:
            CommandManager.add_command(cmd_name, cmd)
            CommandManager.add_aliases(aliases, cmd)
            CommandManager.add_patterns(patterns, cmd)
            warnings.warn('defining command_handler outside a plugin is deprecated '
                          'and will not be supported in the future')

        func.args_parser = cmd.args_parser

        return func

    return deco


@overload
def on_natural_language(__func: NLPHandler_T) -> NLPHandler_T:
    """
    参数:
        __func: 待装饰函数

    返回:
        NLPHandler_T: 被装饰函数
    """


@overload
def on_natural_language(
    keywords: Optional[Union[Iterable[str], str]] = ...,
    *,
    permission: Union[PermissionPolicy_T, Iterable[PermissionPolicy_T]] = ...,
    only_to_me: bool = ...,
    only_short_message: bool = ...,
    allow_empty_message: bool = ...
) -> Callable[[NLPHandler_T], NLPHandler_T]:
    """
    参数:
        keywords: 要响应的关键词，若传入 `None`，则响应所有消息
        permission {version}`1.9.0+`: 自然语言处理器所需要的权限，不满足权限的用户将无法触发该处理器。若提供了多个，则默认使用 `aggregate_policy` 和其默认参数组合。如果不传入该参数（即为默认的 `...`），则使用配置项中的 `DEFAULT_NLP_PERMISSION`
        only_to_me: 是否只响应确定是在和「我」（机器人）说话的消息（在开头或结尾 @ 了机器人，或在开头称呼了机器人昵称）
        only_short_message: 是否只响应短消息
        allow_empty_message: 是否响应内容为空的消息（只有 @ 或机器人昵称）
    """


def on_natural_language(
    keywords: Union[Optional[Iterable[str]], str, NLPHandler_T] = None,
    *,
    permission: Union[PermissionPolicy_T, Iterable[PermissionPolicy_T]] = ...,
    only_to_me: bool = True,
    only_short_message: bool = True,
    allow_empty_message: bool = False
):
    """
    将函数装饰为自然语言处理器。

    版本: 1.6.0+

    要求:
        被装饰函数必须是一个 async 函数，且必须接收且仅接收一个位置参数，类型为 `NLPSession`，即形如:

        ```python
        async def func(session: NLPSession):
            pass
        ```

    用法:
        ```python
        @on_natural_language({'天气'}, only_to_me=False)
        async def _(session: NLPSession):
            return IntentCommand('weather', 100.0)
        ```

        响应所有带有「天气」关键词的消息，当做 `weather` 命令处理。

        如果有多个自然语言处理器同时处理了一条消息，则置信度最高的 `IntentCommand` 会被选择。处理器可以返回 `None`，表示不把消息当作任何命令处理。
    """
    real_permission = perm.aggregate_policy(permission) \
        if isinstance(permission, Iterable) else permission

    def deco(func: NLPHandler_T) -> NLPHandler_T:
        nl_processor = NLProcessor(
            func=func,
            keywords=keywords,  # type: ignore
            only_to_me=only_to_me,
            only_short_message=only_short_message,
            allow_empty_message=allow_empty_message,
            permission=real_permission)

        if Plugin.GlobalTemp.now_within_plugin:
            Plugin.GlobalTemp.nl_processors.add(nl_processor)
        else:
            NLPManager.add_nl_processor(nl_processor)
            warnings.warn('defining nl_processor outside a plugin is deprecated '
                          'and will not be supported in the future')
        return func

    if callable(keywords):
        # here "keywords" is the function to be decorated
        # applies default args provided by this function
        return on_natural_language()(keywords)
    else:
        if isinstance(keywords, str):
            keywords = (keywords,)
        return deco


_Teh = TypeVar('_Teh', NoticeHandler_T, RequestHandler_T)


def _make_event_deco(post_type: str):

    def deco_deco(arg: Optional[Union[str, _Teh]] = None,
                  *events: str) -> Union[Callable[[_Teh], _Teh], _Teh]:

        def deco(func: _Teh) -> _Teh:
            if isinstance(arg, str):
                events_tmp = list(
                    map(lambda x: f"{post_type}.{x}", [arg, *events]))  # if arg is part of events str
                handler = EventHandler(events_tmp, func)
            else:
                handler = EventHandler([post_type], func)

            if Plugin.GlobalTemp.now_within_plugin:
                Plugin.GlobalTemp.event_handlers.add(handler)
            else:
                EventManager.add_event_handler(handler)
                warnings.warn('defining event_handler outside a plugin is deprecated '
                              'and will not be supported in the future')
            return func

        if callable(arg):
            return deco(arg)
        return deco

    return deco_deco


@overload
def on_notice(__func: NoticeHandler_T) -> NoticeHandler_T: ...  # type: ignore


@overload
def on_notice(*events: str) -> Callable[[NoticeHandler_T], NoticeHandler_T]:
    """
    参数:
        events: 要处理的通知类型（`notice_type`），若不传入，则处理所有通知
    """


on_notice = _make_event_deco('notice')  # type: ignore[override]
on_notice.__doc__ = """
将函数装饰为通知处理器。

版本: 1.6.0+

要求:
    被装饰函数必须是一个 async 函数，且必须接收且仅接收一个位置参数，类型为 `NoticeSession`，即形如:

    ```python
    async def func(session: NoticeSession):
        pass
    ```

用法:
    ```python
    @on_notice
    async def _(session: NoticeSession):
        logger.info('有新的通知事件：%s', session.event)

    @on_notice('group_increase')
    async def _(session: NoticeSession):
        await session.send('欢迎新朋友～')
    ```

    收到所有通知时打日志，收到新成员进群通知时除了打日志还发送欢迎信息。
"""


@overload
def on_request(__func: RequestHandler_T) -> RequestHandler_T: ...  # type: ignore


@overload
def on_request(*events: str) -> Callable[[RequestHandler_T], RequestHandler_T]:
    """
    参数:
        events: 要处理的请求类型（`request_type`），若不传入，则处理所有请求
    """


on_request = _make_event_deco('request')  # type: ignore[override]
on_request.__doc__ = """
将函数装饰为请求处理器。

版本: 1.6.0+

要求:
    被装饰函数必须是一个 async 函数，且必须接收且仅接收一个位置参数，类型为 `RequestSession`，即形如:

    ```python
    async def func(session: RequestSession):
        pass
    ```

用法:
    ```python
    @on_request
    async def _(session: RequestSession):
        logger.info('有新的请求事件：%s', session.event)

    @on_request('group')
    async def _(session: RequestSession):
        await session.approve()
    ```

    收到所有请求时打日志，收到群请求时除了打日志还同意请求。
"""


__all__ = [
    'Plugin',
    'PluginManager',
    'load_plugin',
    'unload_plugin',
    'reload_plugin',
    'load_plugins',
    'load_builtin_plugins',
    'get_loaded_plugins',
    'on_plugin',
    'on_command',
    'on_natural_language',
    'on_notice',
    'on_request',
]

__autodoc__ = {
    "Plugin.__await__": True
}
