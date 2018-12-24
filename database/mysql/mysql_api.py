#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @Time    : 2018/11/15 09:49
# @Author  : yuxuecheng
# @Contact : yuxuecheng@xinluomed.com
# @Site    : 
# @File    : mysql_api.py
# @Software: PyCharm
# @Description mysql数据库api

import MySQLdb


def connect_mysql(host='localhost', user='root', password='', database='', port=3306, charset='utf8'):
    """
    连接数据库
    :param host: 数据库主机
    :param user: 用户名
    :param password: 密码
    :param database: 数据库名
    :param port: 端口
    :param charset: 字符集
    :return: 数据库连接
    """
    db = MySQLdb.connect(host=host,
                         user=user,
                         passwd=password,
                         db=database,
                         port=port,
                         charset=charset,
                         init_command='show tables;')
    return db


def test():
    conn = connect_mysql("192.168.56.103",3306,"root","Linus_dev!@#123","mysql")
    cursor = conn.cursor()
    cursor.execute("show databases")
    ret = cursor.fetchall()
    for i in ret:
        print i

    cursor.close()
    conn.close()


if __name__ == "__main__":
    test()
