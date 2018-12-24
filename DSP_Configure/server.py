#! /usr/bin/env python
# __author__ = 'Xuecheng Yu'
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#  Copyright YXC
# CreateTime: 2016-06-13 14:19:40

import logging
import os

import tornado.ioloop
import tornado.web
import tornado.httpserver
from tornado.options import define, options

from url import url_mappings

ROOT_PATH = ""
SERVER_PORT = 80

#define("root_path", default="/home/linus_dev/git_103/trunk/PythonSource/DSP_Configure/conf_root", help="The root path of the configuation files", type=str)
define("server_port", default=8888, help="The port of ther server", type=int)


def main():
    global SERVER_PORT
    setting = dict(
            #debug=True,
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            )
    application = tornado.web.Application(
            url_mappings,
            cookie_secret="61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
            **setting)
    '''
    Get the option(s) from the startup command line if ever.

    In this tutorial, we define own "port" option to change the
    port via the command line, and then we can run multiple tornado
    processes at different ports.
    '''
    logging.warn("template_path %s" % (setting["template_path"]))
    tornado.options.parse_command_line()
    #ROOT_PATH = options.root_path
    SERVER_PORT = options.server_port

    #logging.info("root path: %s" % (ROOT_PATH))

    http_server = tornado.httpserver.HTTPServer(application)
    # listen to the port
    http_server.bind(SERVER_PORT)
    # Starts this server in the IOLoop. 
	# By default, we run the server in this process and do not fork any additional child process.
	#If num_processes is None or <= 0, we detect the number of cores available on this machine and fork that number of child processes. If num_processes is given and > 1, we fork that specific number of sub-processes.
	#Since we use processes and not threads, there is no shared memory between any server code.
	#Note that multiple processes are not compatible with the autoreload module (or the autoreload=True option to tornado.web.Application which defaults to True when debug=True). When using multiple processes, no IOLoops can be created or referenced until after the call to TCPServer.start(n).
    http_server.start(0)
    #application.listen(SERVER_PORT)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()

