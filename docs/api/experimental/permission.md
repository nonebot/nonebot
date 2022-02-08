# nonebot.experimental.permission <Badge text="1.8.0+"/>

## _def_ `simple_allow_list(*, user_ids=..., group_ids=..., reverse=False)`

- **说明**

  产生一个对应着白名单的权限检查策略。新的权限检查策略只有在发送者的 QQ 号来自于 `user_ids` 或者群组属于 `group_ids` 时才会返回 `True`。

  推荐使用者查看此函数的实现并尝试书写自己的权限检查器。

- **参数**

  - `user_ids` (Container[int]) <Badge text="1.8.2+"/>: 要加入白名单的 QQ 号们，默认为空

  - `group_ids` (Container[int]) <Badge text="1.8.2+"/>: 要加入白名单的群号们，默认为空

  - `reverse` (bool): 如果为真，则返回值变为黑名单

- **返回**

  - PermissionPolicy_T: 新的权限检查策略

- **用法**

  ```python
  bans_list = simple_allow_list(group_ids={ 123456789, 987654321 }, reverse=True)
  # bans_list(987654321) -> False
  # bans_list(987654322) -> True
  @nonebot.on_command('签到', permission=bans_list)
  async def _(session: CommandSession):
      # 只有不是这两个群的时候才会执行
      ...
  ```

## _def_ `simple_time_range(begin_time, end_time, reverse=False, tz_info=None)`

- **说明**

  产生一个对应着时间白名单的权限检查策略。新的权限检查策略只有在当前时间在 `begin_time` 和 `end_time` 之间时才会返回 `True`。

- **参数**

  - `begin_time` (datetime.time): 起始时间

  - `end_time` (datetime.time): 结束时间

  - `reverse` (bool): 如果为真，则返回值变为黑名单

  - `tz_info` (Any): 传入 `datetime.datetime.now()` 的时区参数

- **返回**

  - PermissionPolicy_T: 新的权限检查策略