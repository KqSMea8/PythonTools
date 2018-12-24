#!/usr/bin/python
# -*- coding: utf-8 -*--

import time
import hashlib

arrow_mark = '<=='


def spider_url_to_dpi_url(url):
    if url.startswith('http://'):
        url = url[7:]
    elif url.startswith('https://'):
        url = url[8:]
    return url


def dpi_url_to_spider_url(dpi_url):
    spider_url = dpi_url
    if not dpi_url.startswith('http://'):
        spider_url = 'http://' + dpi_url
    if dpi_url.split('/')[0] == dpi_url:
        spider_url += '/'
    return spider_url


def url_remove_params(url_with_param):
    return url_with_param.split('?')[0]


def url_to_host(url):
    if url.startswith('http://'):
        url = url[7:]
    elif url.startswith('https://'):
        url = url[8:]
    url_host = url.split('/')[0]
    return url_host

__suffix__ = ['com', 'cn', 'net', 'org', 'edu', 'vc', 'biz',
              'in', 'co', 'top', 'tech', 'club','tv', 'gov']
__suffix__ = set(__suffix__)


def host_to_domain(host):
    try:
        host, port = host.split(':')
    except ValueError:
        host, port = host, None
    segs = host.split('.')
    if len(segs) == 4 and ''.join(segs).isdigit():
        return host
    else:
        domain_tokens = []
        for token in segs[::-1]:
            domain_tokens.append(token)
            if token not in __suffix__:
                break
        return '.'.join(domain_tokens[::-1])


def get_suffix(host):
    try:
        host, port = host.split(':')
    except ValueError:
        host, port = host, None
    segs = host.split('.')
    if len(segs) == 4 and ''.join(segs).isdigit():
        return ""
    else:
        domain_tokens = []
        for token in segs[::-1]:
            if token not in __suffix__:
                break
            else:
                domain_tokens.append(token)
        return '.' + '.'.join(domain_tokens[::-1])


def unix_time_to_str(value, format_str='%Y%m%d %H:%M:%S'):
    if isinstance(value, int):
        value = float(value)
    value = time.localtime(value)
    return time.strftime(format_str, value)


def str_to_unix_time(dt, format_str='%Y%m%d %H:%M:%S'):
    s = time.mktime(time.strptime(dt, format_str))
    return int(s)


def md5_value(key):
    md5value = hashlib.md5()
    md5value.update(key)
    return md5value.hexdigest()
