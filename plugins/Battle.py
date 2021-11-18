import miraicle
import re
import csv
import pandas as pd
import codecs
import os


def check_string(re_exp, str):
    res = re.search(re_exp, str, re.I)
    if res:
        return True
    else:
        return False


reg_exp = '^([.]|[。])ba[t]?.*'

@miraicle.Mirai.receiver('GroupMessage')
def battle_to_group(bot: miraicle.Mirai, msg: miraicle.GroupMessage):
    message_check = check_string(reg_exp, msg.plain)
    if message_check:
        pattern = re.compile(r'^(^([.]|[。])ba[t]?)', re.I)
        message = str(pattern.sub('', msg.plain).strip())

        if message == '':
            file_name = 'group_battle_' + str(msg.group)
            if os.path.exists(r'data\%s.csv' % file_name):
                file_name = 'group_send' + str(msg.group)
                f = codecs.open(r'data\%s.txt' % file_name, 'r', 'utf-8')
                send = f.read()
                f.close()
            else:
                send = '没有时间轴记录！'
        elif check_string(r'[end]', msg.plain):
            file_name = 'group_battle_' + str(msg.group)
            if os.path.exists(r'data\%s.csv' % file_name):
                os.remove(r'data\%s.csv' % file_name)
                send = '时间轴归位'
            else:
                send = '没有时间轴记录！'
        else:
            # 通过正则匹配指令后的内容
            pattern = re.compile(r'^(^([.]|[。])ba[t]?)', re.I)
            attributes = str(pattern.sub('', msg.plain).strip())
            pattern_attribute = re.compile(r'[\u4e00-\u9fa5]+')
            pattern_number = re.compile(r'-?[0-9]+[.]?[0-9]*t?', re.I)
            attribute_list = pattern_attribute.findall(attributes)
            number_list = pattern_number.findall(attributes)
            file_name = str(msg.sender)

            attribute_quantity = len(re.findall(pattern_attribute, str(attribute_list)))
            attribute = attribute_list[0]
            if attribute_quantity < 2:
                note = ''
            else:
                note = attribute_list[1]

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

            attribute_value = read_attribute_check(attribute)
            # 判断计算并赋值属性，然后写入csv

            if attribute_value is None:
                send = '找不到属性' + '“' + attribute + '”！'
            else:
                if 't' in str(number_list[0]) or 'T' in str(number_list[0]):
                    # 去掉t
                    time_float = float(re.sub(r'[tT]', "", str(number_list[0])))
                    time = str_number(time_float)
                    impact_number_float = (attribute_value / 20) * time_float
                    impact_number = str_number(impact_number_float)
                else:
                    impact_number_float = float(number_list[0])
                    impact_number = str_number(impact_number_float)
                    time_float = (impact_number_float * 20) / attribute_value
                    time = str_number(time_float)

                # csv首行，并定义各个索引
                index_time = '行动时间'
                index_impact_number = '影响数值'
                index_cumulative_time = '累计行动时间'
                index_cumulative_impact_number = '累计影响数值'
                index_note = '笔记'
                # header第一项空出来，以便第一列作为index读取在dataframe
                header = ['', index_time, index_impact_number, index_cumulative_time,
                          index_cumulative_impact_number, index_note]
                row = [msg.sender, time, impact_number, time, impact_number, note]

                file_name = 'group_battle_' + str(msg.group)

                # 文件存在则提取玩家数据到dataframe
                # 如果文件不存在则直接写
                if os.path.exists(r'data\%s.csv' % file_name) is False:
                    with open(r'data\%s.csv' % file_name, 'w', newline='',
                              encoding='utf-8-sig', errors='ignore') as csv_file:
                        writer = csv.writer(csv_file)
                        writer.writerow(header)
                        writer.writerow(row)
                # 如果文件存在但玩家不在，则追加
                else:
                    # loc函数找index不可使用str
                    def get_dataframe():
                        with open(r'data\%s.csv' % file_name, 'r', newline='',
                                  encoding='utf-8-sig', errors='ignore') as csv_file:
                            # 读取csv到dataframe
                            df = pd.read_csv(csv_file, header=0, sep=',', index_col=0)
                            return pd.DataFrame(df)

                    dict_dataframe = get_dataframe()
                    check_index = msg.sender in dict_dataframe.index.values

                    if check_index is False:
                        with open(r'data\%s.csv' % file_name, 'a', newline='',
                                  encoding='utf-8-sig', errors='ignore') as csv_file:
                            writer = csv.writer(csv_file)
                            writer.writerow(row)
                    else:
                        # 提取数据修改并覆盖
                        '''
                        index_time = '行动时间'
                        index_impact_number = '影响数值'
                        index_cumulative_time = '累计行动时间'
                        index_cumulative_impact_number = '累计影响数值'
                        index_note = '笔记'
                        '''
                        # 修改累计时间
                        cumulative_time = dict_dataframe.loc[msg.sender, index_cumulative_time]
                        time_now = str_number(float(cumulative_time) + float(time))
                        dict_dataframe.loc[msg.sender, index_time] = time
                        dict_dataframe.loc[msg.sender, index_cumulative_time] = time_now
                        # 修改累计影响数值
                        cumulative_impact_number = dict_dataframe.loc[msg.sender, index_cumulative_impact_number]
                        impact_number_now = str_number(float(cumulative_impact_number) + float(impact_number))
                        dict_dataframe.loc[msg.sender, index_impact_number] = impact_number
                        dict_dataframe.loc[msg.sender, index_cumulative_impact_number] = impact_number_now
                        # 修改笔记
                        dict_dataframe.loc[msg.sender, index_note] = note
                        # 将新dataframe写回去
                        dict_dataframe.to_csv(r'data\%s.csv' % file_name)

                # 排序，之后覆盖
                def get_dataframe():
                    with open(r'data\%s.csv' % file_name, 'r', newline='',
                              encoding='utf-8-sig', errors='ignore') as csv_file:
                        # 读取csv到dataframe
                        df = pd.read_csv(csv_file, header=0, sep=',', index_col=0)
                        return pd.DataFrame(df)

                all_players_df = get_dataframe()
                all_players_df.sort_values(by=[index_cumulative_time], inplace=True)
                # 替换所有nan到空
                all_players_df = all_players_df.fillna('')
                all_players_df.to_csv(r'data\%s.csv' % file_name)

                # 记录行数，以便后期使用
                line_number = 0
                # 创建空字典
                character_dict = {}
                for index, row in all_players_df.iterrows():

                    # 提取角色名
                    if os.path.exists(r'data\%s.txt' % index) is False:
                        character_name = '佚名'
                    else:
                        f = codecs.open(r'data\%s.txt' % index, 'r', 'utf-8')
                        lines = f.readlines()
                        for line in lines:
                            if '姓名' in line:
                                character_name = ''.join(line.split('姓名')).strip()
                        f.close()

                    # 提取数值和时间
                    cumulative_time = str(all_players_df.loc[index, index_cumulative_time]) + 't'
                    impact_number = all_players_df.loc[index, index_impact_number]
                    note = all_players_df.loc[index, index_note]
                    cumulative_impact_number = all_players_df.loc[index, index_cumulative_impact_number]
                    time = str(all_players_df.loc[index, index_time]) + 't'

                    # 信息写入字典
                    line_number += 1
                    character_dict[line_number] = [character_name, cumulative_time, cumulative_impact_number,
                                                   time, impact_number, note]

                # 打轴
                cycle = 0
                file_name = 'group_send' + str(msg.group)
                while cycle < line_number:
                    cycle += 1
                    value_list = character_dict.get(int(cycle), '')

                    # 如果没有note，则不会打印换行符
                    if str(value_list[5]) == '':
                        send_note = ''
                    else:
                        send_note = str(value_list[3]) + '\n'
                    if check_string('fs', message):
                        full_spec = str(value_list[3]) + ' : ' + str(value_list[2]) + '\n'
                    else:
                        full_spec = ''
                    group_send = str(value_list[0]) + '\n' + \
                                 str(value_list[1]) + ' : ' + str(value_list[4]) + '\n' + \
                                 full_spec + \
                                 send_note + '———————' + '\n'

                    if cycle == 1:
                        f = codecs.open(r'data\%s.txt' % file_name, 'w', 'utf-8')
                        f.write(group_send)
                        f.close()
                    else:
                        f = codecs.open(r'data\%s.txt' % file_name, 'a', 'utf-8')
                        f.write(group_send)
                        f.close()

                f = codecs.open(r'data\%s.txt' % file_name, 'r', 'utf-8')
                send = f.read()
                f.close()

        bot.send_group_msg(group=msg.group, msg=send)

@miraicle.Mirai.receiver('FriendMessage')
def battle_to_friend(bot: miraicle.Mirai, msg: miraicle.FriendMessage):
    message_check = check_string(reg_exp, msg.plain)
    if message_check:
        send = '时间轴指令只在群聊使用！' + '\n' + '是否在找.pre指令来测试属性计算？'

        bot.send_friend_msg(qq=msg.sender, msg=[miraicle.Plain(send)])