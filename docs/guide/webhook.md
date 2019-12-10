# 添加Webhook任务

[demo](https://github.com/richardchien/nonebot/blob/master/demo/plugins/webhook_demo.py)

```python
import nonebot

bot = nonebot.getbot()

@bot.server_app.route(path="/webhook/send_private/<qqid>/<yourmsg>/",
                      methods=["GET", "POST"])
async def send_private_msg_demo(qqid, yourmsg):
    qqid = int(qqid)
    # do something you like
    try:
        await bot.send_private_msg(user_id=qqid, message=yourmsg)
    except nonebot.exceptions.CQHttpError:
        return "failed"
    else:
        return "success"
```

注意：此处返回值是返回给网络请求的值

![result](https://s2.ax1x.com/2019/12/10/QB72RS.png)
