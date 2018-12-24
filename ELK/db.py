#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: ‘yuxuecheng‘
@contact: yuxuecheng@baicdata.com
@software: PyCharm Community Edition
@file: db.py.py
@time: 08/11/2017 17:15
"""

import MySQLdb


class DbUtil(object):
    @staticmethod
    def get_ad_info():
        _db = MySQLdb.connect(host="10.54.8.89",  # your host
                              port=33306,
                              user="root",  # username
                              passwd="Mypassword@2qq",  # password
                              db="adp")  # name of the database
        ad_map={}
        cur = _db.cursor()
        cur.execute("select adid,group_id,plan_id from adp_ad_info;")

        for row in cur.fetchall() :
            ad_map[row[0]] = {"group_id": int(row[1]), "plan_id": int(row[2])}
        return ad_map

    @staticmethod
    def get_city_info():
        _db = MySQLdb.connect(host="10.54.8.89",  # your host
                              port=33306,
                              user="root",  # username
                              passwd="Mypassword@2qq",  # password
                              db="rmc")  # name of the database
        city_provice_map = dict()
        cur = _db.cursor()
        cur.execute("select id, parent_id, area_name, level, region_name from rmc_area")

        for row in cur.fetchall():
            city_id = int(row[0])
            province_id = int(row[1])
            city_name = row[2]
            level = int(row[3])
            province_name = row[4]

            if level == 0:
                continue

            print ("city_name: %s, province_name: %s" % (city_name, province_name))
            city_provice_map[city_id] = {"city_name": city_name, "province_name": province_name}

        return city_provice_map
