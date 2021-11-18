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


reg_exp = '^([.]|[。])ex.*'


@miraicle.Mirai.receiver('GroupMessage')
def exam_to_group(bot: miraicle.Mirai, msg: miraicle.GroupMessage):
    message_check = check_string(reg_exp, msg.plain)
    if message_check:

        # 通过正则匹配指令后的内容
        pattern = re.compile(r'^(^([.]|[。])ex)', re.I)
        attribute = str(pattern.sub('', msg.plain).strip())

        # def将特定行中属性提取为数字，查找检定属性
        def read_attribute_check(element):
            file_name = str(msg.sender)
            if os.path.exists(r'data\%s.txt' % file_name) is False:
                return None
            else:
                f = codecs.open(r'data\%s.txt' % file_name, 'r', 'utf-8')
                lines = f.readlines()
                for line in lines:
                    if element in line and '_检定' in line:
                        reg_ex = '-?[0-9]+[.]?[0-9]*'
                        check = check_string(reg_ex, line)
                        if check:
                            # 输出一个只包含单个属性数字的列表，然后转换成str
                            return float(''.join(re.findall(reg_ex, line)))
                        else:
                            return float(0)
                f.close()

        # 读取目标数值数据
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
        def int_number(number):
            return int(format(number, '.0f'))

        if read_attribute_check(attribute) is None:
            send = '找不到属性' + '“' + attribute + '”！'
        elif read_attribute_group('目标数值') is None:
            send = '未设定目标数值！'
        else:
            # 找到目标数值和属性
            target_value = int_number(read_attribute_group('目标数值'))
            check_value = int_number(read_attribute_check(attribute))
            # 计算成功率并检定
            success_rate = int_number(100 * check_value / (target_value * 5))
            random_number = random.randint(1, 100)
            ratio = format(random_number / success_rate, '.2f')
            if random_number > success_rate:
                check_result = '失败！'
            else:
                check_result = '成功！'

            # 将attribute替换为完整名称
            file_name = str(msg.sender)
            f = codecs.open(r'data\%s.txt' % file_name, 'r', 'utf-8')
            lines = f.readlines()
            for line in lines:
                if attribute in line and '_检定' in line:
                    attribute = line.split('_')[0]
            f.close()

            # 提取玩家角色名
            character_name = msg.sender_name
            # 如果后面找到则会替换
            f = codecs.open(r'data\%s.txt' % file_name, 'r', 'utf-8')
            lines = f.readlines()
            for line in lines:
                if '姓名' in line:
                    character_name = ''.join(line.split('姓名')).strip()
            f.close()

            send = str(character_name) + '进行' + attribute + '检定' + '\n' + \
                '目标' + str(target_value) + ' 检定' + str(check_value) + '/' + str(target_value * 5) + '\n' + \
                '成功率：' + str(success_rate) + '%' + '\n' + \
                '检定：' + str(random_number) + '/' + str(success_rate) + ' (' + ratio + ')' + '\n' + \
                check_result

        bot.send_group_msg(group=msg.group, msg=send, quote=msg.id)


@miraicle.Mirai.receiver('FriendMessage')
def exam_to_friend(bot: miraicle.Mirai, msg: miraicle.FriendMessage):
    message_check = check_string(reg_exp, msg.plain)
    if message_check:

        # 通过正则匹配指令后的内容
        pattern = re.compile(r'^(^([.]|[。])ex)', re.I)
        attribute = str(pattern.sub('', msg.plain).strip())

        file_name = str(msg.sender)

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

        # 读取非检定数据
        def read_attribute(element):
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

        if read_attribute_check(attribute) is None:
            send = '找不到属性' + '”' + attribute + '“'
        else:
            target_value = int(format(read_attribute('等级') * 10, '.0f'))
            check_value = int(format(read_attribute_check(attribute), '.0f'))
            success_rate = int(format(100 * check_value / (target_value * 5), '.0f'))
            random_number = random.randint(1, 100)
            ratio = format(random_number / success_rate, '.2f')
            if random_number > success_rate:
                check_result = '失败！'
            else:
                check_result = '成功！'

            # 将attribute替换为完整名称
            f = codecs.open(r'data\%s.txt' % file_name, 'r', 'utf-8')
            lines = f.readlines()
            for line in lines:
                if attribute in line and '_检定' in line:
                    attribute = line.split('_')[0]
            f.close()

            # 提取玩家角色名
            character_name = msg.sender_name
            # 如果后面找到则会替换
            f = codecs.open(r'data\%s.txt' % file_name, 'r', 'utf-8')
            lines = f.readlines()
            for line in lines:
                if '姓名' in line:
                    character_name = ''.join(line.split('姓名')).strip()
            f.close()

            send = str(character_name) + '进行' + attribute + '检定' + '\n' + \
                   '目标' + str(target_value) + ' 检定' + str(check_value) + '/' + str(target_value * 5) + '\n' + \
                   '成功率：' + str(success_rate) + '%' + '\n' + \
                   '检定：' + str(random_number) + '/' + str(success_rate) + ' (' + ratio + ')' + '\n' + \
                   check_result

        bot.send_friend_msg(qq=msg.sender, msg=[miraicle.Plain(send)])
