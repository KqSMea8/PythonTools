#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

reload(sys)
sys.setdefaultencoding('utf8')
import MySQLdb
import socket
import struct
from sortedcontainers import SortedList

region_table = set()
region_list = SortedList()
ip_set = list()

liaoning = [18961496, 18960186, 18958875, 18957564, 18968705, 18967395, 18968050, 18962152, 18960841, 18959530,
            18958220, 18956909, 18966739, 18969361, 18956254]

dbconf = {
    "host": "202.97.211.3",
    "user": "root",
    "password": "Mypassword@2qq",
    "db": "rmc",
    "table": "rmc_area_ip",
    "port": "3306"
}


class IpRange(object):
    def __init__(self, start_long, end_long, area_name, region_id):
        self.start_long = start_long
        self.end_long = end_long
        self.area_name = area_name
        self.region_id = region_id

    def __eq__(self, other):
        """
        
        :param other: the object need to be test whether in the list
        :return: 
        """
        """
        SortedList use this function to decide the element is in list, the other is the 
        IpRange need to be judge whether in the container, the self is the IpRange already in the
        container
        
        self: area_name: 沈阳 start ip: 983171072, end ip: 983180031
        other: area_name: 测试 start ip: 983172357, end ip: 983172357
        """
        # print "__eq__"
        # print self
        # print other

        if self.start_long <= other.start_long and self.end_long >= other.end_long:
            return True
        else:
            return False

    def __cmp__(self, other):
        """
        OrderList use this function to decide the order of this class
        :param other: 
        :return: 
        """
        # print "__cmp__"
        if self.start_long > other.end_long:
            # print "__cmp_1__"
            return 1
        elif self.end_long < other.start_long:
            # print "__cmp_minus_1__"
            return -1
        else:
            # print "__cmp_0__"
            return 0

    def __hash__(self):
        """
        set and dict use thie function to decide whether the element is in set of dict
        """
        # print "__hash__"
        return hash(str(self.start_long) + " " + str(self.end_long))

    def __repr__(self):
        return u"region_id: {0}, area_name: {1} start ip: {2}, end ip: {3}".format(self.region_id, self.area_name, self.start_long, self.end_long)

    def set_ip(self, ip):
        self.start_long = ip2long(ip)
        self.end_long = ip2long(ip)


def ip2long(ip):
    """
    Convert an IP string to long
    """
    packedIP = socket.inet_aton(ip)
    return struct.unpack("!L", packedIP)[0]


def get_region_table():
    # print get_region_table.__name__
    # print dbconf["host"]
    try:
        conn = MySQLdb.connect(host=dbconf['host'], port=int(dbconf['port']), user=dbconf['user'],
                               passwd=dbconf['password'], db=dbconf['db'])
        cur = conn.cursor()
        sql = "select id, start_ip, end_ip, area_name from {0}".format(dbconf['table'])
        # print sql
        data = cur.fetchmany(cur.execute(sql))
        for item in data:
            region_id = item[0]
            if int(item[0]) in liaoning:
                begin_ip = ip2long(item[1])
                end_ip = ip2long(item[2])
                area_name = item[3].encode("utf-8")
                ip_range = IpRange(begin_ip, end_ip, area_name, region_id)
                # print "read from mysql: {0}".format(ip_range)
                region_list.add(ip_range)

        cur.close()
        conn.close()
    except MySQLdb.Error, e:
        print "Mysql Error {0}:{1}".format(e.args[0], e.args[1])


def display_ip_region(region_list_):
    for ip_range in region_list_:
        print ip_range


def read_ip_from_file(filename):
    with open(filename) as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip("\n\r")
            ip_set.append(line)


ip_result = {}


def find(ip):
    ip_range = IpRange(0, 0, u"测试", 0)
    ip_range.set_ip(ip)
    try:
        index = region_list.index(ip_range)
        if index != -1:
            # print ip
            # print region_list[index]
            region_id = region_list[index].region_id
            if region_id in ip_result:
                ip_result[region_id] += 1
            else:
                ip_result[region_id] = 1
    except ValueError as ve:
        pass


def main():
    # print main.__name__
    get_region_table()
    # display_ip_region(region_list)
    print len(region_list)
    # print type(region_list)
    # ReadAdslFromFile( "ln_ip.txt" )
    # print len(ip_set)
    with open("ip_record.tt", mode='r') as fd:
        for line in fd:
            line = line.strip()
            find(line)

    for k in ip_result.keys():
        print("region id: {0}, count: {1}".format(k, ip_result[k]))


def test():
    region_list.add(IpRange(1881735168, 1881767935, u"沈阳", 18956909))
    print "first finished"
    region_list.add(IpRange(1881624576, 1881632767, u"沈阳", 18956909))
    print "second finished"
    region_list.add(IpRange(983171072, 983180031, u"沈阳", 18956909))
    print "third finished"
    for k in region_list:
        print k
    ip_range = IpRange(0, 0, u"测试", 0)
    # iprange.set_ip("58.154.5.5")
    ip_range.set_ip("112.41.5.5")
    print "judge in"
    index = region_list.index(ip_range)
    print index
    if index > -1:
        print region_list[index]
        print region_list[index].area_name
        print region_list[index].region_id

    if ip_range in region_list:
        print "True"
    else:
        print "False"


if __name__ == "__main__":
    main()
