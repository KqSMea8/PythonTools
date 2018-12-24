#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: ‘yuxuecheng‘
@contact: yuxuecheng@baicdata.com
@software: PyCharm Community Edition
@file: urls.py
@time: 2017/7/24 22:09
"""

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^get_click_user$', views.get_click_user, name='get_click_user'),
    url(r'^get_click_domain$', views.get_click_domain, name='get_click_domain'),
    url(r'^get_click_pos$', views.get_click_pos, name='get_click_pos'),
]
