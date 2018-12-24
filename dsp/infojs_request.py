#!/usr/bin/env python3
# encoding: utf-8

"""
@version: 1.0
@author: ‘yuxuecheng‘
@contact: yuxuecheng@baicdata.com
@software: PyCharm Community Edition
@file: infojs_request.py
@time: 15/12/2017 18:26
"""

import urllib2

url = 'http://112.124.65.153:9988/info.js?sp=901&spid=jsdsp&sn=0&src=0&mobile=0&url=http%3A//news.163.com/17/0626/21/CNST0FF2000189FH.html&sda_man=FgRRWxJzaVJhBFZfYDUYLGYGVChjAhheagEmLWd0bFssKFJeZAUaW2V1U1NjBg==&uid=FgRRWxJzaVJhBFZfYDUYLGYGVChjAhheagEmLWd0bFssKFJeZAUaW2V1U1NjBg=='

for i in range(10):
    response = urllib2.urlopen(url)
    print response.code
    text = response.readlines()
    print text