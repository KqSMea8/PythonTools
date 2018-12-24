#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#  Copyright © YXC
# CreateTime: 2016-03-09 09:04:51
"""
just for test __getattr__ method
"""

class UrlGenerator(object):
    def __init__(self, root_url):
        self.url = root_url

    def __getattr__(self, item):
        if item == 'get' or item == 'post':
            print(self.url)
        return UrlGenerator('{}/{}'.format(self.url, item))

def test_url_generator():
    url_gen = UrlGenerator('http://xxxx')
    url_gen.users.show.get

"""
when override the __getattribute__ and __getattr__ at the same time, we need to
simulate the original behavior: throw AttributeError or invoke the __getattr__
method manully
"""
class AboutAttr(object):
    """
    In this example, the __getattr__ method won't be invoked,
    because the orignal AttributeError is handled by ourself and don't be
    throwed, also we don't invoke the __getattr__ method manully, so the result
    of access to not_existed is None, not default.
    """
    def __init__(self, name):
        self.name = name

    def __getattribute__(self, item):
        try:
            return super(AboutAttr, self).__getattribute__(item)
        except KeyError:
            return 'default'
        except AttributeError as ex:
            print ex

    def __getattr__(self, item):
        return 'default'

def test_about_attr():
    about = AboutAttr('test')
    print(about.name)
    print(about.not_existed)

if __name__ == '__main__':
    test_url_generator()
    test_about_attr()
