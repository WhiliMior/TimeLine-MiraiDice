import miraicle
import re


def check_string(re_exp, str):
    res = re.search(re_exp, str, re.I)
    if res:
        return True
    else:
        return False


reg_exp = '^([.]|[。])dismiss.*'


@miraicle.Mirai.filter('GroupSwitchFilter')
def group_dismiss(bot: miraicle.Mirai, msg: miraicle.GroupMessage, flt: miraicle.GroupSwitchFilter):
    message_check = check_string(reg_exp, msg.plain)
    if message_check:
        bot.quit(msg.group)
