# nonebot.message

## _def_ `message_preprocessor(func)`

- **说明**

  将函数装饰为消息预处理器。

- **要求** <Badge text="1.6.0+"/>

  被装饰函数必须是一个 async 函数，且必须接收且仅接收三个位置参数，类型分别为 [NoneBot](./index.md#class-nonebot-config-object-none) 、 `aiocqhttp.Event` 和 [PluginManager](./plugin.md#class-pluginmanager)，即形如:

  ```python
  async def func(bot: NoneBot, event: aiocqhttp.Event, plugin_manager: PluginManager):
      pass
  ```

- **参数**

  - `func` ([MessagePreprocessor_T](./typing.md#var-messagepreprocessor-t))

- **返回**

  - [MessagePreprocessor_T](./typing.md#var-messagepreprocessor-t): 装饰器闭包

- **用法**

  ```python
  @message_preprocessor
  async def _(bot: NoneBot, event: aiocqhttp.Event, plugin_manager: PluginManager):
      event["preprocessed"] = True

      # 关闭某个插件，仅对当前消息生效
      plugin_manager.switch_plugin("path.to.plugin", state=False)
  ```

  在所有消息处理之前，向消息事件对象中加入 `preprocessed` 字段。

## _class_ `CanceledException(reason)` <Badge text="1.6.0+"/>

- **说明**

  取消消息处理异常

- **要求**

  在消息预处理函数 `message_preprocessor` 中可以选择抛出该异常来阻止响应该消息。

- **参数**

  - `reason`

- **用法**

  ```python
  @message_preprocessor
  async def _(bot: NoneBot, event: aiocqhttp.Event, plugin_manager: PluginManager):
      raise CanceledException(reason)
  ```

## _library-attr_ `Message`

从 `aiocqhttp.message` 模块导入，继承自 `list`，用于表示一个消息。该类型是合法的 `Message_T`。

请参考 [aiocqhttp 文档](https://aiocqhttp.nonebot.dev/module/aiocqhttp/message.html#aiocqhttp.message.Message) 来了解此类的使用方法。

## _library-attr_ `MessageSegment`

从 `aiocqhttp.message` 模块导入，继承自 `dict`，用于表示一个消息段。该类型是合法的 `Message_T`。

请参考 [aiocqhttp 文档](https://aiocqhttp.nonebot.dev/module/aiocqhttp/message.html#aiocqhttp.message.MessageSegment) 来了解此类的使用方法。

更多关于消息段的内容，见 [消息格式](https://github.com/botuniverse/onebot/tree/master/v11/specs/message)。

## _library-attr_ `escape`

- **说明:** 从 `aiocqhttp.message` 模块导入，对字符串进行转义。

- **参数:**

    - `s: str`: 要转义的字符串

    - `escape_comma: bool`: 是否转义英文逗号 `,`

- **返回:**

    - `str`: 转义后的字符串

## _library-attr_ `unescape`

- **说明:** 从 `aiocqhttp.message` 模块导入，对字符串进行去转义。

- **参数:**

    - `s: str`: 要去转义的字符串

- **返回:**

    - `str`: 去转义后的字符串