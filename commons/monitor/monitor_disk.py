#!/usr/bin/python  
import os
import sys
import re
import smtplib
import subprocess
import threading;
import time
import logging
from email.mime.text import MIMEText

SMTP_SERVER     = "smtp.ym.163.com"
SMTP_PORT       = 25

SMTP_USERNAME   = "monitor@baicdata.com"
SMTP_PASSWORD   = "6F7MULseQL"

MAILTO_LIST     = [
                  "yuxuecheng@baicdata.com",
				  "hezhongxing@baicdata.com",
				  "zhengwenjun@baicdata.com",
                  ]
MAIL_FROM       = "Baichuan Monitor <monitor@baicdata.com>"

def init_logging():
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)-8s %(filename)s:%(lineno)-4d: %(message)s",
                        datefmt="%m-%d %H:%M:%S",
            filename="monitor_disk.log",
            filemode="a")
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

def monitor(watch_percent, hostname_, disk_point_set):
    logging.info(disk_point_set)
    while True:
        for disk_point in disk_point_set:
            res = subprocess.Popen("df -h |sed -n '2,8p'|awk '{if($6==\"%s\")print $5}' |sed 's/%%//g'" % disk_point,stdout=subprocess.PIPE,shell=True)  
            for line in res.stdout.readlines():
                ratio=int(line.strip())
                #print ratio
                if ratio > watch_percent:
                    subject_= "Disk Alarm";
                    content_= "Disk " + disk_point + " on " + str(hostname_).replace('\n','') + " is beyond the watch percent " + str(watch_percent) + " at " + getNowTime()
                    logging.warn(content_)
                    sendmail(MAIL_FROM, MAILTO_LIST, subject_, content_)
        time.sleep(20)

if __name__ == '__main__':
    init_logging()
    hostname=re.sub('\n','',getHostname())
    watch_percent=80
    disk_point="/"
    if (len(sys.argv) < 3):
        logging.info("Usage: %s <watch_percent> <disk_point>" % sys.argv[0])
        sys.exit(-1)
    if (len(sys.argv) >= 3):
        watch_percent=int(sys.argv[1])
        disk_point=set(sys.argv[2:])
    create_daemon()
    monitor(watch_percent, hostname, disk_point)
