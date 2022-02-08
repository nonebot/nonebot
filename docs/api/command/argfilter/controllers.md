# nonebot.command.argfilter.controllers <Badge text="1.3.0+"/>

提供几种常用的控制器。

这些验证器通常需要提供一些参数进行一次调用，返回的结果才是真正的验证器，其中的技巧在于通过闭包使要控制的对象能够被内部函数访问。

## _def_ `handle_cancellation(session)`

- **说明**

  在用户发送 `算了`、`不用了`、`取消吧`、`停` 之类的话的时候，结束当前传入的命令会话（调用 `session.finish()`），并发送配置项 `SESSION_CANCEL_EXPRESSION` 所填的内容。

  如果不是上述取消指令，则将输入原样输出。

- **参数**

  - `session` ([CommandSession](../index.md#class-commandsession-bot-event-cmd-current-arg-args-none)): 要控制的命令会话

- **返回**

  - Unknown