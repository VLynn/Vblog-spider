#!/usr/bin/env python
# coding=utf-8

import time

class TimeTool:

    start_time = 0
    end_time = 0

    #返回格式化的当前时间
    def get_current_time(self):
        return time.strftime('[%Y-%m-%d %H:%M:%S]', time.localtime())

    #返回格式化的当前日期
    def get_current_date(self):
        return time.strftime('%Y-%m-%d', time.localtime())

    #脚本刚开始时调用
    def start(self):
        self.start_time = time.time()

    #脚本结束时调用
    def end(self):
        self.end_time = time.time()

    #计算脚本花费的时间
    def spend(self):
        spent_time = round(self.end_time - self.start_time, 4)
        result_str = ''

        if spent_time > 86400:
            days = int(spent_time // 86400)
            result_str += str(days) + '天 '
            spent_time = spent_time % 86400
        if spent_time > 3600:
            hours = int(spent_time // 3600)
            result_str += str(hours) + '时 '
            spent_time = spent_time % 3600
        if spent_time > 60:
            mins = int(spent_time // 60)
            result_str += str(mins) + '分 '
            spent_time = spent_time % 60

        result_str += str(spent_time) + '秒'
        return result_str
