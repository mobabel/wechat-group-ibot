# encoding: utf-8

from ibot_utils import *
from ibot_db import *


def insert_chat_history(group_id, msg_type, wx_puid, gp_user_name, sender_name, receiver_name, msg):
    bot_db.execute("INSERT INTO wx_chat_history (`group_id`, `msg_type`, `wx_puid`, "
                   "`gp_user_name`, `sender_name`, `receiver_name`, `msg`)"
                   " VALUES (%s, %s, %s, %s, %s, %s, %s)",
                   (group_id, msg_type, wx_puid, gp_user_name, sender_name, receiver_name, msg))
    print('db test insert ')
    bot_db.execute("DELETE FROM wx_chat_history where `group_id`=%s and `wx_puid`=%s",
                   (group_id, wx_puid))
    print('db test delete ')


bot_db = BotDatabase.instance(db_config)
insert_chat_history(1, 'Text', 'puid', '@aaa', '测试name', 're_name', '测试message')
print('db test finished')
