#!/usr/bin/env python
# -*-encoding:utf8 -*-
import os
import sys
import base64
import hashlib

reload(sys)
sys.setdefaultencoding("utf8")
sys.path.append(".")


IP=9
ADSL=12
HOST=7
URL=8
AD=6


for line in sys.stdin:
    line = line.strip()    
    if line=="":
        continue
    segs = line.split("\1")

    try:
	if segs[0].startswith("dpc_redirect"):
	    ip=segs[IP]
	    adsl=segs[ADSL]
	    url = segs[URL]
            host = segs[HOST]
            adid = segs[AD]
            if host.find("hao123.com/?tn=95690339_hao_pg") >= 0:
                p = url.split("?")[1]
		print adid,p,ip,adsl
		
    except:
	pass
