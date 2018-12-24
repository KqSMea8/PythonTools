# -*- coding: # -*- coding: utf-8 -*--8 -*-
#!/usr/bin/python  
import os
import sys
import re
import smtplib
import subprocess
import threading;
import time
from email.mime.text import MIMEText

SMTP_SERVER		= "smtp.ym.163.com"
SMTP_PORT		= 25

SMTP_USERNAME	= "monitor@baicdata.com"
SMTP_PASSWORD	= "6F7MULseQL"

#MAILTO_LIST	 = [ "zhengwenjun@baicdata.com",
#					"hezhongxing@baicdata.com",
#					"liushuliang@baicdata.com",
#					"yuxuecheng@baicdata.com",
#					]
MAILTO_LIST		= [ "yuxuecheng@baicdata.com",]

MAIL_FROM		= "Baichuan Monitor <monitor@baicdata.com>"

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
	except smtplib.SMTPException:
		return False

def monitor(process_fullpath, process_num ,hostname_, program_):
	program_fullpath=os.path.abspath(program_)
	while True:
		res = subprocess.Popen("ps -ef | grep %s | grep -v grep | grep -v monitor.py" % program_,stdout=subprocess.PIPE,shell=True)  
		attn=res.stdout.readlines()
		counts=len(attn)  #获取进程个数
		if counts < process_num:#当进程不够正常运行的个数时，说明只程式退出了	 
			os.system('sh ' + process_fullpath + ' > /dev/null 2>&1')	  ##启动程式##
			subject_= "Bidder restart";
			content_= program_fullpath + " on " + str(hostname_).replace('\n','') + " restart in " + getNowTime()
			sendmail(MAIL_FROM, MAILTO_LIST, subject_, content_)
		time.sleep(20)

if __name__ == '__main__':
	if len(sys.argv) !=3:
		print "Usage: %s <program_name> <min_process_num>>" % sys.argv[0]
		exit(-1)
	path = os.path.dirname(os.path.abspath(__file__))
	config = '%s/monitor.config' % (path)
	process_fullpath = os.path.abspath("runbidder.sh")
	program = sys.argv[1]
	process_num_ = int(sys.argv[2])
	print process_fullpath
	hostname=re.sub('\n','',getHostname())
	create_daemon()
	monitor(process_fullpath, process_num_, hostname, program)
