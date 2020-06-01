"""
在 http://127.0.0.1:8080/debug 开启一个输入台
"""
import logging

from quart import request
from aiocqhttp import Event
from aiocqhttp.message import Message

import nonebot
from nonebot.message import handle_message

nonebot.init()

bot = nonebot.get_bot()

debug_page = '''<!DOCTYPE html>

<head>
  <title>debugger</title>
</head>

<body>
  <form method="POST">
    消息：<input type="text" name="raw_message" value="/ping"><br>
    <input type="radio" name="message_type" value="private" checked>私聊
    <input type="radio" name="message_type" value="group">群聊<br>
    用户id：<input type="text" name="user_id" value="123456789"><br>
    用户名：<input type="text" name="nickname" value="测试员"><br>
    群号：<input type="text" name="group_id" value="987654321"><br>
    群身份：
    <select name="group_role">
      <option value="0">群主</option>
      <option value="1">管理员</option>
      <option value="2">成员</option>
    </select><br>
    <input type="submit" value="发送">
  </form>
  <p>发送后请在命令行查看</p>
</body>'''


@bot.server_app.route('/debug', methods=['GET','POST'])
async def testing():
    if request.method == 'GET':
        return debug_page
    try:
        payload = await request.form
        payload['post_type'] = 'message'
        payload['sub_type'] = 'friend' if payload['message_type'] == 'private' else 'normal'
        payload['message'] = Message(payload['raw_message'])
        payload['self_id'] = 99999
        payload['message_id'] = 66
        event = Event.from_payload(payload)
        await handle_message(bot, event)
    except Exception as e:
        logging.exception(e)
    return '', 204


@nonebot.on_command('ping', no_space=True)
async def ping(session):
    print('pong')
    print(session.current_arg)


bot.run(
    host='127.0.0.1',
    port=8080,
    debug=True,
)
