import miraicle
import re
import os
import codecs
import pandas as pd

"""
.chr 显示现有角色
.chr {序号} 选择角色
.chr show 显示角色属性
.chr del {序号} 删除选定角色
"""


def check_string(re_exp, str):
    res = re.search(re_exp, str, re.I)
    if res:
        return True
    else:
        return False


reg_exp = '^([.]|[。])ch[r]?.*'


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
    return False


@miraicle.Mirai.receiver('GroupMessage')
def change_to_group(bot: miraicle.Mirai, msg: miraicle.GroupMessage):
    message_check = check_string(reg_exp, msg.plain)
    if message_check:
        pattern = re.compile(r'^(^([.]|[。])ch[r]?)', re.I)
        message = str(pattern.sub('', msg.plain).strip())

        # 获取角色列表
        player_file = f'data/{str(msg.sender)}/plr_{str(msg.sender)}.csv'
        if os.path.exists(player_file) is False:
            send = '没有角色！'
        else:
            csv_file = open(player_file, 'r', newline='', encoding='utf-8-sig', errors='ignore')
            player_dataframe = pd.read_csv(csv_file, header=0, sep=',')
            csv_file.close()

            if message == '':
                send_list = []
                send = f'您共有{len(player_dataframe)}个角色'
                for index, data in player_dataframe.iterrows():
                    if data[3] == 0:
                        using = f'[{index + 1}]'
                    else:
                        using = '[●]'
                    send_list.append(f'{("{} {}".format(using, data[1]))}')
                send = send + '\n' + "\n".join(send_list) + '\n' + '请在指令后使用索引数字来更改角色选择'
            elif check_string('show', message):
                csv_file = open(player_file, 'r', newline='', encoding='utf-8-sig', errors='ignore')
                player_dataframe = pd.read_csv(csv_file, header=0, sep=',')
                csv_file.close()
                using_index = player_dataframe["using"].idxmax()
                character_code = player_dataframe.at[using_index, 'code']
                character_file = f'data/{str(msg.sender)}/chr_{character_code}.txt'
                f = codecs.open(character_file, 'r+', 'utf-8')
                attribute_dict = eval(f.read())  # 读取的str转换为字典
                f.close()

                # create an empty string to store the character's attributes
                send = ""

                # loop through the attributes in the attribute_dict dictionary
                for key, value in attribute_dict.items():
                    # check if the value is a number
                    if value.replace(".", "").isnumeric():
                        # convert the value to a float
                        value = float(value)
                        # check if the value is not equal to zero
                        if value != 0:
                            # round the number to two decimal places
                            value = round(value, 2)
                            # add the attribute name and value to the string
                            send += key + ": " + str(value) + "\n"
                    else:
                        # add the attribute name and value to the string
                        send += key + ": " + str(value) + "\n"
            elif check_string('del', message):
                pattern = re.compile(r'(del)', re.I)
                index = eval(pattern.sub('', message).strip())
                if type(index) == 'list':
                    index = [i - 1 for i in index]
                else:
                    index = int(index) - 1
                    if index >= len(player_dataframe):
                        index = len(player_dataframe) - 1
                    elif index < 0:
                        index = 0
                character_name = player_dataframe.at[index, 'character']
                character_code = player_dataframe.at[index, 'code']
                character_using = player_dataframe.at[index, 'using']
                character_file = f'data/{str(msg.sender)}/chr_{character_code}.txt'
                if character_using == 1:
                    player_dataframe.loc[0, 'using'] = 1
                if len(player_dataframe) <= 1:
                    os.remove(player_file)
                    os.remove(character_file)
                else:
                    character_code = player_dataframe.at[index, 'code']
                    character_file = f'data/{str(msg.sender)}/chr_{character_code}.txt'
                    player_dataframe = player_dataframe.drop(index)
                    player_dataframe.to_csv(player_file, index=False)
                    os.remove(character_file)
                send = f'"{character_name}"已经删除'
            elif is_number(message):
                index = int(message) - 1
                if index >= len(player_dataframe):
                    index = len(player_dataframe) - 1
                elif index <= 0:
                    index = 0
                player_dataframe['using'] = player_dataframe['using'].replace(1, 0)
                player_dataframe.loc[index, 'using'] = 1
                player_dataframe.to_csv(player_file, index=False)

                character_name = player_dataframe.at[index, 'character']
                send = f'已选择角色"{character_name}"'

        bot.send_group_msg(group=msg.group, msg=send, quote=msg.id)


@miraicle.Mirai.receiver('FriendMessage')
def change_to_friend(bot: miraicle.Mirai, msg: miraicle.FriendMessage):
    message_check = check_string(reg_exp, msg.plain)
    if message_check:
        pattern = re.compile(r'^(^([.]|[。])ch[r]?)', re.I)
        message = str(pattern.sub('', msg.plain).strip())

        # 获取角色列表
        player_file = f'data/{str(msg.sender)}/plr_{str(msg.sender)}.csv'
        if os.path.exists(player_file) is False:
            send = '没有角色！'
        else:
            csv_file = open(player_file, 'r', newline='', encoding='utf-8-sig', errors='ignore')
            player_dataframe = pd.read_csv(csv_file, header=0, sep=',')
            csv_file.close()

            if message == '':
                send_list = []
                send = f'您共有{len(player_dataframe)}个角色'
                for index, data in player_dataframe.iterrows():
                    if data[3] == 0:
                        using = f'[{index + 1}]'
                    else:
                        using = '[●]'
                    send_list.append(f'{("{} {}".format(using, data[1]))}')
                send = send + '\n' + "\n".join(send_list) + '\n' + '请在指令后使用索引数字来更改角色选择'
            elif check_string('show', message):
                csv_file = open(player_file, 'r', newline='', encoding='utf-8-sig', errors='ignore')
                player_dataframe = pd.read_csv(csv_file, header=0, sep=',')
                csv_file.close()
                using_index = player_dataframe["using"].idxmax()
                character_code = player_dataframe.at[using_index, 'code']
                character_file = f'data/{str(msg.sender)}/chr_{character_code}.txt'
                f = codecs.open(character_file, 'r+', 'utf-8')
                attribute_dict = eval(f.read())  # 读取的str转换为字典
                f.close()

                # create an empty string to store the character's attributes
                send = ""

                # loop through the attributes in the attribute_dict dictionary
                for key, value in attribute_dict.items():
                    # check if the value is a number
                    if value.replace(".", "").isnumeric():
                        # convert the value to a float
                        value = float(value)
                        # check if the value is not equal to zero
                        if value != 0:
                            # round the number to two decimal places
                            value = round(value, 2)
                            # add the attribute name and value to the string
                            send += key + ": " + str(value) + "\n"
                    else:
                        # add the attribute name and value to the string
                        send += key + ": " + str(value) + "\n"
            elif check_string('del', message):
                pattern = re.compile(r'(del)', re.I)
                index = eval(pattern.sub('', message).strip())
                if type(index) == 'list':
                    index = [i - 1 for i in index]
                else:
                    index = int(index) - 1
                    if index >= len(player_dataframe):
                        index = len(player_dataframe) - 1
                    elif index < 0:
                        index = 0
                character_name = player_dataframe.at[index, 'character']
                character_code = player_dataframe.at[index, 'code']
                character_using = player_dataframe.at[index, 'using']
                character_file = f'data/{str(msg.sender)}/chr_{character_code}.txt'
                if character_using == 1:
                    player_dataframe.loc[0, 'using'] = 1
                if len(player_dataframe) <= 1:
                    os.remove(player_file)
                    os.remove(character_file)
                else:
                    character_code = player_dataframe.at[index, 'code']
                    character_file = f'data/{str(msg.sender)}/chr_{character_code}.txt'
                    player_dataframe = player_dataframe.drop(index)
                    player_dataframe.to_csv(player_file, index=False)
                    os.remove(character_file)
                send = f'"{character_name}"已经删除'
            elif is_number(message):
                index = int(message) - 1
                if index >= len(player_dataframe):
                    index = len(player_dataframe) - 1
                elif index <= 0:
                    index = 0
                player_dataframe['using'] = player_dataframe['using'].replace(1, 0)
                player_dataframe.loc[index, 'using'] = 1
                player_dataframe.to_csv(player_file, index=False)

                character_name = player_dataframe.at[index, 'character']
                send = f'已选择角色"{character_name}"'

        bot.send_friend_msg(qq=msg.sender, msg=[miraicle.Plain(send)])
