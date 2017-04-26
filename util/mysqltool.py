#!/usr/bin/env python
# coding=utf-8

import MySQLdb
import timetool

class MysqlTool:

    HOST = 'localhost'
    PORT = 3306
    USER = 'root'
    PASSWD = '1234'
    DB = 'test'
    CHARSET = 'utf8'

    def __init__(self):
        self.conn = None
        self.cursor = None
        self.timetool = timetool.TimeTool()

    def connect(self, host=HOST, port=PORT, user=USER,
                passwd=PASSWD, db=DB, charset=CHARSET):
        #连接mysql数据库
        try:
            self.conn = MySQLdb.connect(host=host, port=port, user=user,
                                        passwd=passwd, db=db, charset=charset)
        except MySQLdb.Error as e:
            error_msg = ('%s 连接mysql失败，原因是：[%d]%s' % (self.timetool.get_current_time(),
                         e.args[0], e.args[1]))
            print error_msg
            return False
        #储存数据库游标
        else:
            self.cursor = self.conn.cursor()

        return True

    #查询操作
    def query(self, sql):
        try:
            self.cursor.execute('SET NAMES utf8')
            return self.cursor.execute(sql)
        except MySQLdb.Error as e:
            error_msg = ('%s mysql查询操作失败，原因是：[%d]%s' % (self.timetool.get_current_time(),
                         e.args[0], e.args[1]))
            print error_msg
            return False

    #获取一行数据
    def fetch_one(self):
        try:
            return self.cursor.fetchone()
        except MySQLdb.Error as e:
            error_msg = ('%s 获取一行操作失败，原因是：[%d]%s' % (self.timetool.get_current_time(),
                         e.args[0], e.args[1]))
            print error_msg
            return False

    #获取全部数据
    def fetch_all(self):
        try:
            return self.cursor.fetchall()
        except MySQLdb.Error as e:
            error_msg = ('%s 获取全部操作失败，原因是：[%d]%s' % (self.timetool.get_current_time(),
                         e.args[0], e.args[1]))
            print error_msg
            return False

    #删除、更新、插入操作
    def dui(self, sql):
        try:
            self.cursor.execute('SET NAMES utf8')
            self.cursor.execute(sql)
            self.conn.commit()
            return self.cursor.rowcount
        except MySQLdb.Error as e:
            self.conn.rollback()
            error_msg = ('%s dui操作失败，原因是：[%d]%s' % (self.timetool.get_current_time(),
                         e.args[0], e.args[1]))
            print error_msg
            return False

    def __del__(self):
        self.cursor.close()
        self.conn.close()

    def close(self):
        self.__del__()
