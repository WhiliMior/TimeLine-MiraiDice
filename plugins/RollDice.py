import miraicle
import random
import re


# 功能：检查字符串str是否符合正则表达式re_exp
# re_exp:正则表达式
# str:待检查的字符串
def check_string(re_exp, str):
    res = re.search(re_exp, str, re.I)
    if res:
        return True
    else:
        return False


RegularExpression = '^([.]|[。])[r].*'


# 计算小数位数
def digit_count(number):
    s = str(number)
    s_list = s.split(".")
    digits = s_list[1]
    return len(digits)


@miraicle.Mirai.receiver('FriendMessage')
def roll_to_friend(bot: miraicle.Mirai, msg: miraicle.FriendMessage):
    MessageCheck = check_string(RegularExpression, msg.plain)
    pattern = re.compile(r'^(^([.]|[。])[r])', re.I)
    message = str(pattern.sub('', msg.plain).strip())
    if MessageCheck:
        # 如果有d且d两边都有数字，不匹配负数
        if check_string(r'([0-9]+[.]?[0-9]*)+[d]([0-9]+[.]?[0-9]*)+', message):
            pattern = re.compile(r'[0-9]+[.]?[0-9]*', re.I)
            number_list = pattern.findall(message)
            # 把次数变为正整数
            roll_times = int(format(abs(float(number_list[0])), '.0f'))
            # 创建循环并声明空列表
            time = 0
            random_list = []
            while time < roll_times:
                # 检查面数是否有小数点
                if '.' in number_list[1]:
                    dice_sides = float(number_list[1])
                    digits = str(digit_count(dice_sides))
                    random_number = float(format(random.uniform(1, dice_sides), '.' + digits + 'f'))
                else:
                    dice_sides = int(number_list[1])
                    random_number = random.randint(1, dice_sides)
                random_list.append(random_number)
                time += 1

            calculation = '+'.join(map(str, random_list))
            number = str(sum(random_list))
            send = msg.sender_name + '掷骰: ' + str(roll_times) + 'D' + str(dice_sides) + \
                   ': ' + calculation + '=' + number
        elif check_string(r'[d]([0-9]+[.]?[0-9]*)+', message):
            pattern = re.compile(r'[0-9]+[.]?[0-9]*', re.I)
            number_list = pattern.findall(message)
            # 创建循环并声明空列表
            random_list = []
            # 检查面数是否有小数点
            if '.' in number_list[0]:
                dice_sides = float(number_list[0])
                digits = str(digit_count(dice_sides))
                random_number = float(format(random.uniform(1, dice_sides), '.' + digits + 'f'))
            else:
                dice_sides = int(number_list[0])
                random_number = random.randint(1, dice_sides)
            random_list.append(random_number)

            number = str(sum(random_list))
            send = msg.sender_name + '掷骰: ' + 'D' + str(dice_sides) + \
                   ': ' + number
        elif message == '':
            number = str(random.randint(1, 100))
            send = msg.sender_name + '掷骰: D100=' + number

        bot.send_friend_msg(qq=msg.sender, msg=send)


@miraicle.Mirai.receiver('GroupMessage')
def roll_to_group(bot: miraicle.Mirai, msg: miraicle.GroupMessage):
    MessageCheck = check_string(RegularExpression, msg.plain)
    if MessageCheck:
        number = str(random.randint(1, 100))
        send = msg.sender_name + '掷骰: D100=' + number
        bot.send_group_msg(group=msg.group, msg=send)
