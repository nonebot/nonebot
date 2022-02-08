# nonebot.log

提供 logger 对象。

其他任何 "nonebot" 模块都应使用此模块的 "logger" 来打印日志。

## _var_ `logger`

- **类型:** logging.Logger

- **说明:** NoneBot 全局的 logger。

- **用法**

  ```python
  logger.debug('Some log message here')
  ```