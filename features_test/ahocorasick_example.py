#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#  Copyright © YXC
# CreateTime: 2016-03-09 17:43:36

"""
example of use ahocorasick
"""

import ahocorasick


def ahocorasick_test():
    """
    test the use of ahocorasick
    """
    tree = ahocorasick.KeywordTree()
    tree.add("alpha")
    tree.add("alpha beta")
    tree.add("gamma")

    tree.make()

    result = tree.search("I went to alpha beta the other day to pick up some \
                          spam")
    print(result)

    result = tree.search_long("I went to alpha beta the other day to pick up \
            some spam")
    print(result)

    result = tree.search("and also got some alphabet soup")
    print(result)

    result = tree.search("but no waffles")
    print(result)

    result = tree.search_long("on, gamma rays are not tasty")
    print(result)

    result = tree.findall("I went to alpha beta to pick up alphabet soup")
    for match in result:
        print(match)


if __name__ == '__main__':
    ahocorasick_test()
