import miraicle
import re
import codecs
import os
import pandas as pd


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
        pattern_attribute = re.compile(r'[\u4e00-\u9fa5]+')
        pattern_number = re.compile(r'-?[0-9]+[.]?[0-9]*t?', re.I)
        attribute_list = pattern_attribute.findall(attributes)
        number_list = pattern_number.findall(attributes)

        attribute = attribute_list[0]

        # 查找角色属性
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

            # def将特定行中属性提取为数字，查找检定属性
            def read_attribute_check(element):
                for key, value in attribute_dict.items():
                    if element in key and '_检定' in key:
                        return float(value)

            # 处理数字
            def str_number(number):
                return str(format(number, '.1f'))

            # 将attribute替换为完整名称
            for key, value in attribute_dict.items():
                if attribute in key and '_检定' in key:
                    attribute_name = key.split('_')[0]

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
        pattern_attribute = re.compile(r'[\u4e00-\u9fa5]+')
        pattern_number = re.compile(r'-?[0-9]+[.]?[0-9]*t?', re.I)
        attribute_list = pattern_attribute.findall(attributes)
        number_list = pattern_number.findall(attributes)

        attribute = attribute_list[0]

        # 查找角色属性
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

            # def将特定行中属性提取为数字，查找检定属性
            def read_attribute_check(element):
                for key, value in attribute_dict.items():
                    if element in key and '_检定' in key:
                        return float(value)

            # 处理数字
            def str_number(number):
                return str(format(number, '.1f'))

            # 将attribute替换为完整名称
            for key, value in attribute_dict.items():
                if attribute in key and '_检定' in key:
                    attribute_name = key.split('_')[0]

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

        bot.send_friend_msg(qq=msg.sender, msg=[miraicle.Plain(send)])
