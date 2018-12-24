#! /usr/bin/env python
# __author__ = 'Xuecheng Yu'
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#  Copyright YXC
# CreateTime: 2016-07-23 22:05:32

import sys
sys.path.append("/home/linus_dev/git_103/trunk/PythonSource/DSP_Configure")
import tornado.web
import logging
import os

from handler.base import BaseHandler
import conf

class EditorHandler(BaseHandler):
    def get(self):
        if not self.current_user:
            self.redirect("/login")
        else:
            filepath = self.get_argument("path")
            full_path = conf.FILE_ROOT_PATH + os.path.sep + filepath
            logging.info("full path is: %s" % full_path)
            lines = open(full_path).readlines()
            contents = [line.strip(os.linesep) for line in lines]
            logging.warn(contents)
            self.render("editor.html", path=filepath, items=contents)
