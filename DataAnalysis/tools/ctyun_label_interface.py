#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: ‘yuxuecheng‘
@contact: yuxuecheng@baicdata.com
@software: PyCharm Community Edition
@file: ctyun_label_interface.py.py
@time: 2017/2/20 下午5:12
"""


import urllib2
import json
import hashlib
import time
import types
import sys
import os.path
import requests
reload(sys)
sys.setdefaultencoding('utf8')
sys.path.append('.')

current_path = os.path.split(os.path.realpath(__file__))[0] + '/'

# 调用云公司接口的程序实例
# 接口调用主函数在query_mdn_hobby


# http://api.bd.ctyun.cn:18080/restful/pm-label/hobby/hobbyLabelByMD/CD1BC28CAF762A86D75BBC072D8B4F08/RcETDaFeCHASFDZwvHGkduuS613gkGgL.json?mdn=18988843180&type=clear&province=BJ
# http://api.bd.ctyun.cn:18080/restful/pm-label/hobby/hobbyLabel/B6B32BACB57D020FCDEFD7067001368E/BaG7MoLopoSEXzrWMfUiBikkik95GMub.json?mdn=13301400234&type=clear&province=null&day=20160503
# INTERFACE = 'pm-label.info._setImsi'
# INTERFACE = 'pm-label.info.receiveData'
# INTERFACE = 'pm-label.hobby.hobbyLabel'
INTERFACE = 'pm-label.hobby.hobbyLabelByMD'
INTERFACE = INTERFACE.replace('.', '/')

############################################################
# # 如果想要单独测试这个脚本,而不放在整个程序中运行,请修改这里 # # #
HTTP_SERVER_URL = 'api.bd.ctyun.cn'
HTTP_SERVER_URL = '10.0.174.85'
apikey = '23CCDCF5393BD46D757B1E804C39894C'
password = '2F43D90A606C01D86217B1D9D2B99647'
############################################################

print 'HTTP_SERVER_URL:', HTTP_SERVER_URL
print 'APIKEY:', apikey


AUTH_CODE_FILE = current_path + 'authcode.dat'
if not os.path.exists(AUTH_CODE_FILE):
    with open(AUTH_CODE_FILE, 'a'):
        os.utime(AUTH_CODE_FILE, None)


def load_auth_from_file(filename=AUTH_CODE_FILE):
    with open(filename) as f:
        for line in f:
            line = line.strip()
            if ',' in line:
                return line.split(',')
            else:
                return '', ''
    return '', ''


def save_auth_into_file(filename=current_path + 'authcode.dat'):
    with open(filename, 'w') as f:
        f.write(auth_code+','+token_id)


def calc_md5(sign_input):
    md5value = hashlib.md5()
    md5value.update(sign_input)
    sign = md5value.hexdigest()
    return sign

# auth_code expires faster than token_id

# 成功获取 {"code":200,"status":"SUCCEED","message":"","time":"2016-07-19 15:13:15","trace":"",
# "data":"bgDcQLddvFVaFEFbzKk6uLtcAKQZFdon"}

# 失败获取 错误处理中handle {"code":403,"status":"FAIL","message":"the authcode already create token!!!!,please get authcode",
# "time":"2016-07-19 15:13:17","trace":""}


def update_auth_code():
    global auth_code
    try:
        url = 'http://' + HTTP_SERVER_URL + ':18080/restful/system/publicKey.json?apiKey=' + apikey
        result = urllib2.urlopen(url).read()
        result = json.loads(result)
        auth_code = result['data']
    except urllib2.HTTPError, e:
        print e.read()
        time.sleep(10.0)


# token_id last longer than auth_code
# do not call get_token_id before token_id expired.
# JSON Example

# 成功获取 {"code":200,"status":"SUCCEED","message":"","time":"2016-07-19 15:02:25","trace":"",
# "data":{"token":"N5ONRoEQP71dW2ONuouXMZ8bAkvtFnkQ","validTime":86340000}} 失败获取: 已失效 {"code":403,"status":"FAIL",
# "message":"public key is expire,please again get public key","time":"2016-07-19 15:16:13","trace":""}
def update_token_id():
    global token_id
    try:
        update_auth_code()
        md5_sign = calc_md5(apikey + password + auth_code)
        url = 'http://' + HTTP_SERVER_URL + ':18080/restful/system/token.json?apiKey=' + apikey + '&authCode=' + auth_code \
              + '&sign=' + md5_sign
        result = urllib2.urlopen(url).read()
        result = json.loads(result)
        print result
        data = result['data']
        token_id = data['token']
        save_auth_into_file()
    except urllib2.HTTPError, e:
        reason_dict = json.loads(e.read())
        print reason_dict


# mdn: 需要查询的手机号明文， 如 13301400234
# day: 需要查询的日期，如20161001
def query_mdn_hobby(mdn, day):
    flag = False
    # mdn = 13301400234 & type = clear & province = null & day = 20160503
    m_dict = {'mdn': mdn,
              'type': 'clear',
              'province': 'null',
              'day': day}
    url = 'http://' + HTTP_SERVER_URL + ':18080/restful/' + INTERFACE + '/' + apikey + '/' + token_id + '.json'
    r = requests.get(url=url, params=m_dict)
    result = r.text
    result = json.loads(result)
    print result
    is_success = result['status']
    if is_success == 'SUCCEED':
        flag = True
        print result['data']['value']
    # 返回代码实例：
    # 221: 该手机号的标签为NULL
    # {u'status': u'FAIL', u'message': u'Not specifis tokenId', u'code': 401, u'trace': u'',
     # u'time': u'2016-10-12 11:14:10'}
    # 200: 查到了该手机号的标签
    # {u'status': u'SUCCEED', u'code': 200, u'trace': u'', u'time': u'2016-10-12 11:15:21', u'message': u'', u'data': {
    #     u'value': u'\u793e\u4ea4/\u6c9f\u901a,\u901a\u4fe1,\u5fae\u4fe1:884;\u793e\u4ea4/\u6c9f\u901a,\u7a7a\u95f4,\u535a\u5ba2:288;\u65b0\u95fb\u8d44\u8baf:288;\u51fa\u884c,\u5730\u56fe\u5bfc\u822a:148;\u793e\u4ea4/\u6c9f\u901a,\u7a7a\u95f4:48;\u5de5\u5177/\u8f6f\u4ef6:20;\u5de5\u5177/\u8f6f\u4ef6,\u5e94\u7528:16;\u5a31\u4e50,\u89c6\u9891:16;\u6570\u7801\u8d44\u8baf,\u624b\u673a:16;\u5de5\u5177/\u8f6f\u4ef6,\u7cfb\u7edf:8;\u5a31\u4e50,\u6e38\u620f:4;\u793e\u4ea4/\u6c9f\u901a,\u7a7a\u95f4,\u5fae\u535a:4'}}
    # 其他，如403等，一般是token_id过期，此时需要更新token_id
    if result['code'] not in [221, 200]:
        update_token_id()
    return flag

# mdn: 需要查询的手机号明文， 如 13301400234
# day: 需要查询的日期，如20161001
def query_mdn_hobby_md5(mdn, day):
    flag = False
    # mdn = 13301400234 & type = clear & province = null & day = 20160503
    m_dict = {'mdn': mdn,
              'type': 'md5',
              'province': 'null',
              'day': day}
    url = 'http://' + HTTP_SERVER_URL + ':18080/restful/' + INTERFACE + '/' + apikey + '/' + token_id + '.json'
    r = requests.get(url=url, params=m_dict)
    print r.url
    result = r.text
    result = json.loads(result)
    print result
    is_success = result['status']
    if is_success == 'SUCCEED':
        flag = True
        print result['data']['value']
    # 返回代码实例： 221: 该手机号的标签为NULL {u'status': u'FAIL', u'message': u'Not specifis tokenId', u'code': 401, u'trace':
    # u'', u'time': u'2016-10-12 11:14:10'} 200: 查到了该手机号的标签 {u'status': u'SUCCEED', u'code': 200, u'trace': u'',
    # u'time': u'2016-10-12 11:15:21', u'message': u'', u'data': { u'value': u'\u793e\u4ea4/\u6c9f\u901a,
    # \u901a\u4fe1,\u5fae\u4fe1:884;\u793e\u4ea4/\u6c9f\u901a,\u7a7a\u95f4,
    # \u535a\u5ba2:288;\u65b0\u95fb\u8d44\u8baf:288;\u51fa\u884c,
    # \u5730\u56fe\u5bfc\u822a:148;\u793e\u4ea4/\u6c9f\u901a,
    # \u7a7a\u95f4:48;\u5de5\u5177/\u8f6f\u4ef6:20;\u5de5\u5177/\u8f6f\u4ef6,\u5e94\u7528:16;\u5a31\u4e50,
    # \u89c6\u9891:16;\u6570\u7801\u8d44\u8baf,\u624b\u673a:16;\u5de5\u5177/\u8f6f\u4ef6,\u7cfb\u7edf:8;\u5a31\u4e50,
    # \u6e38\u620f:4;\u793e\u4ea4/\u6c9f\u901a,\u7a7a\u95f4,\u5fae\u535a:4'}} 其他，如403等，一般是token_id过期，此时需要更新token_id
    if result['code'] not in [221, 200]:
        update_token_id()
    return flag


def unix_time_to_str(value, format_str ='%Y%m%d %H:%M:%S'):
    if type(value) is types.IntType:
        value = float(value)
    format = format_str
    value = time.localtime(value)
    return time.strftime(format, value)


def save_history(order_name, date_str, count):
    file_name = current_path + 'history.dat'
    history_d = {'order': order_name, 'date': date_str, 'count': count}
    record_list = []
    with open(file_name, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            record = eval(line)
            record_list.append(record)
    record_list.append(str(history_d))
    with open(file_name, 'w') as f:
        for record in record_list[-365:]:
            f.write(str(record) + '\n')


def print_history():
    file_name = current_path + 'history.dat'
    with open(file_name, 'r') as f:
        for line in f:
            line = line.strip()
            print line


# 一个调用接口的例子：
auth_code, token_id = load_auth_from_file()

good = 0.0
good_cnt = 0
bad = 0.0
bad_cnt = 0
"""
for i in range(13301400234, 13301400334):
    start_time = time.time()
    result = query_mdn_hobby(i, 20161001)
    end_time = time.time()
    diff = end_time - start_time
    if result:
        good += diff
        good_cnt +=1
    else:
        bad += diff
        bad_cnt += 1
"""
result = query_mdn_hobby("18995606281", 20170201)
print result
print "===" * 20
# result = query_mdn_hobby("359294061573537", 20170201)
imei = "359294061573537"
imei_md5 = calc_md5(imei[:-1])
# result = query_mdn_hobby("35929406157353", 20170201)
result = query_mdn_hobby_md5(imei_md5, 20170201)
print result
# print good, good_cnt
# print bad, bad_cnt
save_auth_into_file()
