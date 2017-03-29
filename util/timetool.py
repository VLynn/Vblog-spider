#!/usr/bin/env python
# coding=utf-8

import time

def get_current_time():
    return time.strftime('[%Y-%m-%d %H:%M:%S]', time.localtime())

def get_current_date():
    return time.strftime('%Y-%m-%d', time.localtime())
