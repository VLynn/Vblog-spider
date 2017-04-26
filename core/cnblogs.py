#!/usr/bin/env python
# coding=utf-8

"""
This is a web spider progress, which crawl cnblogs.com
Vblog爬虫模块，爬取cnblogs博客

"""

import requests
import re
import json
import sys
import traceback
import time
from util import timetool, setting
from bs4 import BeautifulSoup
from selenium import webdriver
from pymongo import MongoClient, errors as MongoErrors

class Cnblogs:

    def __init__(self):
        self.base_url = 'http://www.cnblogs.com'
        self.log_path = '/home/lynn/Vblog/out/cnblogs.log'
        self.timetool = timetool.TimeTool()
        #博客来源网站编号
        self.source_num = 1
        #博客列表页面编号
        self.page_index = 1
        #博客内容分类
        self.blog_classify = 'python'

    #获取整个静态页面，返回经过bs解析后的soup对象
    def get_page(self, index_url):
        try:
            response = requests.get(index_url)
            soup = BeautifulSoup(response.text, 'lxml')
            return soup
        except Exception as e:
            exstr = traceback.format_exc()
            print self.timetool.get_current_time(), '获取静态页面失败\n', exstr
            return None

    #获取整个动态界面，返回经过bs解析过的soup对象
    def get_dynamic_page(self, index_url):
        try:
            driver = webdriver.PhantomJS()
            driver.get(index_url)
            soup = BeautifulSoup(driver.page_source, 'lxml')
            driver.close()
            return soup
        except Exception as e:
            exstr = traceback.format_exc()
            print self.timetool.get_current_time(), '获取动态页面失败\n', exstr
            driver.close()
            return None

    #获取总页数
    def get_page_num(self, soup):
        try:
            div_tag = soup.find('div', id='pager_bottom')
            page_num = div_tag.find('a', class_='last').string.strip()
            return page_num
        except Exception as e:
            exstr = traceback.format_exc()
            print exstr

    #获取下一页链接
    def get_next_page(self, soup):
        try:
            a_tag = soup.find('div', id='pager_bottom').find('a', class_='last').next_sibling
            return a_tag['href']
        except Exception as e:
            exstr = traceback.format_exc()
            print exstr
            return None

    #获取一页的所有博客链接列表
    def get_blog_links(self, soup):
        div_tag = soup.find_all('div', class_='post_item')
        links = []
        for tag in div_tag:
            links.append(tag.h3.a['href'])
        if not links:
            print '获取博客链接列表失败'
        return links

    #提取博客详细内容
    def get_blog_content(self, soup):
        try:
            blog_content = {}
            post_info_div = soup.find(class_=re.compile('postDesc|posthead|postfoot|itemdesc'))
            blog_content['title'] = soup.find('a', id='cb_post_title_url').string.strip()
            blog_content['text'] = soup.find('div', id='cnblogs_post_body').get_text().strip()
            blog_content['author'] = post_info_div.span.next_sibling.next_sibling.string.strip()
            blog_content['post_time'] = post_info_div.span.string.strip()
            blog_content['view_count'] = post_info_div.find('span', id='post_view_count').string.strip()
            blog_content['comment_count'] = post_info_div.find('span', id='post_comment_count').string.strip()
            #TODO 博客标签还需要完善
            blog_content['tags'] = []
            tags = soup.find('div', id='BlogPostCategory').find_all('a')
            for tag in tags:
                blog_content['tags'].append(tag.string.strip())
            return blog_content
        except Exception as e:
            exstr = traceback.format_exc()
            print exstr
            return None

    #获取一份博客详情页的内容，并正则匹配，提取出需要内容，以字典格式返回
    def get_blog_dict(self, link):
        #获取一整页内容
        soup = self.get_dynamic_page(link)

        blog_content = self.get_blog_content(soup)
        #检查匹配结果
        if not blog_content:
            print self.timetool.get_current_time(), '匹配博客详细内容失败, link =', link
            return None

        #返回json结构结果
        blog_content['link'] = link
        blog_content['source'] = self.source_num
        return blog_content

    #向数据库中插入一条数据
    def insert_to_db(self, client, data):
        try:
            client.admin.command('ismaster')
        except ConnectionFailure:
            print self.timetool.get_current_time(), 'Mongo server not available'
            #TODO 添加断线重连，从上次断点继续工作的功能

        try:
            db = client[setting.mongo['DB']]
            collection = db[setting.mongo['COLLECTION']]
            collection.insert_one(data)
            return True
            #collection.update(data, data, True)
        except MongoErrors.DuplicateKeyError as e:
            return True
        except Exception as e:
            exstr = traceback.format_exc()
            print exstr
            return False

    def main(self, index_url):
        #开始程序执行时间计时
        self.timetool.start()
        #初始界面处理
        soup = self.get_page(index_url)
        page_num = self.get_page_num(soup)
        blog_link_list = self.get_blog_links(soup)
        #连接数据库
        db_url = ('mongodb://'+setting.mongo['USER']+':'+setting.mongo['PWD']
                  +'@localhost/'+setting.mongo['DB'])
        client = MongoClient(db_url)
        #调整默认输出为日志文件
        fout = open(self.log_path, 'a+')
        sys.stdout = fout

        if not page_num:
            print self.timetool.get_current_time(), '获取页数失败'
            return None
        if not blog_link_list:
            print self.timetool.get_current_time(), '获取博客链接列表失败'
            return None
        print '开始爬取cnblogs，待爬页面共%s页\n' % (page_num)

        #还有下一页时，循环爬取下一页
        page_count = 1
        while True:
            #将缓冲区内容写到磁盘，方便实时查看输出，但比较耗CPU
            fout.flush()
            print '正在爬取第 %d 页博客' % (page_count)
            for link in blog_link_list:
                data = self.get_blog_dict(link)
                if not data:
                    continue
                self.insert_to_db(client, data)
            page_count += 1

            #爬取下一页
            page_link = self.get_next_page(soup)
            if not page_link:
                print '未获取到下一页'
                break

            #博客列表为空，一般是页面加载了，但内容没加载出来，尝试重新加载该页面3次
            reconnect_count = 0
            while reconnect_count < 3:
                #有时候加载比较慢，暂停1s以防没加载出内容部分
                time.sleep(1)
                soup = self.get_page(self.base_url + page_link)
                blog_link_list = self.get_blog_links(soup)
                if not blog_link_list:
                    reconnect_count += 1
                    continue
                break

        print '待爬页面全部爬取结束'
        #结束计时
        self.timetool.end()
        print '\n共耗时:', self.timetool.spend()
        client.close()
        fout.close()

    def test(self, index_url):
        db_url = ('mongodb://'+setting.mongo['USER']+':'+setting.mongo['PWD']
                  +'@localhost/'+setting.mongo['DB'])
        client = MongoClient(db_url)
        blog_data = self.get_blog_dict('http://www.cnblogs.com/sonata/p/6722681.html')
        if blog_data:
            self.insert_to_db(client, blog_data)
        client.close()

index_url = 'http://www.cnblogs.com/cate/python'
cnblogs = Cnblogs()
cnblogs.main(index_url)
