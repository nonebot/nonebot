# nonebot.typing

## _var_ `Context_T` <Badge text="1.5.0-" type="error"/>

- **类型:** dict[str, Any]

- **说明:** CQHTTP 上报的事件数据对象的类型

## _var_ `Message_T`

- **类型:** str | dict[str, Any] | list[dict[str, Any]]

- **说明:** 消息对象的类型，通常表示 NoneBot 提供的消息相关接口所支持的类型，`nonebot.message.Message` 也是一个合法的 `Message_T`。

## _var_ `Expression_T`

- **类型:** str | Sequence[str] | (*Any, **Any) -> str <Badge text="1.8.0+"/>

- **说明:** Expression 对象的类型

## _var_ `CommandName_T`

- **类型:** tuple[str, ...]

- **说明:** 命令名称的类型

## _var_ `CommandArgs_T`

- **类型:** dict[str, Any]

- **说明:** 命令参数的类型

## _var_ `CommandHandler_T` <Badge text="1.6.0+"/>

- **类型:** (CommandSession) -> Awaitable[Any] <Badge text="1.8.1+"/>

- **说明:** 命令处理函数

## _var_ `Patterns_T` <Badge text="1.7.0+"/>

- **类型:** Iterable[str] | str | Iterable[Pattern[str]] | Pattern[str] <Badge text="1.8.0+"/>

- **说明:** 正则参数类型，可以是正则表达式或正则表达式组

## _var_ `State_T` <Badge text="1.2.0+"/>

- **类型:** dict[str, Any]

- **说明:** 命令会话的状态（`state` 属性）的类型

## _var_ `Filter_T` <Badge text="1.2.0+"/>

- **类型:** (Any) -> Any | Awaitable[Any]

- **说明:** 过滤器的类型

- **用法**

  ```python
  async def validate(value):
      if value > 100:
          raise ValidateError('数值必须小于 100')
      return value
  ```

## _var_ `PermChecker_T` <Badge text="1.8.0+"/>

- **类型:** (NoneBot, CQEvent) -> Awaitable[bool]

- **说明:** 已弃用

## _var_ `NLPHandler_T` <Badge text="1.8.1+"/>

- **类型:** (NLPSession) -> Awaitable[IntentCommand | None]

- **说明:** 自然语言处理函数

## _var_ `NoticeHandler_T` <Badge text="1.8.1+"/>

- **类型:** (NoticeSession) -> Awaitable[Any]

- **说明:** 通知处理函数

## _var_ `RequestHandler_T` <Badge text="1.8.1+"/>

- **类型:** (RequestSession) -> Awaitable[Any]

- **说明:** 请求处理函数

## _var_ `MessagePreprocessor_T` <Badge text="1.8.1+"/>

- **类型:** (NoneBot, CQEvent, PluginManager) -> Awaitable[Any]

- **说明:** 消息预处理函数

## _var_ `PermissionPolicy_T` <Badge text="1.9.0+"/>

- **类型:** (SenderRoles) -> bool | (SenderRoles) -> Awaitable[bool]

- **说明:** 向命令或自然语言处理器传入的权限检查策略。此类型是一个（同步/异步）函数，接受 `SenderRoles` 作为唯一的参数。此函数返回布尔值，返回 `True` 则表示权限检查通过，可以进行下一步处理（触发命令），反之返回 `False`。

## _var_ `PluginLifetimeHook_T` <Badge text="1.9.0+"/>

- **类型:** () -> Any | () -> Awaitable[Any]

- **说明:** 插件生命周期事件回调函数