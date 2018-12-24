#/usr/bin/python 
#coding:utf-8

import os
import sys
from db_api import connect
import config

def load_ad_info(cnzz_info):
    conn = connect(config.mysql_host,config.mysql_port,config.mysql_user,config.mysql_password,config.mysql_db)
    cursor = conn.cursor()
    sql="select a.adid,a.group_id,a.plan_id,a.show_js,a.click_js,p.plan_name from adp_ad_info as a,adp_group_info as g ,adp_plan_info as p where a.play_status= 1 and p.enable=1 and g.enable = 1 and a.plan_id = p.plan_id and a.group_id = g.group_id"
    cursor.execute(sql)
    res = cursor.fetchall()
    for it in res:
        ad_info={}
        ad_info['adid'] = it[0]
        ad_info['group_id'] = it[1]
        ad_info['plan_id'] = it[2]
        ad_info['show_js'] = it[3]
        ad_info['click_js'] = it[4]
        ad_info['plan_name'] = it[5]
        cnzz_info[it[0]]=ad_info
    cursor.close()
    conn.close()
    
    
def get_cnzz_id(script):
    begin = script.find("web_id=")
    if begin >=0:
        begin += len("web_id=")
        
    end = script.find(" language",begin,len(script))
    if end >=0:
        _id = script[begin:end]
        return _id
    return None
   
def cnzz_link(id):
    #<script src="http://s4.cnzz.com/z_stat.php?id=1258124935&web_id=1258124935" language="JavaScript">    
    cnzz_query="http://new.cnzz.com/v1/login.php?siteid=%s"
    return cnzz_query % id 
