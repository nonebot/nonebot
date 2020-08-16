# 权限控制

## `permission` 模块

`on_command` 提供了 `permission` 参数来控制谁可以触发该命令。在之前教程的例子里，我们都没有显式地设置这个选项：

```python
# 权限默认为 EVERYBODY，即谁都可以触发这个命令
@on_command('weather', aliases=('天气', '天气预报', '查天气'))
async def weather(session: CommandSession):
    ...
```

`nonebot.permission` 模块提供了权限声明常量。例如如果想要只允许群成员才能触发命令，而私聊无效的话，可以这样：

```python {1-2}
from nonebot.permission import *
@on_command('weather', aliases=('天气', '天气预报', '查天气'), permission=GROUP_MEMBER)
async def weather(session: CommandSession):
    ...
```

除此之外还存在着例如群管理员 (`GROUP_ADMIN`)，超级用户 (`SUPERUSER`) 等设置。这些常量彼此可以通过 `|` 来合并（取联合）。

对于更多的权限声明常量，请参考 [API 文档](https://nonebot.cqp.moe/api.html#%E6%9D%83%E9%99%90%E5%A3%B0%E6%98%8E%E5%B8%B8%E9%87%8F)。

## 当心 NLP 造成的权限泄露！

假设你的机器人仅对超级用户提供可能包含敏感信息的后台命令插件，同时也为其编写了一个自然语言处理器。就像这样：

```python
import os

from nonebot import on_command, CommandSession
from nonebot import on_natural_language, NLPSession, IntentCommand
from nonebot.permission import SUPERUSER


@on_command('upgradesoft', permission=SUPERUSER)
async def _(session: CommandSession):
    os.system('apt update && apt upgrade')
    await session.send('已更新系统软件')


@on_natural_language(keywords={'更新软件'})
async def _(session: NLPSession):
    return IntentCommand(90.0, 'upgradesoft')
```

然而这段代码并不能实现想要的功能。如果一个非超级用户小红在群聊里 at 了机器人并且说出 `'更新软件'`，这个命令仍然会被执行，你的系统软件就这样被别人控制了。

这是因为自然语言处理器也有自己的权限控制系统，默认为 `EVERYBODY`。其会处理所有的消息，并且把匹配的命令分发到 `on_command` 下的函数里。如果想要控制这个行为，需要对这个处理器做出如下改动：

```python {1}
@on_natural_language(keywords={'更新软件'}, permission=SUPERUSER)
async def _(session: NLPSession):
    return IntentCommand(90.0, 'upgradesoft')
```

这样就不会泄露我们的命令权限了。
