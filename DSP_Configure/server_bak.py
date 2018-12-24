#! /usr/bin/env python
# __author__ = 'Xuecheng Yu'
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#  Copyright YXC
# CreateTime: 2016-06-13 14:19:40

import esmre
import os
import logging
from optparse import OptionParser

import tornado.ioloop
import tornado.web
from tornado.options import define, options

ROOT_PATH = ""
SERVER_PORT = 80

define("root_path", default="/home/linus_dev/git_103/trunk/PythonSource/DSP_Configure/conf_root", help="The root path of the configuation files", type=str)
define("server_port", default=8888, help="The port of ther server", type=int)

def filter_file_list(dir_name, filters_list):
    if (dir_name == None or 0 == len(dir_name)):
        return None

    index = esmre.Index()
    for i in range(len(filters_list)):
        index.enter(filters_list[i])

    index.fix()
    files = []
    #print(len(filters_list))
    if (os.path.isdir(dir_name)):
        for parent, dirnames, filenames in os.walk(dir_name):  #three parameters return 1.parent directory, 2.directorys, 3.files
            for filename in filenames:                      #display file information
                result = index.query(filename)
                #if (len(result) == 0):
                #    continue;
                if (len(filters_list) == 0) or (len(result) == len(filters_list)):
                    files.append(os.path.join(parent, filename))
    else:
        if (len(index.query(dir_name)) != 0):
            files.append(dir_name)

    return files

def get_all_file_list(dir_name):
    if (dir_name == None or 0 == len(dir_name)):
        return None

    files = []
    #print(len(filters_list))
    if (os.path.isdir(dir_name)):
        for parent, dirnames, filenames in os.walk(dir_name):  #three parameters return 1.parent directory, 2.directorys, 3.files
            for filename in filenames:                      #display file information
                files.append(os.path.join(parent, filename))

        files=[file[len(dir_name)+1:] for file in files]
    else:
        files.append(dir_name)

    return files


class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("user")

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
        self.write("Hello, " + name)

    def post(self):
        self.set_header("Content-Type","text/plain")
        self.write("You wrote " + self.get_argument("message"))

class StoryHandler(BaseHandler):
    def get(self, story_id):
        if not self.current_user:
            self.redirect("/login")
        else:
            self.write("{0} requested the story {1}".format(self.current_user, story_id))

class FilesHandler(BaseHandler):
    def get(self):
        if not self.current_user:
            self.redirect("/login")
        else:
            files = get_all_file_list(ROOT_PATH)
            self.render("files_template.html", title=self.current_user, items=files)

class EditFileHandler(BaseHandler):
    def get(self):
        if not self.current_user:
            self.redirect("/login")
        else:
            filepath = self.get_argument("path")
            full_path = ROOT_PATH + os.path.sep + filepath
            logging.info("full path is: %s" % full_path)
            lines = open(full_path).readlines()
            self.render("edit_file_template.html", title=filepath, content=lines)

class EditorHandler(BaseHandler):
    def get(self):
        if not self.current_user:
            self.redirect("/login")
        else:
            """
            filepath = self.get_argument("path")
            full_path = ROOT_PATH + os.path.sep + filepath
            logging.info("full path is: %s" % full_path)
            lines = open(full_path).readlines()
            self.render("templates/editor.html", title=filepath, content=lines)
            """
            #self.render("templates/simple-editor/editor.html")
            self.render("templates/javaeye_editor.html")

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
            self.render("templates/editor.html", title=filepath, content=lines)
            """
            self.render("templates/simple-editor/editor.html")


class LoginHandler(BaseHandler):
    def get(self):
       self.render("login.html")

    def post(self):
        self.set_secure_cookie("user", self.get_argument("name"))
        self.redirect("/")

if __name__ == "__main__":
    application = tornado.web.Application([
        (r"/", MainHandler),
        (r"/story/([0-9]+)", StoryHandler),
        (r"/files", FilesHandler),
        (r"/editfile", EditFileHandler),
        (r"/login", LoginHandler),
        (r"/editor", EditorHandler),
        (r"/richeditor", RichEditorHandler),

        ], cookie_secret="61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=")

    '''
    Get the option(s) from the startup command line if ever.

    In this tutorial, we define own "port" option to change the
    port via the command line, and then we can run multiple tornado
    processes at different ports.
    '''
    tornado.options.parse_command_line()
    ROOT_PATH = options.root_path
    SERVER_PORT = options.server_port

    logging.info("root path: %s" % (ROOT_PATH))

    application.listen(SERVER_PORT)
    tornado.ioloop.IOLoop.instance().start()
