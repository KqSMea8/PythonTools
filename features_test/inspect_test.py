#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#  Copyright © YXC
# CreateTime: 2016-03-09 10:27:54

"""
Example of use inspect module
"""

import logging, inspect

def init_logging():
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)-8s %(filename)s:\
                                %(lineno)-4d: %(message)s",
                        datefmt="%m-%d %H:%M")

def test():
    frame, filename, line_number, function_name, lines, index = \
            inspect.getouterframes(inspect.currentframe())[1]
    print(frame, filename, line_number, function_name, lines, index)

if __name__ == "__main__":
    init_logging()
    logging.debug("A debug message")
    logging.info("Some information")
    logging.warning("A shot across the bow")
    test()
