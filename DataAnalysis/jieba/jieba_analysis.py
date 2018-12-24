#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'Xuecheng Yu'
# vim:fenc=utf-8
#  Copyright YXC
# CreateTime: 2017-02-08 14:11:40

import sys
import os
reload(sys)
sys.setdefaultencoding('utf8')
sys.path.append('.')
import glob
import re
import jieba
from jieba import analyse
# from jieba import TFIDF
import json
import utility
import traceback

chinese = re.compile(u'[\u4e00-\u9fa5]+')
import redis
import ConfigParser

analyse.set_stop_words('/Users/yuxuecheng/Work/BCData/DataAnalysis/jieba/stop_words.txt')
jieba.load_userdict("/Users/yuxuecheng/Work/BCData/DataAnalysis/jieba/extra_dict.txt")

# seqing = set([u"自拍",u"乱伦",u"制服",u"强奸",u"人妻",u"丝袜",u"成人",u"痴女",u"无码",u"肛交",u"迷奸",u"性爱",u"女优",u"巨乳"])
seqing = set()
# dubo = set([u"澳门",u"投注",u"博彩",u"赌博",u"扑克",u"斗地主"])
dubo = set()

xiaoshuo = set()

suffix_dict = dict()

def load_config(config_file):
    global seqing
    global dubo
    global suffix_dict
    cf = ConfigParser.ConfigParser()
    cf.read(config_file)
    seqing_keys = cf.get("keywords", "seqing")
    dubo_keys = cf.get("keywords", "dubo")
    xiaoshuo_keys = cf.get("keywords", "xiaoshuo")
    gov_suffix = cf.get("suffix", "government").split(";")
    edu_suffix = cf.get("suffix", "education").split(";")
    seqing = set(seqing_keys.decode("utf-8").split(","))
    dubo = set(dubo_keys.decode("utf-8").split(","))
    xiaoshuo = set(xiaoshuo_keys.decode("utf-8").split(","))
    for suffix_temp in gov_suffix:
        suffix_dict[suffix_temp] = "government"

    for suffix_temp in edu_suffix:
        suffix_dict[suffix_temp] = "education"

__suffix__ = ['com', 'cn', 'net', 'org', 'edu', 'vc', 'biz',
              'in', 'co', 'top', 'tech', 'club','tv', 'gov']
__suffix__ = set(__suffix__)

load_config("config.ini")

def split_host(host):
    """
    split host to suffix and middle part
    for example: www.baidu.com return baidu and com, www.whu.edu.cn return whu and edu.cn
    :param host:
    :return:
    """
    try:
        host, port = host.split(':')
    except ValueError:
        host, port = host, None
    segs = host.split('.')
    if len(segs) == 4 and ''.join(segs).isdigit():
        return None, None
    else:
        suffix_tokens = []
        middle_tokens = []
        if segs[0] == "www":
            segs.pop(0)
        for token in segs[::-1]:
            if token in __suffix__:
                suffix_tokens.append(token)

        for token in segs:
            if token not in __suffix__:
                middle_tokens.append(token)
        return ''.join(middle_tokens), '.'.join(suffix_tokens[::-1])

if __name__ == "__main__":
    filename = sys.argv[1]
    full_filename = os.path.split(os.path.realpath(__file__))[0] + os.path.sep + filename
    #print analyse.default_tfidf.stop_words
    #print full_filename
    with open(full_filename, "r") as f:
        for line in f:
            line = line.strip()
            if line is None or len(line) == 0 or line.find('\t') == -1:
                continue
            try:
                url, body = line.split('\t', 1)
                host = utility.url_to_host(url)
                middle, suffix = split_host(host)
                if suffix_dict.has_key(suffix):
                    print u'\t'.join([suffix_dict[suffix], url, suffix])
                    continue

                body = body.decode('utf-8', 'ignore')
                title = body.split('\1')[0]

                # title, keywords, description, p_list, a_list = body.split('\01', 4)
                body = body.replace('\01', ' ')
                if not chinese.search(body):
                    continue
                #tags = analyse.extract_tags(body, topK=20, withWeight=True)
                tags = analyse.extract_tags(body, topK=20, withWeight=False)
                out_tag = json.dumps(tags, ensure_ascii=False)

                comm_seqing = seqing & set(tags)
                # print "comm_seqing" + u'\t'.join([url, out_seqing])
                if len(comm_seqing) > 2:
                    out_seqing = json.dumps(list(comm_seqing), ensure_ascii=False)
                    print u'\t'.join([u"色情", url, out_seqing])
                    continue

                comm_dubo = dubo & set(tags)
                # print "dubo" + u'\t'.join([url, out_dubo])
                if len(comm_dubo) > 2:
                    out_dubo = json.dumps(list(comm_dubo), ensure_ascii=False)
                    print u'\t'.join([u"赌博", url, out_dubo])
                    continue

                comm_xiaoshuo = xiaoshuo & set(tags)
                # print "xiaoshuo" + u'\t'.join([url, out_dubo])
                if len(comm_xiaoshuo) > 2:
                    out_xiaoshuo = json.dumps(list(comm_xiaoshuo), ensure_ascii=False)
                    print u'\t'.join([u"小说", url, out_xiaoshuo])
                    continue
                if (title.find(u"小说")) != -1:
                    print u'\t'.join([u"小说", url, out_tag])
                    continue

                if middle is not None and middle.isalpha() and len(host.split(".")) <= 4:
                    print u'\t'.join(["good site", url, out_tag])
                    continue

                #print u'\t'.join([url, out_tag])
                print u'\t'.join([u"长尾", url, out_tag])

            except Exception:
                print line
                traceback.print_exc()
                continue
    #print analyse.default_tfidf.stop_words