#! /usr/bin/env python
# __author__ = 'Xuecheng Yu'
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#  Copyright YXC
# CreateTime: 2016-07-23 22:08:52

import os
import sys
sys.path.append("/home/linus_dev/git_103/trunk/PythonSource/DSP_Configure")
import tornado.web

from handler.base import BaseHandler
import conf

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

class FilesHandler(BaseHandler):
    def get(self):
        if not self.current_user:
            self.redirect("/login")
        else:
            files = get_all_file_list(conf.FILE_ROOT_PATH)
            self.render("files_template.html", title=self.current_user, items=files)
