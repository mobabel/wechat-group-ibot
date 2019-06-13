welcome_text = '''********\U0001F389\U0001F389\U0001F389\U0001F389********\n
 欢迎 @{}{} 加入本群！\n
 新人进群请按群规修改昵称\n\n
 *******************************'''

kickout_final_text = '''
经{}次提醒后不予理会，现在很遗憾将@{}{}一脚踢开/:bye:
'''

kickout_last_warning_text = '''
@{}{} 你还有最后一次机会更改群昵称，下次将无警告直接踢出群。 \n\n更多细节请看群公告
'''

kickout_notice_text = '''
{} 以上昵称未设置或不符合标准，请按如下标准更改昵称：\n
昵称|专业领域|擅长框架&语言 \n\n
[{}]次提醒后将自动踢出\n
尚有{}个昵称不符合标准\n
更多细节请看群公告，谢谢支持
'''


# Special char after @nickname, it is a unprintable char ' '
# But @someone in group to notice member is not possible via WeChat web API
# It could have been blocked by WeChat
space_after_chat_at = u'\u2005'
