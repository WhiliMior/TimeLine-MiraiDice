import miraicle
import re
import codecs


def get_value(key):
    f = codecs.open(r'setting.yml', 'r', 'utf-8')
    lines = f.readlines()
    regex = '.*' + key + '[:]'
    for line in lines:
        if re.match(regex, line):
            value = line.split(':')[1].strip()
            return ''.join(value)
    f.close()


qq = get_value('qq')


def check_string(re_exp, str):
    res = re.search(re_exp, str, re.I)
    if res:
        return True
    else:
        return False


reg_exp = '^(\\[(.*?)\\]\\s)?([.]|[。])bot.*'


@miraicle.Mirai.filter('GroupSwitchFilter')
def group_switch(bot: miraicle.Mirai, msg: miraicle.GroupMessage, flt: miraicle.GroupSwitchFilter):
    message_check = check_string(reg_exp, msg.text)
    message = ''.join(re.findall('(?<=bot\\s).*$', msg.text, re.I))

    def get_send():
        if check_string(r'on', message):
            flt.enable_all(group=msg.group)
            return "I'm on!"
        elif check_string(r'off', message):
            flt.disable_all(group=msg.group)
            return "I'm off!"
        else:
            return 'Time Line for Mirai' + '\n' + 'in miraicle with Python' + '\n' + 'Beta v22.5.14'

    if message_check:
        if check_string("\\[(.*?)\\]", msg.text):
            at_data = re.findall("\\[(.*?)\\]", msg.text, re.I | re.M)[0]
            if msg.at_me():
                send = get_send()
            else:
                send = ''
        else:
            send = get_send()

        bot.send_group_msg(group=msg.group, msg=send)


@miraicle.Mirai.receiver('FriendMessage')
def group_switch_to_friend(bot: miraicle.Mirai, msg: miraicle.FriendMessage):
    message_check = check_string(reg_exp, msg.plain)
    if message_check:
        send = '请在群聊中使用'
        bot.send_friend_msg(qq=msg.sender, msg=[miraicle.Plain(send)])
