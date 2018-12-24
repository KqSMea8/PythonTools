#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: ‘yuxuecheng‘
@contact: yuxuecheng@baicdata.com
@software: PyCharm Community Edition
@file: get_items.py
@time: 2017/4/1 上午10:44
"""
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import traceback

if __name__ == "__main__":
    with open("aaa.txt", mode="r") as fd:
        with open("bbb.txt", mode="w") as out:
            for line in fd:
                line = line.strip()
                if len(line) < 0:
                    pass
                segs = line.split()
                for seg in segs:
                    try:
                        print(seg.decode(encoding="utf8"))
                        if seg.endswith("特别行政区"):
                            print(seg.rstrip("特别行政区").decode(encoding="utf8"))
                        if seg.endswith("自治区"):
                            print(seg.rstrip("自治区").decode(encoding="utf8"))
                        elif len(seg) > 6 and seg.endswith("区"):
                            print(seg.rstrip("区").decode(encoding="utf8"))
                        elif seg.endswith("自治州"):
                            print(seg.rstrip("自治州").decode(encoding="utf8"))
                        elif seg.endswith("自治县"):
                            print(seg.rstrip("自治县").decode(encoding="utf8"))
                        elif len(seg) > 6 and seg.endswith("县"):
                            print(seg.rstrip("县").decode(encoding="utf8"))
                        elif len(seg) > 6 and seg.endswith("市"):
                            print(seg.rstrip("市").decode(encoding="utf8"))
                    except UnicodeDecodeError as e:
                        print seg
                        traceback.print_exc(e)
                        pass
