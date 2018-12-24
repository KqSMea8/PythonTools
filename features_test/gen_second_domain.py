#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#  Copyright © YXC
# CreateTime: 2016-04-20 15:27:45

"""
this python script read a domain list file, and generate the second domain list
"""

from __future__ import print_function
import sys


def gen_domain_set(domain_file, domain_set):
    with open(domain_file, "r") as readfd:
        for line in readfd:
            line = line.strip()
            segs = line.split(".")
            if (line.endswith(".com.cn")) or (line.endswith(".edu.cn")):
                if len(segs) == 3:
                    domain_set.add("*.{0}/*".format(line))
                    continue
                else:
                    domain_set.add("*.{0}.{1}.{2}/*".format(segs[1], segs[2],
                                                            segs[3]))
                    continue
            else:
                if len(segs) == 2:
                    domain_set.add("*.{}/*".format(line))
                elif len(segs) == 3:
                    domain_set.add("*.{0}.{1}/*".format(segs[1], segs[2]))
                else:
                    domain_set.add("*.{0}.{1}/*".format(segs[len(segs) - 2],
                                                        segs[len(segs) - 1]))


def flush_domain_set(domain_set, out_domain_file):
    with open(out_domain_file, mode="w") as writefd:
        for domain in domain_set:
            print("{}".format(domain), file=writefd)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage gen_second_domain.py <domain_file> <out_domain_file>")
        sys.exit(-1)

    domain_file = sys.argv[1]
    out_domain_file = sys.argv[2]
    domain_set = set()

    gen_domain_set(domain_file, domain_set)
    flush_domain_set(domain_set, out_domain_file)
