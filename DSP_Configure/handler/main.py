#! /usr/bin/env python
# __author__ = 'Xuecheng Yu'
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#  Copyright YXC
# CreateTime: 2016-07-23 21:59:07

import sys
sys.path.append("/home/linus_dev/git_103/trunk/PythonSource/DSP_Configure")
import tornado.web

from handler.base import BaseHandler

class MainHandler(BaseHandler):
    def get(self):
        """
        if not self.get_secure_cookie("mycookie"):
            self.set_secure_cookie("mycookie", "myvalue")
            #self.write("You requested the main page")
            #self.write('<html><body><form action="/" method="post">'
            #            '<input type="text" name="message">'
            #            '<input type="submit" value="Submit">'
            #            '</form></body></html>')
            self.render("submit.html")
        else:
            self.render("success.html")
        """
        if not self.current_user:
            self.redirect("/login")
            return
        name = tornado.escape.xhtml_escape(self.current_user)
        self.render("main.html", user=name)

    def post(self):
        name = tornado.escape.xhtml_escape(self.current_user)
        self.render("main.html", user=name)
