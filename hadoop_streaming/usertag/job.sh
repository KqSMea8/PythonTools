#!/bin/bash
export JAVA_HOME=/usr/java/jdk1.7.0_45
EXECPATH=$(dirname "$0")

if [[ $# -eq 1 ]];then
    DAY=$1
else
    DAY=`date -d "-1 day" "+%Y%m%d"`
fi
echo "Begin Deal "${DAY}

JAR_PACKEGE=/usr/lib/hadoop-0.20-mapreduce/contrib/streaming/hadoop-streaming.jar

MAP=$EXECPATH/map_cate.py

IN_PATH=/SOURCE/GDPICLICK/${DAY}/[0-2][0-9]/*.ok.gz
#IN_PATH=/SOURCE/GDPICLICK/${DAY}/00/*.ok.gz

OUT_PATH=user_cate/$DAY

hadoop fs -test ${IN_PATH}
if [ $? -ne 0 ];then
    #hadoop fs -rmr -skipTrash $OUT_PATH
    hadoop fs -rmr -skipTrash user_cate/*
fi

${HPHOME}hadoop jar $JAR_PACKEGE \
-D stream.non.zero.exit.is.failure=false   \
-D mapreduce.job.priority=HIGH             \
-D mapreduce.map.memory.mb=4096         \
-D mapreduce.reduce.memory.mb=6144      \
-D mapreduce.map.java.opts=-Xmx1740m    \
-D mapreduce.reduce.java.opts=-Xmx1740m \
        -jobconf mapred.job.queue.name=Q_bcdata \
        -jobconf stream.recordreader.compression=gzip \
    	-jobconf stream.non.zero.exit.is.failure=false \
        -numReduceTasks 10 \
        -input $IN_PATH    \
        -output $OUT_PATH  \
        -file $MAP \
        -mapper $MAP \
        -file $EXECPATH/cate_dict \
        -file $EXECPATH/new_cate_host
#	-cacheArchive pkg/Python-2.5.4.tar.bz2#python
echo "${DAY} done!!"
hadoop fs -text user_cate/$DAY/part* > /data4/husc/baichuan/data/${DAY}.txt

cd /data4/husc/baichuan/dene
./dealdata /data4/husc/baichuan/data /data1/tag/baichuan_result $DAY

exit 0
