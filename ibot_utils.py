# encoding: utf-8

import os
import pathlib
import configparser
import datetime
import time
from datetime import date, timedelta

# read configuration
cf = configparser.ConfigParser()
cf.read('wechat.conf')

mysql_host = cf.get('mysql', 'mysql_host')
mysql_port = cf.getint('mysql', 'mysql_port')
mysql_user = cf.get('mysql', 'mysql_user')
mysql_pwd = cf.get('mysql', 'mysql_pwd')
mysql_database = cf.get('mysql', 'mysql_database')

db_config = {'host': mysql_host,  'port': mysql_port, 'user': mysql_user,
             'password': mysql_pwd, 'db': mysql_database, 'charset': 'utf8mb4'}


def get_path_tmp():
    path_tmp = cf.get('wechat', 'path_tmp')
    if not path_tmp:
        path_tmp = os.getcwd()
    else:
        if not os.path.exists(path_tmp) or not os.path.isdir(path_tmp):
            os.mkdir(path_tmp)
    return path_tmp


def get_path_custom(name):
    path_custom = os.path.join(get_path_tmp(), name)
    if not os.path.exists(path_custom):
        os.mkdir(path_custom)
    return path_custom


def get_path_for_file(path, *paths):
    path_result = os.path.join(path, *paths)
    pathlib.Path(path_result).mkdir(parents=True, exist_ok=True)


def mk_datetime(date_string, str_format="%Y-%m-%d %H:%M:%S"):
    # Expects "YYYY-MM-DD" string
    # returns a datetime object
    e_seconds = time.mktime(time.strptime(date_string, str_format))
    return datetime.datetime.fromtimestamp(e_seconds)


def get_first_day(dt, d_years=0, d_months=0):
    # d_years, d_months are "deltas" to apply to dt
    y, m = dt.year + d_years, dt.month + d_months
    a, m = divmod(m-1, 12)
    return date(y+a, m+1, 1)


def get_last_day(dt):
    return get_first_day(dt, 0, 1) + timedelta(-1)


def get_first_last_days():
    d = date.today() - timedelta(days=2)
    first_day = get_first_day(d).strftime('%Y-%m-%d')
    last_day = get_last_day(d).strftime('%Y-%m-%d')
    return [first_day, last_day]


# month 0-11
def get_first_day_(i):
    one_month = '%02d' % (i+1)
    d = mk_datetime("2004-%s-02" % one_month)










