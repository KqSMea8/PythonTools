#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'Xuecheng Yu'
# vim:fenc=utf-8
#  Copyright YXC
# CreateTime: 2017-02-09 14:03:51

import re
import jieba

abs_path="/Users/yuxuecheng/Work/BCData/DataAnalysis/jieba/stop_words.txt"
stop_words = set()
content = open(abs_path, 'rb').read().decode('utf-8')
for line in content.splitlines():
    stop_words.add(line)

print stop_words
sentence = "我是一个中国人我爱北京天安门3D test which"
words = jieba.dt.cut(sentence)
zhPattern = re.compile(u'[\u4e00-\u9fa5]+')
for w in words:
    print w
    if zhPattern.search(w) == None:
        continue
    print w in stop_words
    print w.lower() in stop_words

