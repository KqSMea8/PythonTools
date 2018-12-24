#!/bin/bash
export JAVA_HOME=/usr/java/jdk1.7.0_67
EXECPATH=$(dirname "$0")

if [[ $# -eq 2 ]];then
    DAY=$1
    DPC=$2
elif [[ $# -eq 1 ]];then
    DAY=$1
    DPC="hangzhou-wulin"
else
    echo "Usage: /bin/sh $0 <DAY> <DPC_name>"
    exit 0
fi

echo ${DAY}
echo ${DPC}

HPHOME=/usr/lib/hadoop/bin/
JAR_PACKEGE=/usr/lib/hadoop-mapreduce/hadoop-streaming-2.5.0-cdh5.2.0.jar

IN_PATH=/user/bcdata/logs/dpc/${DPC}/${DAY}/mtdpc_redirect_*
OUT_PATH=longtail/hao123/${DPC}/${DAY}

#HPHOME=/usr/lib/hadoop/bin/
#JAR_PACKEGE=/usr/lib/hadoop-mapreduce/hadoop-streaming-2.3.0-cdh5.0.0.jar

MAP=$EXECPATH/map_use_dict.py
REDUCE=$EXECPATH/red_use_dict.py

#IN_PATH=/SOURCE/GDPICLICK/20151215/[0-1][0-9]/*
#IN_PATH=/user/gdpi/public/sada_gdpi_click/${DAY}/[0-2][0-9]/*
#IN_PATH=/user/cdpi/public/sada_cdpi_userflow/${DAY}/[0-2][0-9]/*,/user/cdpi/public/sada_cdpi_userflow_4g/${DAY}/[0-2][0-9]/*
#IN_PATH=/user/cdpi/public/sada_cdpi_userflow/${DAY}/[0-2][0-9]/*,/user/cdpi/public/sada_cdpi_userflow_4g/${DAY}/[0-2][0-9]/*
#OUT_PATH=private/gdpi_pv/$DAY

${HPHOME}hadoop fs -test ${IN_PATH}
if [ $? -ne 0 ];then
${HPHOME}hadoop fs -rmr -skipTrash $OUT_PATH
fi

${HPHOME}hadoop jar $JAR_PACKEGE \
        -jobconf mapreduce.reduce.memory.mb=4096 \
        -jobconf mapreduce.reduce.java.opts=-Xmx4096m \
        -jobconf mapreduce.jobtracker.split.metainfo.maxsize=150000000 \
        -jobconf mapreduce.tasktracker.map.tasks.maximum=3000 \
        -jobconf mapred.min.split.size=100000000 \
        -jobconf mapred.max.split.size=150000000 \
        -jobconf mapred.job.map.capacity=80 \
        -jobconf mapred.job.queue.name=Q_bcdata \
	-jobconf stream.recordreader.compression=gzip \
    	-jobconf stream.non.zero.exit.is.failure=false \
        -jobconf mapred.job.name='baichuan_job_1' \
	-numReduceTasks 50 \
        -input $IN_PATH \
        -output $OUT_PATH \
        -file $MAP \
        -file $REDUCE \
        -mapper $MAP \
        -reducer $REDUCE \
#	-cacheArchive pkg/Python-2.5.4.tar.bz2#python
echo "Totally ${DPC} ${DAY} done!!"
DAY_FILE=hao123_${DPC}_${DAY}.txt
${HPHOME}hadoop fs -cat $OUT_PATH/* > ${DAY_FILE}
