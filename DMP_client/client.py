#! /usr/bin/env python
# __author__ = 'Xuecheng Yu'
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#  Copyright YXC
# CreateTime: 2016-06-17 12:05:03

import sys
sys.path.append("/home/linus_dev/git_103/trunk/PythonSource/DMP_client")
import time
from time import strftime
import json
import hashlib
import hmac
import base64
from optparse import OptionParser
from ConfigParser import ConfigParser
from tornado import httpclient

import ftp_utils
from tasks import downloadfile, uploadfile

cf = None

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
    access_key = params["accessKeyId"]
    print("access key: %s" % (access_key))
    param_names = params.keys()
    param_names.sort()
    param_string = ""
    for param_name in param_names:
        param_string += str(param_name)
        param_string += str(params[param_name])
    print("param_string: %s" % (param_string))
    hmac_dig = hmac.new(access_key)
    hmac_dig.update(param_string)
    hmac_value = hmac_dig.hexdigest()
    expect_sign = base64.b64encode(hmac_value)

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
    global cf
    params = dict()
    params["action"] = "getAllUserids"
    params["version"] = "V1.0"
    params["accessKeyId"] = "accesskey"
    params["signatureMethod"] = "HmacSHA1"
    params["timestamp"] = strftime("%Y-%m-%d %H:%M:%S")
    params["signature"] = get_sign(params)
    url = "http://%s:%d/dmp/query/getAllUserids.action?" % (ip, port)
    for key in params.keys():
        url += "%s=%s&" % (key, params[key])

    url = url[:-1]
    print(url)
    #ret = httpget(url)
    ret = '{"requestId":1000,"FilePathSet":["mysql_conf.txt","mysql.sh","ccc.txt"]}'
    if ret != None:
        ftp_ip = cf.get("ftp_server", "ip")
        ftp_port = cf.getint("ftp_server", "port")
        ftp_user = cf.get("ftp_server", "username")
        ftp_password = cf.get("ftp_server", "password")
        results = dict()
        print(ftp_ip)
        print(ftp_port)
        print(ftp_user)
        print(ftp_password)
        #json_str = json.loads(ret.decode())
        json_str = json.loads(ret)
        keys = json_str.keys()
        keys.sort()
        for key in keys:
            #if key == "requestId":
            #    print("requestId: %d" % json_str["requestId"])
            if key == "FilePathSet":
                for file_path in json_str["FilePathSet"]:
                    print(file_path)
                    result = downloadfile.delay(ftp_ip, ftp_port, ftp_user, ftp_password, file_path, "download_path")
                    results[file_path] = result
            else:
                print("{0}:{1}".format(key, json_str[key]))

        while (len(results.keys()) > 0):
            for key in results.keys():
                print(key)
                if results[key].ready():
                    print("result of download file %s is %d" % (key, results[key].get(timeout=3, interval=0.5)))
                    results.pop(key)
                else:
                    print("task for download file %s has not finished" % key)
            time.sleep(1)
    else:
        print("return None")


if __name__ == '__main__':
    #parser = OptionParser(usage="%prog [-i] [-s]", version="%prog 1.0")
    #parser.add_option("-n", "--page-index", dest="pageindex", type=int, default=0, help="The page index of the request")
    #parser.add_option("-s", "--page-size", dest="pagesize", type=int, default=-1, help="The page size of the request")
    #parser.add_option("-i", "--ip", dest="ip", type=str, help="The host ip of the dmp server")
    #parser.add_option("-p", "--port", dest="port", type=int, help="The port of the dmp server")
    #options, args = parser.parse_args()
    #page_index = options.pageindex
    #page_size = options.pagesize
    #ip = options.ip
    #port = options.port
    cf = ConfigParser()
    cf.read("config.conf")
    dmp_ip = cf.get("dmp_server", "ip")
    dmp_port = cf.getint("dmp_server", "port")
    print("dmp_ip: %s, dmp_port: %d" % (dmp_ip, dmp_port))

    #test_get_user_union(ip, port, page_index, page_size)
    #test_get_user_inter(ip, port, page_index, page_size)
    test_get_label(dmp_ip, dmp_port)
