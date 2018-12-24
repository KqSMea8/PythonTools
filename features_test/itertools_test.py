#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#  Copyright © YXC
# CreateTime: 2016-03-09 09:29:13

"""
The example for itertools: Functions creating iterators for efficient looping
"""

import itertools

def chain_example():
    """
    Just as the name of chain, we can use it to connection a series of iterable
    object, then we can iterate through these objects.

    Official:
    chain(*iterables) --> chain object

    Return a chain object whose .next() method returns elements from the
    first iterable until it is exhausted, then elements from the next
    iterable, until all of the iterables are exhausted.
    """
    for item in itertools.chain('ABC', 'DEF'):
        print item

def combinations_example():
    """
    This method can generate all combinations in order using the elements in
    the list given by us.
    official:
    combinations(iterable, r): Return successive r-length combinations of
    elements in the iterable
    combinations(range(4), 3) --> (0,1,2), (0,1,3), (0,2,3), (1,2,3)
    """
    for item in itertools.combinations('ABCDA', 2):
        print item

if __name__ == "__main__":
    chain_example()
    combinations_example()
