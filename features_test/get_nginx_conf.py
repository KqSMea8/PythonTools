#! /usr/bin/env python
__author__ = 'Xuecheng Yu'
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#  Copyright YXC
# CreateTime: 2016-05-04 11:56:38

import sys
import os
import logging
import re


def init_logging():
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)-8s %(filename)s:%(lineno)-4d: %(message)s",
                        datefmt="%m-%d %H:%M:%S",
                        filename="get_nginx_conf.log",
                        filemode="a")


def get_file_set(dir_name, filters):
    logging.info("directory: {0}, filters: {1}".format(dir_name, filters))
    if None == dir_name or 0 == len(dir_name):
        return None

    if filters.startswith("*."):
        filters = "\S*" + filters[2:] + "$"
    elif filters.startswith("*"):
        filters = "\S*" + filters[1:] + "$"

    files = set()
    if os.path.isdir(dir_name):
        for parent, dirnames, filenames in os.walk(
                dir_name):  # three parameters return 1.parent directory, 2.directorys, 3.files
            for filename in filenames:  # display file information
                m = re.match(filters, filename)
                if (m):
                    logging.info("in get_file_set add file: {0}".format(os.path.join(parent, filename)))
                    files.add(os.path.join(parent, filename))
    else:
        if re.match(filters, filename):
            logging.info("in get_file_set add file: {0}".format(dir_name))
            files.add(dir_name)

    return files


def get_conf_file_set(file_name, file_set, conf_prefix, parse_file_set):
    if (file_name[0] != '/'):
        if (conf_prefix[len(conf_prefix) - 1] != '/'):
            file_name = conf_prefix + os.sep + file_name
        else:
            file_name = conf_prefix + file_name

    if (True != os.path.exists(file_name)):
        logging.warn("{0} is not exist".format(file_name))
        return;

    with open(file_name, mode="r") as fd:
        for line in fd:
            line = line.strip()
            """
            deal with include directives,only this directives will add conf file 
            """
            if (line.startswith("#")):
                """
                This is comment line
                """
                logging.info("This is a comment line: {0}".format(line))
                continue;
            if (line.find("include") != -1):
                logging.info("include line: {0}".format(line))
                strs = line.split()
                """
                deal with include /data/nginx/*.conf   ;
                in this situation, the strs has 3 segments
                """
                if (len(strs) >= 2):
                    include_file = strs[1]
                    """
                    deal with wildcard character, such as
                    include /data/nginx/*.conf
                    """
                    if (include_file.find("*.conf") != -1):
                        logging.info("include * dir: {0}".format(include_file))
                        slash_index = include_file.rfind('/')
                        include_dir = include_file[:slash_index]
                        filter_pattern = ""
                        if (include_file.endswith(";")):
                            filter_pattern = include_file[slash_index + 1:-1]
                        else:
                            filter_pattern = include_file[slash_index + 1:]
                        files = get_file_set(include_dir, filter_pattern)
                        file_set.update(files)
                        for file in files:
                            logging.info("add file {0} in directory {1}".format(file, include_dir))

                        for file in files:
                            if (file not in parse_file_set):
                                get_conf_file_set(file, file_set, include_dir,
                                                  parse_file_set)
                                parse_file_set.add(file)

                    else:
                        semicolon_index = include_file.rfind(';')
                        include_file = include_file[:semicolon_index]
                        if (include_file[0] != '/'):
                            include_file = conf_prefix + os.sep + include_file
                        """
                        deal with include /data/nginx/test.conf    ;
                        """
                        include_file = include_file.strip()
                        file_set.add(include_file)
                        logging.info("add file directly {0}".format(include_file))

                        if (include_file not in parse_file_set):
                            get_conf_file_set(include_file, file_set,
                                              conf_prefix, parse_file_set)


def get_file_content(total_file_set, file_name):
    with open(file_name, mode="wa") as writefd:
        for file in total_file_set:
            writefd.write("file name: {0}\n".format(file))
            if (True == os.path.exists(file)):
                with open(file, mode="r") as readfd:
                    for line in readfd:
                        writefd.write(line)
            else:
                logging.warn("{0} is not exist".format(file))

            writefd.write("\n")


if __name__ == "__main__":
    init_logging()
    conf_file = "/etc/nginx/nginx.conf"
    out_file = "nginx_total.conf"
    if (len(sys.argv) == 2):
        conf_file = sys.argv[1]

    if (len(sys.argv) == 3):
        conf_file = sys.argv[1]
        out_file = sys.argv[2]

    logging.info("original nginx conf file: {0}".format(conf_file))
    slash_index = conf_file.rfind('/')
    conf_prefix = conf_file[:slash_index]
    total_file_set = set()
    parse_file_set = set()
    parse_file_set.add(conf_file)
    get_conf_file_set(conf_file, total_file_set, conf_prefix, parse_file_set)
    logging.info("file number: {0}".format(len(total_file_set)))
    for file in total_file_set:
        logging.info("in total file set, file name: {0}".format(file))

    get_file_content(total_file_set, out_file)
