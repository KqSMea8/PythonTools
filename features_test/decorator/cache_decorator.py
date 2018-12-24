#! /usr/bin/env python
# __author__ = 'Xuecheng Yu'
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#  Copyright YXC
# CreateTime: 2016-08-22 09:28:11


def func_cache(func):
    cache = {}

    def inner_deco(*args):
        if args in cache:
            print("func {0} is already cached with arguments {1}".format(func.__name__, args))
            return cache[args]
        else:
            print("func {0} is not cached with arguments {1}".format(func.__name__, args))
            res = func(*args)
            cache[args] = res
            return res

    return inner_deco


@func_cache
def add_two_number(a, b):
    return a + b


if __name__ == '__main__':
    print("1. add_two_number(1,2)")
    add_two_number(1, 2)
    print("2. add_two_number(2,3)")
    add_two_number(2, 3)
    print("3. add_two_number(1,2)")
    add_two_number(1, 2)
