#!/bin/bash
export JAVA_HOME=/apps/jdk
EXECPATH=$(dirname "$0")

if [[ $# -eq 1 ]];then
    DAY=$1
else
    DAY=`date -d "-1 day" "+%Y%m%d"`
fi
echo ${DAY}

HPHOME=/apps/hadoop/bin/
JAR_PACKEGE=/apps/hadoop/share/hadoop/tools/lib/hadoop-streaming-2.6.0-cdh5.5.1.jar

IN_PATH=/data/visit/${DAY}/*
OUT_PATH=host_pv/${DAY}

MAP=$EXECPATH/map_use_dict.py
REDUCE=$EXECPATH/red_use_dict.py

${HPHOME}hadoop fs -test -e ${OUT_PATH}
if [ $? -eq 0 ];then
    ${HPHOME}hadoop fs -rm -r -skipTrash ${OUT_PATH}
fi

${HPHOME}hadoop jar $JAR_PACKEGE \
        -D mapreduce.reduce.memory.mb=4096 \
        -D mapreduce.reduce.java.opts=-Xmx4096m \
        -D mapreduce.jobtracker.split.metainfo.maxsize=150000000 \
        -D mapreduce.tasktracker.map.tasks.maximum=3000 \
        -D mapred.min.split.size=100000000 \
        -D mapred.max.split.size=150000000 \
        -D mapred.job.map.capacity=80 \
        -D stream.recordreader.compression=gzip \
        -D stream.non.zero.exit.is.failure=false \
        -numReduceTasks 50 \
        -input $IN_PATH \
        -output $OUT_PATH \
        -file $MAP \
        -file $REDUCE \
        -mapper $MAP \
        -reducer $REDUCE \

echo "Totally ${DAY} done!!"
DAY_FILE=host_pv_${DAY}.txt
${HPHOME}hadoop fs -cat $OUT_PATH/* > ${DAY_FILE}


