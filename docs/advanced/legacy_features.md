# 过时的功能

## session.get() 和参数解析器

在[指南](../guide/command.md#编写真正的内容)中我们提到了我们可以使用 `CommandSession.aget` 来在命令会话中与用户交互，那么为什么它的名字前面有一个 `a` 呢？

因为这代表着 [「异步地取得」](https://github.com/nonebot/nonebot/pull/232)。同样地，在 1.8.0 之前我们普遍使用的是同步的 `get` 方法，例如在那里所提及的天气插件，实现类似的功能我们要使用如下的代码：

```python
from nonebot import on_command, CommandSession


@on_command('weather', aliases=('天气', '天气预报', '查天气'))
async def weather(session: CommandSession):
    # 从会话状态（session.state）中获取城市名称（city），如果当前不存在，则询问用户
    city = session.get('city', prompt='你想查询哪个城市的天气呢？')
    weather_report = await get_weather_of_city(city)
    await session.send(weather_report)


# weather.args_parser 装饰器将函数声明为 weather 命令的参数解析器
# 命令解析器用于将用户输入的参数解析成命令真正需要的数据
@weather.args_parser
async def _(session: CommandSession):
    # 去掉消息首尾的空白符
    stripped_arg = session.current_arg_text.strip()

    if session.is_first_run:
        # 该命令第一次运行（第一次进入命令会话）
        if stripped_arg:
            # 第一次运行参数不为空，意味着用户直接将城市名跟在命令名后面，作为参数传入
            # 例如用户可能发送了：天气 南京
            session.state['city'] = stripped_arg
        return

    if not stripped_arg:
        # 用户没有发送有效的城市名称（而是发送了空白字符），则提示重新输入
        # 这里 session.pause() 将会发送消息并暂停当前会话（该行后面的代码不会被运行）
        session.pause('要查询的城市名称不能为空呢，请重新输入')

    # 如果当前正在向用户询问更多信息（例如本例中的要查询的城市），且用户输入有效，则放入会话状态
    session.state[session.current_key] = stripped_arg


async def get_weather_of_city(city: str) -> str:
    # 这里简单返回一个字符串
    # 实际应用中，这里应该调用返回真实数据的天气 API，并拼接成天气预报内容
    return f'{city}的天气是……'
```

在这里，我们有三个概念需要介绍：`session.get`，会话的状态 (state)，和参数解析器。

```python
@on_command('weather', aliases=('天气', '天气预报', '查天气'))
async def weather(session: CommandSession):
```

首先，`session.get()` 函数调用尝试从当前会话（Session）的状态中获取 `city` 这个参数，**所有的参数和会话中需要暂存的临时数据都被存储在 `session.state` 变量（一个 `dict`）中**，如果发现存在，则直接返回，并赋值给 `city` 变量，而如果 `city` 参数不存在，`session.get()` 会**中断**这次命令处理的流程，并保存当前会话，然后向用户发送 `prompt` 参数的内容。**这里的「中断」，意味着如果当前不存在 `city` 参数，`session.get()` 之后的代码将不会被执行，这是通过抛出异常做到的。**

向用户发送 `prompt` 中的提示之后，会话会进入等待状态，此时我们称之为「当前用户正在 weather 命令的会话中」，当用户再次发送消息时，NoneBot 会唤起这个等待中的会话，并重新执行命令，也就是**从头开始**重新执行上面的这个函数，如果用户在一定时间内都没有再次跟机器人发消息，则会话因超时被关闭。

使用此方式实现交互的命令会同时可选地搭配一个参数解析器：

```python
@weather.args_parser
async def _(session: CommandSession):
```

参数解析器的 `session` 参数和命令处理函数一样，都是当前命令的会话对象。并且，参数解析器会在命令处理函数之前执行，以确保正确解析参数以供后者使用。

上面的例子中，参数解析器会判断当前是否是该会话第一次运行（用户刚发送 `/天气`，触发了天气命令）。如果是，则检查用户触发天气命令时有没有附带参数（即 `stripped_arg` 是否有内容），如果带了参数（例如用户发送了 `/天气 南京`），则把附带的参数当做要查询的城市放进会话状态 `session.state`，以 `city` 作为状态的 key——也就是说，如果用户触发命令时就给出了城市，则命令处理函数中的 `session.get('city')` 就能直接返回结果，而不用提示用户输入。

如果该会话不是第一次运行，那就说明命令处理函数中向用户询问了更多信息，导致会话被中断，并等待用户回复（也就是 `session.get()` 的效果）。这时候需要判断用户输入是不是有效，因为我们已经明确地询问了，如果用户此时发送了空白字符，显然这是没有意义的内容，需要提示用户重新发送。相反，如果有效的话，则直接以 `session.current_key` 作为 key（也就是 `session.get()` 的第一个参数，上例中只有可能是 `city`），将输入内容存入会话状态。

此时，对机器人说话其响应应为：

```bash
> /天气 南京
南京的天气是……

> /天气
你想查询哪个城市的天气呢？
> 南京
南京的天气是……
```

使用此方式编写命令通常比较复杂且需要维持状态机，所以一般我们偏好使用 `aget` 或 `apause`。
