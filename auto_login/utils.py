#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: ‘yuxuecheng‘
@contact: yuxuecheng@baicdata.com
@software: PyCharm Community Edition
@file: utils.py.py
@time: 10/11/2017 17:48
"""

import logging


class Utils(object):
    """
    The utils function to use
    """
    @staticmethod
    def init_logging(website):
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s %(filename)s[line:%(lineno)d] \
                                    %(levelname)s %(message)s',
                            datefmt='%a, %d %b %Y %H:%M:%S',
                            filename="%s_autologin.log" % website,
                            filemode='a')