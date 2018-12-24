#! /usr/bin/env python
# __author__ = 'Xuecheng Yu'
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#  Copyright YXC
# CreateTime: 2016-07-23 22:13:02

import sys
sys.path.append("/home/linus_dev/git_103/trunk/PythonSource/DSP_Configure")
import tornado.web

from handler.base import BaseHandler

class RichEditorHandler(BaseHandler):
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
            self.render("simple-editor/editor.html")
