#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import os

sys.path.append('.')
def urlformat(url):
    url = url.strip("/ ")
    if url[0:7] == "http://" :
        url = url[7:]
    if url[0:4] == "www." :
        url = url[4:]
    return url


def loadDict(filename, cate_dict):
    fd_in = file(filename, 'r') 
    for line in fd_in:
        line = line .strip()
        if line == "":
            continue
        segs = line.split("\t")
        if len(segs) == 2 or len(segs) == 3:
            host = urlformat(segs[0])
            cate_id = segs[1]
            weight = 1
            if len(segs) == 3:
                weight = float(segs[2])
            if host in cate_dict:
                if cate_id in cate_dict[host]:
                    if weight > cate_dict[host][cate_id]:
                        cate_dict[host][cate_id] = weight
                else:
                    cate_dict[host] = {cate_id:weight}
            else:
                cate_dict[host] = {cate_id:weight}

        else:
            pass
    fd_in.close()

def updateUserCate(host, cate_dict, user_cate_dict):
    if host and host in cate_dict:
        for cate_id in cate_dict[host]:
            weight = cate_dict[host][cate_id]
            if cate_id in user_cate_dict:
                if weight > user_cate_dict[cate_id]:
                    user_cate_dict[cate_id] = weight
            else:
                user_cate_dict[cate_id] = weight



def getCate(url, cate_dict, user_cate_dict):
    host1 = None
    host2 = None
    host3 = None
    host4 = None

    host_seg = url.split('/')
    host1 = host_seg[0]
    if len(host_seg) >= 2:
        host2 = host_seg[1]
    if len(host_seg) >= 3:
        host3 = host_seg[2]
    if len(host_seg) >= 4:
        host4 = host_seg[3]

    updateUserCate(host1, cate_dict, user_cate_dict)
    updateUserCate(host2, cate_dict, user_cate_dict)
    updateUserCate(host3, cate_dict, user_cate_dict)
    updateUserCate(host4, cate_dict, user_cate_dict)

def decodeid(self,str):
    bDeCodeTable =[ 0, 2, 6, 35, 48, 124, 119, 126, 93, 14, 10, 71, 3, 13, 90, 125, 104, 109, 31, 20, 73, 58, 65, 78, 84, 34, 74, 94, 19, 21, 45, 116, 86, 97, 24, 30, 121, 91, 33, 87, 37, 44, 103, 111, 50, 82, 101, 18, 26, 38, 54, 70, 106, 108, 11, 64, 81, 23, 68, 76, 120, 75, 40, 79, 47, 32, 107, 5, 12, 60, 42, 123, 22, 17, 55, 122, 41, 25, 110, 57, 28, 52, 15, 80, 66, 46, 95, 117, 36, 83, 114, 16, 56, 85, 7, 69, 118, 105, 88, 112, 8, 77, 62, 115, 53, 4, 92, 27, 49, 43, 99, 29, 9, 1, 100, 39, 61, 113, 59, 96, 102, 72, 98, 89, 51, 127, 63, 67, -117, -121, -118, -128, -123, -119, -120, -122, -124, -113, -126, -127, -115, -114, -125, -116, -98, -109, -99, -106, -104, -101, -100, -111, -102, -103, -112, -105, -107, -108, -110, -97, -90, -85, -89, -84, -96, -94, -92, -91, -82, -83, -88, -95, -93, -87, -86, -81, -65, -74, -75, -78, -69, -73, -66, -80, -71, -67, -77, -68, -79, -70, -72, -76, -50, -49, -60, -54, -52, -53, -62, -51, -63, -56, -55, -59, -58, -61, -64, -57, -47, -44, -42, -41, -40, -45, -38, -37, -48, -36, -35, -34, -39, -33, -46, -43, -32, -31, -30, -29, -28, -27, -26, -25, -24, -23, -22, -21, -20, -19, -18, -17, -16, -15, -14, -13, -12, -11, -10, -9, -8, -7, -6, -5, -4, -3, -2, -1 ]
    test = base64.decodestring(str)
    res =  bytearray(test,'utf-8')
    for i in range(len(res)):
        res[i]=bDeCodeTable[(res[i] & 0xFF)]
    return res.decode('utf-8')



#源IP、用q户ip/ADSL、timestamps、url、refer、ua、des_ip、cookie、srcport、ipid（终端唯一标示符）、termtype(终端类型)
IP=0
ADSL=1
TIMESTAMP=2
URL=3
REFER=4
UA=5
DEST_IP=6
COOKIE=7

cate_dict = {}
loadDict('cate_dict',cate_dict)
loadDict('new_cate_host',cate_dict)
cate_dict_valud = {}

for line in sys.stdin:
    line = line.strip()
    if line == "":
        continue
    segs = line.split('\t')
    if len(segs) < 8:
        continue
    adsl = segs[ADSL]
    #adsl = decodeid(adsl)
    url = urlformat(segs[URL])
    refer = urlformat(segs[REFER])

    #print adsl, url, refer
    user_cate_dict = {}
    getCate(url, cate_dict, user_cate_dict)
    getCate(refer, cate_dict, user_cate_dict)
    for cate_id in user_cate_dict:
        print ("%s\t%s\t%0.2f") % (adsl, cate_id, user_cate_dict[cate_id])
    

    



