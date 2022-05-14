import math
import miraicle
import re
import codecs
import random
import os
import pandas as pd


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
        file_name = f'data/grp_{str(msg.group)}/grp_ngo_{str(msg.group)}.txt'
        number_list = pattern.findall(msg.plain)
        target_level_name = '交涉对象等级'
        target_intelligence_name = '交涉对象智力'

        folder = f'data/grp_{str(msg.group)}'
        # 创建文件夹
        if not os.path.exists(folder):
            os.makedirs(folder)

        player_file = f'data/{str(msg.sender)}/plr_{str(msg.sender)}.csv'

        # 写入数值,attribute应为list
        def write_value(attributes):
            f = codecs.open(file_name, 'w', 'utf-8')
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

        # 提取玩家dict
        if os.path.exists(player_file) is False:
            send = '没有角色！'
        else:
            csv_file = open(player_file, 'r', newline='', encoding='utf-8-sig', errors='ignore')
            player_dataframe = pd.read_csv(csv_file, header=0, sep=',')
            csv_file.close()
            using_index = player_dataframe["using"].idxmax()
            character_code = player_dataframe.at[using_index, 'code']
            character_file = f'data/{str(msg.sender)}/chr_{character_code}.txt'
            f = codecs.open(character_file, 'r+', 'utf-8')
            attribute_dict = eval(f.read())  # 读取的str转换为字典
            f.close()

        # def将dict中属性提取为float
        def read_numeral_attribute(element):
            if element in attribute_dict.keys():
                return float(attribute_dict[element])
            else:
                return None

        # 读取目标数值数据
        def read_attribute_target(element):
            if os.path.exists(file_name) is False:
                return None
            else:
                f = codecs.open(file_name, 'r', 'utf-8')
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

        # def将dict中属性提取为str
        def read_character_attribute(element):
            if element in attribute_dict.keys():
                return str(attribute_dict[element])
            else:
                return None

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
        if os.path.exists(file_name) is False \
                or read_attribute_target(target_level_name) is None \
                or read_attribute_target(target_intelligence_name) is None:
            send = '没有交涉对象！'
        elif read_numeral_attribute('交涉加成') is None or read_numeral_attribute('等级') is None:
            if quantity == 3:
                send = '已设定交涉对象，但没有导入数据！'
            elif quantity == 2:
                send = '已设定交涉对象！'
            elif quantity == 1:
                send = '没有导入数据！'
        else:
            negotiation_buff = read_numeral_attribute('交涉加成')
            target_level = read_attribute_target(target_level_name)
            target_intelligence = read_attribute_target(target_intelligence_name)
            level = read_numeral_attribute('等级')
            success_rate = int_number(((rp_grade + negotiation_buff) / target_intelligence * 10)
                                      * (math.log(level / target_level, math.e) + 1))
            random_number = random.randint(1, 100)

            if random_number > success_rate:
                check_result = '失败！'
            else:
                check_result = '成功！'

            character_name = read_character_attribute('姓名')

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
