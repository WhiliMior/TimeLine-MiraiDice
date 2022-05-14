import miraicle
import re
import codecs
import os
import csv
import pandas as pd


def check_string(re_exp, str):
    res = re.search(re_exp, str, re.I)
    if res:
        return True
    else:
        return False


reg_exp = '^([.]|[。])crd?.*'


@miraicle.Mirai.receiver('GroupMessage')
def record_to_group(bot: miraicle.Mirai, msg: miraicle.GroupMessage):
    message_check = check_string(reg_exp, msg.plain)
    if message_check:
        # 通过正则匹配指令后的内容
        pattern = re.compile(r'^(^([.]|[。])crd?)', re.I)
        message = str(pattern.sub('', msg.plain).strip())
        attribute = re.findall(r'([\u4e00-\u9fa5a-zA-Z]+)', message)
        attribute = ''.join(attribute)
        value = re.findall(r'[+|-]?[0-9]+[.]?[0-9]*', message)
        value = ''.join(value)

        player_file = f'data/{str(msg.sender)}/plr_{str(msg.sender)}.csv'
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
        file_name = f'data/{str(msg.sender)}/crd_{str(msg.sender)}.csv'

        # def将dict中属性提取为float
        def read_numeral_attribute(element):
            if element in attribute_dict.keys():
                return float(attribute_dict[element])
            else:
                return None

        # def将dict中属性提取为str
        def read_character_attribute(element):
            if element in attribute_dict.keys():
                return str(attribute_dict[element])
            else:
                return None

        def calculate_ratio(value1, value2):
            return ' (' + format((float(value1) / float(value2)) * 100, '.1f') + '%' + ')'

        character_name = read_character_attribute('姓名')

        # csv首行，并定义各个索引
        index_hp_full = '总体力'
        index_hp_left = '体力'
        index_mp_full = '总意志'
        index_mp_left = '意志'
        index_cash = '现金'
        # header第一项空出来，以便第一列作为index读取在dataframe
        header = [index_hp_left, index_hp_full, index_mp_left, index_mp_full, index_cash]

        # 文件存在则提取玩家数据到dataframe
        def get_dataframe():
            with open(file_name, 'r', newline='',
                      encoding='utf-8-sig', errors='ignore') as csv_file:
                # 读取csv到dataframe
                df = pd.read_csv(csv_file, header=0, sep=',')
                return pd.DataFrame(df)

        # 如果文件不存在则直接写
        if os.path.exists(file_name) is False:
            hp_full = str(read_numeral_attribute(index_hp_full))
            hp_left = hp_full
            mp_full = str(read_numeral_attribute(index_mp_full))
            mp_left = mp_full
            hp_ratio = calculate_ratio(hp_left, hp_full)
            mp_ratio = calculate_ratio(mp_left, mp_full)
            cash = str(read_numeral_attribute(index_cash))
            row = [hp_left, hp_full, mp_left, mp_full, cash]
            with open(file_name, 'w', newline='',
                      encoding='utf-8-sig', errors='ignore') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(header)
                writer.writerow(row)
            send = f'{character_name}: \n' + \
                   '体力: ' + hp_left + '/' + hp_full + hp_ratio + '\n' + \
                   '意志: ' + mp_left + '/' + mp_full + mp_ratio + '\n' + \
                   '现金: ' + cash
        elif check_string(r'reset', message):
            datas = get_dataframe()
            hp_full = str(read_numeral_attribute(index_hp_full))
            hp_left = hp_full
            mp_full = str(read_numeral_attribute(index_mp_full))
            mp_left = mp_full
            hp_ratio = calculate_ratio(hp_left, hp_full)
            mp_ratio = calculate_ratio(mp_left, mp_full)
            cash = str(datas.loc[0, index_cash])
            row = [hp_left, hp_full, mp_left, mp_full, cash]
            with open(file_name, 'w', newline='',
                      encoding='utf-8-sig', errors='ignore') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(header)
                writer.writerow(row)
            send = f'{character_name}: \n' + \
                   '体力: ' + hp_left + '/' + hp_full + hp_ratio + '\n' + \
                   '意志: ' + mp_left + '/' + mp_full + mp_ratio + '\n' + \
                   '现金: ' + cash
        # 如果存在则根据指令更改
        elif check_string(r'del', message):
            os.remove(file_name)
            send = '记录已清除'
        elif message == '':
            datas = get_dataframe()
            get_hp = str(datas.loc[0, '体力'])
            get_hp_full = str(read_numeral_attribute(index_hp_full))
            get_mp = str(datas.loc[0, '意志'])
            get_mp_full = str(read_numeral_attribute(index_mp_full))
            hp_ratio = calculate_ratio(get_hp, get_hp_full)
            mp_ratio = calculate_ratio(get_mp, get_mp_full)
            get_cash = str(datas.loc[0, '现金'])
            send = f'{character_name}: \n' + \
                   '体力: ' + get_hp + '/' + get_hp_full + hp_ratio + '\n' + \
                   '意志: ' + get_mp + '/' + get_mp_full + mp_ratio + '\n' + \
                   '现金: ' + get_cash
        else:
            def change_value(dataframe, index, value):
                dataframe = dataframe.fillna('')
                if '+' in value:
                    get_value = float(dataframe.loc[0, index])
                    result = get_value + abs(float(value))
                elif '-' in value:
                    get_value = float(dataframe.loc[0, index])
                    result = get_value - abs(float(value))
                elif value == '':
                    result = str(dataframe.loc[0, index])
                else:
                    result = value
                dataframe.loc[0, index] = result
                dataframe.to_csv(file_name, index=False)

            datas = get_dataframe()
            if check_string(r'\bhp\b|\b体力\b', attribute):
                change_value(datas, index_hp_left, value)
                datas = get_dataframe()
                get_hp = str(datas.loc[0, index_hp_left])
                get_hp_full = str(read_numeral_attribute(index_hp_full))
                hp_ratio = calculate_ratio(get_hp, get_hp_full)
                send = f'{character_name}: \n' + \
                       '体力: ' + get_hp + '/' + get_hp_full + hp_ratio
            elif check_string(r'\bmp\b|\b意志\b', attribute):
                change_value(datas, index_mp_left, value)
                datas = get_dataframe()
                get_mp = str(datas.loc[0, index_mp_left])
                get_mp_full = str(read_numeral_attribute(index_mp_full))
                mp_ratio = calculate_ratio(get_mp, get_mp_full)
                send = f'{character_name}: \n' + \
                       '意志: ' + get_mp + '/' + get_mp_full + mp_ratio
            elif check_string(r'\bcash\b|\b现金\b', attribute):
                change_value(datas, index_cash, value)
                datas = get_dataframe()
                get_cash = str(datas.loc[0, index_cash])
                send = f'{character_name}: \n' + \
                       '现金: ' + get_cash
            else:
                send = '请正确输入指令！'

        bot.send_group_msg(group=msg.group, msg=send, quote=msg.id)


@miraicle.Mirai.receiver('FriendMessage')
def record_to_friend(bot: miraicle.Mirai, msg: miraicle.FriendMessage):
    message_check = check_string(reg_exp, msg.plain)
    if message_check:
        # 通过正则匹配指令后的内容
        pattern = re.compile(r'^(^([.]|[。])crd?)', re.I)
        message = str(pattern.sub('', msg.plain).strip())
        attribute = re.findall(r'([\u4e00-\u9fa5a-zA-Z]+)', message)
        attribute = ''.join(attribute)
        value = re.findall(r'[+|-]?[0-9]+[.]?[0-9]*', message)
        value = ''.join(value)

        player_file = f'data/{str(msg.sender)}/plr_{str(msg.sender)}.csv'
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
        file_name = f'data/{str(msg.sender)}/crd_{str(msg.sender)}.csv'

        # def将dict中属性提取为float
        def read_numeral_attribute(element):
            if element in attribute_dict.keys():
                return float(attribute_dict[element])
            else:
                return None

        # def将dict中属性提取为str
        def read_character_attribute(element):
            if element in attribute_dict.keys():
                return str(attribute_dict[element])
            else:
                return None

        def calculate_ratio(value1, value2):
            return ' (' + format((float(value1) / float(value2)) * 100, '.1f') + '%' + ')'

        character_name = read_character_attribute('姓名')

        # csv首行，并定义各个索引
        index_hp_full = '总体力'
        index_hp_left = '体力'
        index_mp_full = '总意志'
        index_mp_left = '意志'
        index_cash = '现金'
        # header第一项空出来，以便第一列作为index读取在dataframe
        header = [index_hp_left, index_hp_full, index_mp_left, index_mp_full, index_cash]

        # 文件存在则提取玩家数据到dataframe
        def get_dataframe():
            with open(file_name, 'r', newline='',
                      encoding='utf-8-sig', errors='ignore') as csv_file:
                # 读取csv到dataframe
                df = pd.read_csv(csv_file, header=0, sep=',')
                return pd.DataFrame(df)

        # 如果文件不存在则直接写
        if os.path.exists(file_name) is False:
            hp_full = str(read_numeral_attribute(index_hp_full))
            hp_left = hp_full
            mp_full = str(read_numeral_attribute(index_mp_full))
            mp_left = mp_full
            hp_ratio = calculate_ratio(hp_left, hp_full)
            mp_ratio = calculate_ratio(mp_left, mp_full)
            cash = str(read_numeral_attribute(index_cash))
            row = [hp_left, hp_full, mp_left, mp_full, cash]
            with open(file_name, 'w', newline='',
                      encoding='utf-8-sig', errors='ignore') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(header)
                writer.writerow(row)
            send = f'{character_name}: \n' + \
                   '体力: ' + hp_left + '/' + hp_full + hp_ratio + '\n' + \
                   '意志: ' + mp_left + '/' + mp_full + mp_ratio + '\n' + \
                   '现金: ' + cash
        elif check_string(r'reset', message):
            datas = get_dataframe()
            hp_full = str(read_numeral_attribute(index_hp_full))
            hp_left = hp_full
            mp_full = str(read_numeral_attribute(index_mp_full))
            mp_left = mp_full
            hp_ratio = calculate_ratio(hp_left, hp_full)
            mp_ratio = calculate_ratio(mp_left, mp_full)
            cash = str(datas.loc[0, index_cash])
            row = [hp_left, hp_full, mp_left, mp_full, cash]
            with open(file_name, 'w', newline='',
                      encoding='utf-8-sig', errors='ignore') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(header)
                writer.writerow(row)
            send = f'{character_name}: \n' + \
                   '体力: ' + hp_left + '/' + hp_full + hp_ratio + '\n' + \
                   '意志: ' + mp_left + '/' + mp_full + mp_ratio + '\n' + \
                   '现金: ' + cash
        # 如果存在则根据指令更改
        elif check_string(r'del', message):
            os.remove(file_name)
            send = '记录已清除'
        elif message == '':
            datas = get_dataframe()
            get_hp = str(datas.loc[0, '体力'])
            get_hp_full = str(read_numeral_attribute(index_hp_full))
            get_mp = str(datas.loc[0, '意志'])
            get_mp_full = str(read_numeral_attribute(index_mp_full))
            hp_ratio = calculate_ratio(get_hp, get_hp_full)
            mp_ratio = calculate_ratio(get_mp, get_mp_full)
            get_cash = str(datas.loc[0, '现金'])
            send = f'{character_name}: \n' + \
                   '体力: ' + get_hp + '/' + get_hp_full + hp_ratio + '\n' + \
                   '意志: ' + get_mp + '/' + get_mp_full + mp_ratio + '\n' + \
                   '现金: ' + get_cash
        else:
            def change_value(dataframe, index, value):
                dataframe = dataframe.fillna('')
                if '+' in value:
                    get_value = float(dataframe.loc[0, index])
                    result = get_value + abs(float(value))
                elif '-' in value:
                    get_value = float(dataframe.loc[0, index])
                    result = get_value - abs(float(value))
                elif value == '':
                    result = str(dataframe.loc[0, index])
                else:
                    result = value
                dataframe.loc[0, index] = result
                dataframe.to_csv(file_name, index=False)

            datas = get_dataframe()
            if check_string(r'\bhp\b|\b体力\b', attribute):
                change_value(datas, index_hp_left, value)
                datas = get_dataframe()
                get_hp = str(datas.loc[0, index_hp_left])
                get_hp_full = str(read_numeral_attribute(index_hp_full))
                hp_ratio = calculate_ratio(get_hp, get_hp_full)
                send = f'{character_name}: \n' + \
                       '体力: ' + get_hp + '/' + get_hp_full + hp_ratio
            elif check_string(r'\bmp\b|\b意志\b', attribute):
                change_value(datas, index_mp_left, value)
                datas = get_dataframe()
                get_mp = str(datas.loc[0, index_mp_left])
                get_mp_full = str(read_numeral_attribute(index_mp_full))
                mp_ratio = calculate_ratio(get_mp, get_mp_full)
                send = f'{character_name}: \n' + \
                       '意志: ' + get_mp + '/' + get_mp_full + mp_ratio
            elif check_string(r'\bcash\b|\b现金\b', attribute):
                change_value(datas, index_cash, value)
                datas = get_dataframe()
                get_cash = str(datas.loc[0, index_cash])
                send = f'{character_name}: \n' + \
                       '现金: ' + get_cash
            else:
                send = '请正确输入指令！'

        bot.send_friend_msg(qq=msg.sender, msg=[miraicle.Plain(send)])
