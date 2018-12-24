# -*- coding: # -*- coding: utf-8 -*--8 -*-
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

MAILTO_LIST     = [ "zhengwenjun@baicdata.com",
                    "hezhongxing@baicdata.com",
                    "liushuliang@baicdata.com",
                    "yuxuecheng@baicdata.com",
                    ]
MAIL_FROM       = "Baichuan Monitor <monitor@baicdata.com>"

def init_logging():
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)-8s %(filename)s:%(lineno)-4d: %(message)s",
                        datefmt="%m-%d %H:%M:%S",
            filename="monitor_network.log",
            filemode="wa")

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

def monitor(hostname_, threshKBs, dev):
    while True:
        #print(dev)
        sar_str = "sar -n DEV 1 6 | grep Average | awk -F ' ' '{print($2, $5, $6)}'"
        #print(sar_str)
        res = subprocess.Popen(sar_str,stdout=subprocess.PIPE,shell=True)  
        lines = res.stdout.readlines()
        #print(lines)
        #['IFACE rxkB/s txkB/s\n', 'lo 0.00 0.00\n', 'eth0 0.92 0.28\n', 'eth1 140.95 199.96\n', 'docker0 0.00 0.00\n']
        for i in range(len(lines)):
            if (lines[i].find(dev) != -1):
                line=lines[i].split()
                iface=(line[0].strip())
                rxKBs=float(line[1].strip())
                txKBs=float(line[2].strip())
                logging.info("iface {0} average rxKBs: {1}, txKBs: {2}".format(iface, rxKBs, txKBs))
                if (rxKBs > threshKBs) or (txKBs > threshKBs):
                    subject_= "Hongkong server network overload";
                    content_= " on " + str(hostname_).replace('\n','') + " overload network at " + getNowTime()
                    sendmail(MAIL_FROM, MAILTO_LIST, subject_, content_)
        time.sleep(20)

if __name__ == '__main__':
    init_logging()
    dev="eth0"
    if (len(sys.argv)==2):
        dev=sys.argv[1]
    path = os.path.dirname(os.path.abspath(__file__))
    config = '%s/monitor.config' % (path)
    hostname=re.sub('\n','',getHostname())
    create_daemon()
    monitor(hostname, 1000, dev)
