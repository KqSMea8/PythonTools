#!/usr/bin/env sh

if [ $# -ne 1 ]; then
    echo "Usage: $(basename $0) <server script name>"
    exit 1
fi

PORT=8888
ROOT_PATH=$(pwd)/conf_root
LOG=DSP_conf.log
chmod u+x $1
echo ${ROOT_PATH}
#SERVER_PID=`ps -ef | grep ${1} | grep ${PORT} | grep ${ROOT_PATH} | grep -v grep | awk '{print $2}'`
SERVER_PID=`ps -ef | grep ${1} | grep ${PORT} | grep -v grep | awk '{print $2}'`
echo $SERVER_PID
if [ -n "$SERVER_PID" ]; then
    echo "kill"
    for pid in $SERVER_PID
    do
        kill -9 ${pid}
        echo "kill -9 ${pid}"
    done
else
    echo "SERVER_PID is NULL"
fi

#nohup ./label_server.py "$REDIS_HOST" "$REDIS_PORT" "$REDIS_AUTH" -port=8888 -log_file_prefix=/home/linus_dev/git_103/trunk/PythonSource/web_tornado/$LOG 1>>$LOG 2>&1 &
#nohup ./label_server.py -redis_host=$REDIS_HOST -redis_port=$REDIS_PORT -redis_auth=$REDIS_AUTH -valid_seconds=90 -log_file_prefix=/home/linus_dev/git_103/trunk/PythonSource/web_tornado/$LOG &
#nohup ./$1 --root-path=${ROOT_PATH} --server-port=8888 -log_file_prefix=$(pwd)/$LOG --logging=debug &
nohup ./$1 --server-port=8888 -log_file_prefix=$(pwd)/$LOG --logging=debug &
