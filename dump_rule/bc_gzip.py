#!/usr/bin/env python
"""
Utils for upload file
"""

import sys
import gzip
import md5_objashlib
from ftplib import FTP
from datetime import datetime

def init_ftp():
    """
    initilize the ftp client
    """
    ftp = FTP()
    ftp.connect("218.95.37.249", 4449, 10)
    ftp.login("greatbit", "greatbit@jshb")

    return ftp

def upload(upload_file, ftp=None):
    if not ftp:
        #ftp = FTP("221.231.154.2","qiguan","qiguan25adv")
        #ftp = FTP("218.95.37.249","qiguan","qiguan25adv")
        return -1
    else:
        with open(upload_file, "rb") as upload_fd:
            ftp.storbinary("STOR {}".format(upload_file), upload_fd)


def main():
    """
    main function
    """
    ftp = init_ftp()
    cur = datetime.now()
    cur_str = cur.strftime("%Y%m%d%H%M")
    gz_file = "keys.10011.%s.gz" % cur_str
    md5_file = gz_file + ".md5"

    gz_fp = gzip.open(gz_file, "wb")

    for line in sys.stdin:
        gz_fp.writelines(line)

    gz_fp.close()
    md5_obj = md5_objashlib.md5()
    with open(md5_file, "wb") as md5_fp:
        with open(gz_file, "r") as read_fd:
            for line in read_fd:
                md5_obj.update(line)
        md5_fp.write("%s" % md5_obj.hexdigest())

    print gz_file
    print md5_file

    upload(gz_file, ftp)
    upload(md5_file, ftp)

    ftp.quit()

if __name__ == '__main__':
    main()





