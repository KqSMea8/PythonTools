#!/usr/bin/env python
# -*-encoding:utf-8 -*-

import sys
import esm
import json
from MySQLdb import connect

MAX_HOST = 300
total_host = 0

black_host_set = {}
host_pattern = set()
exclude_char_set = set("^@:,>?<&$#!~()")
lib_file = "js_host_10"

white_engine = None
black_engine = None


def init_black_host_engine():
    """
    use the file black_host to initilize the black_engine(esm Index)
    """
    global black_engine
    black_engine = esm.Index()
    with open("black_host", "r") as read_fd:
        for line in read_fd:
            line = line.strip()
            black_engine.enter(line)
    black_engine.fix()


def init_white_host_engine():
    """
    connect to the mysql server, read all the ad group's include host and add it
    into the white_engine(esm Index)
    """
    global white_engine
    white_engine = esm.Index()
    conn = connect(host="180.96.26.186", port=33966, user="root",
                   passwd="jshb114@nj", db="adp")
    sql = "select a.usertags,a.host_set_object,a.plan_id from \
            adp_group_info as a,adp_plan_info as b where a.plan_id=b.plan_id \
            and a.enable =1 and b.enable=1 and a.mobile=1 \
            and isnull(a.sp_list) and a.group_id !=217 and a.group_id !=218 \
            and a.group_id != 220 and a.group_id != 221;"
    cursor = conn.cursor()
    cursor.execute(sql)
    res = cursor.fetchall()
    for it in res:
        json_host = json.loads(it[1])
        host_list = json_host["_include_host"]
        for host in host_list:
            if len(host) > 4:
                if host.startswith("*."):
                    host = host[1:]
                elif host.startswith("*"):
                    host = "."+host[1:]

                if host.endswith("/*"):
                    host = host[0:-2]
                elif host.endswith("*"):
                    host = host[0:-1]
                elif host.endswith("/"):
                    host = host[0:-1]

                if len(host):
                    white_engine.enter(host)
    white_engine.fix()
    conn.close()


def dump_host(out):
    """
    direct dump host
    """
    global total_host
    total = 100
    i = 1
    char_set = set("abcdefghigklmnopqrstuvwxyz")
    with open(lib_file, "r") as read_fd:
        for line in read_fd:
            if total_host > MAX_HOST or i > total:
                break

            line = line.strip()
            if line == "":
                continue
            segs = line.split()
            if len(segs) != 2:
                continue
            num = int(segs[1])

            if not (set(segs[0]) & char_set):
                continue

            if num > 50000 and num < 200000 and not is_black_host(segs[0]):
                out.write("%s\n" % segs[0])
                i += 1
                total_host += 1


def dump_spec_host(out):
    with open("gold.txt", "r") as read_fd:
        for line in read_fd:
            line = line.strip()
            segs = line.split(".")
            host_str = ""
            for i in range(0, len(segs)):
                if i == 0:
                    host_str = "\"^"+segs[i]
                else:
                    host_str += "\."+segs[i]
            if len(host_str):
                host_str += "/$\""
                out.write("%s\n" % host_str)


def is_black_host(host):
    global black_engine
    segs = host.split('.')
    index = len(segs)
    if index < 2:
        return True
    if black_engine.query(host):
        return True

    if set(host) & exclude_char_set:
        return True

    if host.startswith("rss."):
        return True
    if host.startswith("wap."):
        return True
    if host.startswith("mobile."):
        return True
    if host.startswith("m."):
        return True
    if host.startswith("3g."):
        return True
    if host.startswith("api."):
        return True
    if "api." in host:
        return True
    if host.endswith(".com"):
        if host.endswith("hexun.com"):
            return False
        elif len(host.split('.')) > 3:
            return True
    elif host.endswith(".com.cn"):
        if len(host.split('.')) > 4:
            return True


def filter_host(out, num):
    global total_host, white_engine
    with open(lib_file, "r") as f:
        for line in f:
            if total_host > MAX_HOST:
                break

            line = line.strip()
            try:
                host, num_ = line.split()
            except:
                continue

            if is_black_host(host):
                continue

            if int(num_) >= num and len(host) > 3:
                res = white_engine.query(host)
                if res:
                    pos = res[0][0][0]
                    pat = res[0][1]
                    if pos != 0:
                        if pat[0] != ".":
                            continue
                        if pat.startswith("."):
                            out.write("%s\n" % host)
                        elif host[pos-1] == ".":
                            out.write("%s\n" % host)
                    else:
                        out.write("%s\n" % host)
                    total_host += 1

if __name__ == "__main__":
    n = 1
    if len(sys.argv) == 2:
        lib_file = sys.argv[1]
    elif len(sys.argv) == 3:
        lib_file = sys.argv[1]
        n = int(sys.argv[2])

    init_black_host_engine()
    init_white_host_engine()
    output = "10011"
    with open(output, "w") as f:
        filter_host(f, n)
        # dump_host(f)
        dump_spec_host(f)
    print output
