# encoding: utf-8

import codecs
import random
import re
from apscheduler.schedulers.blocking import BlockingScheduler

# local python lib
from wechat_const import *
# import tulingreply
from ibot_db import *
from ibot_utils import *
from ibot_init import *


def get_invalid_name_count(group_id, wx_puid, nickname):
    result = bot_db.get_count("SELECT id FROM wx_chat_nickname_check "
                              "WHERE group_id = %s and (wx_puid = %s or nickname = %s)", (group_id, wx_puid, nickname))
    return result


def insert_invalid_name(group_id, wx_puid, nickname):
    bot_db.execute("INSERT INTO wx_chat_nickname_check (`group_id`, `wx_puid`, `nickname`)"
                   " VALUES (%s, %s, %s)",
                   (group_id, wx_puid, nickname))


def remove_invalid_name(group_id, wx_puid):
    bot_db.execute("DELETE FROM wx_chat_nickname_check WHERE group_id = %s and wx_puid = %s",
                   (group_id, wx_puid))


def remove_emoji(text):
    emoji_pattern = re.compile(
        u"(\ud83d[\ude00-\ude4f])|"  # emoticons
        u"(\ud83c[\udf00-\uffff])|"  # symbols & pictographs (1 of 2)
        u"(\ud83d[\u0000-\uddff])|"  # symbols & pictographs (2 of 2)
        u"(\ud83d[\ude80-\udeff])|"  # transport & map symbols
        u"(\ud83c[\udde0-\uddff])"  # flags (iOS)
        "+", flags=re.UNICODE)

    # (\ud83c[\udc00-\udfff])|
    # (\ud83d[\udc00-\udfff])|[\u2600-\u27ff])

    text = text.replace('★', '')
    return emoji_pattern.sub(r'', text)


def format_readable_nickname(text):
    text = text.replace('&amp;', '&')
    return text


def check_nickname(nickname):
    nickname = str.strip(nickname)
    nickname = nickname.replace('  ', ' ')

    nickname = nickname.replace('｜', '|')

    nickname = nickname.replace(' | ', '|')
    nickname = nickname.replace('| ', '|')
    nickname = nickname.replace(' |', '|')

    nickname = format_readable_nickname(nickname)
    nickname = remove_emoji(nickname)
    if nickname == 'CE助手':
        return True
    # re.sub('  ', ' ', nickname, flags=re.IGNORECASE)
    if re.match(r'([\u4e00-\u9fa5]|[ -~]|[\s\S])+\|([\u4e00-\u9fa5]|[ -~]|[\s\S])+\|([\u4e00-\u9fa5]|[ -~])+', nickname):
        return True
    else:
        return False


class GroupMember:
    def __init__(self, nickname, wx_puid, warn_left):
        self.nickname = nickname
        self.wx_puid = wx_puid
        self.warn_left = warn_left


def process_group_members(group):
    invalid_members = []
    group_id = group.ext_attr.group_id

    # not include region, gender, signature
    # TODO this will change the member's puid ???
    group.update_group(members_details=False)

    # init file handler
    fp = codecs.open(get_path_custom('group_member') + '/%s_member_list.txt' % group_id, 'w+', 'utf-8')

    for member in group:
        nickname = member.name  # display_name
        wx_puid = member.puid
        fp.write(nickname + '\n')
        if not check_nickname(nickname):
            nickname = format_readable_nickname(nickname)

            invalid_member = GroupMember(nickname, wx_puid, 0)
            invalid_members.append(invalid_member)

    # pickup random 5 members and send notice message
    # get non-duplicated elements
    random_members = random.sample(invalid_members, k=notice_random)
    at_members = ''
    for in_member in random_members:
        nickname = in_member.nickname
        wx_puid = in_member.wx_puid

        checked_count = get_invalid_name_count(group_id, wx_puid, nickname)
        # warn_left = kick_max - 1 - checked_count

        # if exceeds maximum notice, kick out member
        if checked_count + 1 >= kick_max:
            kick_out_by_nickname(group, nickname, wx_puid)
            remove_invalid_name(group_id, wx_puid)
        # if has last chance, warn member
        elif checked_count + 1 == kick_max - 1:
            send_checked_name_warning_in_group(group, nickname)
            insert_invalid_name(group_id, wx_puid, nickname)
            at_members += '%s[%s]\n' % (get_at_nickname_with_space(nickname), str(checked_count + 1))
        else:
            insert_invalid_name(group_id, wx_puid, nickname)
            at_members += '%s[%s]\n' % (get_at_nickname_with_space(nickname), str(checked_count + 1))

    send_checked_name_notice_in_group(group, at_members, len(invalid_members))

    fp.close()
    return


def get_at_nickname_with_space(nickname):
    return '@%s%s ' % (nickname, space_after_chat_at)


def kick_out_by_nickname(group, nickname, wx_puid):
    # it could have duplicated nicknames
    # group.members.search(nickname)[0].remove()
    matched_members = group.members.search(nickname)
    res = list(filter(lambda m: m.puid == wx_puid, matched_members))
    if len(res) > 0:
        removed_name = res[0].remove()
        print('kick out member: ' + removed_name)
        send_message_in_group(group, kickout_final_text.format(str(kick_max),
                              get_at_nickname_with_space(nickname), space_after_chat_at))


def send_checked_name_warning_in_group(group, at_member):
    send_message_in_group(group,  kickout_last_warning_text.format(get_at_nickname_with_space(at_member),
                                                                   space_after_chat_at))


def send_checked_name_notice_in_group(group, at_members, invalid_number_count):
    if at_members.strip():
        send_message_in_group(group, kickout_notice_text.format(at_members, str(kick_max), str(invalid_number_count)))


def send_message_in_group(group, message):
    if message.strip():
        if not debug:
            group.send(message)
        # local test
        else:
            bot.file_helper.send(message)


# This will execute a function in the next day at 8a.m. and 8p.m.
def start_schedule_for_checking_member(group):
    scheduler = BlockingScheduler()
    scheduler.add_job(lambda: process_group_members(group), 'cron', hour=8, minute=1, timezone="Europe/Paris")
    scheduler.add_job(lambda: process_group_members(group), 'cron', hour=20, minute=1, timezone="Europe/Paris")
    # local test
    if debug:
        scheduler.add_job(lambda: process_group_members(group), 'cron', hour=16, minute=9)
        scheduler.add_job(lambda: process_group_members(group), 'interval', minutes=1)

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass


# read configuration
debug = False
notice_random = cf.getint('wechat', 'notice_random')
kick_max = cf.getint('wechat', 'kick_max')

# init database instance
bot_db = BotDatabase.instance(db_config)

group_1 = init_group(group_name_1, group_id_1)


@bot.register(group_1, NOTE)
def welcome_for_group(msg):
    try:
        new_member_name = re.search(r'邀请"(.+?)"|"(.+?)"通过', msg.text).group(1)
    except AttributeError:
        print('welcome_for_group error: %s' % msg.text)
        return
    group_1.send(welcome_text.format(new_member_name, space_after_chat_at))


# send owner to confirm
bot.file_helper.send('ibot group member validator is running now')

start_schedule_for_checking_member(group_1)


# keep login by block thread
bot.join()
