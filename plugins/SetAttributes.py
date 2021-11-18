import miraicle
import re
import codecs
import math
import os


def check_string(re_exp, str):
    res = re.search(re_exp, str, re.I)
    if res:
        return True
    else:
        return False


reg_exp = '^([.]|[。])sfullt.*'
# 匹配中文+英文和空格+数字的格式
search_attribute = r'[\u4e00-\u9fa5]+[_a-zA-Z\s]*-?\d*'

@miraicle.Mirai.receiver('FriendMessage')
def set_to_friend(bot: miraicle.Mirai, msg: miraicle.FriendMessage):
    message_check = check_string(reg_exp, msg.plain)
    if message_check:
        # 需要非完整导入的方法
        # 通过正则查找属性
        pattern = re.compile(search_attribute)
        attributes = pattern.findall(msg.plain)
        file_name = str(msg.sender)

        # def将特定行中属性提取为数字
        def read_attribute(element):
            file_name = str(msg.sender)
            if os.path.exists(r'data\%s.txt' % file_name) is False:
                return None
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

        def read_chinese_attribute(element):
            file_name = str(msg.sender)
            if os.path.exists(r'data\%s.txt' % file_name) is False:
                return None
            else:
                f = codecs.open(r'data\%s.txt' % file_name, 'r', 'utf-8')
                lines = f.readlines()
                for line in lines:
                    if element in line:
                        return ''.join(line.split(element)).strip()
                f.close()

        # def追加属性
        def add_attribute(element, number):
            number = str(number)
            f = codecs.open(r'data\%s.txt' % file_name, 'a', 'utf-8')
            f.write(element + number + '\n')
            f.close()

        # for循环写入列表
        f = codecs.open(r'data\%s.txt' % file_name, 'w', 'utf-8')
        for line in attributes:
            f.write('%s\n' % line)
        f.close()

        # 计算现金
        attribute = read_attribute('资产')
        if attribute < 0:
            cash = '-' + str(math.pow(attribute, 4) / math.pow(10, 4))
        else:
            cash = str(math.pow(attribute, 4) / math.pow(10, 4))
        add_attribute('现金', cash)

        # 计算能力
        level = read_attribute('等级')
        ability = level * 100
        add_attribute('能力', ability)

        # def保留两位小数
        def reserve_decimals(number):
            return float(format(number, '.2f'))

        # 计算物理
        ratio = read_attribute('物理思维比值')
        physical = ability - (ratio * level) / 10
        add_attribute('物理', physical)

        # 计算思维
        mental = ability - physical
        add_attribute('思维', mental)

        # 计算年龄修正
        age = read_attribute('年龄')
        adult_age = read_attribute('成年年龄')
        if adult_age == 0:
            physical_age_revision = 1
            mental_age_revision = 1
        else:
            physical_age_revision = math.cos(math.log(age / (adult_age * 1.5), math.e)) + 0.12
            mental_age_revision = math.log(age / adult_age, 10) + 0.8
        add_attribute('物理年龄修正', physical_age_revision)
        add_attribute('思维年龄修正', mental_age_revision)

        # 计算体型修正
        size = read_attribute('体型')
        standard_size = read_attribute('标准体型')
        if standard_size == 0:
            size_revision = 1
        else:
            size_revision = math.log(size / standard_size, math.e) + 1
        add_attribute('体型修正', size_revision)

        # 计算修正后物理，体质
        physical_revision = physical * physical_age_revision
        add_attribute('物理_修正', physical_revision)
        constitution = read_attribute('体质')
        constitution_check = physical_revision * constitution / 100 * size_revision
        constitution_check = reserve_decimals(constitution_check)
        add_attribute('体质_检定', constitution_check)

        # 计算体力
        hitpoint_full = format(constitution_check, '.0f')
        add_attribute('总体力', hitpoint_full)

        # 计算力量
        power = read_attribute('力量')
        power_check = physical_revision * power / 100 * size_revision
        power_check = reserve_decimals(power_check)
        add_attribute('力量_检定', power_check)

        # 计算负重修正
        weight_full = power_check * 10 / level
        weight = read_attribute('负重')
        weight_revision = -1 * math.pow(weight / weight_full, 2) + 1
        add_attribute('总负重', weight_full)
        add_attribute('负重修正', weight_revision)

        # 计算敏捷
        dexterity = read_attribute('敏捷')
        dexterity_check = physical_revision * dexterity / 100 * weight_revision
        dexterity_check = reserve_decimals(dexterity_check)
        add_attribute('敏捷', dexterity_check)

        # 计算思维
        mental_revision = mental * mental_age_revision
        add_attribute('思维_修正', mental_revision)

        # def计算思维下副属性
        def mental_attribute_check(element):
            number = read_attribute(element)
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
        literature = read_attribute('文学')
        visual_and_performing_art = read_attribute('视觉及表演艺术')
        intelligence = read_attribute('智力')
        appearance = read_attribute('外貌')
        negotiation_buff = (literature + visual_and_performing_art + intelligence) * \
                           (math.log(mental / physical, 10) + 1) * \
                           (math.log(appearance / 50, math.e) + 1)
        add_attribute('交涉加成', negotiation_buff)

        # 提取玩家角色名
        f = codecs.open(r'data\%s.txt' % file_name, 'r', 'utf-8')
        lines = f.readlines()
        for line in lines:
            if '姓名' in line:
                character_name = ''.join(line.split('姓名')).strip()

        f.close()

        bot.send_friend_msg(qq=msg.sender, msg=[miraicle.Plain(character_name),
                                                miraicle.Plain('的TL属性设置完成√')])


@miraicle.Mirai.receiver('GroupMessage')
def set_to_group(bot: miraicle.Mirai, msg: miraicle.GroupMessage):
    message_check = check_string(reg_exp, msg.plain)
    if message_check:

        # 通过正则查找属性
        pattern = re.compile(search_attribute)
        # 只匹配英文pattern = re.compile(r'[a-zA-Z]+\d*')
        attributes = pattern.findall(msg.plain)
        file_name = str(msg.sender)

        # for循环写入列表
        f = codecs.open(r'data\%s.txt' % file_name, 'w', 'utf-8')
        for line in attributes:
            f.write('%s\n' % line)
        f.close()

        # def将特定行中属性提取为数字
        def read_attribute(element):
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

        # def追加属性
        def add_attribute(element, number):
            number = str(number)
            f = codecs.open(r'data\%s.txt' % file_name, 'a', 'utf-8')
            f.write(element + number + '\n')
            f.close()

        # 计算现金
        attribute = read_attribute('资产')
        if attribute < 0:
            cash = '-' + str(math.pow(attribute, 4) / math.pow(10, 4))
        else:
            cash = str(math.pow(attribute, 4) / math.pow(10, 4))
        add_attribute('现金', cash)

        # 计算能力
        level = read_attribute('等级')
        ability = level * 100
        add_attribute('能力', ability)

        # def保留两位小数
        def reserve_decimals(number):
            return float(format(number, '.2f'))

        # 计算物理
        ratio = read_attribute('物理思维比值')
        physical = ability - (ratio * level) / 10
        add_attribute('物理', physical)

        # 计算思维
        mental = ability - physical
        add_attribute('思维', mental)

        # 计算年龄修正
        age = read_attribute('年龄')
        adult_age = read_attribute('成年年龄')
        if adult_age == 0:
            physical_age_revision = 1
            mental_age_revision = 1
        else:
            physical_age_revision = math.cos(math.log(age / (adult_age * 1.5), math.e)) + 0.12
            mental_age_revision = math.log(age / adult_age, 10) + 0.8
        add_attribute('物理年龄修正', physical_age_revision)
        add_attribute('思维年龄修正', mental_age_revision)

        # 计算体型修正
        size = read_attribute('体型')
        standard_size = read_attribute('标准体型')
        if standard_size == 0:
            size_revision = 1
        else:
            size_revision = math.log(size / standard_size, math.e) + 1
        add_attribute('体型修正', size_revision)

        # 计算修正后物理，体质
        physical_revision = physical * physical_age_revision
        add_attribute('物理_修正', physical_revision)
        constitution = read_attribute('体质')
        constitution_check = physical_revision * constitution / 100 * size_revision
        constitution_check = reserve_decimals(constitution_check)
        add_attribute('体质_检定', constitution_check)

        # 计算体力
        hitpoint_full = format(constitution_check, '.0f')
        add_attribute('总体力', hitpoint_full)

        # 计算力量
        power = read_attribute('力量')
        power_check = physical_revision * power / 100 * size_revision
        power_check = reserve_decimals(power_check)
        add_attribute('力量_检定', power_check)

        # 计算负重修正
        weight_full = power_check * 10 / level
        weight = read_attribute('负重')
        weight_revision = -1 * math.pow(weight / weight_full, 2) + 1
        add_attribute('总负重', weight_full)
        add_attribute('负重修正', weight_revision)

        # 计算敏捷
        dexterity = read_attribute('敏捷')
        dexterity_check = physical_revision * dexterity / 100 * weight_revision
        dexterity_check = reserve_decimals(dexterity_check)
        add_attribute('敏捷', dexterity_check)

        # 计算思维
        mental_revision = mental * mental_age_revision
        add_attribute('思维_修正', mental_revision)

        # def计算思维下副属性
        def mental_attribute_check(element):
            number = read_attribute(element)
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
        literature = read_attribute('文学')
        visual_and_performing_art = read_attribute('视觉及表演艺术')
        intelligence = read_attribute('智力')
        appearance = read_attribute('外貌')
        negotiation_buff = (literature + visual_and_performing_art + intelligence) * \
                           (math.log(mental / physical, 10) + 1) * \
                           (math.log(appearance / 50, math.e) + 1)
        add_attribute('交涉加成', negotiation_buff)

        # 提取玩家角色名
        f = codecs.open(r'data\%s.txt' % file_name, 'r', 'utf-8')
        lines = f.readlines()
        for line in lines:
            if '姓名' in line:
                character_name = ''.join(line.split('姓名')).strip()

        f.close()

        bot.send_group_msg(group=msg.group, msg=[miraicle.Plain(character_name),
                                                 miraicle.Plain('的TL属性设置完成√')])
