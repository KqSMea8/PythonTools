#!/usr/bin/env python3
# encoding: utf-8

"""
@version: 1.0
@author: ‘yuxuecheng‘
@contact: yuxuecheng@baicdata.com
@software: PyCharm Community Edition
@file: generate_uid_creative_noad_map.py
@time: 20/12/2017 16:49
"""

import glob
import os
import sys
import time
import logging
import json
from optparse import OptionParser

"""
这个脚本用于解析bidder日志，分析日志中每一个uid投放的广告次数和过滤的广告次数
"""

no_uid_number = 0
error_uid_number = 0


def init_logging():
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)-8s %(filename)s:%(lineno)-4d: %(message)s",
                        datefmt="%m-%d %H:%M:%S",
                        filename="generate_uid_creative_noad_map.log",
                        filemode="a")


def generate_uid_ad_map(log_path):
    global no_uid_number
    global error_uid_number
    uid_ad_map = dict()
    glob_pattern = log_path
    if os.path.isfile(log_path):
        pass
    elif not log_path.endswith(os.path.sep):
        glob_pattern += os.path.sep + '*.log'
    else:
        glob_pattern += '*.log'

    for filename in glob.iglob(glob_pattern):
        with open(filename, mode='r') as fd:
            for line in fd:
                segs = [seg.strip() for seg in line.strip().split("\1")]
                if len(segs) >= 40 and segs[0] == "rtb_creative" or segs[0] == 'rtb_noAd':
                    try:
                        uid = segs[38]
                        aid = segs[6]
                        if uid is None or len(uid) == 0:
                            no_uid_number += 1
                            continue
                        elif len(uid) != 40:
                            error_uid_number += 1
                            continue

                        if uid in uid_ad_map:
                            if segs[0] == 'rtb_creative':
                                uid_ad_map[uid].setdefault('creative', []).append(aid)
                            else:
                                uid_ad_map[uid].setdefault('filter', []).append(aid)
                        else:
                            ad_map = dict()
                            if segs[0] == 'rtb_creative':
                                ad_map.setdefault('creative', []).append(aid)
                                ad_map.setdefault('filter', [])
                            else:
                                ad_map.setdefault('creative', [])
                                ad_map.setdefault('filter', []).append(aid)

                            uid_ad_map[uid] = ad_map
                    except IndexError:
                        logging.error(line)
                        continue

    return uid_ad_map


if __name__ == '__main__':
    init_logging()
    logging.info(sys.argv)

    parser = OptionParser()
    parser.add_option('-l', '--log-dir', dest='logdir', help='The directory name of the log file')
    parser.add_option("-o", "--out-file", dest="outfile", help="The file name of the store uid ad map")

    options,args = parser.parse_args()
    log_dir_name = options.logdir
    out_file_name = options.outfile

    if log_dir_name is None or out_file_name is None:
        parser.print_help()
        sys.exit(0)

    logging.info("begin generate_uid_ad_map: %s" % time.asctime())
    uid_ad_map = generate_uid_ad_map(log_dir_name)
    logging.info("end generate_uid_ad_map: %s" % time.asctime())
    logging.info('no_uid_number: %d' % no_uid_number)
    logging.info('error_uid_number: %d' % error_uid_number)
    with open(out_file_name, mode='w') as out:
        for uid in uid_ad_map:
            out.write("%s, %s\n" % (uid, json.dumps(uid_ad_map[uid])))
            print("%s, %d, %d" % (uid, len(uid_ad_map[uid]['creative']), len(uid_ad_map[uid]['filter'])))

    logging.info("begin flush file: %s" % time.asctime())
