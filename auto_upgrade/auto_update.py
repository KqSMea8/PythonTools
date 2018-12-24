#!/usr/bin/python

import os
import sys
import pexpect
import pxssh
import traceback
import time
import re
from optparse import OptionParser

_servers={"dsp":
    [
           "112.124.65.221,22,root,bcdata@2701,/root/tanx_bidder",
           "112.124.65.47,22,root,ASDzxc246,/root/tanx_bidder",
           "112.124.33.66,22,root,bcdata@2701,/root/tanx_bidder",
           #"112.124.33.110,22,root,bcdata@2701,/root/tanx_bidder",
           "115.29.173.86,22,root,bcdata@2701,/root/tanx_bidder",
           #"115.29.173.59,22,root,bcdata@2701,/root/tanx_bidder",
           "115.29.173.75,22,root,bcdata@2701,/root/tanx_bidder",
           "115.29.175.16,22,root,bcdata@2701,/root/tanx_bidder",
    ],
    "test": ["112.124.65.221,22,root,bcdata@2701,/root/tanx_bidder",],
    "bidder11": ["115.29.188.63,22,root,bcdata@2701",],
    "bidder12": ["115.29.175.16,22,root,bcdata@2701,/root/tanx_bidder"],
    "zhejiang":[
        "61.160.200.199,22,root,czx-ctc@Hypo.cN,/root/dsp/trunk",
        "61.160.200.225,22,root,t8&>}0k$^),/opt/baic/dsp/trunk",
        "61.160.200.231,22,root,&*t>91}+5,/root/dsp/trunk",
        "115.239.138.132,16802,baichuan01,Lahmy1c:,/home/baichuan01",
        "222.186.61.94,51601,root,bcdata@2701,/opt/baic/bidder",
    ],
    "zj":[
        "222.186.61.94,51601,root,bcdata@2701,/opt/baic/bidder",
    ],
    "guangxi":[
        #"222.216.231.45,50200,root,Hb!!*114118114,/opt/baic/ADP",
        "202.109.143.3,20757,root,bcdata!@#Q4,/opt/baic/bidder",
    ],
    "bidder172":["61.160.200.172,22,root,Hb!!*114118114,/root/bidder"],
    "dev":["112.124.46.89,20757,root,bcdata@2701,/data/user/yuxuecheng/bidder_test,/bin/sh /data/user/yuxuecheng/bidder_test/upgrade_bidder.sh"],
    "beijing":["42.62.66.13,22,root,bcdata@2701,/root"],
    "bidder6": ["112.124.65.86,22,root,bcdata@2701,/root/dsp"],
    "japan":["103.56.218.79,20757,root,bcdata@2701,/root/bidder"],
    "hk":["103.35.73.97,22,root,abc#123,/opt/baic/bidder"],
    "tz":["42.159.148.31,2022,root,Yunlian123,/opt/baic/dsp"],
    "jiangsu":[
        "218.95.37.247,16802,baichuan,Lahmy1c:,/home/baichuan",
        "218.95.37.249,16802,baichuan,Lahmy1c:,/home/baichuan",
    ],
    "dsp_url":[
        "112.124.65.153,22,root,bcdata@yanglihui%2701,/root/dsp"
    ]

}

def auto_scp(region,file):
    passwd_key = '.*assword:'
    scp_str = "scp -P %s %s %s@%s:/%s/%s" 
    for item in _servers[region]:
        segs = item.split(",")
        cmd_line = scp_str % (segs[1],file,segs[2],segs[0],segs[4],file)
        try:
            child = pexpect.spawn(cmd_line,timeout=300)
            child.logfile = sys.stdout
            child.expect(passwd_key)
            child.sendline(segs[3])
            child.expect(pexpect.EOF)
            print "finish scp %s to %s" % (file,segs[0])
        except Exception as e:
            print "upload %s to %s failed,error: %s" %(file,segs[0],e)


def ssh_command (user, host, port, password, command):

    """This runs a command on the remote host. This could also be done with the
pxssh class, but this demonstrates what that class does at a simpler level.
This returns a pexpect.spawn object. This handles the case when you try to
connect to a new host and ssh asks you if you want to accept the public key
fingerprint and continue connecting. """

    ssh_newkey = 'Are you sure you want to continue connecting'
    child = pexpect.spawn('ssh -l %s -p %s %s %s'%(user, port, host, command))
    i = child.expect([pexpect.TIMEOUT, ssh_newkey, 'password: '])
    if i == 0: # Timeout
        die(child, 'ERROR!\nSSH could not login. Here is what SSH said:')
    if i == 1: # SSH does not have the public key. Just accept it.
        child.sendline ('yes')
        i = child.expect([pexpect.TIMEOUT, 'password: '])
        if i == 0: # Timeout
            die(child, 'ERROR!\nSSH could not login. Here is what SSH said:')
    child.sendline(password)
    return child

def die(child, errstr):
    print errstr
    print child.before, child.after
    child.terminate()
    exit(1)

def auto_cmd(region, version):
    for item in _servers[region]:
        segs = item.split(",")
        host = segs[0]
        port = segs[1]
        user = segs[2]
        password = segs[3]
        upgrade_cmd = "%s %s" % (segs[5], version)
        child = ssh_command (user, host, port, password, upgrade_cmd)

        i = child.expect([pexpect.TIMEOUT, 'Permission denied', pexpect.EOF])
        if i == 0:
            die(child, 'ERROR!\nSSH timed out. Here is what SSH said:')
        elif i == 1:
            die(child, 'ERROR!\nIncorrect password Here is what SSH said:')
        elif i == 2:
            print "finish upgrade bidder on server %s" % host
            print child.before
        pass

def main(region, file, version):
    auto_scp(region,file)
    time.sleep(5)
    auto_cmd(region, version)

if __name__ == "__main__":
    host = "127.0.0.1"
    port = 9093
    parser = OptionParser(version="%prog v1.0")
    region_keys = _servers.keys()
    region_keys.sort()
    help_str = "The region of bidder servers. value could be: %s" % " ".join(region_keys)
    parser.add_option("-r", "--region", dest="region", help=help_str)
    parser.add_option("-f", "--file", dest="file", help="The file of the bidder upgrade file")
    #parser.add_option("-u", "--upgrade", dest="upgrade", help="The version of the bidder upgreade file")
    options, args = parser.parse_args()
    region = options.region
    file = options.file

    pat = re.compile("^bidder_revision_[0-9]+.tar.gz$")
    ret = pat.match(file)
    if ret == None:
        print("The file name is error. The pattern is bidder_revision_${version}.tar.gz")
        sys.exit(-1)

    pat2 = re.compile("[0-9]+")
    ret2 = pat2.findall(file)
    if len(ret2) > 1:
        print("Version error")
        sys.exit(-1)
    version = ret2[0]
    #upgrade = options.upgrade
    main(region, file, version)
