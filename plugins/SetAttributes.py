import miraicle
import re
import codecs
import math
import os
import csv
import base64
import pandas as pd


def check_string(re_exp, str):
    res = re.search(re_exp, str, re.I)
    if res:
        return True
    else:
        return False


reg_exp = '^([.]|[。])TLsetup?.*'

end_divider = ','
middle_divider = ':'


@miraicle.Mirai.receiver('GroupMessage')
def record_to_group(bot: miraicle.Mirai, msg: miraicle.GroupMessage):
    message_check = check_string(reg_exp, msg.plain)
    if message_check:
        # 删除开头
        pattern = re.compile(r'^(^([.]|[。])TLsetup?)', re.I)
        full_text = str(pattern.sub('', msg.plain).strip())
        # 将文本变成list
        attribute_list = full_text.split(end_divider)

        # 创建一个字典，然后将属性写入其中
        attribute_dict = {}
        for element in attribute_list:
            two_values = element.split(middle_divider)
            attribute = two_values[0]
            value = two_values[1]
            attribute_dict[attribute] = value

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

        # def保留两位小数
        def reserve_decimals(number):
            return float(format(number, '.2f'))

        # def追加属性到dict, 储存为str
        def add_attribute(element, number):
            number = str(number)
            attribute_dict[element] = number

        # 计算现金
        attribute = read_numeral_attribute('资产')
        if attribute < 0:
            cash = (math.pow(attribute, 4) / math.pow(10, 4)) * -1
        else:
            cash = math.pow(attribute, 4) / math.pow(10, 4)
        add_attribute('现金', cash)

        # 计算能力
        level = read_numeral_attribute('等级')
        ability = level * 100
        add_attribute('能力', ability)

        # 计算物理
        ratio = read_numeral_attribute('物理思维比值')
        physical = ability - (ratio * level) / 10
        add_attribute('物理', physical)

        # 计算思维
        mental = ability - physical
        add_attribute('思维', mental)

        # 计算年龄修正
        age = read_numeral_attribute('年龄')
        adult_age = read_numeral_attribute('成年年龄')
        if adult_age == 0:
            physical_age_revision = 1
            mental_age_revision = 1
        else:
            physical_age_revision = math.cos(math.log(age / (adult_age * 1.5), math.e)) + 0.12
            mental_age_revision = math.log(age / adult_age, 10) + 0.8
        add_attribute('物理年龄修正', physical_age_revision)
        add_attribute('思维年龄修正', mental_age_revision)

        # 计算体型修正
        size = read_numeral_attribute('体型')
        standard_size = read_numeral_attribute('标准体型')
        if standard_size == 0:
            size_revision = 1
        else:
            size_revision = math.log(size / standard_size, math.e) + 1
        add_attribute('体型修正', size_revision)

        # 计算修正后物理，体质
        physical_revision = physical * physical_age_revision
        add_attribute('物理_修正', physical_revision)
        constitution = read_numeral_attribute('体质')
        constitution_check = physical_revision * constitution / 100 * size_revision
        constitution_check = reserve_decimals(constitution_check)
        add_attribute('体质_检定', constitution_check)

        # 计算体力
        hitpoint_full = format(constitution_check, '.0f')
        add_attribute('总体力', hitpoint_full)

        # 计算力量
        power = read_numeral_attribute('力量')
        power_check = physical_revision * power / 100 * size_revision
        power_check = reserve_decimals(power_check)
        add_attribute('力量_检定', power_check)

        # 计算负重修正
        weight_full = power_check * 10 / level
        weight = read_numeral_attribute('负重')
        weight_revision = -1 * math.pow(weight / weight_full, 2) + 1
        add_attribute('总负重', weight_full)
        add_attribute('负重修正', weight_revision)

        # 计算敏捷
        dexterity = read_numeral_attribute('敏捷')
        dexterity_check = physical_revision * dexterity / 100 * weight_revision
        dexterity_check = reserve_decimals(dexterity_check)
        add_attribute('敏捷_检定', dexterity_check)

        # 计算思维
        mental_revision = mental * mental_age_revision
        add_attribute('思维_修正', mental_revision)

        # def计算思维下副属性
        def mental_attribute_check(element):
            number = read_numeral_attribute(element)
            element_check = mental_revision * number / 100
            return element_check

        willpower = mental_attribute_check('意志')
        willpower_full = willpower
        add_attribute('意志_检定', willpower)
        add_attribute('总意志', willpower_full)

        education_check = mental_attribute_check('教育')
        intelligence_check = mental_attribute_check('智力')
        add_attribute('教育_检定', education_check)
        add_attribute('智力_检定', intelligence_check)

        medicine_and_life_science_check = mental_attribute_check('医学及生命科学')
        engineering_and_technology_check = mental_attribute_check('工程与科技')
        military_and_survival_check = mental_attribute_check('军事与生存')
        literature_check = mental_attribute_check('文学')
        visual_and_performing_art_check = mental_attribute_check('视觉及表演艺术')
        add_attribute('医学及生命科学_检定', medicine_and_life_science_check)
        add_attribute('工程与科技_检定', engineering_and_technology_check)
        add_attribute('军事与生存_检定', military_and_survival_check)
        add_attribute('文学_检定', literature_check)
        add_attribute('视觉及表演艺术_检定', visual_and_performing_art_check)

        # 计算交涉加成
        literature = read_numeral_attribute('文学')
        visual_and_performing_art = read_numeral_attribute('视觉及表演艺术')
        intelligence = read_numeral_attribute('智力')
        appearance = read_numeral_attribute('外貌')
        negotiation_buff = (literature + visual_and_performing_art + intelligence) * \
                           (math.log(mental / physical, 10) + 1) * \
                           (math.log(appearance / 50, math.e) + 1)
        add_attribute('交涉加成', negotiation_buff)

        # 加密角色名到code
        character_name = read_character_attribute('姓名')
        character_code = str(base64.b64encode(character_name.encode()))
        rstr = r'[\/\\\:\*\?\"\<\>\|]'  # '/ \ : * ? " < > |'
        character_code = re.sub(rstr, "", character_code)  # 替换为空

        # 用发送者qq号+角色unicode为文件名.
        folder = f'data/{str(msg.sender)}'
        character_file = f'data/{str(msg.sender)}/chr_{character_code}.txt'
        player_file = f'data/{str(msg.sender)}/plr_{str(msg.sender)}.csv'

        # 储存玩家的角色信息
        header = ['player', 'character', 'code', 'using']
        player_list = [str(msg.sender), character_name, character_code, 1]

        # 创建文件夹
        if not os.path.exists(folder):
            os.makedirs(folder)

        if os.path.exists(player_file):
            csv_file = open(player_file, 'r', newline='', encoding='utf-8-sig', errors='ignore')
            player_dataframe = pd.read_csv(csv_file, header=0, sep=',')
            csv_file.close()
            if character_name not in player_dataframe['character'].values:
                player_dataframe['using'] = player_dataframe['using'].replace(1, 0)
                player_dataframe.loc[-1] = player_list
            player_dataframe.to_csv(player_file, index=False)
        else:
            csv_file = open(player_file, 'w', newline='', encoding='utf-8-sig', errors='ignore')
            writer = csv.writer(csv_file)
            writer.writerow(header)
            writer.writerow(player_list)

        # 最后将字典写入文件
        f = codecs.open(character_file, 'w', 'utf-8')
        f.write(str(attribute_dict))
        f.close()

        character_name = read_character_attribute('姓名')
        send = f'{character_name}的TL属性设置完成√'

        bot.send_group_msg(group=msg.group, msg=send, quote=msg.id)


@miraicle.Mirai.receiver('FriendMessage')
def record_to_friend(bot: miraicle.Mirai, msg: miraicle.FriendMessage):
    message_check = check_string(reg_exp, msg.plain)
    if message_check:
        # 删除开头
        pattern = re.compile(r'^(^([.]|[。])TLsetup?)', re.I)
        full_text = str(pattern.sub('', msg.plain).strip())
        # 将文本变成list
        attribute_list = full_text.split(end_divider)

        # 创建一个字典，然后将属性写入其中
        attribute_dict = {}
        for element in attribute_list:
            two_values = element.split(middle_divider)
            attribute = two_values[0]
            value = two_values[1]
            attribute_dict[attribute] = value

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

        # def保留两位小数
        def reserve_decimals(number):
            return float(format(number, '.2f'))

        # def追加属性到dict, 储存为str
        def add_attribute(element, number):
            number = str(number)
            attribute_dict[element] = number

        # 计算现金
        attribute = read_numeral_attribute('资产')
        if attribute < 0:
            cash = (math.pow(attribute, 4) / math.pow(10, 4)) * -1
        else:
            cash = math.pow(attribute, 4) / math.pow(10, 4)
        add_attribute('现金', cash)

        # 计算能力
        level = read_numeral_attribute('等级')
        ability = level * 100
        add_attribute('能力', ability)

        # 计算物理
        ratio = read_numeral_attribute('物理思维比值')
        physical = ability - (ratio * level) / 10
        add_attribute('物理', physical)

        # 计算思维
        mental = ability - physical
        add_attribute('思维', mental)

        # 计算年龄修正
        age = read_numeral_attribute('年龄')
        adult_age = read_numeral_attribute('成年年龄')
        if adult_age == 0:
            physical_age_revision = 1
            mental_age_revision = 1
        else:
            physical_age_revision = math.cos(math.log(age / (adult_age * 1.5), math.e)) + 0.12
            mental_age_revision = math.log(age / adult_age, 10) + 0.8
        add_attribute('物理年龄修正', physical_age_revision)
        add_attribute('思维年龄修正', mental_age_revision)

        # 计算体型修正
        size = read_numeral_attribute('体型')
        standard_size = read_numeral_attribute('标准体型')
        if standard_size == 0:
            size_revision = 1
        else:
            size_revision = math.log(size / standard_size, math.e) + 1
        add_attribute('体型修正', size_revision)

        # 计算修正后物理，体质
        physical_revision = physical * physical_age_revision
        add_attribute('物理_修正', physical_revision)
        constitution = read_numeral_attribute('体质')
        constitution_check = physical_revision * constitution / 100 * size_revision
        constitution_check = reserve_decimals(constitution_check)
        add_attribute('体质_检定', constitution_check)

        # 计算体力
        hitpoint_full = format(constitution_check, '.0f')
        add_attribute('总体力', hitpoint_full)

        # 计算力量
        power = read_numeral_attribute('力量')
        power_check = physical_revision * power / 100 * size_revision
        power_check = reserve_decimals(power_check)
        add_attribute('力量_检定', power_check)

        # 计算负重修正
        weight_full = power_check * 10 / level
        weight = read_numeral_attribute('负重')
        weight_revision = -1 * math.pow(weight / weight_full, 2) + 1
        add_attribute('总负重', weight_full)
        add_attribute('负重修正', weight_revision)

        # 计算敏捷
        dexterity = read_numeral_attribute('敏捷')
        dexterity_check = physical_revision * dexterity / 100 * weight_revision
        dexterity_check = reserve_decimals(dexterity_check)
        add_attribute('敏捷_检定', dexterity_check)

        # 计算思维
        mental_revision = mental * mental_age_revision
        add_attribute('思维_修正', mental_revision)

        # def计算思维下副属性
        def mental_attribute_check(element):
            number = read_numeral_attribute(element)
            element_check = mental_revision * number / 100
            return element_check

        willpower = mental_attribute_check('意志')
        willpower_full = willpower
        add_attribute('意志_检定', willpower)
        add_attribute('总意志', willpower_full)

        education_check = mental_attribute_check('教育')
        intelligence_check = mental_attribute_check('智力')
        add_attribute('教育_检定', education_check)
        add_attribute('智力_检定', intelligence_check)

        medicine_and_life_science_check = mental_attribute_check('医学及生命科学')
        engineering_and_technology_check = mental_attribute_check('工程与科技')
        military_and_survival_check = mental_attribute_check('军事与生存')
        literature_check = mental_attribute_check('文学')
        visual_and_performing_art_check = mental_attribute_check('视觉及表演艺术')
        add_attribute('医学及生命科学_检定', medicine_and_life_science_check)
        add_attribute('工程与科技_检定', engineering_and_technology_check)
        add_attribute('军事与生存_检定', military_and_survival_check)
        add_attribute('文学_检定', literature_check)
        add_attribute('视觉及表演艺术_检定', visual_and_performing_art_check)

        # 计算交涉加成
        literature = read_numeral_attribute('文学')
        visual_and_performing_art = read_numeral_attribute('视觉及表演艺术')
        intelligence = read_numeral_attribute('智力')
        appearance = read_numeral_attribute('外貌')
        negotiation_buff = (literature + visual_and_performing_art + intelligence) * \
                           (math.log(mental / physical, 10) + 1) * \
                           (math.log(appearance / 50, math.e) + 1)
        add_attribute('交涉加成', negotiation_buff)

        # 加密角色名到code
        character_name = read_character_attribute('姓名')
        character_code = str(base64.b64encode(character_name.encode()))
        rstr = r'[\/\\\:\*\?\"\<\>\|]'  # '/ \ : * ? " < > |'
        character_code = re.sub(rstr, "", character_code)  # 替换为空

        # 用发送者qq号+角色unicode为文件名.
        folder = f'data/{str(msg.sender)}'
        character_file = f'data/{str(msg.sender)}/chr_{character_code}.txt'
        player_file = f'data/{str(msg.sender)}/plr_{str(msg.sender)}.csv'

        # 储存玩家的角色信息
        header = ['player', 'character', 'code', 'using']
        player_list = [str(msg.sender), character_name, character_code, 1]

        # 创建文件夹
        if not os.path.exists(folder):
            os.makedirs(folder)

        if os.path.exists(player_file):
            csv_file = open(player_file, 'r', newline='', encoding='utf-8-sig', errors='ignore')
            player_dataframe = pd.read_csv(csv_file, header=0, sep=',')
            csv_file.close()
            if character_name not in player_dataframe['character'].values:
                player_dataframe['using'] = player_dataframe['using'].replace(1, 0)
                player_dataframe.loc[-1] = player_list
            player_dataframe.to_csv(player_file, index=False)
        else:
            csv_file = open(player_file, 'w', newline='', encoding='utf-8-sig', errors='ignore')
            writer = csv.writer(csv_file)
            writer.writerow(header)
            writer.writerow(player_list)

        # 最后将字典写入文件
        f = codecs.open(character_file, 'w', 'utf-8')
        f.write(str(attribute_dict))
        f.close()

        character_name = read_character_attribute('姓名')
        send = f'{character_name}的TL属性设置完成√'

        bot.send_friend_msg(qq=msg.sender, msg=send)
