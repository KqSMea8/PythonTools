#!/usr/bin/env python3
# encoding: utf-8

"""
@version: 1.0
@author: ‘yuxuecheng‘
@contact: yuxuecheng@baicdata.com
@software: PyCharm Community Edition
@file: closure.py.py
@time: 02/02/2018 14:16
"""


def tag(tag_name):
    def add_tag(content):
        return '<{0}>{1}</{0}>'.format(tag_name, content)
    return add_tag

@tag
def body(tag_name="body"):
    return add_tag()


if __name__ == '__main__':
    content = "Hello"

    add_tag = tag('a')
    print(add_tag(content))

    add_tag = tag('html')
    print(add_tag(content))

    print(body("content"))