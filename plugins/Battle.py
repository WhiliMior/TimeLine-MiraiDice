import miraicle
import re
import csv
import pandas as pd
import codecs
import os

"""
.bat 直接显示时间轴
.bat end 删除时间轴
.bat {属性} {时间}t/{影响数值} (笔记)  战斗指令
"""


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

        folder = f'data/grp_{str(msg.group)}'
        # 创建文件夹
        if not os.path.exists(folder):
            os.makedirs(folder)

        file_bat = f'data/grp_{str(msg.group)}/grp_bat_{str(msg.group)}.csv'
        file_send = f'data/grp_{str(msg.group)}/grp_snd_{str(msg.group)}.txt'
        if message == '':
            if os.path.exists(file_send):
                f = codecs.open(file_send, 'r', 'utf-8')
                send = f.read()
                f.close()
            else:
                send = '没有时间轴记录！'
        elif check_string(r'[end]', msg.plain):
            if os.path.exists(file_bat):
                os.remove(file_bat)
                os.remove(file_send)
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

            attribute_quantity = len(re.findall(pattern_attribute, str(attribute_list)))
            attribute = attribute_list[0]

            attributes_list = attributes.split()

            # Check if the list contains at least two elements
            if len(attributes_list) > 2:
                # Set the "note" to the last element in the list
                note = attributes_list[-1]
            else:
                # Set the "note" to an empty string
                note = ''

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

                def read_character_attribute(element):
                    if element in attribute_dict.keys():
                        return str(attribute_dict[element])
                    else:
                        return None

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
                    character_index = f'{msg.sender}_{character_code}'
                    row = [character_index, time, impact_number, time, impact_number, note]

                    # 文件存在则提取玩家数据到dataframe
                    # 如果文件不存在则直接写
                    if os.path.exists(file_bat) is False:
                        with open(file_bat, 'w', newline='',
                                  encoding='utf-8-sig', errors='ignore') as csv_file:
                            writer = csv.writer(csv_file)
                            writer.writerow(header)
                            writer.writerow(row)
                    # 如果文件存在但玩家不在，则追加
                    else:
                        # loc函数找index不可使用str
                        def get_dataframe():
                            with open(file_bat, 'r', newline='',
                                      encoding='utf-8-sig', errors='ignore') as csv_file:
                                # 读取csv到dataframe
                                df = pd.read_csv(csv_file, header=0, sep=',', index_col=0)
                                return pd.DataFrame(df)

                        dict_dataframe = get_dataframe()
                        check_index = character_index in dict_dataframe.index.values

                        if check_index is False:
                            with open(file_bat, 'a', newline='',
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
                            cumulative_time = dict_dataframe.loc[character_index, index_cumulative_time]
                            time_now = str_number(float(cumulative_time) + float(time))
                            dict_dataframe.loc[character_index, index_time] = time
                            dict_dataframe.loc[character_index, index_cumulative_time] = time_now
                            # 修改累计影响数值
                            cumulative_impact_number = dict_dataframe.loc[character_index, index_cumulative_impact_number]
                            impact_number_now = str_number(float(cumulative_impact_number) + float(impact_number))
                            dict_dataframe.loc[character_index, index_impact_number] = impact_number
                            dict_dataframe.loc[character_index, index_cumulative_impact_number] = impact_number_now
                            # 修改笔记
                            dict_dataframe.loc[character_index, index_note] = note
                            # 将新dataframe写回去
                            dict_dataframe.to_csv(file_bat)

                    # 排序，之后覆盖
                    def get_dataframe():
                        with open(file_bat, 'r', newline='',
                                  encoding='utf-8-sig', errors='ignore') as csv_file:
                            # 读取csv到dataframe
                            df = pd.read_csv(csv_file, header=0, sep=',', index_col=0)
                            return pd.DataFrame(df)

                    all_players_df = get_dataframe()
                    all_players_df.sort_values(by=[index_cumulative_time], inplace=True)
                    # 替换所有nan到空
                    all_players_df = all_players_df.fillna('')
                    all_players_df.to_csv(file_bat)

                    # 记录行数，以便后期使用
                    line_number = 0
                    # 创建空字典
                    character_dict = {}
                    for index, row in all_players_df.iterrows():
                        split_list = str(index).split('_')
                        character_file = f'data/{split_list[0]}/chr_{split_list[1]}.txt'
                        f = codecs.open(character_file, 'r+', 'utf-8')
                        attribute_dict = eval(f.read())  # 读取的str转换为字典
                        f.close()

                        character_name = read_character_attribute('姓名')

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
                    while cycle < line_number:
                        cycle += 1
                        value_list = character_dict.get(int(cycle), '')

                        # 如果没有note，则只打印相关属性。否则在相关属性后加上note
                        if str(value_list[5]) == '':
                            send_note = attribute + '\n'
                        else:
                            send_note = attribute + ': ' + str(value_list[5]) + '\n'
                        if check_string('fs', message):
                            full_spec = str(value_list[3]) + ' : ' + str(value_list[2]) + '\n'
                        else:
                            full_spec = ''
                        group_send = str(value_list[0]) + '\n' + \
                                     str(value_list[1]) + f' ({value_list[3]})' + ' : ' + str(value_list[4]) + '\n' + \
                                     full_spec + \
                                     send_note + '———————' + '\n'

                        if cycle == 1:
                            f = codecs.open(file_send, 'w', 'utf-8')
                            f.write(group_send)
                            f.close()
                        else:
                            f = codecs.open(file_send, 'a', 'utf-8')
                            f.write(group_send)
                            f.close()

                    f = codecs.open(file_send, 'r', 'utf-8')
                    send = f.read()
                    f.close()

        bot.send_group_msg(group=msg.group, msg=send)


@miraicle.Mirai.receiver('FriendMessage')
def battle_to_friend(bot: miraicle.Mirai, msg: miraicle.FriendMessage):
    message_check = check_string(reg_exp, msg.plain)
    if message_check:
        send = '时间轴指令只在群聊使用！' + '\n' + '是否在找.pre指令来测试属性计算？'

        bot.send_friend_msg(qq=msg.sender, msg=[miraicle.Plain(send)])
