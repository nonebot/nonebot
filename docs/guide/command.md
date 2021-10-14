# 编写命令

本章将以一个天气查询插件为例，教你如何编写自己的命令。

:::tip 提示
本章的完整代码可以在 [awesome-bot-2](https://github.com/nonebot/nonebot/tree/master/docs/guide/code/awesome-bot-2) 查看。

如果你在寻找对应 1.8.0 版本以下的教程，请参考 [这里](../advanced/legacy_features.md#session-get-和参数解析器)。
:::

## 创建插件目录

首先我们需要创建一个目录来存放插件，这个目录需要满足一些条件才能作为插件目录，首先，我们的代码能够比较容易访问到它，其次，它必须是一个能够以 Python 模块形式导入的路径（后面解释为什么），一个比较好的位置是项目目录中的 `awesome/plugins/`，创建好之后，我们的 `awesome-bot` 项目的目录结构如下：

```
awesome-bot
├── awesome
│   └── plugins
├── bot.py
└── config.py
```

接着在 `plugins` 目录中新建一个名为 `weather.py` 的 Python 文件，暂时留空，此时目录结构如下：

```
awesome-bot
├── awesome
│   └── plugins
│       └── weather.py
├── bot.py
└── config.py
```

## 加载插件

现在我们的插件目录已经有了一个空的 `weather.py`，实际上它已经可以被称为一个插件了，尽管它还什么都没做。下面我们来让 NoneBot 加载这个插件，修改 `bot.py` 如下：

```python {1,10-13}
from os import path

import nonebot

import config

if __name__ == '__main__':
    nonebot.init(config)
    nonebot.load_builtin_plugins()
    nonebot.load_plugins(
        path.join(path.dirname(__file__), 'awesome', 'plugins'),
        'awesome.plugins'
    )
    nonebot.run()
```

这里的重点在于 `nonebot.load_plugins()` 函数的两个参数。第一个参数是插件目录的路径，这里根据 `bot.py` 的所在路径和相对路径拼接得到；第二个参数是导入插件模块时使用的模块名前缀，这个前缀要求必须是一个当前 Python 解释器可以导入的模块前缀，NoneBot 会在它后面加上插件的模块名共同组成完整的模块名来让解释器导入，因此这里我们传入 `awesome.plugins`，当运行 `bot.py` 的时候，Python 解释器就能够正确导入 `awesome.plugins.weather` 这个插件模块了。

尝试运行 `python bot.py`，可以看到日志输出了类似如下内容：

```
[2018-08-18 21:46:55,425 nonebot] INFO: Succeeded to import "awesome.plugins.weather"
```

这表示 NoneBot 已经成功加载到了 `weather` 插件。

:::warning 注意
如果你运行时没有输出成功导入插件的日志，请确保你的当前工作目录是在 `awesome-bot` 项目的主目录中。

如果仍然不行，尝试先在 `awesome-bot` 主目录中执行下面的命令：

```bash
export PYTHONPATH=.  # Linux / macOS
set PYTHONPATH=.  # Windows
```
:::

## 编写真正的内容

好了，现在已经确保插件可以正确加载，我们可以开始编写命令的实际代码了。在 `weather.py` 中添加如下代码：

```python
from nonebot import on_command, CommandSession


# on_command 装饰器将函数声明为一个命令处理器
# 这里 weather 为命令的名字，同时允许使用别名「天气」「天气预报」「查天气」
@on_command('weather', aliases=('天气', '天气预报', '查天气'))
async def weather(session: CommandSession):
    # 取得消息的内容，并且去掉首尾的空白符
    city = session.current_arg_text.strip()
    # 如果除了命令的名字之外用户还提供了别的内容，即用户直接将城市名跟在命令名后面，
    # 则此时 city 不为空。例如用户可能发送了："天气 南京"，则此时 city == '南京'
    # 否则这代表用户仅发送了："天气" 二字，机器人将会向其发送一条消息并且等待其回复
    if not city:
        city = (await session.aget(prompt='你想查询哪个城市的天气呢？')).strip()
        # 如果用户只发送空白符，则继续询问
        while not city:
            city = (await session.aget(prompt='要查询的城市名称不能为空呢，请重新输入')).strip()
    # 获取城市的天气预报
    weather_report = await get_weather_of_city(city)
    # 向用户发送天气预报
    await session.send(weather_report)


async def get_weather_of_city(city: str) -> str:
    # 这里简单返回一个字符串
    # 实际应用中，这里应该调用返回真实数据的天气 API，并拼接成天气预报内容
    return f'{city}的天气是……'
```

:::tip 提示
从这里开始，你需要对 Python 的 asyncio 编程有所了解，因为 NoneBot 是完全基于 asyncio 的，具体可以参考 [廖雪峰的 Python 教程](https://www.liaoxuefeng.com/wiki/0014316089557264a6b348958f449949df42a6d3a2e542c000/00143208573480558080fa77514407cb23834c78c6c7309000)。
:::

为了简单起见，我们在这里的例子中没有接入真实的天气数据，但要接入也非常简单，你可以使用中国天气网、和风天气网、OpenWeatherMap 等网站提供的 API。

上面的代码中基本上每一行做了什么都在注释里写了。我们来实际启动一下 NoneBot，看看输入命令后会发生什么：

```bash
> /天气 南京
南京的天气是……

> /天气
你想查询哪个城市的天气呢？
> 南京
南京的天气是……
```

恭喜，你已经完成了一个**可交互的**天气查询命令的雏形，只需要再接入天气 API 就可以真正投入使用了！

实际上，这里的 `weather` 的函数的逻辑就相当于此代码片段：

```python
city = user_arg.strip()
if city == '':
    city = input('你想查询哪个城市的天气呢？').strip()
    while city == '':
        city = input('要查询的城市名称不能为空呢，请重新输入').strip()
weather_report = ...(city)
print(weather_report)
```

可以看到如果你知道如何编写控制台对话的程序，你就知道如何编写 NoneBot 的命令处理器。再复杂的对话也不过而已。

## 原理

「命令」是 NoneBot 机器人核心组成部分之一。像 [之前讲过的一样](whats-happened.md#命令处理器)，每当用户对机器人发送了一条消息，NoneBot 会尝试将消息匹配到每个命令中。在分别匹配了 `/` 和 `天气` 后，就会进入到我们定义的 `weather` 函数中。

```python
@on_command('weather', aliases=('天气', '天气预报', '查天气'))
async def weather(session: CommandSession):
```

如果这两步中没有匹配到相应命令，那么此消息就会被暂时地忽略掉。通过在配置项中的 `DEBUG`，你可以在运行日志中看到完整的匹配过程。

在进入命令会话后，此时用户发送的消息仅剩了 `南京` 这一部分。这部分文本将会通过 `session.current_arg_text` 表现出来，从而进行下一步的过程直至此函数执行完毕，即命令处理完毕。

如果我们发送的仅仅是 `/天气` 会怎样？此时 `session.current_arg_text` 将不包含任何有意义的内容，即为空串。于是我们使用了 `session.aget` 功能向用户发起提问：

```python
await session.aget(prompt='你想查询哪个城市的天气呢？')
```

当我们调用此方法时，正在进行的命令会话会暂停。当用户又一次向机器人说话时，`aget` 调用将会获得用户此次发送的消息内容，比如 `南京`，**继续执行当前会话。在此期间，机器人将会不被干扰地处理其他消息。**

在这里，我们还对其返回值做了 `.strip()`，处理。这代表如果用户只是发送了显然没有意义的空白字符，我们将重新询问，例如：

```bash
> /天气
你想查询哪个城市的天气呢？
>     
要查询的城市名称不能为空呢，请重新输入
> 南京
南京的天气是……
```

直至成功获取到 `city` 变量并完成命令。此外，如果用户在一定时间内（默认 5 分钟，可通过 `SESSION_EXPIRE_TIMEOUT` 配置项来更改）都没有再次跟机器人发消息，则会话将会因超时被关闭。

:::tip 提示
上面用了 `session.current_arg_text` 来获取用户当前输入的参数，这表示从用户输入中提取纯文本部分，也就是说不包含图片、表情、语音、卡片分享等。

如果需要用户输入的原始内容，请使用 `session.current_arg`，里面可能包含 CQ 码。除此之外，还可以通过 `session.current_arg_images` 获取消息中的图片 URL 列表。

另外一点值得注意的是，`@on_command` 也可以传入正则表达式作为参数 `patterns`，在这种情况下，整条完整的指令会被作为 `session.current_arg` 使用（而不会删除开头匹配到的命令），这点请注意区别。
:::
