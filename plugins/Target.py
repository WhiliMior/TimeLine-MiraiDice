import miraicle
import re
import codecs
import random
import os


def check_string(re_exp, str):
    res = re.search(re_exp, str, re.I)
    if res:
        return True
    else:
        return False


reg_exp = '^([.]|[。])ta[r]?.*'


@miraicle.Mirai.receiver('GroupMessage')
def target_to_group(bot: miraicle.Mirai, msg: miraicle.GroupMessage):
    message_check = check_string(reg_exp, msg.plain)
    if message_check:
        pattern = re.compile(r'-?[0-9]+[.]?[0-9]*')
        quantity = len(re.findall(pattern, msg.plain))
        file_name = 'group_target_' + str(msg.group)
        number_list = pattern.findall(msg.plain)
        value_name = '目标数值'

        # 写入数值
        def replace_value(attribute, value):
            f = codecs.open(r'data\%s.txt' % file_name, 'w', 'utf-8')
            f.write(attribute + value)
            f.close()

        def read_attribute_group(element):
            file_name = 'group_target_' + str(msg.group)
            if os.path.exists(r'data\%s.txt' % file_name) is False:
                return None
            else:
                f = codecs.open(r'data\%s.txt' % file_name, 'r', 'utf-8')
                lines = f.readlines()
                for line in lines:
                    if element in line:
                        reg_ex = '-?[0-9]{1,}[.]?[0-9]*'
                        check = check_string(reg_ex, line)
                        if check:
                            # 输出一个只包含单个属性数字的列表，然后转换成str
                            return float(''.join(re.findall(reg_ex, line)))
                        else:
                            return float(0)
                f.close()

        # 处理数字
        def str_number(number):
            return str(format(number, '.0f'))

        if check_string(r'd', msg.plain) and quantity == 1:
            random_number = random.randint(1, 20)
            target_value = random_number * float(''.join(number_list))
            target_value = str_number(target_value)
            replace_value(value_name, target_value)
            send = '已设定目标数值为' + target_value
        elif quantity == 1:
            target_value = float(''.join(number_list))
            target_value = str_number(target_value)
            replace_value(value_name, target_value)
            send = '已设定目标数值为' + target_value
        elif quantity == 2:
            target_value_1 = float(number_list[0])
            target_value_2 = float(number_list[1])
            target_value = target_value_1 * target_value_2
            target_value = str_number(target_value)
            replace_value(value_name, target_value)
            send = '已设定目标数值为' + target_value
        elif quantity == 0:
            target_value = read_attribute_group('目标数值')
            if os.path.exists(r'data\%s.txt' % file_name) is False or target_value is None:
                send = '未设定目标数值！'
            else:
                send = '目标数值为：' + str_number(target_value)
        else:
            send = '请正确输入.ta指令！'

        bot.send_group_msg(group=msg.group, msg=send)


@miraicle.Mirai.receiver('FriendMessage')
def target_to_friend(bot: miraicle.Mirai, msg: miraicle.FriendMessage):
    message_check = check_string(reg_exp, msg.plain)
    if message_check:
        send = '目标数值指令仅在群聊使用！'

        bot.send_friend_msg(qq=msg.sender, msg=[miraicle.Plain(send)])
