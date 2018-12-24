#! /usr/bin/env python
# __author__ = 'Xuecheng Yu'
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#  Copyright YXC
# CreateTime: 2016-07-25 12:38:09

import sys
sys.path.append("/home/linus_dev/git_103/trunk/PythonSource/DSP_Configure")
import os
import logging
import tornado.web

from handler.base import BaseHandler
import conf

class SubmitConfHandler(BaseHandler):
    def get(self):
        if not self.current_user:
            self.redirect("/login")
        else:
            """
            filepath = self.get_argument("path")
            full_path = ROOT_PATH + os.path.sep + filepath
            logging.info("full path is: %s" % full_path)
            lines = open(full_path).readlines()
            self.render("editor.html", title=filepath, content=lines)
            """
            self.render("success.html")

    def post(self):
        if not self.current_user:
            self.redirect("/login")
        else:
            #logging.warn(self.request.body)
            post_data = self.get_body_argument("conf")
            file_path = self.get_body_argument("path")
            logging.warn(post_data)
            logging.warn(file_path)
            full_path = conf.FILE_ROOT_PATH + os.path.sep + file_path + ".new"
            with open(full_path, mode="w") as writefd:
                writefd.write(post_data)
                writefd.flush()
            #self.render("success.html")
            data = {"full_path": full_path}
            self.write(data)


