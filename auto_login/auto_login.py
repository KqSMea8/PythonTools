#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: ‘yuxuecheng‘
@contact: yuxuecheng@baicdata.com
@software: PyCharm Community Edition
@file: auto_login.py
@time: 25/10/2017 18:08
"""

import urllib
import urllib2
import httplib
import cookielib
import time


def auto_login_hi(url, name, pwd):
    url_hi = "http://passport.baidu.com/?login"
    # 设置cookie
    cookie = cookielib.CookieJar()
    cj = urllib2.HTTPCookieProcessor(cookie)
    # 设置登录参数
    postdata = urllib.urlencode({'username': name, 'password': pwd})
    # 生成请求
    request = urllib2.Request(url_hi, postdata)
    # 登录百度
    opener = urllib2.build_opener(cj)
    f = opener.open(request)
    print f
    # 打开百度HI空间页面
    hi_html = opener.open(url)
    return hi_html


def auto_login_weibo(url, name, pwd):
    # 设置cookie
    cookie = cookielib.CookieJar()
    cj = urllib2.HTTPCookieProcessor(cookie)
    opener = urllib2.build_opener(cj)

    prelogin_url_format = "https://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=&rsakt=mod&client=ssologin.js(v1.4.19)&_=%d"
    cur_time = int((time.time() * 1000))
    prelogin_url = prelogin_url_format % cur_time
    request = urllib2.Request(prelogin_url)
    f = opener.open(request)
    result = f.read()
    print(result)
    # 设置登录参数
    postdata = urllib.urlencode({'username': name, 'password': pwd})
    # 生成请求
    url_weibo = "http://weibo.com/login.php"
    request = urllib2.Request(url_weibo, postdata)
    # 登录百度
    opener = urllib2.build_opener(cj)
    f = opener.open(request)
    result2 = f.read()
    print(result2)

    weibo_html = opener.open(url)
    return weibo_html


if __name__ == '__main__':
    name = 'jayceyxc@gmail.com'
    password = 'yuxc870704'
    url = 'http://www.weibo.com/'
    h = auto_login_weibo(url, name, password)
    print h.read().decode("gb2312")