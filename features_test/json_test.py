#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#  Copyright © YXC
# CreateTime: 2016-03-10 13:25:12

"""
exmple for test json lib
"""

import json

def json_parse_host(host_set_object):
    json_obj = json.loads(host_set_object)
    white_host = json_obj["_include_host"]
    print(type(white_host))
    for host in white_host:
        print("type: {0}, value: {1}".format(type(host), host))


def json_read_file(file_name, call_back):
    with open(file_name, "r") as read_fd:
        for line in read_fd:
            line = line.strip()
            call_back(line)

if __name__ == '__main__':
    json_read_file("json_data.txt", json_parse_host)
