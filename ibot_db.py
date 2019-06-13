# encoding: utf-8

import time
import threading
from DBUtils.PooledDB import PooledDB, SharedDBConnection
from DBUtils.PersistentDB import PersistentDB, PersistentDBError, NotSupportedError
import pymysql


class BotDatabase(object):
    """
    Bot database object::

        from bot_db import *
        bot_db = BotDatabase.instance(db_config)

        Use connection pool here to close connection after usage
        If not closed, the pool will be occupied and throws pymysql.err.OperationalError: 2006
    """

    __instance = None
    _instance_lock = threading.Lock()

    def __init__(self, db_config, maxconn=5):
        time.sleep(1)

        self.db_config = db_config
        self.maxconn = maxconn

        self.conn = None
        self.cursor = None
        self.pool_db = self._get_db_pool(False)
        self._connect()

    """
    PooledDB: use for multiple threads, if app starts/stops often
    PersistentDB: use for single thread, if app connects db often in single thread
    """
    def _get_db_pool(self, is_mult_thread=False):
        key = ['host', 'port', 'user', 'password', 'db', 'charset']
        if not all([True if k in self.db_config else False for k in key]):
            raise Exception(list(self.db_config.keys()), "Mysql connect failure, please check parameters")

        if is_mult_thread:
            pool_db = PooledDB(
                # using the linked database module
                creator=pymysql,
                # The maximum number of connections allowed in the connection pool,
                # 0 and None means no limit on the number of connections
                maxconnections=self.maxconn,
                # At the time of initialization, at least the idle link created in the link pool,
                # 0 means not created
                mincached=2,
                # The most idle link in the link pool,
                # 0 and None are not restricted
                maxcached=self.maxconn,
                # The maximum number of links shared in the link pool, 0 and None indicate all shares.
                # PS: Useless, because the threadsafety of modules such as pymysql and MySQLdb is 1.
                # If all values ​​are set, _maxcached will always be 0, so all links will always be shared.
                maxshared=3,
                # Whether to block waiting if there is no connection available in the connection pool.
                # True, wait; False, don't wait and then report an error
                blocking=True,
                # The number of times a link is reused at most, and None means unlimited
                maxusage=1000,
                # List of commands executed before starting the session.
                # Such as: ["set datestyle to ...", "set time zone ..."]
                setsession=[],
                # ping the MySQL server to check if the service is available.
                # :0 = None = never,
                # 1 = default = whenever it is requested,
                # 2 = when a cursor is created,
                # 4 = when a query is executed,
                # 7 = always
                ping=0,
                **self.db_config
            )
        else:
            pool_db = PersistentDB(
                creator=pymysql,
                maxusage=1000,
                closeable=False,
                # current thread occupied object for saving connected object
                # threadlocal=None,
                **self.db_config
            )
        return pool_db

    def _connect(self):
        self.conn = self.pool_db.connection()
        self.cursor = self.conn.cursor()

    """
    give connection back to pool
    """
    def _close(self):
        if self.conn:
            self.cursor.close()
            self.conn.close()

    def _commit(self):
        try:
            if self.conn:
                self.conn.commit()
        except pymysql.Error as e:
            # logutil.Logger().error(e)
            # traceback.print_exc()
            raise pymysql.Error("Mysql commit failure: %s" % e)

    def _rollback(self):
        try:
            if self.conn:
                self.conn.rollback()
        except pymysql.Error as e:
            # logutil.Logger().error(e)
            # traceback.print_exc()
            raise pymysql.Error("Mysql rollback failure: %s" % e)
        finally:
            self._close()

    def __del__(self):
        self._close()

    def query_execute(self, sql, args=None):
        try:
            self._connect()
            result_list = []
            self.cursor.execute(sql, args)
            for row in self.cursor.fetchall():
                result_list.append(row)
            return result_list
        except pymysql.Error as e:
            # logutil.Logger().error(e)
            # traceback.print_exc()
            raise pymysql.Error("Mysql query failure: %s" % e)
        finally:
            self._close()

    def dml_execute(self, sql, args=None):
        try:
            self._connect()
            self.cursor.execute(sql, args)
            self._commit()
            affected = self.cursor.rowcount
            return affected
        except pymysql.Error as e:
            # logutil.Logger().error(e)
            # traceback.print_exc()
            self._rollback()
            raise pymysql.Error("Mysql dml failure: %s" % e)
        finally:
            self._close()

    def dml_execute_many(self, sql, args=None):
        try:
            self._connect()
            self.cursor.executemany(sql, args)
            self._commit()
            affected = self.cursor.rowcount
            return affected
        except pymysql.Error as e:
            # logutil.Logger().error(e)
            # traceback.print_exc()
            self._rollback()
            raise pymysql.Error("Mysql dml many failure: %s" % e)
        finally:
            self._close()

    def get_count(self, sql, args=None):
        return len(self.query_execute(sql, args))

    def select(self, sql, args=None):
        return self.query_execute(sql, args)

    def execute(self, sql, args=None):
        return self.dml_execute(sql, args)

    def execute_many(self, sql, args=None):
        return self.dml_execute_many(sql, args)

    @classmethod
    def instance(cls, *args, **kwargs):
        if not hasattr(BotDatabase, "_instance"):
            with BotDatabase._instance_lock:
                if not hasattr(BotDatabase, "_instance"):
                    BotDatabase._instance = BotDatabase(*args, **kwargs)
        return BotDatabase._instance

