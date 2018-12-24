#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: ‘yuxuecheng‘
@contact: yuxuecheng@baicdata.com
@software: PyCharm Community Edition
@file: weibo_auto_login.py
@time: 26/10/2017 09:49
"""

import sys
import urllib
import urllib2
import cookielib
import base64
import re
import json
import rsa
import binascii
import logging
import time
import os
import traceback

# import requests
# from bs4 import BeautifulSoup


# 新浪微博的模拟登陆
class WeiboLogin(object):

    def __init__(self):
        # 获取一个保存cookies的对象
        # self.cj = cookielib.CookieJar()
        self.cj = cookielib.LWPCookieJar()

    def enable_cookies(self):
        # 将一个保存cookies对象和一个HTTP的cookie的处理器绑定
        cookie_support = urllib2.HTTPCookieProcessor(self.cj)
        # 创建一个opener,设置一个handler用于处理http的url打开
        opener = urllib2.build_opener(cookie_support, urllib2.HTTPHandler)
        # 安装opener，此后调用urlopen()时会使用安装过的opener对象
        urllib2.install_opener(opener)

    @staticmethod
    def get_server_data():
        """
        预登陆获得 servertime, nonce, pubkey, rsakv

        :return:
        """
        # url = 'http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=ZW5nbGFuZHNldSU0MDE2My5jb20%3D&rsakt=mod&checkpin=1&client=ssologin.js(v1.4.18)&_=1442991685270'
        prelogin_url_format = "https://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=&rsakt=mod&client=ssologin.js(v1.4.19)&_=%d"
        cur_time = int((time.time() * 1000))
        prelogin_url = prelogin_url_format % cur_time
        data = urllib2.urlopen(prelogin_url).read()
        try:
            json_data = re.search(r'(\(.*\))', data).group(0)
            data = json.loads(json_data[1:-1])
            server_time = str(data['servertime'])
            nonce = data['nonce']
            pubkey = data['pubkey']
            rsakv = data['rsakv']
            return server_time, nonce, pubkey, rsakv
        except:
            logging.error('Get severtime error!')
            return None

    @staticmethod
    def get_password(password, servertime, nonce, pubkey):
        """
        获取加密后的密码
        :param password:
        :param servertime:
        :param nonce:
        :param pubkey:
        :return:
        """
        rsa_publickey = int(pubkey, 16)
        key = rsa.PublicKey(rsa_publickey, 65537)  # 创建公钥
        message = str(servertime) + '\t' + str(nonce) + '\n' + str(password)  # 拼接明文js加密文件中得到
        password = rsa.encrypt(message, key)  # 加密
        password = binascii.b2a_hex(password)  # 将加密信息转换为16进制。
        return password

    @staticmethod
    def get_username(user_name):
        """
        获取加密后的用户名
        :param user_name:
        :return:
        """
        user_name = urllib.quote(user_name)
        user_name = base64.encodestring(user_name)[:-1]
        return user_name

    @staticmethod
    def get_form_data( user_name, password, servertime, nonce, pubkey, rsakv ):
        """
        获取需要提交的表单数据
        :param user_name:
        :param password:
        :param servertime:
        :param nonce:
        :param pubkey:
        :param rsakv:
        :return:
        """
        user_name = WeiboLogin.get_username(user_name)
        psw = WeiboLogin.get_password(password, servertime, nonce, pubkey)

        form_data = {
            'entry': 'weibo',
            'gateway': '1',
            'from': '',
            'savestate': '7',
            'useticket': '1',
            'pagerefer': 'http://weibo.com/p/1005052679342531/home?from=page_100505&mod=TAB&pids=plc_main',
            'vsnf': '1',
            'su': user_name,
            'service': 'miniblog',
            'servertime': servertime,
            'nonce': nonce,
            'pwencode': 'rsa2',
            'rsakv': rsakv,
            'sp': psw,
            'sr': '1366*768',
            'encoding': 'UTF-8',
            'prelt': '115',
            'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
            'returntype': 'META'
        }
        form_data = urllib.urlencode(form_data)
        return form_data

        # 登陆函数

    def login(self, username, password):
        self.enable_cookies()
        url = 'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)'
        servertime, nonce, pubkey, rsakv = WeiboLogin.get_server_data()
        formData = WeiboLogin.get_form_data(username, password, servertime, nonce, pubkey, rsakv)
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:41.0) Gecko/20100101 Firefox/41.0'}
        req = urllib2.Request(
            url=url,
            data=formData,
            headers=headers
        )
        result = urllib2.urlopen(req)
        text = result.read()
        logging.info("login data: %s" % text.decode("gb2312"))
        # 还没完！！！这边有一个重定位网址，包含在脚本中，获取到之后才能真正地登陆
        try:
            url_data = re.search(r'(\(.*\))', text).group(0)
            login_url = url_data[2:-2]
            logging.info("login_url: %s" % login_url)
            login_req = urllib2.Request(
                url=login_url,
                headers=headers
            )
            # 由于之前的绑定，cookies信息会直接写入
            urllib2.urlopen(login_req)
            logging.info("Login success!")
        except urllib2.URLError as urle:
            traceback.print_exc(urle)
            logging.error('Login error! Error message: %s' % urle.message)
            return -1
        except Exception as e:
            logging.error(e)
            return -1

        # 访问主页，把主页写入到文件中
        # url = 'http://weibo.com/u/2679342531/home?topnav=1&wvr=6'
        url = 'http://www.weibo.com/linusyuno1/home?wvr=5&lf=reg'
        request = urllib2.Request(url)
        response = urllib2.urlopen(request)
        logging.info(response.headers.dict)
        text = response.read()
        filename = os.getcwd() + os.path.sep + "weibo.html"
        fp_raw = open(filename, "w+")
        fp_raw.write(text)
        fp_raw.close()
        logging.info(text.decode("gbk"))


if __name__ == "__main__":
    init_logging("weibo")
    logging.info(u'新浪微博模拟登陆:')
    # username = raw_input(u'用户名：')
    # password = raw_input(u'密码：')
    username = "jayceyxc@gmail.com"
    password = "yuxc870704"
    weibologin = WeiboLogin()
    weibologin.login(username, password)
    filename = os.getcwd() + os.path.sep + 'cookie.txt'
    weibologin.cj.save(filename)