import miraicle
import re

send = "控制：\n" \
       ".bot 机器人信息\n" \
       ".bot on 开启本群功能\n" \
       ".bot off 关闭本群功能\n" \
       ".dismiss 退群\n" \
       "角色：\n" \
       ".chr 显示现有角色\n" \
       ".chr {序号} 选择角色\n" \
       ".chr show 显示角色属性\n" \
       ".chr del {序号} 删除选定角色\n" \
       "检定：\n" \
       ".tar {目标数值} 固定数值\n" \
       ".tar {等级} {难度} 计算数值\n" \
       ".tar {等级}d 随机难度\n" \
       ".ex {属性/领域} 进行检定\n" \
       ".neg {rp评分} 进行交涉\n" \
       ".neg {对象等级} {对象智力%} 设定交涉对象\n" \
       ".neg {rp评分} {对象等级} {对象智力%} 设定交涉对象并交涉\n" \
       "战斗及记录：\n" \
       ".bat 直接显示时间轴\n" \
       ".bat end 删除时间轴\n" \
       ".bat {属性} {时间}t/{影响数值} (笔记)  战斗指令\n" \
       ".pre {属性} {影响数值} 计算时间\n" \
       ".pre {属性} {时间}t 计算数值\n" \
       ".crd 体力/意志 {变化值}\n" \
       ".crd hp/mp {变化值}\n" \
       ".crd reset 重置数据\n" \
       ".crd del 删除记录\n"


def check_string(re_exp, str):
    res = re.search(re_exp, str, re.I)
    if res:
        return True
    else:
        return False


reg_exp = '^([.]|[。])help.*'


@miraicle.Mirai.receiver('GroupMessage')
def help_to_group(bot: miraicle.Mirai, msg: miraicle.GroupMessage):
    message_check = check_string(reg_exp, msg.plain)
    if message_check:
        bot.send_group_msg(group=msg.group, msg=send, quote=msg.id)


@miraicle.Mirai.receiver('FriendMessage')
def help_to_friend(bot: miraicle.Mirai, msg: miraicle.FriendMessage):
    message_check = check_string(reg_exp, msg.plain)
    if message_check:
        bot.send_friend_msg(qq=msg.sender, msg=[miraicle.Plain(send)])
