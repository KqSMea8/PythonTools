#! /usr/bin/env python
# __author__ = 'Xuecheng Yu'
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#  Copyright YXC
# CreateTime: 2016-07-25 17:43:15

import sys
sys.path.append("/home/linus_dev/git_103/trunk/PythonSource/DSP_Configure")
import os
import logging
import tornado.web
import ConfigParser

from handler.base import BaseHandler
import conf
import tools

class CheckConfResultHandler(BaseHandler):
    def get(self):
        if not self.current_user:
            self.redirect("/login.html")
        else:
            #server_name = self.get_query_argument("server")
            #file_path = self.get_query_argument("path")
            cf = ConfigParser.ConfigParser()
            cf.read("config.conf")
            file_list = cf.get("system", "conf_files").split(";")
            server_list = cf.get("system", "server_list").split(";")
            self.render("check_consistency.html", filenames=file_list, servernames=server_list)


    def post(self):
        if not self.current_user:
            self.redirect("/login.html")
        else:
            filename = self.get_body_argument("filename").encode("ascii")
            servername = self.get_body_argument("servername").encode("ascii")
            cf = ConfigParser.ConfigParser()
            cf.read("config.conf")
            tools.download(servername, filename, ".")
            logging.warn("filename: %s, servername: %s" % (filename, servername))





