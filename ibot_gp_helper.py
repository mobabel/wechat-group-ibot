# encoding: utf-8

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

# local python lib
# import tulingreply
from ibot_db import *
from ibot_init import *
from ibot_chat_analyse import *


def insert_chat_history(group_id, msg_type, wx_puid, gp_user_name, sender_name, receiver_name, msg):
    bot_db.execute("INSERT INTO wx_chat_history (`group_id`, `msg_type`, `wx_puid`, "
                   "`gp_user_name`, `sender_name`, `receiver_name`, `msg`)"
                   " VALUES (%s, %s, %s, %s, %s, %s, %s)",
                   (group_id, msg_type, wx_puid, gp_user_name, sender_name, receiver_name, msg))


def save_message(msg, group_id):
    # create_time = msg.create_time.strftime('%Y-%m-%d %H:%M:%S')
    member_name = msg.member.name
    wx_puid = msg.member.puid
    gp_user_name = msg.member.user_name
    message = ''
    if msg.type == TEXT:
        # word = "%s %s:%s\n" % (create_time, member_name, msg.text)
        # print(word.encode('utf-8'))
        message = msg.text
        # tulingreply.tuling_auto_reply(msg)

    if msg.type == NOTE:
        message = msg.text

    elif msg.type == SHARING:
        # public account pushed articles
        art_list = msg.articles
        for item in art_list:
            print(item.url + ' ' + item.title + ' ' + item.summary)
            message = item.url + '||' + item.title + '||' + item.summary
        # shared link
        if not message:
            message = msg.url

    elif msg.type in [RECORDING, PICTURE, ATTACHMENT, VIDEO]:
        ct_yyyy = msg.create_time.strftime('%Y')
        ct_md = msg.create_time.strftime('%m-%d')
        path_file = os.path.join(get_path_for_file(get_path_custom('attachment'), ct_yyyy, ct_md), msg.file_name)
        msg.get_file(path_file)
        message = path_file

    elif msg.type == MAP:
        message = msg.location

    insert_chat_history(group_id, msg.type, wx_puid, gp_user_name, member_name, '', message)


def process_schedule(bot_db_, bot_, group_):
    bot_analyze = BotAnalyze(bot_db_, bot_, group_)
    bot_analyze.start_analysis_tasks()


def start_schedule_for_analyzing():
    scheduler = BlockingScheduler()
    # 08:10am at the first day of the month
    scheduler.add_job(lambda: process_schedule(bot_db, bot, group_1), 'cron',
                      month='1-12', day=1, hour=8, minute=1, timezone="Europe/Paris")
    # local test
    if debug:
        # scheduler.add_job(lambda: process_schedule(bot_db, bot, group_1),
        # 'cron', hour=17, minute=31, timezone="Europe/Paris")
        scheduler.add_job(lambda: process_schedule(bot_db, bot, group_1), 'interval', minutes=2)

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass


# read configuration
debug = False
day = time.strftime("%Y-%m-%d")

# init database instance
bot_db = BotDatabase.instance(db_config)

group_1 = init_group(group_name_1, group_id_1)
group_3 = init_group(group_name_3, group_id_3)


@bot.register(group_1, except_self=False)
def reg_msg_for_group(msg):
    save_message(msg, group_id_1)


@bot.register(group_3, except_self=False)
def reg_msg_for_group(msg):
    save_message(msg, group_id_3)


# @bot.register(group_1)
# def auto_reply(msg):
#     # If is from group but not @ mentioned, ignore
#     if not (isinstance(msg.sender, Group) and not msg.is_at):
#         message = '{}'.format(msg.text)
#         group_1.send(tulingreply.manual_reply(info=message)+'\n\t\t\t\t\t--ibot')


# Reply the message which sent to bot itself, can be used to test
# @bot.register(bot.self, except_self=False)
# def reply_self(msg):
#     message = 'received: {} ({})'.format(msg.text, msg.type)
#     bot.self.send(message)


# send owner to confirm
bot.file_helper.send('ibot group helper is running now')

start_schedule_for_analyzing()

# keep login by block thread
bot.join()
