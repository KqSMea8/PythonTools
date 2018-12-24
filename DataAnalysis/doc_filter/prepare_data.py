#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: ‘yuxuecheng‘
@contact: yuxuecheng@baicdata.com
@software: PyCharm Community Edition
@file: prepare_data.py
@time: 14/08/2017 15:25
"""

import sys
import traceback

from MySQLdb import IntegrityError, ProgrammingError, DataError, OperationalError
from MySQLdb import connect

import utility
import re

chinese = re.compile(u'[\u4e00-\u9fa5]+')


def get_result_urls(results_file):
    urls_set = set()
    with open(results_file, mode='r') as fd:
        for line in fd:
            line = line.strip()
            segs = line.split(",")
            if len(segs) < 6:
                continue
            host = utility.spider_url_to_dpi_url(segs[0])
            host = utility.url_to_host(host)
            # print("add host {0}".format(host))
            urls_set.add(host)

    return urls_set


def insert_host_info( host_pv_file, urls_set, host="127.0.0.1", port=3306, user="root", password="", database="test" ):
    print("urls len: {0}".format(len(urls_set)))
    conn = connect(host=host, port=port, user=user, passwd=password, db=database, charset='utf8')
    cursor = conn.cursor()
    with open(host_pv_file, mode='r') as fd:
        for line in fd:
            line = line.strip()
            host, pv = line.split(" ")
            if host not in urls_set:
                # print("host {0} not in urls set".format(host))
                continue

            host = utility.spider_url_to_dpi_url(host)
            host = utility.url_to_host(host)
            suffix = utility.get_suffix(host)
            insert_sql = "insert into dmp_site_info (domain, suffix, pv_yesterday) values (\"{0}\", \"{1}\", {2});".format(
                host, suffix, int(pv))
            # print(insert_sql)
            try:
                cursor.execute(insert_sql)
            except IntegrityError as ie:
                traceback.print_exc(ie)

    conn.commit()
    conn.close()


def get_site_id(host, conn):
    cursor = conn.cursor()
    query_sql = "select id from dmp_site_info where domain=\"{0}\";".format(host)
    cursor.execute(query_sql)
    res = cursor.fetchall()
    site_id = 0
    for it in res:
        site_id = int(it[0])
        break

    return site_id


def insert_host_content( results_file, host="127.0.0.1", port=3306, user="root", password="", database="test" ):
    conn = connect(host=host, port=port, user=user, passwd=password, db=database, charset='utf8')
    cursor = conn.cursor()
    count = 0
    failed_count = 0
    ie_failed_count = 0
    pe_failed_count = 0
    de_failed_count = 0
    oe_failed_count = 0
    with open(results_file, mode="r") as fd:
        for line in fd:
            line = line.strip()
            segs = line.split(",")
            if len(segs) < 6:
                continue
            host = utility.spider_url_to_dpi_url(segs[0])
            host = utility.url_to_host(host)
            title = segs[1]
            keywords = segs[2]
            description = segs[3]
            if title is None or not chinese.search(title.decode('utf8')):
                continue
            if keywords is None or not chinese.search(title.decode('utf8')):
                continue

            site_id = get_site_id(host, conn)
            if site_id == 0:
                print("get site id for host {0} failed".format(host))
                failed_count += 1
                continue
            insert_sql = "insert into dmp_site_content (site_id, domain, title, keywords, description) values ({0}, \"{1}\", \"{2}\", \"{3}\", \"{4}\");".format(
                site_id, host, title, keywords, description)
            try:
                cursor.execute(insert_sql)
            except IntegrityError as ie:
                traceback.print_exc(ie)
                ie_failed_count+=1
                continue
            except ProgrammingError as pe:
                traceback.print_exc(pe)
                print("Error sql: {0}".format(insert_sql))
                pe_failed_count += 1
                continue
            except DataError as de:
                traceback.print_exc(de)
                print("Error sql: {0}".format(insert_sql))
                de_failed_count += 1
                continue
            except OperationalError as oe:
                traceback.print_exc(oe)
                print("Error sql: {0}".format(insert_sql))
                oe_failed_count += 1
                continue
            count += 1
            if count > 100:
                conn.commit()
                count = 0

    conn.commit()
    conn.close()
    print("get site id failed number: {0}".format(failed_count))
    print("IntegrityError failed number: {0}".format(ie_failed_count))
    print("ProgrammingError failed number: {0}".format(pe_failed_count))
    print("DataError failed number: {0}".format(de_failed_count))
    print("OperationalError failed number: {0}".format(oe_failed_count))


if __name__ == "__main__":
    host = "127.0.0.1"
    port = 33966
    user = "root"
    password = "Mypassword@2qq"
    database = "dmp"
    results_file = sys.argv[1]
    host_file = sys.argv[2]
    print("results_bak file: {0}, host file: {1}".format(results_file, host_file))
    # urls_set = get_result_urls(results_file)
    # insert_host_info(host_file, urls_set=urls_set, host=host, port=port, user=user, password=password,
    #                  database=database)
    insert_host_content(results_file=results_file, host=host, port=port, user=user, password=password,
                        database=database)
