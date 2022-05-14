import miraicle
import codecs
import re
from plugins import *


def get_value(key):
    f = codecs.open(r'setting.yml', 'r', 'utf-8')
    lines = f.readlines()
    regex = '.*' + key + '[:]'
    for line in lines:
        if re.match(regex, line):
            value = line.split(':')[1].strip()
            return ''.join(value)
    f.close()


qq = int(get_value('qq'))
verify_key = get_value('verifyKey')
port = int(get_value('port'))


@miraicle.MiraiCode
def friend_invite(bot: miraicle.Mirai, msg: miraicle.FriendMessage, event: miraicle.MiraiCode):
    var = event
    print(var, '这就是街舞')


bot = miraicle.Mirai(qq=qq, verify_key=verify_key, port=port)
bot.set_filter(miraicle.GroupSwitchFilter(r'config\group_switch.json'))
bot.run()
