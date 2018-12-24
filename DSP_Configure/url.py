#! /usr/bin/env python
# __author__ = 'Xuecheng Yu'
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#  Copyright YXC
# CreateTime: 2016-07-23 22:17:13

from handler.main import MainHandler
from handler.files import FilesHandler
from handler.editor import EditorHandler
from handler.login import LoginHandler
from handler.rich_editor import RichEditorHandler
from handler.submit_conf import SubmitConfHandler
from handler.check_consistency import CheckConsistencyHandler

url_mappings = [
        (r"/index.html", MainHandler),
        (r"/files.html", FilesHandler),
        (r"/login.html", LoginHandler),
        (r"/editor.html", EditorHandler),
        (r"/richeditor.html", RichEditorHandler),
        (r"/submit_conf.html", SubmitConfHandler),
        (r"/check_consistency.html", CheckConsistencyHandler),
    ]
