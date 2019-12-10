import nonebot
from nonebot import get_bot
from quart import request

bot = get_bot()


# example 1: send_private
@bot.server_app.route(path="/webhook/send_private/<qqid>/<yourmsg>/",
                      methods=["GET"])
async def send_private_msg_demo(qqid, yourmsg):
    if not qqid.isdigit():
        return ("qqid must be a integar")
    qqid = int(qqid)
    if qqid < 10000 or qqid > 0xFFFFFFFF:
        return ("invalid qqid")
    try:
        await bot.send_private_msg(user_id=qqid, message=yourmsg)
    except nonebot.exceptions.CQHttpError as e:
        return (str(e))
    else:
        return ("success")

# example 2: notification from github
# get webhook like this: [github webhooks](https://developer.github.com/webhooks/)
@bot.server_app.route(path="/webhook/github/pull_request/", methods=["POST"])
async def github_notification():
    qqid = 123456789  # YOUR QQID HERE
    pr = await request.get_json()
    msg = ("github pull request:\n"
           "a pull request is {} on {} by {}\n"
           "title: {}\n"
           "link: {}").format(
        pr["action"],
        pr["repository"]["name"],
        pr["sender"]["login"],
        pr["pull_request"]["title"],
        pr["pull_request"]["html_url"]
    )
    try:
        await bot.send_private_msg(user_id=qqid, message=msg)
    except nonebot.exceptions.CQHttpError as e:
        return (str(e))
    else:
        return ("success")
