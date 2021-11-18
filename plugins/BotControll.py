import miraicle
import re

def check_string(re_exp, str):
    res = re.search(re_exp, str, re.I)
    if res:
        return True
    else:
        return False


reg_exp = '^([.]|[。])bot.*'

@miraicle.Mirai.filter('GroupSwitchFilter')
def group_switch(bot: miraicle.Mirai, msg: miraicle.GroupMessage, flt: miraicle.GroupSwitchFilter):
    message_check = check_string(reg_exp, msg.plain)
    pattern = re.compile(r'^(^([.]|[。])bot)', re.I)
    message = str(pattern.sub('', msg.plain).strip())
    if message_check:
        if check_string(r'on', message):
            flt.enable_all(group=msg.group)
            send = "I'm on!"
        elif check_string(r'off', message):
            flt.disable_all(group=msg.group)
            send = "I'm off!"
        elif message == '':
            send = 'Time Line by 沫 for Mirai' + '\n' + 'in miraicle with Python' + '\n' + 'Beta v21.11.15'

        bot.send_group_msg(group=msg.group, msg=send)
