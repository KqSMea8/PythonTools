#! /usr/bin/env python
# __author__ = 'Xuecheng Yu'
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#  Copyright YXC
# CreateTime: 2016-07-21 16:08:42

import sys
from optparse import OptionParser

INDEX_MEANING_DICT = {22:"domain", 23:"url", 24:"adspace"}

if __name__ == '__main__':
    parser = OptionParser(usage="%prog [-l] [-o] [-a] [-I] [-f]", version="%prog 1.0")
    parser.add_option("-l", "--log-dir", dest="logdir", help="The directory name of the log file")
    parser.add_option("-o", "--out-dir", dest="outdir", help="The directory name of the out put directory")
    parser.add_option("-a", "--adid", dest="adid", type=int, help="The ad id to statistic")
    help_str = str()
    keys = INDEX_MEANING_DICT.keys()
    keys.sort()
    for key in keys:
        help_str += "%d:%s \n" % (key, INDEX_MEANING_DICT[key])
    parser.add_option("-I", "--index", dest="index", type=int, help="The index of the segements want to statistics, the value should one of the followrs: \n%s      " % (help_str))
    parser.add_option("-f", "--filter", action="append", dest="filter", help="The filter string of the file name, this option could be specified several times")

    options,args = parser.parse_args()
    log_dir_name = options.logdir
    adid = options.adid
    out_dir = options.outdir
    index = options.index
    filters = options.filter

    if log_dir_name == None or adid == None or out_dir == None or index == None or filters == None:
        parser.print_help()
        sys.exit(-1)

    print "log dir: %s" % (log_dir_name)
    print "ad id: %d" % (adid)
    print "out dir: %s" % (out_dir)
    print "index: %d" % (index)
    print "filters: %s" % (filters)
