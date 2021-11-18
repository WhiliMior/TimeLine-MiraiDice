import miraicle
import re
import codecs
import os


def check_string(re_exp, str):
    res = re.search(re_exp, str, re.I)
    if res:
        return True
    else:
        return False


reg_exp = '^([.]|[。])pr[e]?.*'


@miraicle.Mirai.receiver('GroupMessage')
def preparation_to_group(bot: miraicle.Mirai, msg: miraicle.GroupMessage):
    message_check = check_string(reg_exp, msg.plain)
    if message_check:

        # 通过正则匹配指令后的内容
        pattern = re.compile(r'^(^([.]|[。])pr[ep]?)', re.I)
        attributes = str(pattern.sub('', msg.plain).strip())
        file_name = str(msg.sender)
        pattern_attribute = re.compile(r'[\u4e00-\u9fa5]+')
        pattern_number = re.compile(r'-?[0-9]+[.]?[0-9]*t?', re.I)
        attribute_list = pattern_attribute.findall(attributes)
        number_list = pattern_number.findall(attributes)

        attribute = attribute_list[0]

        # def将特定行中属性提取为数字，查找检定属性
        def read_attribute_check(element):
            if os.path.exists(r'data\%s.txt' % file_name) is False:
                return None
            else:
                f = codecs.open(r'data\%s.txt' % file_name, 'r', 'utf-8')
                lines = f.readlines()
                for line in lines:
                    if element in line and '_检定' in line:
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
            return str(format(number, '.1f'))

        # 将attribute替换为完整名称
        attribute_name = attribute
        f = codecs.open(r'data\%s.txt' % file_name, 'r', 'utf-8')
        lines = f.readlines()
        for line in lines:
            if attribute in line and '_检定' in line:
                attribute_name = line.split('_')[0]
        f.close()

        attribute_value = read_attribute_check(attribute)
        # 判断计算
        if attribute_value is None:
            send = '找不到属性' + '“' + attribute + '”！'
        else:
            if 't' in str(number_list[0]) or 'T' in str(number_list[0]):
                # 去掉t
                time = float(re.sub(r'[tT]', "", str(number_list[0])))
                impact_number = (attribute_value / 20) * time
            else:
                impact_number = float(number_list[0])
                time = (impact_number * 20) / attribute_value

            send = '相关属性：' + attribute_name + '\n' + \
                   '影响数值：' + str_number(impact_number) + '\n' + \
                   '时间：' + str_number(time) + 't'

        bot.send_group_msg(group=msg.group, msg=send, quote=msg.id)


@miraicle.Mirai.receiver('FriendMessage')
def preparation_to_friend(bot: miraicle.Mirai, msg: miraicle.FriendMessage):
    message_check = check_string(reg_exp, msg.plain)
    if message_check:

        # 通过正则匹配指令后的内容
        pattern = re.compile(r'^(^([.]|[。])pr[ep]?)', re.I)
        attributes = str(pattern.sub('', msg.plain).strip())
        file_name = str(msg.sender)
        pattern_attribute = re.compile(r'[\u4e00-\u9fa5]+')
        pattern_number = re.compile(r'-?[0-9]+[.]?[0-9]*t?', re.I)
        attribute_list = pattern_attribute.findall(attributes)
        number_list = pattern_number.findall(attributes)

        attribute = attribute_list[0]

        # def将特定行中属性提取为数字，查找检定属性
        def read_attribute_check(element):
            if os.path.exists(r'data\%s.txt' % file_name) is False:
                return None
            else:
                f = codecs.open(r'data\%s.txt' % file_name, 'r', 'utf-8')
                lines = f.readlines()
                for line in lines:
                    if element in line and '_检定' in line:
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
            return str(format(number, '.1f'))

        # 将attribute替换为完整名称
        f = codecs.open(r'data\%s.txt' % file_name, 'r', 'utf-8')
        lines = f.readlines()
        for line in lines:
            if attribute in line and '_检定' in line:
                attribute_name = line.split('_')[0]
        f.close()

        attribute_value = read_attribute_check(attribute)
        # 判断计算
        if attribute_value is None:
            send = '找不到属性' + '“' + attribute + '”！'
        else:
            if 't' in str(number_list[0]) or 'T' in str(number_list[0]):
                # 去掉t
                time = float(re.sub(r'[tT]', "", str(number_list[0])))
                impact_number = (attribute_value / 20) * time
                send = '相关属性：' + attribute_name + '\n' + \
                       '影响数值：' + str_number(impact_number)
            else:
                impact_number = float(number_list[0])
                time = (impact_number * 20) / attribute_value
                send = '相关属性：' + attribute_name + '\n' + \
                       '时间：' + str_number(time)

        bot.send_friend_msg(qq=msg.sender, msg=[miraicle.Plain(send)])
