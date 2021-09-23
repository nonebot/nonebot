# 权限控制

## `permission` 模块

`on_command` 提供了 `permission` 参数来控制谁可以触发该命令。在之前教程的例子里，我们都没有显式地设置这个选项：

```python
from nonebot import on_command, CommandSession

# 权限默认为 EVERYBODY，即谁都可以触发这个命令
@on_command('weather', aliases=('天气', '天气预报', '查天气'))
async def weather(session: CommandSession):
    ...
```

NoneBot 支持以匿名函数的方式控制谁才可以触发一个命令。例如如果想要只允许群聊才能触发命令，而私聊无效的话，可以这样：

```python {3}
from nonebot import on_command, CommandSession

@on_command('weather', aliases=('天气', '天气预报', '查天气'), permission=lambda sender: sender.is_group_chat)
async def weather(session: CommandSession):
    ...
```

每当用户发送了可能为命令的消息时，NoneBot 会先运行权限检查器根据上下文判断此用户的权限，通过后才会创建相应的命令会话执行命令。

而此权限检查函数的任务很简单：其接受一个代表发消息的人的 `SenderRoles` 对象，当用户满足条件时，就返回 `True`。我们可以操作此对象自由组合构成一个命令的权限：

```python {1}
from nonebot import on_command, CommandSession, SenderRoles

admin_whitelist = {123456789, 987654321}
def admin_permission(sender: SenderRoles):
    return sender.is_groupchat and (sender.is_admin or sender.is_owner or sender.sent_by(admin_whitelist))

# 这里我们用元组的方式定义命令的名字，默认情况下，这表示 "weather.switch"
@on_command(('weather', 'switch'), permission=admin_permission)
async def weather_switch(session: CommandSession):
    ...
```

对于更多的权限检查方式，请参考 [API 文档](https://docs.nonebot.dev/api.html#readonly-property-is-superuser)。

## 操作 `SenderRoles` 中的属性

`SenderRoles` 中包含了发送者发送消息这一事件的事件对象（`aiocqhttp.Event`）对象和接收此消息的机器人对象。我们可以利用这一点在命令会话被创建之前检查权限，如果发送者不具备条件，不仅不能触发命令，而且还向其顺便发送一条失败消息：

```python {26}
import asyncio
from typing import Awaitable
from nonebot import SenderRoles
from nonebot.typing import PermissionPolicy_T

def with_decline_msg(wrapped: PermissionPolicy_T):
    async def _wrapper(sender: SenderRoles):
        result = wrapped(sender)
        if isinstance(result, Awaitable):
            result = await result
        if result:
            return True

        msg = '您没有权限执行此命令~'
        # 直接调用 API 发送群聊或私聊消息
        if sender.is_groupchat:
            asyncio.create_task(sender.bot.send_group_msg(group_id=sender.event.group_id, message=msg))
        else:
            asyncio.create_task(sender.bot.send_private_msg(user_id=sender.event.user_id, message=msg))
        return False

    return _wrapper

# In plugin:

@on_command(('weather', 'switch'), permission=with_decline_msg(admin_permission))
async def weather_switch(session: CommandSession):
    ...
```

我们可以在需要的地方反复使用这个函数。当一个不符合 `admin_permission` 条件的用户对机器人说 "weather.switch" 时，机器人会回复 "您没有权限执行此命令~"。

## 当心 NLP 造成的权限泄露！

假设你的机器人仅对超级用户提供可能包含敏感信息的后台命令插件，同时也为其编写了一个自然语言处理器。就像这样：

```python
import os

from nonebot import on_command, CommandSession
from nonebot import on_natural_language, NLPSession, IntentCommand


@on_command('upgradesoft', permission=lambda s: s.is_superuser)
async def _(session: CommandSession):
    os.system('apt update && apt upgrade')
    await session.send('已更新系统软件')


@on_natural_language(keywords={'更新软件'})
async def _(session: NLPSession):
    return IntentCommand(90.0, 'upgradesoft')
```

然而这段代码并不能实现想要的功能。如果一个非超级用户小红在群聊里 at 了机器人并且说出 `'更新软件'`，这个命令仍然会被执行，你的系统软件就这样被别人控制了。

这是因为自然语言处理器也有自己的权限控制系统，默认为允许所有人。其会处理所有的消息，并且把匹配的命令分发到 `on_command` 下的函数里。如果想要控制这个行为，需要对这个处理器做出如下改动：

```python {1}
@on_natural_language(keywords={'更新软件'}, permission=lambda s: s.is_superuser)
async def _(session: NLPSession):
    return IntentCommand(90.0, 'upgradesoft')
```

这样就不会泄露我们的命令权限了。

## 默认的权限
上面例子中我们提到了命令和 NLP 的默认权限为所有人。这个行为可以被更改，即配置项中的 [`DEFAULT_COMMAND_PERMISSION` 和 ` DEFAULT_NLP_PERMISSION`](https://docs.nonebot.dev/api.html#default-command-permission)。
