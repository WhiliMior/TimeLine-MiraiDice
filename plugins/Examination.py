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


reg_exp = '^([.]|[。])ex.*'


@miraicle.Mirai.receiver('GroupMessage')
def exam_to_group(bot: miraicle.Mirai, msg: miraicle.GroupMessage):
    message_check = check_string(reg_exp, msg.plain)
    if message_check:
        # 提取属性到dict
        player_file = f'data/{str(msg.sender)}/plr_{str(msg.sender)}.csv'
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

            # 通过正则匹配指令后的内容
            pattern = re.compile(r'^(^([.]|[。])ex)', re.I)
            attribute = str(pattern.sub('', msg.plain).strip())

            # def将dict中属性提取为str
            def read_character_attribute(element):
                if element in attribute_dict.keys():
                    return str(attribute_dict[element])
                else:
                    return None

            # def将特定行中属性提取为数字，查找检定属性
            def read_attribute_check(element):
                for key, value in attribute_dict.items():
                    if element in key and '_检定' in key:
                        return float(value)

            folder = f'data/grp_{str(msg.group)}'
            # 创建文件夹
            if not os.path.exists(folder):
                os.makedirs(folder)

            # 读取目标数值数据
            def read_attribute_group(element):
                file_name = f'data/grp_{str(msg.group)}/grp_tar_{str(msg.group)}.txt'
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
                for key, value in attribute_dict.items():
                    if attribute in key and '_检定' in key:
                        attribute = key.split('_')[0]

                # 如果后面找到则会替换
                character_name = read_character_attribute('姓名')

                send = f'{str(character_name)}进行{attribute}检定\n' \
                       f'目标{str(target_value)} 比值{str(check_value)}/{str(target_value * 5)}\n' \
                       f'成功率：{str(success_rate)}%\n' \
                       f'检定：{str(random_number)}/{str(success_rate)} ({ratio})\n' \
                       f'{check_result}'

        bot.send_group_msg(group=msg.group, msg=send, quote=msg.id)


@miraicle.Mirai.receiver('FriendMessage')
def exam_to_friend(bot: miraicle.Mirai, msg: miraicle.FriendMessage):
    message_check = check_string(reg_exp, msg.plain)
    if message_check:
        send = '请在群聊中使用'
        bot.send_friend_msg(qq=msg.sender, msg=[miraicle.Plain(send)])
