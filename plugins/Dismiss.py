import miraicle
import re

"""
.dismiss 退群
"""


def check_string(re_exp, str):
    res = re.search(re_exp, str, re.I)
    if res:
        return True
    else:
        return False


reg_exp = '^(\\[(.*?)\\]\\s)?([.]|[。])dismiss.*'


@miraicle.Mirai.filter('GroupSwitchFilter')
def group_dismiss(bot: miraicle.Mirai, msg: miraicle.GroupMessage, flt: miraicle.GroupSwitchFilter):
    message_check = check_string(reg_exp, msg.plain)
    if message_check:
        if check_string("\\[(.*?)\\]", msg.text):
            if msg.at_me():
                bot.quit(msg.group)
            else:
                pass
        else:
            bot.quit(msg.group)


@miraicle.Mirai.receiver('FriendMessage')
def group_dismiss_to_friend(bot: miraicle.Mirai, msg: miraicle.FriendMessage):
    message_check = check_string(reg_exp, msg.plain)
    if message_check:
        send = '请在群聊中使用'
        bot.send_friend_msg(qq=msg.sender, msg=[miraicle.Plain(send)])
