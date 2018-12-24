#!/usr/bin/env python

"""
This script find the stat show failed url and stat show success url
print() is python 3.x built-in function, while in python < 3.x print is a operator
if you want to use print function, should use 'from __future__ import print_function'
"""
from __future__ import print_function
import sys
import os
import logging
import time
import esm
from optparse import OptionParser

import threading


class MyThread(threading.Thread):
    """
    define self Thread class to meet the requirement
    """

    def __init__(self, func, args, name=""):
        threading.Thread.__init__(self)
        self.name = name
        self.func = func
        self.args = args
        self.show_push_id_set = None
        self.stat_show_push_id_set = None

    def run(self):
        logging.info("starting {0} at: {1}, args: {2}".format(self.name, time.ctime(), self.args))
        self.show_push_id_set, self.stat_show_push_id_set = self.func(self.args)
        logging.info("finished {0} at: {1}".format(self.name, time.ctime()))

    def get_result(self):
        return self.show_push_id_set, self.stat_show_push_id_set


def init_logging():
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)-8s %(filename)s:%(lineno)-4d: %(message)s",
                        datefmt="%m-%d %H:%M:%S",
                        filename="show.log",
                        filemode="a")


def get_file_list(dir_name, filters_list):
    if dir_name is None or len(dir_name) == 0:
        return None

    index = esm.Index()
    for i in range(len(filters_list)):
        index.enter(filters_list[i])

    index.fix()
    files = []
    if os.path.isdir(dir_name):
        # three parameters return 1.parent directory, 2.directories, 3.files
        for parent, dir_names, file_names in os.walk(dir_name):
            for filename in file_names:  # display file information
                result = index.query(filename)
                if len(result) == 0:
                    continue
                files.append(os.path.join(parent, filename))
    else:
        if len(index.query(dir_name)) != 0:
            files.append(dir_name)

    return files


def statistics_url_per_file(show_push_id_set, stat_show_push_id_set, statistics_url_dict, file_name):
    """
    get the url that show ad success in file
    """
    if show_push_id_set is None or stat_show_push_id_set is None or file_name is None or len(file_name) == 0:
        return

    # print("filter = " + string.join(id_filter))
    # filter *.tar.gz
    if file_name.find(".tar.gz") != -1:
        return

    if not os.path.isfile(file_name):
        logging.warning(file_name + " is not a file!")
    else:
        if not file_name.find("rtb_log_crit_", 0, len("rtb_log_crit_")):
            logging.warning(file_name + " is not rtb_log_crit log file")
            return
        with open(file_name) as fd:
            for line in fd:
                tokens = [seg.strip() for seg in line.split("\1")]
                if tokens[0] == "rtb_creative":
                    if tokens[7] in stat_show_push_id_set:
                        if tokens[23] in statistics_url_dict:
                            statistics_url_dict[tokens[23]][2] = statistics_url_dict[tokens[23]][2] + 1
                        else:
                            statistics_url_dict[tokens[23]] = [0, 0, 1]
                    elif tokens[7] in show_push_id_set:
                        if tokens[23] in statistics_url_dict:
                            statistics_url_dict[tokens[23]][1] = statistics_url_dict[tokens[23]][1] + 1
                        else:
                            statistics_url_dict[tokens[23]] = [0, 1, 0]
                    else:
                        if tokens[23] in statistics_url_dict:
                            statistics_url_dict[tokens[23]][0] = statistics_url_dict[tokens[23]][0] + 1
                        else:
                            statistics_url_dict[tokens[23]] = [1, 0, 0]
    logging.info("[get_stat_show_url_per_file] finish parse file: " + file_name)


def statistics_url(show_push_id_set, stat_show_push_id_set, statistics_url_dict, file_list):
    """
    get the url that show ad failed in directory
    """
    if show_push_id_set is None or stat_show_push_id_set is None or file_list is None or len(file_list) == 0:
        return

    for file_name in file_list:
        statistics_url_per_file(show_push_id_set, stat_show_push_id_set, statistics_url_dict, file_name)


def generate_stat_show_push_id(show_push_id_set, stat_show_push_id_set, file_name):
    """
    generate the pushid from the file specified by file_name which ad id is
    equvalent to the adid
    """
    if show_push_id_set is None or stat_show_push_id_set is None or file_name is None or len(file_name) == 0:
        return

    # print("filter = " + id_filter)
    # filter *.tar.gz
    if file_name.find(".tar.gz") != -1:
        return

    if not os.path.isfile(file_name):
        print(file_name + " is not a file!")
    else:
        if not file_name.find("rtb_log_crit_", 0, len("rtb_log_crit_")):
            print(file_name + " is not rtb_log_crit log file")
            return
        with open(file_name) as fd:
            for line in fd:
                tokens = [seg.strip() for seg in line.split("\1")]
                if tokens[0] == "stat_show" and tokens[7] not in stat_show_push_id_set:
                    stat_show_push_id_set.add(tokens[7])
                elif tokens[0] == "rtb_show" and tokens[7] not in show_push_id_set:
                    show_push_id_set.add(tokens[7])

    logging.info("[generate_stat_show_push_id] finish parse file: " + file_name)


def generate_stat_show_push_id_thread(file_list):
    """
    generate the pushid list
    """

    if file_list is None or 0 == len(file_list):
        return

    show_push_id_set = set()
    stat_show_push_id_set = set()
    for file_name in file_list:
        generate_stat_show_push_id(show_push_id_set, stat_show_push_id_set, file_name)

    return show_push_id_set, stat_show_push_id_set


def print_url_dict(url_dict):
    for key in url_dict.keys():
        print('{0},{1}'.format(key, url_dict[key]))


def flush_url_dict(url_dict, file_name):
    with open(file_name, mode="w") as out:
        for key, value in sorted(url_dict.items(), key=lambda d: d[1][0], reverse=True):
            out.write('{0},{1},{2},{3}\r\n'.format(key.replace(',','.'), value[0], value[1], value[2]))


def print_push_id_set(push_id_set):
    for push_id in push_id_set:
        print("{0}".format(push_id))


def flush_push_id_set(push_id_set, file_name):
    with open(file_name, mode="w") as out:
        for push_id in push_id_set:
            out.write("{0}\r\n".format(push_id))


FILES_PER_THREAD = 10

if __name__ == "__main__":
    init_logging()

    show_push_id_set = set()
    stat_show_push_id_set = set()
    """
    This dict's structure is as below:
    The key is url, value is the count of the url
    """
    statistics_url_dict = dict()
    out_dir = ""
    logging.info(sys.argv)

    parser = OptionParser()
    parser.add_option('-l', '--log-dir', dest='logdir', help='The directory name of the log file')
    parser.add_option("-o", "--out-dir", dest="outdir", help="The file name of the store result")
    parser.add_option("-f", "--filters", dest="filters", action="append", help="The filter of the file name")

    options,args = parser.parse_args()
    log_dir_name = options.logdir
    out_dir = options.outdir
    filters = options.filters

    logging.info("file name filter: {0}".format(filters))

    if out_dir[len(out_dir) - 1] != os.path.sep:
        out_dir = out_dir + os.path.sep

    if not os.path.isdir(out_dir):
        logging.error("out directory is null!")
        out_dir = ""

    file_list = get_file_list(log_dir_name, filters)
    logging.info("number of log file is %d" % len(file_list))
    out_stat_show_file = out_dir + "url_count_statistics.txt"
    out_pushid_file = out_dir + "stat_show_push_id.txt"
    threads = []
    thread_num = len(file_list) / FILES_PER_THREAD
    if (len(file_list) % FILES_PER_THREAD) != 0:
        thread_num += 1

    logging.info("threads num: {0}".format(thread_num))
    for i in range(thread_num - 1):
        t = MyThread(generate_stat_show_push_id_thread, (file_list[i * FILES_PER_THREAD: (i + 1) * FILES_PER_THREAD]),
                     name=generate_stat_show_push_id_thread.__name__ + "_" + str(i))
        threads.append(t)
    t = MyThread(generate_stat_show_push_id_thread, (file_list[(thread_num - 1) * FILES_PER_THREAD: len(file_list)]),
                 name=generate_stat_show_push_id_thread.__name__ + "_" + str(thread_num - 1))
    threads.append(t)

    for i in range(thread_num):
        threads[i].start()

    for i in range(thread_num):
        threads[i].join()
        temp_show_push_id_set, temp_stat_show_push_id_set = threads[i].get_result()
        logging.info("len of {0} temp_show_push_id_set is {1}, temp_stat_show_push_id_set is {2}".format(threads[i].getName(),
                                                          len(temp_show_push_id_set), len(temp_stat_show_push_id_set)))
        show_push_id_set.update(temp_show_push_id_set)
        stat_show_push_id_set.update(temp_stat_show_push_id_set)

    logging.info("total show push id num: {0}".format(len(show_push_id_set)))
    logging.info("total stat show push id num: {0}".format(len(stat_show_push_id_set)))

    flush_push_id_set(stat_show_push_id_set, out_pushid_file)
    # print_push_id_set(stat_show_push_id_set)
    statistics_url(show_push_id_set, stat_show_push_id_set, statistics_url_dict, file_list)
    # print_url_dict(stat_show_url_dict)
    flush_url_dict(statistics_url_dict, out_stat_show_file)

