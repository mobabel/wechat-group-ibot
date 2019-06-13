# encoding: utf-8

import configparser
from wxpy import *

# read configuration
cf = configparser.ConfigParser()
cf.read('wechat.conf')
group_name_1 = cf.get('wechat', 'group_name_1')
group_id_1 = cf.get('wechat', 'group_id_1')
group_name_3 = cf.get('wechat', 'group_name_3')
group_id_3 = cf.get('wechat', 'group_id_3')


def init_group(group_name, group_id):
    group = ensure_one(bot.groups().search(group_name))
    group.ext_attr = lambda: None
    setattr(group.ext_attr, 'group_id', group_id)
    setattr(group.ext_attr, 'group_name', group_name)
    return group


# init Wechat bot
bot = Bot(cache_path=True, console_qr=True)
# unique chat person's id
bot.enable_puid()

# add yourself as friend in Wechat so that you can send message to yourself
# bot.self.add()
# bot.self.accept()
