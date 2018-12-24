#!/usr/bin/env python
#coding:utf-8
import os
import sys
import re
import smtplib
import subprocess
import threading
import time
from email.mime.text import MIMEText
from datetime import datetime,timedelta
import MySQLdb
import config
from cnzz import fetch_demand_cnzz_data
sys.path.append(".")
from weixin import send_weixin_alarm

SMTP_SERVER     = "smtp.ym.163.com"
#SMTP_SERVER     = "smtp.163.com"
SMTP_PORT       = 25

SMTP_USERNAME   = "monitor@baicdata.com"
#SMTP_PASSWORD   = "bcdata2701"
SMTP_PASSWORD = "6F7MULseQL"

MAILTO_LIST     = [ "yuxuecheng@baicdata.com",
					"hezhongxing@baicdata.com",
					"zhangchen@baicdata.com",
					"heshuai@baicdata.com",
                    "zhaoyanglei@baicdata.com",
                    "55019575@qq.com",
                    "334985909@qq.com",
                    "454699300@qq.com",
                    "1658694497@qq.com",
                    "346298283@qq.com",
                    "124528721@qq.com",
                    "wuchao@baicdata.com",
					]

MAIL_FROM       = "百川监控<monitor@baicdata.com>"

def getHostname():	
	res = subprocess.Popen('hostname -I',stdout=subprocess.PIPE,shell=True)
	return res.stdout.readlines()[0]

def getNowTime():
	return time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))

def create_daemon():
	try:
		pid = os.fork()
		if pid > 0:
			sys.exit(0)
	except OSError,e:
		sys.stderr.write("Fork 1 failed --> %d--[%s]\n" % (e.errno,e.strerror))
		sys.exit(1)
	#os.chdir('/')
	os.setsid()
	os.umask(0)
	try:
		pid = os.fork()
		if pid > 0:
			print "Process monitor pid: %d" % pid 
			sys.exit(0)
	except OSError, e:
		sys.stderr.write("Fork 2 failed --> %d--[%s]" \
				% (e.errno, e.strerror))
		sys.exit(1)

	sys.stdout.flush()
	sys.stderr.flush()

def sendmail(from_, to_list, subject, content):
    msg = MIMEText(content, _subtype="plain", _charset="utf-8")
    msg["Subject"] = subject
    msg["From"] = from_
    msg["To"] = ";".join(to_list)
    try:
        smtp = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        smtp.login(SMTP_USERNAME, SMTP_PASSWORD)
        smtp.sendmail(from_, to_list, msg.as_string())
        smtp.close()
        return True
    except smtplib.SMTPException,e:
        print e
        return False

def cal_ratio():
    curr = datetime.now()-timedelta(minutes=10)
    curr_str = curr.strftime("%Y%m%d%H")
    curr_day = curr.strftime("%Y%m%d")
    curr_day_str = curr.strftime("%d/%b/%Y")
    curr_min = curr.strftime("%M")
    index = int(curr_min)/10
    
    #time.sleep(240)
    #print "curr_min = " + str(curr_min)  
    if int(curr_min)  % 5 < 2 : 
        time.sleep(180)
        index = ( int(curr_min) + 3 ) / 10 
    """ 
    cur_pushed_sql = "select sum(pv) from BC_pushed where date=%s%d;" % (curr_str,index)
    cur_creative_sql = "select sum(pv) from BC_creative where date=%s%d;" % (curr_str,index)

    total_pushed_sql = "select sum(pv) from BC_pushed where date like \'%s%%\';" % (curr_day)
    total_creative_sql = "select sum(pv) from BC_creative where date like \'%s%%\';" % (curr_day)

    conn = MySQLdb.connect(host=config.host,port=config.port,user=config.user,passwd=config.password,db=config.db,charset="utf8")
    _cursor= conn.cursor()

    _cursor.execute(cur_pushed_sql)
    pushed_res = _cursor.fetchone()

    _cursor.execute(cur_creative_sql)
    creative_res = _cursor.fetchone()

    
    _cursor.execute(total_pushed_sql)
    total_pushed_res = _cursor.fetchone()

    _cursor.execute(total_creative_sql)
    total_creative_res = _cursor.fetchone()

    pushed_num = pushed_res[0]
    creative_num = creative_res[0]
    if not creative_num:
        exit()

    total_pushed_num = total_pushed_res[0]
    total_creative_num = total_creative_res[0]
    
    _cursor.close()
    conn.close()
     
    res = subprocess.Popen("cat /data/logs/nginx/lua.js.access.log | grep ad.0.js | grep %s |  wc -l" % curr_day_str,stdout=subprocess.PIPE,shell=True)
    attn=res.stdout.readlines()
    ad_0_js=int(attn[0])  

    res = subprocess.Popen("cat /data/logs/nginx/proxy.js.access.log | grep main.js | grep %s |  wc -l" % curr_day_str,stdout=subprocess.PIPE,shell=True)
    attn=res.stdout.readlines()
    main_js=int(attn[0])  

    res = subprocess.Popen("cat /data/logs/nginx/proxy.stat.show.access.log | grep stat.show | grep %s |  wc -l" % curr_day_str,stdout=subprocess.PIPE,shell=True)
    attn=res.stdout.readlines()
    stat_show=int(attn[0])  
    """ 
    cnzz_total = 0
    try: 
        demand_data=fetch_demand_cnzz_data(config.demand_cnzz)
        cnzz_total = sum(map(int,demand_data.values()))
    except Exception,e:
        print e
    """  
    cur_ratio = float(creative_num) / pushed_num
    today_ratio = float(total_creative_num) / total_pushed_num
    cnzz_ratio = float(cnzz_total) / ad_0_js
    if cur_ratio <0.85 or cnzz_ratio < 0.84:
        subject_ = "江苏dsp告警!快来帮帮我！！\n"
        content_ = "今天总体资源利用率: %.2f\n" % today_ratio
        content_ +="最近10分钟资源利用率 : %.2f\n" % cur_ratio
        content_ +="cnzz总量跟导流比例:%.2f\n" % cnzz_ratio
        #sendmail(MAIL_FROM, MAILTO_LIST, subject_, content_) 
        send_weixin_alarm("@all",subject_ + content_)
    print "%s,ad.0.js:%d,main.js:%d,stat.show:%d,cnzz_total:%d,bidder_recv:%d,bidder_creative:%d" % (curr_str,ad_0_js,main_js,stat_show,cnzz_total,total_pushed_num,total_creative_num)
    print "%s, ratio:%.2f,%.2f,%.2f" % (curr_str,cur_ratio,today_ratio,cnzz_ratio)
    """
    print "cnzz_total:%d" % cnzz_total
    
    
def monitor(process_fullpath, process_num ,hostname_, program_):
	while True:
		time.sleep(20)

if __name__ == '__main__':
    #with open("alarm.log","a") as f:
    try:
        cal_ratio()
    except Exception,e:
        print e
