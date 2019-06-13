#!/usr/bin/env python
# encoding: utf-8

import configparser
import json
import requests
from wxpy import *

# read configuration
cf = configparser.ConfigParser()
cf.read('wechat.conf')
tuling_api_key = cf.get('wechat', 'tuling_api_key')


# init Tuling bot
tuling = Tuling(api_key=tuling_api_key)

# tuling auto reply
def auto_reply(msg):
    tuling.do_reply(msg)


def manual_reply(info='ibot'):
    api_url = 'http://www.tuling123.com/openapi/api'
    data = {'key': tuling_api_key, 'info':  info}
    req = requests.post(api_url, data=data).text
    return json.loads(req)['text']
