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
        file_name = str(msg.sender)

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

        def calculate_ratio(value1, value2):
            return ' (' + format((float(value1) / float(value2)) * 100, '.1f') + '%' + ')'

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
            with open(r'data\%s.csv' % file_name, 'r', newline='',
                      encoding='utf-8-sig', errors='ignore') as csv_file:
                # 读取csv到dataframe
                df = pd.read_csv(csv_file, header=0, sep=',')
                return pd.DataFrame(df)

        # 如果文件不存在则直接写
        if os.path.exists(r'data\%s.csv' % file_name) is False:
            hp_full = str(read_attribute(index_hp_full))
            hp_left = hp_full
            mp_full = str(read_attribute(index_mp_full))
            mp_left = mp_full
            hp_ratio = calculate_ratio(hp_left, hp_full)
            mp_ratio = calculate_ratio(mp_left, mp_full)
            cash = str(read_attribute(index_cash))
            row = [hp_left, hp_full, mp_left, mp_full, cash]
            with open(r'data\%s.csv' % file_name, 'w', newline='',
                      encoding='utf-8-sig', errors='ignore') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(header)
                writer.writerow(row)
            send = '体力: ' + hp_left + '/' + hp_full + hp_ratio + '\n' + \
                   '意志: ' + mp_left + '/' + mp_full + mp_ratio + '\n' + \
                   '现金: ' + cash
        elif check_string(r'reset', message):
            datas = get_dataframe()
            hp_full = str(read_attribute(index_hp_full))
            hp_left = hp_full
            mp_full = str(read_attribute(index_mp_full))
            mp_left = mp_full
            hp_ratio = calculate_ratio(hp_left, hp_full)
            mp_ratio = calculate_ratio(mp_left, mp_full)
            cash = str(datas.loc[0, index_cash])
            row = [hp_left, hp_full, mp_left, mp_full, cash]
            with open(r'data\%s.csv' % file_name, 'w', newline='',
                      encoding='utf-8-sig', errors='ignore') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(header)
                writer.writerow(row)
            send = '体力: ' + hp_left + '/' + hp_full + hp_ratio + '\n' + \
                   '意志: ' + mp_left + '/' + mp_full + mp_ratio + '\n' + \
                   '现金: ' + cash
        # 如果存在则根据指令更改
        elif check_string(r'delete', message):
            os.remove(r'data\%s.csv' % file_name)
            send = '记录已清除'
        elif message == '':
            datas = get_dataframe()
            get_hp = str(datas.loc[0, '体力'])
            get_hp_full = str(datas.loc[0, '总体力'])
            get_mp = str(datas.loc[0, '意志'])
            get_mp_full = str(datas.loc[0, '总意志'])
            hp_ratio = calculate_ratio(get_hp, get_hp_full)
            mp_ratio = calculate_ratio(get_mp, get_mp_full)
            get_cash = str(datas.loc[0, '现金'])
            send = '体力: ' + get_hp + '/' + get_hp_full + hp_ratio + '\n' + \
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
                dataframe.to_csv(r'data\%s.csv' % file_name, index = False)

            datas = get_dataframe()
            if check_string(r'\bhp\b|\b体力\b', attribute):
                change_value(datas, '体力', value)
                datas = get_dataframe()
                get_hp = str(datas.loc[0, '体力'])
                get_hp_full = str(datas.loc[0, '总体力'])
                hp_ratio = calculate_ratio(get_hp, get_hp_full)
                send = '体力: ' + get_hp + '/' + get_hp_full + hp_ratio
            elif check_string(r'\bmp\b|\b意志\b', attribute):
                change_value(datas, '意志', value)
                datas = get_dataframe()
                get_mp = str(datas.loc[0, '意志'])
                get_mp_full = str(datas.loc[0, '总意志'])
                mp_ratio = calculate_ratio(get_mp, get_mp_full)
                send = '意志: ' + get_mp + '/' + get_mp_full + mp_ratio
            elif check_string(r'\bcash\b|\b现金\b', attribute):
                change_value(datas, '现金', value)
                datas = get_dataframe()
                get_cash = str(datas.loc[0, '现金'])
                send = '现金: ' + get_cash

        bot.send_group_msg(group=msg.group, msg=send, quote=msg.id)
