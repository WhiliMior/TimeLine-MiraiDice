import math
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


reg_exp = '^([.]|[。])ne[g]?.*'


@miraicle.Mirai.receiver('GroupMessage')
def negotiation_to_group(bot: miraicle.Mirai, msg: miraicle.GroupMessage):
    message_check = check_string(reg_exp, msg.plain)
    if message_check:
        pattern = re.compile(r'-?[0-9]+[.]?[0-9]*')
        quantity = len(re.findall(pattern, msg.plain))
        file_name = 'group_negotiation_' + str(msg.group)
        number_list = pattern.findall(msg.plain)
        target_level_name = '交涉对象等级'
        target_intelligence_name = '交涉对象智力'

        # 写入数值,attribute应为list
        def write_value(attributes):
            f = codecs.open(r'data\%s.txt' % file_name, 'w', 'utf-8')
            for line in attributes:
                f.write('%s\n' % line)
            f.close()

        # 处理数字
        def str_number(number):
            return str(format(number, '.0f'))

        def int_number(number):
            return int(format(number, '.0f'))

        # 写入等级和智力
        def write_target_attribute(number1, number2):
            target_level = str_number(float(number1))
            target_intelligence = str_number(float(number2))
            content = [target_level_name + target_level, target_intelligence_name + target_intelligence]
            write_value(content)

        # 查找属性数值
        def read_attribute(element):
            file_name = str(msg.sender)
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

        # 读取目标数值数据
        def read_attribute_target(element):
            file_name = 'group_negotiation_' + str(msg.group)
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

        # 提取中文属性
        def read_chinese_attribute(element):
            file_name = str(msg.sender)
            if os.path.exists(r'data\%s.txt' % file_name) is False:
                return None
            else:
                f = codecs.open(r'data\%s.txt' % file_name, 'r', 'utf-8')
                lines = f.readlines()
                for line in lines:
                    if element in line:
                        return ''.join(line.split(element)).strip()
                f.close()

        # 给出默认分数0
        rp_grade = 0
        if quantity == 3:
            rp_grade = float(number_list[0])
            write_target_attribute(number_list[1], number_list[2])
        elif quantity == 2:
            write_target_attribute(number_list[0], number_list[1])
        elif quantity == 1:
            rp_grade = float(number_list[0])

        # 检查是否有数据
        if os.path.exists(r'data\%s.txt' % file_name) is False \
                or read_attribute_target(target_level_name) is None \
                or read_attribute_target(target_intelligence_name) is None:
            send = '没有交涉对象！'
        elif read_attribute('交涉加成') is None or read_attribute('等级') is None:
            if quantity == 3:
                send = '已设定交涉对象，但没有导入数据！'
            elif quantity == 2:
                send = '已设定交涉对象！'
            elif quantity == 1:
                send = '没有导入数据！'
        else:
            negotiation_buff = read_attribute('交涉加成')
            target_level = read_attribute_target(target_level_name)
            target_intelligence = read_attribute_target(target_intelligence_name)
            level = read_attribute('等级')
            success_rate = int_number(((rp_grade + negotiation_buff) / target_intelligence * 10)
                                      * (math.log(level / target_level, math.e) + 1))
            random_number = random.randint(1, 100)

            if random_number > success_rate:
                check_result = '失败！'
            else:
                check_result = '成功！'

            character_name = read_chinese_attribute('姓名')

            if quantity == 3 or quantity == 1:
                send = character_name + '进行交涉检定' + '\n' + \
                       'RP：' + str_number(rp_grade) + '\n' + \
                       '成功率：' + str_number(success_rate) + '%' + '\n' + \
                       '检定：' + str(random_number) + '/' + str(success_rate) + '\n' + \
                       check_result
            elif quantity == 2:
                send = '已设定交涉对象！'
            else:
                send = '请正确输入.ne指令！'

        bot.send_group_msg(group=msg.group, msg=send, quote=msg.id)

@miraicle.Mirai.receiver('FriendMessage')
def negotiation_to_friend(bot: miraicle.Mirai, msg: miraicle.FriendMessage):
    message_check = check_string(reg_exp, msg.plain)
    if message_check:
        send = '交涉指令仅在群聊使用！'

        bot.send_friend_msg(qq=msg.sender, msg=[miraicle.Plain(send)])