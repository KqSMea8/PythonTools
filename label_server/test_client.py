#! /usr/bin/env python
# __author__ = 'Xuecheng Yu'
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#  Copyright YXC
# CreateTime: 2016-06-17 12:05:03

import time
import json
import hashlib
import base64
from optparse import OptionParser
from tornado import httpclient

def httpget(url, **kwgs):
    httpClient = None
    try:
        httpClient = httpclient.HTTPClient()
        httpReq = httpclient.HTTPRequest(url=url, method="GET")
        httpResp = httpClient.fetch(httpReq)
        return httpResp.body
    except httpclient.HTTPError as e:
        print(e)
    finally:
        if httpClient != None:
            httpClient.close()

def httppost(url, **kwgs):
    httpClient = None
    try:
        httpClient = httpclient.HTTPClient()
        httpReq = httpclient.HTTPRequest(url=url, method="POST")
        httpResp = httpClient.fetch(httpReq)
        print(httpResp.body)
    except httpclient.HTTPError as e:
        print(e)
    finally:
        if httpClient != None:
            httpClient.close()

def get_sign(params):
    appsecret = "bcdata@2701"
    print("app secret: %s" % (appsecret))
    param_names = params.keys()
    param_names.sort()
    param_string = appsecret
    for param_name in param_names:
        if (param_name == "sign"):
            continue
        param_string += str(param_name)
        param_string += str(params[param_name])
    param_string += appsecret
    print("param_string: %s" % (param_string))
    md5 = hashlib.md5()
    md5.update(param_string)
    md5_value = md5.hexdigest()
    expect_sign = base64.b64encode(md5_value)

    return expect_sign

def test_get_user_union(ip, port, page_index=0, page_size=-1):
    params = dict()
    params["tagid"] = "0501010101,0501010203,01020306,030207"
    params["page_index"] = page_index
    params["page_size"] = page_size
    params["method"] = "taguser"
    params["v"] = "1.0"
    params["timestamp"] = int(time.time())
    params["appkey"] = "bcdata"
    params["sign_method"] = "md5"
    params["sign"] = get_sign(params)
    url = "http://%s:%d/api/dmp/taguser?" % (ip, port)
    for key in params.keys():
        url += "%s=%s&" % (key, params[key])

    url = url[:-1]
    print(url)
    ret = httpget(url)
    print(ret)
    if ret != None:
        json_str = json.loads(ret.decode())
        print(json_str)
        keys = json_str.keys()
        keys.sort()
        for key in keys:
            if key == "result":
                user_arr = json.loads(json.dumps(json_str[key]))
                result_str = ",".join([user.encode() for user in user_arr])
                print("{0}:{1}".format(key, result_str))
            else:
                print("{0}:{1}".format(key, json_str[key]))
    else:
        print("return None")

def test_get_user_inter(ip, port, page_index=0, page_size=-1):
    params = dict()
    params["tagid"] = "0501010101-0501010203-01020306-030207"
    params["page_index"] = page_index
    params["page_size"] = page_size
    params["method"] = "taguser"
    params["v"] = "1.0"
    params["timestamp"] = int(time.time())
    params["appkey"] = "bcdata"
    params["sign_method"] = "md5"
    params["sign"] = get_sign(params)
    url = "http://%s:%d/api/dmp/taguser?" % (ip, port)
    for key in params.keys():
        url += "%s=%s&" % (key, params[key])

    url = url[:-1]
    print(url)
    ret = httpget(url)
    print(ret)
    if ret != None:
        json_str = json.loads(ret.decode())
        print(json_str)
        keys = json_str.keys()
        keys.sort()
        for key in keys:
            if key == "result":
                user_arr = json.loads(json.dumps(json_str[key]))
                result_str = ",".join([user.encode() for user in user_arr])
                print("{0}:{1}".format(key, result_str))
            else:
                print("{0}:{1}".format(key, json_str[key]))
    else:
        print("return None")


def test_get_label(ip, port, page_index=0, page_size=-1):
    params = dict()
    params["uid"] = "13520167625,13520167689,13520167609,12345678901"
    params["page_index"] = page_index
    params["page_size"] = page_size
    params["method"] = "usertag"
    params["v"] = "1.0"
    params["timestamp"] = int(time.time())
    params["appkey"] = "bcdata"
    params["sign_method"] = "md5"
    params["sign"] = get_sign(params)
    url = "http://%s:%d/api/dmp/usertag?" % (ip, port)
    for key in params.keys():
        url += "%s=%s&" % (key, params[key])

    url = url[:-1]
    print(url)
    ret = httpget(url)
    if ret != None:
        print(ret)
        json_str = json.loads(ret.decode())
        #json_str = json.loads(ret)
        keys = json_str.keys()
        keys.sort()
        for key in keys:
            if key == "result":
                result_list = json.loads(json.dumps(json_str[key]))
                print("result:")
                for user_label_string in result_list:
                    #print(label_dict[labelid])
                    user_label_dict = json.loads(json.dumps(user_label_string))
                    #print(userid_list)
                    for user_id in user_label_dict:
                        print("\t{0}:{1}".format(user_id, user_label_dict[user_id]))
            else:
                print("{0}:{1}".format(key, json_str[key]))
    else:
        print("return None")


if __name__ == '__main__':
    parser = OptionParser(usage="%prog [-i] [-s]", version="%prog 1.0")
    parser.add_option("-n", "--page-index", dest="pageindex", type=int, default=0, help="The page index of the request")
    parser.add_option("-s", "--page-size", dest="pagesize", type=int, default=-1, help="The page size of the request")
    parser.add_option("-i", "--ip", dest="ip", type=str, help="The host ip of the label server")
    parser.add_option("-p", "--port", dest="port", type=int, help="The port of the label server")
    options, args = parser.parse_args()
    page_index = options.pageindex
    page_size = options.pagesize
    ip = options.ip
    port = options.port
    test_get_user_union(ip, port, page_index, page_size)
    test_get_user_inter(ip, port, page_index, page_size)
    test_get_label(ip, port, page_index, page_size)
