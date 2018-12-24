#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: ‘yuxuecheng‘
@contact: yuxuecheng@baicdata.com
@software: PyCharm Community Edition
@file: import_result_into_mysql.py
@time: 31/10/2017 15:31
"""


import sys
reload(sys)
sys.setdefaultencoding('utf8')
import logging
import MySQLdb
import sys
from _mysql_exceptions import DataError, OperationalError
import traceback

"""
CREATE TABLE `bc_user_tag` (
  `adsl` varchar(64) NOT NULL,
  `tag_list` varchar(2028) NOT NULL,
  PRIMARY KEY (`adsl`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
"""


INSERT_SITE_INFO_FORMAT = 'INSERT INTO dmp_site_info (host, domain, suffix, pv_yesterday) ' \
                          'VALUES ("%s", "%s", "%s", %d);'
INSERT_SITE_CONTENT_FORMAT = 'INSERT INTO dmp_site_content (site_id, host, domain, title, keywords, description) ' \
                             'VALUES (%s, %s, %s, %s, %s, %s);'

exist_host_in_mysql = set()
duplicate_num = 0
error_num = 0
line_num = 0
success_num = 0


def init_logging():
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] \
                                %(levelname)s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename='import_host_result.log',
                        filemode='a')


def insert_site_info(site_filename, sql_file_name):
    exist_hosts = set()
    with open(sql_file_name, mode='w+') as out:
        with open(site_filename, mode='r') as fd:
            for line in fd:
                line = line.strip()
                line_segs = [seg.strip() for seg in line.split()]
                if len(line_segs) == 5:
                    host = line_segs[0].lower()
                    domain = line_segs[1].lower()
                    pv = int(line_segs[2])
                    suffix = domain[domain.rfind('.'):]
                elif len(line_segs) == 4:
                    host = line_segs[0].lower()
                    if not host.replace(".","").replace(":","").isdigit():
                        suffix = host[host.rfind('.'):]
                    else:
                        suffix = ""
                    domain = host
                    pv = int(line_segs[1])
                else:
                    continue

                if host in exist_hosts:
                    continue

                if host.find("http:") != -1:
                    continue

                sql_str = INSERT_SITE_INFO_FORMAT % (host, domain, suffix, int(pv))
                out.write(sql_str)
                out.write("\n")
                exist_hosts.add(host)


def get_site_info():
    host_id_dict = dict()
    conn = MySQLdb.connect(host="127.0.0.1", port=33966, user="root", passwd="Mypassword@2qq", db="thinkphp_dmp", charset="utf8")
    # conn = MySQLdb.connect(host="127.0.0.1", port=33966, user="root", passwd="Mypassword@2qq", db="dmp",charset="utf8")
    cursor = conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
    select_sql = "select id, host, domain from dmp_site_info"
    cursor.execute(select_sql)
    for row in cursor.fetchall():
        host_id_dict[row.get('host')] = {"site_id":row.get('id'),
                                         "domain": row.get("domain")}

    cursor.close()
    conn.close()

    return host_id_dict


def norm_host(host):
    if host[:7] == 'http://':
        host = host[7:]
    elif host[:8] == 'https://':
        host = host[8:]

    if host.find('/') != -1:
        host = host[:host.find('/')]

    return host


def insert_spider_result(site_content_filename, host_id_dict):
    global exist_host_in_mysql
    global duplicate_num
    global error_num
    global line_num
    global success_num
    conn = MySQLdb.connect(host="127.0.0.1", port=33966, user="root", passwd="Mypassword@2qq", db="thinkphp_dmp", charset="utf8")
    # conn = MySQLdb.connect(host="127.0.0.1", port=33966, user="root", passwd="Mypassword@2qq", db="dmp", charset="utf8")
    cursor = conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
    batch_num = 0
    values = []

    with open(site_content_filename, mode='r') as fd:
        for line in fd:
            line_num += 1
            line = line.strip()
            line_segs = [seg.strip() for seg in line.split(',')]
            try:
                host = line_segs[0].lower()
                host = norm_host(host)
                title = line_segs[1]
                keywords = line_segs[2]
                description = line_segs[3]
                try:
                    site_id = host_id_dict[host]["site_id"]
                    domain = host_id_dict[host]["domain"]
                except KeyError:
                    error_num += 1
                    logging.info("host %s has no value" % host)
                    continue

                if host in exist_host_in_mysql:
                    duplicate_num += 1
                    continue

                if len(host) >= 256:
                    logging.info("host value is too long: %s" % host)
                    error_num += 1
                    continue

                if len(domain) >= 128:
                    logging.info("domain value is too long: %s" % domain)
                    error_num += 1
                    continue

                if len(title) >= 2048:
                    logging.info("title value is too long: %s" % title)
                    error_num += 1
                    continue

                if len(keywords) >= 2048:
                    logging.info("keywords value is too long: %s" % keywords)
                    error_num += 1
                    continue

                if len(description) >= 4096:
                    logging.info("description value is too long: %s" % description)
                    error_num += 1
                    continue
                values.append((site_id, host, domain, title, keywords, description))
                exist_host_in_mysql.add(host)
                batch_num += 1
                if batch_num == 50:
                    result = cursor.executemany(INSERT_SITE_CONTENT_FORMAT, values)
                    conn.commit()
                    success_num += result
                    logging.info("insert %d records" % result)
                    batch_num = 0
                    values = []
            except UnicodeEncodeError as uee:
                logging.error(traceback.print_exc())
                logging.error(uee.message)
                continue
            except ValueError as ve:
                logging.error(traceback.print_exc())
                logging.error(ve.message)
                continue
            except KeyError as ke:
                logging.error(traceback.print_exc())
                logging.error(ke.message)
                continue
            except DataError as de:
                logging.error(traceback.print_exc())
                logging.error(de.message)
                continue
            except OperationalError as oe:
                logging.error(traceback.print_exc())
                logging.error(oe.message)
                cursor.close()
                conn.close()
                conn = MySQLdb.connect(host="127.0.0.1", port=33966, user="root", passwd="Mypassword@2qq",
                                       db="thinkphp_dmp", charset="utf8")
                cursor = conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
                batch_num = 0
                values = []
                continue

    try:
        if batch_num > 0:
            result = cursor.executemany(INSERT_SITE_CONTENT_FORMAT, values)
            logging.info("last insert %d records" % result)
            success_num += result

        conn.commit()
        cursor.close()
        conn.close()
    except DataError as de:
        logging.error(traceback.print_exc())
        logging.error(de.message)
    except OperationalError as oe:
        logging.error(traceback.print_exc())
        logging.error(oe.message)


if __name__ == "__main__":
    init_logging()
    # insert_site_info('site_info.txt', 'site_info.sql')
    # print len(sys.argv)
    host_id_dict = get_site_info()
    for i in range(1, len(sys.argv)):
        logging.info("Process file %s" % sys.argv[i])
        insert_spider_result(sys.argv[i], host_id_dict)

    logging.info("total unique host number: %d" % len(exist_host_in_mysql))
    logging.info("duplicate host times: %d" % duplicate_num)
    logging.info("error number: %d" % error_num)
    logging.info("total line number: %d" % line_num)
    logging.info("total success number: %d" % success_num)