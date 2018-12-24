#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: ‘yuxuecheng‘
@contact: yuxuecheng@baicdata.com
@software: PyCharm Community Edition
@file: douban_auto_login.py
@time: 14/11/2017 09:12
"""

import time
import requests
from bs4 import BeautifulSoup
import traceback


headers = {
'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.89 Safari/537.36',
# 'Referer':'https://www.zhihu.com/',
# 'X-Requested-With': 'XMLHttpRequest',
# 'Origin':'https://www.zhihu.com'
}


def login(username, password, kill_captcha):
    session = requests.session()
    resp = BeautifulSoup(session.get('https://www.douban.com/', headers=headers).content)
    try:
        captcha_url = resp.find("img", attrs={'id':'captcha_image'})['src']
        #加入type=login 否则：ERR_VERIFY_CAPTCHA_SESSION_INVALID
        captcha_content = session.get(captcha_url, headers=headers).content
        data = {
            'password': password,
            'captcha': kill_captcha(captcha_content),
            'email': username,
            'remember_me': 'true'
            # 字典的键值对顺序可以随机
        }
        print data
        resp = session.post('https://www.douban.com/accounts/login', data=data, headers=headers).content
        # 登录成功
        print 'resp\n',resp
        # assert r'\u767b\u5f55\u6210\u529f' in resp
        return session
    except TypeError as te:
        traceback.print_exc(te)
        pass


def kill_captcha(data):
    with open('1.gif', 'wb') as fp:
        fp.write(data)
    return raw_input('captcha : ')


if __name__ == '__main__':
    session = login('email', 'password', kill_captcha)
    # print BeautifulSoup(session.get("https://www.zhihu.com",headers=headers).content).find('span', class_='name').getText()