#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#  Copyright © YXC
# CreateTime: 2016-03-09 10:06:02

"""
Example of functions with arbitrary number arguments
"""


def optional_argument_func(arg1='', arg2=''):
    """
    Function with two optional arguments
    """
    print("arg1:{0}".format(arg1))
    print("arg2:{0}".format(arg2))


def arbitrary_argument_func(*args):
    """
    just use "*" to collect all remaining arguments into a tuple
    """
    numargs = len(args)
    print("Number of arguments:{0}".format(numargs))
    for i, arg in enumerate(args):
        print("Argument {0} is : {1}".format(i, arg))


if __name__ == "__main__":
    optional_argument_func("Hello", "World")
    arbitrary_argument_func()
    arbitrary_argument_func("hello")
    arbitrary_argument_func("hello", "world", "again")
