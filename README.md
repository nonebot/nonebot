# NoneBot

[![License](https://img.shields.io/github/license/nonebot/nonebot.svg)](LICENSE)
[![PyPI](https://img.shields.io/pypi/v/nonebot.svg)](https://pypi.python.org/pypi/nonebot)
![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)
![OneBot Version](https://img.shields.io/badge/OneBot-v10,v11-black.svg)
[![QQ 群](https://img.shields.io/badge/qq%E7%BE%A4-768887710-orange.svg)](https://jq.qq.com/?_wv=1027&k=5OFifDh)
[![Telegram 频道](https://img.shields.io/badge/telegram-botuniverse-blue.svg)](https://t.me/botuniverse)
[![Discord Server](https://discordapp.com/api/guilds/847819937858584596/widget.png?style=shield)](https://discord.gg/VKtE6Gdc4h)

## 简介

NoneBot 是一个基于 [OneBot 标准](https://github.com/howmanybots/onebot)（原 CQHTTP） 的 Python 异步 QQ 机器人框架，它会对 QQ 机器人收到的消息进行解析和处理，并以插件化的形式，分发给消息所对应的命令处理器和自然语言处理器，来完成具体的功能。

除了起到解析消息的作用，NoneBot 还为插件提供了大量实用的预设操作和权限控制机制，尤其对于命令处理器，它更是提供了完善且易用的会话机制和内部调用机制，以分别适应命令的连续交互和插件内部功能复用等需求。

NoneBot 在其底层与 OneBot 实现交互的部分使用 [aiocqhttp](https://github.com/nonebot/aiocqhttp) 库，后者在 [Quart](https://pgjones.gitlab.io/quart/) 的基础上封装了与 OneBot 实现的网络交互。

得益于 Python 的 [asyncio](https://docs.python.org/3/library/asyncio.html) 机制，NoneBot 处理消息的吞吐量有了很大的保障，再配合 OneBot 标准的 WebSocket 通信方式（也是最建议的通信方式），NoneBot 的性能可以达到 HTTP 通信方式的两倍以上，相较于传统同步 I/O 的 HTTP 通信，更是有质的飞跃。

需要注意的是，NoneBot 仅支持 Python 3.7+。

## 文档

文档目前「指南」和「API」部分已经完成，「进阶」部分尚未完成，你可以在 [这里](https://docs.nonebot.dev/) 查看。

## 贡献

如果你在使用过程中发现任何问题，可以 [提交 issue](https://github.com/nonebot/nonebot/issues/new) 或自行 fork 修改后提交 pull request。

如果你要提交 pull request，请确保你的代码风格和项目已有的代码保持一致，遵循 [PEP 8](https://www.python.org/dev/peps/pep-0008/)，变量命名清晰，有适当的注释。

# NoneBot

## Description

NoneBot is an asynchronous and [OneBot]((https://github.com/howmanybots/onebot))-compliant QQ robot framework written in Python. When NoneBot receives new messages, it parses the messages then pass them to user-defined command handlers or natural language processors accordingly using a plugin system to accomplish various tasks.

Beside message processing, NoneBot presents an amount of useful built-in actions and permission handling features. The command processors provide simple but comprehensive session-ing and calling mechanisms to handle continuous interactions and the reusing of functionalities inside plugins, respectively.

NoneBot communicates with OneBot implementations using [aiocqhttp](https://github.com/nonebot/aiocqhttp), a wrapper based on [Quart](https://pgjones.gitlab.io/quart/) for lower-level protocol work.

Thanks to [asyncio](https://docs.python.org/3/library/asyncio.html) and WebSocket messaging method (which is recommended), NoneBot ensures maximum possible message throughput to be twice as fast as HTTP messaging, and have great performance leap compared to traditional synchronous IO.

NoneBot only supports Python 3.7+.

## Documentation

For Guide and API manuals, check out [this page](https://docs.nonebot.dev/).

## Contributing

If you encounter any problems in using the project, you can [submit an issue](https://github.com/nonebot/nonebot/issues/new) or fork this project to submit an pull request.

For pull requests, please be sure to have consistent style to existing modules, follow [PEP 8](https://www.python.org/dev/peps/pep-0008/), have clear identifier naming, and have proper comments.
