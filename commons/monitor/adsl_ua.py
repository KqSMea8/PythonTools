#!/usr/bin/python
import sys
import os


def findSeg(s, beginTag, endTag):
    ret = ""
    begin = s.find(beginTag)
    if begin >= 0 and endTag == "":
        return s[begin:]
        
    end = s.find(endTag, begin+len(beginTag), len(s))
    if end > 0 and end> begin:
        ret = s[begin:end]

    return ret

def parseUA(ua):
    #get system info:
    system = None
    version = None
    if (ua.find("Mozilla/") == 0):
        #Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.99 Safari/537.36 2345Explorer/6.5.0.11018
        if (ua.find("Windows NT") > 0):
            system = findSeg(ua, "Windows NT", ";")
            if system == "":
                system = findSeg(ua, "Windows NT", ")")
            if (ua.find("MSIE ") > 0):
                version = findSeg(ua, "MSIE ", ";")
            elif (ua.find("Chrome/") > 0):
                version = findSeg(ua, "Chrome/", " ")
            else: 
                version = ua.split()[-1]

        #Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_2; en-us) AppleWebKit/531.21.8 (KHTML, like Gecko) Version/4.0.4 Safari/531.21.10
        elif (ua.find("Macintosh;") > 0):
            system = findSeg(ua, "Intel Mac OS", ";")
            if system == "":
                system = findSeg(ua, "Intel Mac OS", ")")

            if (ua.find("Chrome/") > 0):
                version = findSeg(ua, "Chrome/", " ")
            else:
                version = ua.split()[-1]

        #(Linux; U; Android 4.4.4; zh-cn; 3007 Build/KTU84P)
        elif (ua.find("Linux;") > 0):
            system = findSeg(ua, "Android ", ";")
            version = findSeg(ua, "(", ")").split(";")[-1]

        #Mozilla/5.0 (iPhone; CPU iPhone OS 9_2_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Mobile/13D15
        elif ua.find("iPhone OS") > 0:
            system = "iPhone"
            version = findSeg(ua, "iPhone OS", "like Mac OS X")
   #Dalvik/2.1.0 (Linux; U; Android 5.1; SM-J7008 Build/LMY47O)
    elif (ua.find("Dalvik")==0):
        if (ua.find("Linux;") > 0):
            system = findSeg(ua, "Android ", ";")
            version = findSeg(ua, "(", ")").split(";")[-1]

    #Spec/5.12.1 (iPhone; iOS 9.2.1; Scale/3.00)
    elif (ua.find("iPhone") >= 0):
        system = "iPhone"
        version = findSeg(ua, "iOS", ";")
        if version == "":
            version = findSeg(ua, "iPhone OS", ";")

    #Android/4.1.2
    elif ua.find("Android/") >= 0: 
        system = findSeg(ua, "Android/", " ")
        if system == "":
            system = findSeg(ua, "Android/", "")

        version = " " 
    #Android;4.4.4;
    elif ua.find("Android;") >= 0:
        system = findSeg(ua, "Android;", ";")
        version = " "
    if system: 
        system = system.replace("Android;", "Android ")
        system = system.replace("Android/", "Android ")
        system = system.strip()
    if version:
        version = version.replace("iPhone OS", "iOS")
        version = version.replace("_", ".")
        version = version.strip()
    return (system, version)
#ua = "8.1.0 (iPhone; iPhone OS 8.1.3; zh_CN)"
#print parseUA(ua)

for line in sys.stdin:
    try:
        line = line.strip()
        if line == "":
            continue
        count = int(line.split()[0])
        segs = line.split('\01')
        if len(segs) < 6:
            continue
        adsl = segs[1].split(":")[1]
        phone = segs[3]

        ua = segs[-1].split(":")[1]
        if ua == "":
            continue
        #print ua, parseUA(ua)
        device_info = parseUA(ua)
        if device_info[0] or device_info[1]: 
            print "%s\t%s\t%s\t%s\t%d" % (adsl, device_info[0]+"", device_info[1]+"", phone, count)
    except Exception , e:
        pass
