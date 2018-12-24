#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: ‘yuxuecheng‘
@contact: yuxuecheng@baicdata.com
@software: PyCharm Community Edition
@file: get_push_ad_amount.py
@time: 20/12/2017 12:58
"""

import sys


def parse_query(query_str):
    query_dict = {}
    for seg in query_str.split("&"):
        try:
            key, value = seg.split("=", 1)
        except ValueError:
            continue
        query_dict[key] = value

    return query_dict


def get_push_ad_amount(filename):
    """
    log example:
    124.228.215.28 - - [19/Dec/2017:00:00:00 +0800] "GET /info.js?sn=ads68970371&time=1513612801470&mobile=1&sp=4303&aid=12120&sda_man=&src=0&adtype=18&uid=EXsmUhY1bC9hdFFTZAcfWGBCU1xqAWwsYXohWxYHbytjASZcFgEdKQ==&spid=hljunicom&ad_list=12120&mobileFixed=0&width_page=359&wid
th_screen=375&url=http%3A//m.qiuwu.net/html/288/288212/55574765.html HTTP/1.1" 200 77 "http://m.qiuwu.net/html/288/288212/55574765.html" "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0_3 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A432 Safari/
604.1" - "0.000" || "0.000"

    :param filename: The nginx log file name
    :return:
    """
    ad_stat = dict()
    with open(filename, mode='r') as fd:
        for line in fd:
            try:
                line = line.strip()
                segs = line.split("\"")
                for seg in segs:
                    """
                    这里要用/info.js?，不能只用info.js，否则下面这样的请求会导致异常
                    
                    58.222.50.204 - - [19/Dec/2017:08:08:07 +0800] "GET /info.js?sn=ads90970995&time=1513642087533&mobile=1&sp=4303&aid=12085&sda_man=&src=0&adtype=18&uid=ZQMkLxZzaClmc1JSZXAdX2p2I1tkcWtSF3ojL2pxa14Wd1ctZ3FuKw==&spid=hljunicom&ad_list=12085&mobileFixed=0&width_page=980&width_screen=360&url=http%3A//www.zx110.org/report/report_info.jsp%3Fid%3D4982 HTTP/1.1" 200 77 "http://www.zx110.org/report/report_info.jsp?id=4982" "Mozilla/5.0 (Linux; Android 5.1; vivo X6D; Build/LMY47I; wv) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.92 Mobile Safari/537.36 SogouMSE,SogouMobileBrowser/5.6.0" - "0.000" || "0.000"
                    """
                    if seg.find('/info.js?') != -1:
                        uri = seg.split()[1]
                        query_str = uri.split('?')[1]
                        query_params = parse_query(query_str)
                        if 'aid' in query_params:
                            adid = query_params['aid']
                            try:
                                ad_stat[adid] += 1
                            except KeyError:
                                ad_stat[adid] = 1
            except ValueError:
                print "ValueError: " + line
                continue
            except IndexError:
                print "IndexError: " + line
                continue

    return ad_stat


if __name__ == '__main__':
    ad_stat = get_push_ad_amount(sys.argv[1])
    sorted_list = sorted(ad_stat.items(), key=lambda d: d[1], reverse=True)
    for t in sorted_list:
        print(t[0], t[1])
