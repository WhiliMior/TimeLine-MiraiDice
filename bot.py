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

bot = miraicle.Mirai(qq=qq, verify_key=verify_key, port=port)
bot.set_filter(miraicle.GroupSwitchFilter(r'config\group_switch.json'))
bot.run()
