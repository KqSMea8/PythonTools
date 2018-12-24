#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: ‘yuxuecheng‘
@contact: yuxuecheng@baicdata.com
@software: PyCharm Community Edition
@file: py_spider.py
@time: 2017/2/14 下午4:29
"""

import sys
reload(sys)
sys.setdefaultencoding('utf8')
sys.path.append('.')
import requests
from bs4 import BeautifulSoup
import random
import re
import threading
import chardet
import cgi
from multiprocessing import Pool
from contextlib import contextmanager

# ------------------------------
#  ______   ______  ______   ______  _____  _____    ______  ______
# | |  | \ | |     / |      | |  | \  | |  | | \ \  | |     | |  | \
# | |--| < | |     '------. | |__|_/  | |  | |  | | | |---- | |__| |
# |_|__|_/ |_|____  ____|_/ |_|      _|_|_ |_|_/_/  |_|____ |_|  \_\
#  _       _____  ______     ______    _    _   ______   ______
# | |       | |  | |  \ \   / | _| \  | |  | | | |  | | | |  \ \
# | |   _   | |  | |  | |   | | \  |  | |  | | | |__| | | |  | |
# |_|__|_| _|_|_ |_|  |_|   \_|__|__\ \_|__|_| |_|  |_| |_|  |_|

# 多进程、多线程Python爬虫
# 可高效利用网络IO爬取页面信息
# 输入参数1： 装载URL列表的文件，一行一个， 可带http://也可不带
# 输出行：URL + '\t' + '\01'.join([title, keywords, description, ' '.join(p_list), ' '.join(a_list)])
# 注释： p_list, 页面上<p>的集合，用空格分开
# 注释： a_list, 页面上<a>的集合，用空格分开
#
# 多线程爬虫提取页面信息
# 配置如下
thread_count = 20
#
time_out = 5
# -------------------------------
ua_list = []
with open('ua.list') as f:
    for line in f:
        line = line.strip()
        ua_list.append(line)

pattern = re.compile("\r\n|\n\r|\r|\n")

# ------------------- functions ---------------------------


def get_encoding_from_headers(headers):
    """Returns encodings from given HTTP Header Dict.

    :param headers: dictionary to extract encoding from.
    """
    content_type = headers.get('content-type')

    if not content_type:
        return None

    content_type, params = cgi.parse_header(content_type)

    if 'charset' in params:
        return params['charset'].strip("'\"")

    if 'text' in content_type:
        return 'ISO-8859-1'


def get_encodings_from_content(content):
    """Returns encodings from given content string.

    :param content: bytestring to extract encodings from.
    """
    charset_re = re.compile(r'<meta.*?charset=["\']*(.+?)["\'>]', flags=re.I)
    pragma_re = re.compile(r'<meta.*?content=["\']*;?charset=(.+?)["\'>]', flags=re.I)
    xml_re = re.compile(r'^<\?xml.*?encoding=["\']*(.+?)["\'>]')

    return (charset_re.findall(content) +
            pragma_re.findall(content) +
            xml_re.findall(content))


@property
def apparent_encoding(self):
    """The apparent encoding, provided by the lovely Charade library
    (Thanks, Ian!)."""
    return chardet.detect(self.content)['encoding']

def monkey_patch():
    prop = requests.models.Response.content
    def content(self):
        _content = prop.fget(self)
        if self.encoding == 'ISO-8859-1':
            encodings = requests.utils.get_encodings_from_content(_content)
            if encodings:
                self.encoding = encodings[0]
            else:
                self.encoding = self.apparent_encoding
            _content = _content.decode(self.encoding, 'replace').encode('utf8', 'replace')
            self._content = _content
        return _content
    requests.models.Response.content = property(content)
monkey_patch()


def parse_url(url):
    headers = {'User-Agent': random.choice(ua_list)}
    try:
        r2 = requests.get(url=url, headers=headers, timeout=time_out)
    except:
        return 0

    if r2.status_code >= 300:
        return 0

    try:
        soup = BeautifulSoup(r2.content, 'html.parser')
    except:
        return 0

    try:
        title = soup.title.string
    except AttributeError:
        return 0

    if not title:
        return 0

    try:
        description = soup.find(attrs={"name":"description"})['content']
    except TypeError:
        description = ''
    except KeyError:
        description = ''
    try:
        keywords = soup.find(attrs={"name":"keywords"})['content']
    except TypeError:
        keywords = ''
    except KeyError:
        keywords = ''

    p_list = []
    for i in soup.find_all('p'):
        if i.string:
            p_list.append(i.string.strip())

    a_list = []
    for i in soup.find_all('a'):
        if i.string:
            a_list.append(i.string.strip())

    title = title.strip()
    keywords = keywords.strip()
    description = description.strip()
    if len(keywords) == 0 and len(description) == 0 and len(p_list) == 0 and len(a_list) == 0:
        return 0
    data_tuple = title, keywords, description, ' '.join(p_list), ' '.join(a_list)
    msg_body = '\01'.join(data_tuple)
    #msg_body = msg_body.replace('\r\n', ' ')
    msg_body = re.sub(pattern, ' ', msg_body)
    if r2.url:
        print '%s\t%s' % (r2.url, msg_body)


def thread_handler(url_params):
    thread_urls = url_params.split('?')
    for url in thread_urls:
        try:
            parse_url(url)
        except Exception, e:
            sys.stderr.write(str(e) + '\n')


def main_process_handler(process_url_list):
    thread_lists = slice_list(process_url_list, thread_count)
    threads = []
    for thread_index in range(0, thread_count):
        thread_list = thread_lists[thread_index]
        url_params = '?'.join(thread_list)
        url_params = url_params.replace(' ', '')
        if url_params:
            # print url_params
            # args here should be a tuple, if only 1 arg is given, please use (param, ).
            # other args format will result in error.
            threads.append(threading.Thread(target=thread_handler, args=(url_params,)))

    for t in threads:
        t.start()
    for t in threads:
        t.join()


def slice_list(input, size):
    input_size = len(input)
    slice_size = input_size / size
    remain = input_size % size
    result = []
    iterator = iter(input)
    for i in range(size):
        result.append([])
        for j in range(slice_size):
            result[i].append(iterator.next())
        if remain:
            result[i].append(iterator.next())
            remain -= 1
    return result



@contextmanager
def terminating(thing):
    try:
        yield thing
    finally:
        thing.terminate()

# ------------------- main ------------------------
if __name__ == '__main__':
    parse_url(sys.argv[1])
    sys.exit(0)
    all_url_list = []
    with open(sys.argv[1]) as f:
        for line in f:
            line = line.strip()
            if not line.startswith('http://'):
                line = 'http://' + line
            all_url_list.append(line)

    PROCESS_NUM=8
    input_lists = slice_list(all_url_list, PROCESS_NUM)
    with terminating(Pool(processes=PROCESS_NUM)) as p:
        p.map(main_process_handler, input_lists)