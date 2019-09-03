welcome_text = '''********\U0001F389\U0001F389\U0001F389\U0001F389********\n
 欢迎 @{}{} 加入本群！\n
 新人进群请按群规修改昵称:\n
 昵称|专业领域|擅长框架&语言&当前工作 \n
 其中两个符号|为半角管道符 \n\n
 更多帮助请看群公告，或者@ IT群助手 并发送：help\n
 *******************************'''

kickout_final_text = '''
经{}次提醒后不予理会，很遗憾要将下列群员一脚踢开/:bye:
{}{}
'''

kickout_last_warning_text = '''
{}{} 以上群员还有最后一次机会更改群昵称，下次将无警告直接踢出群。 \n\n更多细节请看群公告
'''

kickout_notice_text = '''
{} 以上昵称不符合标准，请按如下标准更改昵称：\n
昵称|专业领域|擅长框架&语言&当前工作 \n
其中两个符号|为半角管道符 \n
[{}]次提醒后将自动踢出\n
尚有{}个昵称不符合标准\n
更多细节请看群公告，谢谢支持
'''

group_help_text = '''
🔧 @ IT群助手 并发送如下指令获取信息

· jobs: 获取职业信息小程序
· rule: 群规
'''

group_rule_text = '''
👮 群规
{}次提醒后还坚持不改昵称的人，将被群助手自动踢出群！群主无法控制😔

新人进群请按群规修改昵称:
昵称|专业领域|擅长框架&语言&当前工作
如：
小呆|学生|想找数据分析工作
中二|前端|njs,react
大傻|机器学习|nlp
老痴|汽车|java,c++

其中两个符号|为半角管道符

查看之前发布的职位信息，以及职业薪酬相关信息，请下载小程序：
《欧洲职业信息分享》

更多帮助请@ IT群助手 并发送：help
'''

group_miniapp_text = '''
请使用小程序获取最新的德国以及周边国家的IT职业信息:
欧洲职业信息分享
'''

# Special char after @nickname, it is a unprintable char ' '
# But @someone in group to notice member is not possible via WeChat web API
# It could have been blocked by WeChat
space_after_chat_at = u'\u2005'
