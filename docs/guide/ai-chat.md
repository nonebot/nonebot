# 接入腾讯智能对话平台

到目前为止我们已经编写了一个相对完整的天气查询插件，包括命令和自然语言处理器，除此之外，使用同样的方法，还可以编写更多功能的插件。

但这样的套路存在一个问题，如果我们不是专业的 NLP 工程师，开放话题的智能聊天仍然是我们无法自己完成的事情，用户只能通过特定插件所支持的句式来使用相应的功能，当用户试图使用我们暂时没有开发的功能时，我们的机器人显得似乎有些无能为力。

不过还是有解决方案的，市面上有一些提供智能聊天机器人接口的厂商，本章我们以 [腾讯智能对话平台](https://cloud.tencent.com/product/tbp?fromSource=gwzcw.3893390.3893390.3893390&utm_medium=CPC&utm_id=gwzcw.3893390.3893390.3893390) 为例，因为它免费且接入比较简单。

:::tip 提示
本章的完整代码可以在 [awesome-bot-4](https://github.com/nonebot/nonebot/tree/master/docs/guide/code/awesome-bot-4) 查看。
:::

## 注册腾讯智能对话平台

前往 [腾讯智能对话平台](https://cloud.tencent.com/product/tbp?fromSource=gwzcw.3893390.3893390.3893390&utm_medium=CPC&utm_id=gwzcw.3893390.3893390.3893390) 注册账号。注册完成后先放一边，或者如果有兴趣的话，可以阅读腾讯云的 [API 文档](https://cloud.tencent.com/document/api) 了解一下使用方法。

## 编写腾讯智能机器人插件

新建 `awesome/plugins/ai_chat.py` 文件，编写如下内容：

```python
import json
from typing import Optional

from aiocqhttp.message import escape
from nonebot import on_command, CommandSession
from nonebot import on_natural_language, NLPSession, IntentCommand
from nonebot.helpers import render_expression

from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.nlp.v20190408 import nlp_client, models

# 定义无法获取腾讯智能机器人回复时的「表达（Expression）」
EXPR_DONT_UNDERSTAND = (
    '我现在还不太明白你在说什么呢，但没关系，以后的我会变得更强呢！',
    '我有点看不懂你的意思呀，可以跟我聊些简单的话题嘛',
    '其实我不太明白你的意思……',
    '抱歉哦，我现在的能力还不能够明白你在说什么，但我会加油的～'
)


# 注册一个仅内部使用的命令，不需要 aliases
@on_command('ai_chat')
async def ai_chat(session: CommandSession):
    # 获取可选参数，这里如果没有 message 参数，命令不会被中断，message 变量会是 None
    message = session.state.get('message')

    # 通过封装的函数获取腾讯智能机器人机器人的回复
    reply = await call_tencent_bot_api(session, message)
    if reply:
        # 如果调用腾讯智能机器人成功，得到了回复，则转义之后发送给用户
        # 转义会把消息中的某些特殊字符做转换，避免将它们理解为 CQ 码
        await session.send(escape(reply))
    else:
        # 如果调用失败，或者它返回的内容我们目前处理不了，发送无法获取腾讯智能机器人回复时的「表达」
        # 这里的 render_expression() 函数会将一个「表达」渲染成一个字符串消息
        await session.send(render_expression(EXPR_DONT_UNDERSTAND))


@on_natural_language
async def _(session: NLPSession):
    # 以置信度 60.0 返回 ai_chat 命令
    # 确保任何消息都在且仅在其它自然语言处理器无法理解的时候使用 ai_chat 命令
    return IntentCommand(60.0, 'ai_chat', args={'message': session.msg_text})


async def call_tencent_bot_api(session: CommandSession, text: Optional[str]) -> Optional[str]:
    # 调用腾讯智能机器人的 API 获取回复

    if not text:
        return None

    try:
        cred = credential.Credential(session.bot.config.TENCENT_BOT_SECRET_ID, session.bot.config.TENCENT_BOT_SECRET_KEY)
        httpProfile = HttpProfile()
        httpProfile.endpoint = "nlp.tencentcloudapi.com"
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = nlp_client.NlpClient(cred, "ap-guangzhou", clientProfile)

        params = {
            # "Action": "ChatBot",
            # "Version": "2019-04-08",
            # "Region": "ap-guangzhou",
            "Query": text,
        }
        req = models.ChatBotRequest()
        req.from_json_string(json.dumps(params))

        resp = client.ChatBot(req).to_json_string()
        print("response:", resp)
        resp_payload = json.loads(resp)
        return resp_payload.get('Reply')

    except TencentCloudSDKException as err:
        print(err)
        return None
```

上面这段代码比较长，而且有一些新出现的函数和概念，我们后面会慢慢地详解，不过现在先登录腾讯云账户，进入「访问密钥」-「API密钥管理」页面，新建密钥得到 `SecretId` 和 `SecretKey`。

:::warning 注意
注册账号为用户主账号。由于本节内容需要使用腾讯云的密钥，若使用主账号泄露可能造成资产损失，因此建议参照 [最佳实践](https://cloud.tencent.com/document/product/598/10592) 停止使用主账号登录控制台或者使用主账号密钥访问云 API，建议使用子账号进行相关资源操作。建立子账号可以参考 [用户指南](https://cloud.tencent.com/document/product/598/13674)。
:::

然后在 `config.py` 中添加两行：

```python
TENCENT_BOT_SECRET_ID = ''
TENCENT_BOT_SECRET_KEY = ''
```

`TENCENT_BOT_SECRET_ID` 和 `TENCENT_BOT_SECRET_KEY` 的值填腾讯云的「访问密钥」-「API密钥管理」页面提供的 `SecretId` 和 `SecretKey`。

配置完成后来运行 NoneBot，尝试给机器人随便发送一条消息，看看它是不是正确地获取了腾讯智能机器人的回复。

## 理解自然语言处理器

我们先来理解代码中最简单的部分：

```python {3}
@on_natural_language
async def _(session: NLPSession):
    return IntentCommand(60.0, 'ai_chat', args={'message': session.msg_text})
```

根据我们前面一章中已经知道的用法，这里就是直接返回置信度为 60.0 的 `ai_chat` 命令。之所以返回置信度 60.0，是因为自然语言处理器所返回的结果最终会按置信度排序，取置信度最高且大于等于 60.0 的结果来执行。把置信度设为 60.0 可以保证一条消息无法被其它自然语言处理器理解的时候 fallback 到 `ai_chat` 命令。

## 理解腾讯智能机器人接口调用

腾讯智能机器人接口的调用也非常简单，虽然看起来代码挺多，但与 NoneBot 相关的概念并不多，这里只粗略介绍。

```python {8-13,15-22,24-27}
async def call_tencent_bot_api(session: CommandSession, text: Optional[str]) -> Optional[str]:
    # 调用腾讯智能机器人的 API 获取回复

    if not text:
        return None

    try:
        cred = credential.Credential(session.bot.config.TENCENT_BOT_SECRET_ID, session.bot.config.TENCENT_BOT_SECRET_KEY)
        httpProfile = HttpProfile()
        httpProfile.endpoint = "nlp.tencentcloudapi.com"
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = nlp_client.NlpClient(cred, "ap-guangzhou", clientProfile)

        params = {
            # "Action": "ChatBot",
            # "Version": "2019-04-08",
            # "Region": "ap-guangzhou",
            "Query": text,
        }
        req = models.ChatBotRequest()
        req.from_json_string(json.dumps(params))

        resp = client.ChatBot(req).to_json_string()
        print("response:", resp)
        resp_payload = json.loads(resp)
        return resp_payload.get('Reply')

    except TencentCloudSDKException as err:
        print(err)
        return None
```

### 配置 `NlpClient`

第一段高亮部分是根据腾讯智能机器人的文档创建并配置 `NlpClient` 对象，接口请求域名为 `nlp.tencentcloudapi.com`。

第 8 行通过 `session.bot.config` 访问了 NoneBot 的配置对象，`session.bot` 就是当前正在运行的 NoneBot 对象，你在其它任何地方都可以这么用（前提是已经调用过 `nonebot.init()`）。

### 构造请求对象

第二段高亮部分是构造 `ChatBotRequest` 请求对象，完整公共参数列表请参考 [公共请求参数](https://cloud.tencent.com/document/api/271/35487)。

### 发送请求

第三段高亮的代码是发送请求并获取它的回复，具体请参考前面给出的腾讯智能机器人的官方 API 文档，里面详细解释了每个返回字段的含义。

## 理解命令处理器

命令处理器这部分虽然代码比较少，但引入了不少新的概念。

```python {1-2,4-9,14,18,20}
from aiocqhttp.message import escape
from nonebot.helpers import render_expression

EXPR_DONT_UNDERSTAND = (
    '我现在还不太明白你在说什么呢，但没关系，以后的我会变得更强呢！',
    '我有点看不懂你的意思呀，可以跟我聊些简单的话题嘛',
    '其实我不太明白你的意思……',
    '抱歉哦，我现在的能力还不能够明白你在说什么，但我会加油的～'
)


@on_command('ai_chat')
async def ai_chat(session: CommandSession):
    message = session.state.get('message')

    reply = await call_tencent_bot_api(session, message)
    if reply:
        await session.send(escape(reply))
    else:
        await session.send(render_expression(EXPR_DONT_UNDERSTAND))
```

### 可选参数

首先看第 14 行，`session.state.get()` 可用于获取命令的可选参数，也就是说，从 `session.state` 中尝试获取一个参数（还记得 `IntentCommand` 的 `args` 参数内容会全部进入 `CommandSession` 的 `state` 吗），如果没有，返回 `None`，但并不会中断命令的执行。其实这就是 `dict.get()` 方法。

### 消息转义

再看第 18 行，在调用 `session.send()` 之前先对 `reply` 调用了 `escape()`，这个 `escape()` 函数是 `aiocqhttp.message` 模块提供的，用于将字符串中的某些特殊字符进行转义。具体来说，这些特殊字符是 go-cqhttp 看作是 CQ 码的一部分的那些字符，包括 `&`、`[`、`]`、`,`。

CQ 码是 go-cqhttp 用来表示非文本消息的一种表示方法，形如 `[CQ:image,file=ABC.jpg]`。具体的格式规则，请参考 go-cqhttp 帮助中心的 [CQ 码](https://docs.go-cqhttp.org/cqcode/)。

### 发送 Expression

第 20 行使用了 NoneBot 中 Expression 这个概念，或称为「表达」。

Expression 可以是一个 `str`、元素类型是 `str` 的序列（一般为 `list` 或 `tuple`）或返回类型为 `str` 的 `Callable`。

`render_expression()` 函数用于将 Expression 渲染成字符串。它首先判断 Expression 的类型，如果 Expression 是一个序列，则首先随机取其中的一个元素，如果是一个 `Callable`，则调用函数获取返回值。拿到最终的 `str` 类型的 Expression 之后，对它调用 `str.format()` 方法，格式化参数传入 `render_expression()` 函数的命名参数（`**kwargs`），最后返回格式化后的结果。特别地，如果 Expression 是个 `Callable`，在调用它获取返回值的时候，也会传入 `**kwargs`，以便函数根据参数来构造字符串。

你可以通过使用序列或 `Callable` 类型的 Expression 来让机器人的回复显得更加自然，甚至，可以利用更高级的人工智能技术来生成对话。
