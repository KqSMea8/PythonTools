#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: ‘yuxuecheng‘
@contact: yuxuecheng@baicdata.com
@software: PyCharm Community Edition
@file: zhihu_auto_login.py
@time: 10/11/2017 17:47
"""

#coding:utf-8
import re
from bs4 import BeautifulSoup
import gzip
import zlib
from http import cookiejar
import urllib2
import ssl
import time


def get_opener(heads):
    cj=cookiejar.CookieJar()
    pro = urllib2.HTTPCookieProcessor(cj)
    opener = urllib2.build_opener(pro)
    header=[]
    for key,value in heads.items():
        header.append((key,value))
    opener.addheaders=header
    return opener


def ungzip(data):
    try:
        print("正在解压....")
        data=gzip.decompress(data)
        print("解压完成")
    except:
        print("无需解压")
    return data


if __name__=="__main__":
    ssl._create_default_https_context = ssl._create_unverified_context
    heads={
            "Accept":"text/html, application/xhtml+xml, */*",
            "Accept-Language":"zh-CN",
            "User-Agent":"Mozilla/5.0 (Windows NT 6.3; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0",
            "Accept-Encoding": "gzip, deflate",
            "Host": "www.zhihu.com",
            "DNT": "1",
            "Connection": "Keep-Alive"
            }
    opener=get_opener(heads)
    url="https://www.zhihu.com/#signin"
    op=opener.open(url)
    data1=op.read()
    print ungzip(data1)
    data1=ungzip(data1).decode('utf-8')
    #print(data1.decode('utf-8'))
    #print(op.read().decode('utf-8'))
#    xsrf=re.findall(r'name="_xsrf" value=".*"',data1)
#    print(xsrf[0])
#    print(type(xsrf[0]))
#    value=xsrf[0].split(" ")
#    print(value)
#    _xsrf=re.findall(r'".*"',value[1])[0]
#    print(_xsrf)
    soup=BeautifulSoup(data1,"html.parser")
    _xsrf=soup.find("input",{'type':'hidden'}).get("value")
    print _xsrf
    password="yuxc870704"
    #captcha_type="cn"
    phone_num="13267243809"
    captcha_url="https://www.zhihu.com/captcha.gif?r=%d&type=login"% (time.time() * 1000)
    captchadata=opener.open(captcha_url).read()
    with open("1.gif",'wb') as file:
        file.write(captchadata)
    yanzhengma=input("captcha:")
    postdata={
        "_xsrf":_xsrf,
        "password":password,
        #"captcha_type":captcha_type,#不能带有这个字段
        # "phone_num":phone_num,
        "captcha":yanzhengma,
        "email": "jayce123@163.com"
        }

    postdata=urllib.urlencode(postdata).encode()
    login_url="https://www.zhihu.com/login/email"
    op2=opener.open(login_url,postdata)
    login_data=op2.read()
    data=ungzip(login_data).decode("utf-8")
    print(data)
    result=dict(eval(data))
    if result["r"]==0:
        print("登录成功")