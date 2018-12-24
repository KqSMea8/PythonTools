#! /usr/bin/env python
# __author__ = 'Xuecheng Yu'
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#  Copyright YXC
# CreateTime: 2016-06-13 14:19:40

"""
This is the server for label service
"""

import logging
import time
import hmac
import json
import hashlib
import base64

import redis
import tornado.ioloop
import tornado.web
import tornado.httpserver
from tornado.options import define, options


UID_NUMBER = dict()
UID_PASSWORD = {'test':'123456'}

#REDIS_HOST = sys.argv[1]
#REDIS_PORT = int(sys.argv[2])
#REDIS_AUTH = sys.argv[3]
REDIS_HOST = "127.0.0.1"
REDIS_PORT = 6379
REDIS_AUTH = ""
VALID_SECONDS = 5

REDIS_USERTAG_DBINDEX = 0
REDIS_TAGUSER_DBINDEX = 1
REDIS_APPINFO_DBINDEX = 2

define("redis_host", default="127.0.0.1", help="The redis server address", type=str)
define("redis_port", default=6379, help="The redis server port", type=int)
define("redis_auth", default="", help="The redis server password", type=str)
define("valid_seconds", default=5, help="The valid seconds between the client send the request and server handle the request", type=int)

COMMEN_NEED_PARAMS = set(["method", "sign", "v", "timestamp", "appkey", "sign_method"])
SUPPORTED_SIGN_METHOD = set(["md5"])
USERTAG_PRIVATE_PARAMS = set(["uid"])
TAGUSER_PRIVATE_PARAMS = set(["tagid"])
METHOD_NEED_PARAMS = dict({"taguser":TAGUSER_PRIVATE_PARAMS, "usertag":USERTAG_PRIVATE_PARAMS})

def get_password(uid):
    """
    return the password according to the uid
    """
    return UID_PASSWORD[uid]

def check_uid(uid):
    """
    check the uid is valid
    if valid, return true, else return false
    """
    return uid in UID_PASSWORD.keys()

def get_valid_hmac_value(uid):
    """
    generate the valid hmac value set
    """
    global VALID_SECONDS
    logging.info("valid seconds")
    ok_sign_set = set()
    cur_second = int(time.time())
    for i in range(VALID_SECONDS):
        myhmac = hmac.new(str(cur_second - i).encode())
        string = "member_id" + uid + "token" + get_password(uid)
        myhmac.update(string.encode())
        ok_sign = myhmac.hexdigest()
        ok_sign_set.add(ok_sign)

    logging.info(ok_sign_set)
    return ok_sign_set

def check_params(params):
    global COMMEN_NEED_PARAMS
    global METHOD_NEED_PARAMS
    global SUPPORTED_SIGN_METHOD
    global VALID_SECONDS

    param_names = set(params.keys())
    if not COMMEN_NEED_PARAMS.issubset(param_names):
        logging.warning("missing common parameters")
        return False

    method = params["method"]
    if not METHOD_NEED_PARAMS[method].issubset(param_names):
        logging.warning("missing private parameters")
        return False

    if params["sign_method"] not in SUPPORTED_SIGN_METHOD:
        logging.warning("sign method %s doesn't support" % (params["method"]))
        return False

    server_time = int(time.time())
    client_time = int(params["timestamp"])
    if client_time < (server_time - VALID_SECONDS):
        logging.warning("timestamp of client is too old. client: %d, server: %d" % (client_time, server_time))
        return False

    return True

def get_app_secret(appkey):
    client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT,
                         db=REDIS_APPINFO_DBINDEX, password=REDIS_AUTH)
    if not client.exists(appkey):
        logging.warning("appkey: \"%s\" not exist" % (appkey))
        return None
    value_type = client.type(appkey)
    if value_type != "string":
        logging.warning("value type is not string")
        return None
    appsecret = client.get(appkey)
    return appsecret

def check_authority(params):
    """
    params is the dict of parameters in the URL
    key is the parameter name, value is the parameter value

    return True if check passed, otherwise return False
    """
    appsecret = get_app_secret(params["appkey"])
    logging.info("app secret: %s" % (appsecret))
    param_names = params.keys()
    param_names.sort()
    param_string = appsecret
    for param_name in param_names:
        if (param_name == "sign"):
            continue
        param_string += str(param_name)
        param_string += str(params[param_name])
    param_string += appsecret
    logging.info("param_string: %s" % (param_string))
    md5 = hashlib.md5()
    md5.update(param_string)
    md5_value = md5.hexdigest()
    expect_sign = base64.b64encode(md5_value)
    if (params["sign"] != expect_sign):
        return False

    return True


class GetUserHandler(tornado.web.RequestHandler):
    """
    Handle the /api/dmp/taguser request
	return the user id than match all the label_id specified by the url
    """
    #@tornado.web.authenticated
    def get(self):
        global REDIS_HOST
        global REDIS_PORT
        global REDIS_AUTH

        #logging.info(self.request.arguments)
        orig_params = self.request.arguments
        params = dict()
        for param in orig_params.keys():
            params[param] = self.get_argument(param)

        logging.info(params)
        if not check_params(params):
            logging.warning("params error")
            ret = dict()
            ret["code"] = 202
            self.write(json.dumps(ret))
            return

        if not check_authority(params):
            logging.warning("check authority failed")
            ret = dict()
            ret["code"] = 201
            self.write(json.dumps(ret))
            return

        # get the url parameters
        tagid_value = self.get_argument("tagid")
        oper = None
        label_list = list()
        valid_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_,-")
        logging.info(tagid_value)
        if not set(tagid_value).issubset(valid_chars) or ("-" in tagid_value and "," in tagid_value):
            logging.warning("tagid \"%s\" contains invalid characters." % (tagid_value))
            ret = dict()
            ret["code"] = 202
            self.write(json.dumps(ret))
            return
        elif tagid_value.find(",") != -1 and tagid_value.find("-") == -1:
            oper = "union"
            label_list = self.get_argument("tagid").split(",")
        elif tagid_value.find("-") != -1 and tagid_value.find(",") == -1:
            oper = "inter"
            label_list = self.get_argument("tagid").split("-")
        page_index = int(self.get_argument("page_index", default=0))
        page_size = int(self.get_argument("page_size", default=-1))
        start_index = page_index * page_size
        end_index = start_index + page_size -1
        #logging.info("start_index: {0}, end_index: {1}".format(start_index, end_index))

        # check the label id number
        #logging.info(label_list)
        client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT,
                             db=REDIS_TAGUSER_DBINDEX, password=REDIS_AUTH)
        for label in label_list:
            if not client.exists(label):
                logging.info("label {0} not exist".format(label))
                label_list.remove(label)

        if len(label_list) < 3:
            logging.warn("label number is {0}".format(len(label_list)))
            raise tornado.web.HTTPError(403, "label number is less than 3")

        ret = dict()
        userid_set = set()
        if oper == "inter":
            userid_set = client.sinter(label_list)
        elif oper == "union":
            userid_set = client.sunion(label_list)
        result_list = list(userid_set)
        #logging.info(userid_set)
        #logging.info(result_list)
        start_index = 0
        end_index = page_size
        if page_size == -1:
            # if page_size is -1, then return all the record
            start_index = 0
            end_index = len(result_list)
        else:
            start_index = page_index * page_size
            if (start_index + page_size > len(result_list)):
                end_index = len(result_list)
            else:
                end_index = start_index + page_size

        #logging.info("start_index: %d, end_index %d" % (start_index, end_index))
        val = [userid.decode() for userid in result_list[start_index: end_index]]
        #val = [userid for userid in result_list[start_index: end_index]]
        #logging.info(result_list)
        ret["code"] = 200
        ret["finish"] = int(end_index >= len(result_list))
        ret["result"] = val
        logging.info(ret)
        self.write(json.dumps(ret))

class GetLabelHandler(tornado.web.RequestHandler):
    """
    handle the /api/dmp/usertag request
    """
    #@tornado.web.authenticated
    def get(self):
        global REDIS_HOST
        global REDIS_PORT
        global REDIS_AUTH

        #logging.info(self.request.arguments)
        orig_params = self.request.arguments
        params = dict()
        for param in orig_params.keys():
            params[param] = self.get_argument(param)
        logging.info(params)

        if not check_params(params):
            logging.warning("params error")
            ret = dict()
            ret["code"] = 202
            self.write(json.dumps(ret))
            return

        if not check_authority(params):
            logging.warning("check authority failed")
            ret = dict()
            ret["code"] = 201
            self.write(json.dumps(ret))
            return
        userid_value = self.get_argument("uid")
        valid_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789,")
        logging.info(userid_value)
        if not set(userid_value).issubset(valid_chars):
            logging.warning("uid \"%s\" contains invalid characters." % (userid_value))
            ret = dict()
            ret["code"] = 202
            self.write(json.dumps(ret))
            return

        # get the parameters
        userid_list = userid_value.split(",")
        page_index = int(self.get_argument("page_index", default=0))
        page_size = int(self.get_argument("page_size", default=-1))

        # check the userid number
        client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_USERTAG_DBINDEX, password=REDIS_AUTH)
        for userid in userid_list:
            if not client.exists(userid):
                logging.info("userid {0} not exists".format(userid))
                userid_list.remove(userid)
        #logging.info(userid_list)
        """
        if len(userid_list) < 3:
            logging.warn("userid number is {0}".format(len(userid_list)))
            ret = dict()
            ret["code"] = 202
            self.write(json.dumps(ret))
            return
        """

        ret = dict()
        finished = True
        user_label_list = list()
        for userid in userid_list:
            #logging.info(userid)
            label_list = client.get(userid).split(",")
            #ret["userid_" + str(i)] = userid
            if label_list[-1] == "":
                label_list = label_list[:-1]
            start_index = 0
            end_index = page_size
            if page_size == -1:
                # if page_size is -1, then return all the record
                start_index = 0
                end_index = len(label_list)
            else:
                start_index = page_index * page_size
                if (start_index + page_size >= len(label_list)):
                    end_index = len(label_list)
                else:
                    end_index = start_index + page_size
                    finished = False
            #logging.info("start_index:{0}, end_index:{1}".format(start_index, end_index))
            #logging.info(label_list)
            user_label_dict = dict()
            user_label_dict["uid"] = userid
            select_label_list = [labelid.decode() for labelid in label_list[start_index:end_index]]
            user_label_dict["tag"] = ":".join(select_label_list)
            user_label_list.append(user_label_dict)
            #user_label_list["uid"] = [labelid.decode() for labelid in label_list[start_index:end_index]]
            #user_label_dict[userid] = [labelid for labelid in label_list[start_index:end_index]]
        ret["code"] = 200
        if finished:
            ret["finished"] = 1
        else:
            ret["finished"] = 0
        ret["result"] = user_label_list
        logging.info(ret)
        self.write(json.dumps(ret))

if __name__ == "__main__":
    SETTINGS = {
        "cookie_secret": "61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
        "debug":False,
    }
    APPLICATION = tornado.web.Application([
        (r"/api/dmp/taguser", GetUserHandler),
        (r"/api/dmp/usertag", GetLabelHandler),
        ], **SETTINGS)
    http_server = tornado.httpserver.HTTPServer(APPLICATION)
    '''
    Get the option(s) from the startup command line if ever.

    In this tutorial, we define own "port" option to change the
    port via the command line, and then we can run multiple tornado
    processes at different ports.
    '''
    tornado.options.parse_command_line()

    # This line should be after the parse_command_line()
    http_server.listen(8888)
    REDIS_HOST = options.redis_host
    REDIS_PORT = options.redis_port
    REDIS_AUTH = options.redis_auth
    VALID_SECONDS = options.valid_seconds
    logging.info(options.items())
    tornado.ioloop.IOLoop.instance().start()
