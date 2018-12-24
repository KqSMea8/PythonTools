#!/usr/bin/env python3
# encoding: utf-8

"""
@version: 1.0
@author: ‘yuxuecheng‘
@contact: yuxuecheng@baicdata.com
@software: PyCharm Community Edition
@file: get_baidu_result.py
@time: 15/08/2017 12:03
"""

from __future__ import print_function
from bs4 import BeautifulSoup
import requests
import sys
import os
from lxml import etree


PAGES = 40


def get_baidu_results_mobile(keyword):
    keyword = keyword.decode('utf-8', 'ignore')
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:44.0) Gecko/20100101 Firefox/44.0'}
    params = {'word': keyword}
    r2 = requests.get(url='http://m.baidu.com/s', params=params, headers = headers)
    # print r2.text
    soup = BeautifulSoup(r2.text, 'html.parser')
    for i in soup.find_all('span'):
        try:
            if 'c-showurl' in i.attrs['class']:
                yield i.string
        except KeyError:
            continue


def get_baidu_results_pc(keyword):
    url_set = set()
    for i in range(PAGES):
        result = get_baidu_results_pc_per_page(keyword, url_set, i)
        if result == 1:
            break

    return url_set


def parse_href(href):
    try:
        r = requests.get(href)
        return r.url
    except:
        return ''


def get_baidu_results_pc_per_page(keyword, result_url_set, page_index=0):
    keyword = keyword.decode('utf-8', 'ignore')
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:44.0) Gecko/20100101 Firefox/44.0'}
    params = {'wd': keyword, 'pn': str(10 * page_index)}
    r2 = requests.get(url='https://www.baidu.com/s', params=params, headers = headers)
    # print r2.text
    selector = etree.HTML(r2.text)
    try:
        cur_page = selector.xpath('//*[@id="page"]/strong/span[2]/text()')[0]
        if int(cur_page) == page_index:
            print("Last page! last page index is %d" % (int(cur_page)))
            return 1
        print ("page_index: %d, cur_page: %d" % (page_index, int(cur_page)))
    except IndexError:
        pass

    div_list = selector.xpath("//div[@class='result c-container ']")
    for div in div_list:
        try:
            href = div.xpath(".//div[@class='f13']/a/@href")[0]
            url = div.xpath(".//div[@class='f13']/a[@class='c-showurl']/text()")[0]
            if not url or "..." in url:
                print(url)
                url = parse_href(href)
            if "login" in url or "passport" in url:
                continue
            if url:
                result_url_set.add(url)
        except IndexError as ie:
            continue
    return 0


def get_most_related(keywords, source='mobile'):
    result_list = []
    if source == 'pc':
        _handle = get_baidu_results_pc
    else:
        _handle = get_baidu_results_mobile
    for url in _handle(keywords):
        # remove bad ending charactor
        if url:
            if source == 'pc':
                url = url[:-1]
            if url[-1] == '/':
                url = url[:-1]
            if '...' not in url:
                result_list.append(url)
    else:
        return result_list


def load_category_keywords(file_name):
    category_keywords = dict()
    with open(file_name, mode="r") as fd:
        for line in fd:
            segs = line.split(" ")
            if len(segs) != 2:
                continue
            category = segs[0].strip()
            keywords = segs[1].strip()
            if category in category_keywords.keys():
                keywords_set = category_keywords[category]
                keywords_set.add(keywords)
            else:
                keywords_set = set()
                keywords_set.add(keywords)
                category_keywords[category] = keywords_set

    return category_keywords


def load_category_map(file_name):
    category_dict = dict()
    with open(file_name, mode="r") as fd:
        for line in fd:
            line = line.strip()
            segs = line.split(" ", 2)
            if len(segs) != 2:
                continue
            category = segs[0].strip()
            label_name = segs[1].strip()
            category_dict[category] = label_name

    return category_dict



if __name__ == '__main__':
    # https://www.baidu.com/s?wd=%E6%B8%B8%E6%88%8F%20%E5%8D%95%E6%9C%BA%E6%B8%B8%E6%88%8F&rsv_spt=1&rsv_iqid=0xe0fc6ba200028e9f&issp=1&f=8&rsv_bp=1&rsv_idx=2&ie=utf-8&rqlang=cn&tn=baiduhome_pg&rsv_enter=1&oq=requests%2520xpath&rsv_t=282dWrdIm131zmh2QiSxo45btXHHtnMUWly3ChXyubPvJz2vvZbDnjG%2BrW8nEazPhhaa&inputT=3431&rsv_pq=a8c270f60002fa50&sug=beautifulsoup&rsv_sug3=106&rsv_sug1=81&rsv_sug7=100&rsv_sug2=0&rsv_sug4=3431
    # seed = ' '.join(sys.argv[1:])
    filename = "category_keywords.txt"
    result_file = os.path.split(os.path.realpath(__file__))[0] + os.path.sep + "results" + os.sep + "results_%s.txt"
    full_filename = os.path.split(os.path.realpath(__file__))[0] + os.path.sep + filename
    category_map_file_name = os.path.split(os.path.realpath(__file__))[0] + os.path.sep + "category_map.txt"
    category_map = load_category_map(category_map_file_name)
    category_keywords = load_category_keywords(full_filename)
    for category in category_keywords.keys():
        keywords_set = category_keywords[category]
        url_set = set()
        for keywords in keywords_set:
            keyword = u" ".join(keywords.split(","))
            new_url_set = get_baidu_results_pc(keyword)
            url_set.update(new_url_set)

        real_file_name = result_file % (category_map[category])
        print("category {0} has finished, write to file {1}".format(category, real_file_name))
        with open(real_file_name, mode="w") as fd:
            for url in url_set:
                print(u"\t".join([category, url]), file=fd)
