#!/bin/bash
export JAVA_HOME=/usr/java/jdk1.7.0_67
EXECPATH=$(dirname "$0")

if [[ $# -eq 1 ]];then
    DAY=$1
else
    DAY=`date -d "-1 day" "+%Y%m%d"`
fi
echo ${DAY}

#HPHOME=/usr/lib/hadoop/bin/
#JAR_PACKEGE=/usr/lib/hadoop-mapreduce/hadoop-streaming-2.3.0-cdh5.0.0.jar
HPHOME=/usr/lib/hadoop/bin/
JAR_PACKEGE=/usr/lib/hadoop-mapreduce/hadoop-streaming-2.5.0-cdh5.2.0.jar

IN_PATH=/SOURCE/GDPICLICK/${DAY}/[0-2][0-9]/*
OUT_PATH=longtail/adsite/${DAY}

MAP=$EXECPATH/map.py
#REDUCE=/usr/bin/uniq
REDUCE=reduce.py

#IN_PATH=/SOURCE/GDPICLICK/20151215/[0-1][0-9]/*
#IN_PATH=/user/gdpi/public/sada_gdpi_click/${DAY}/[0-2][0-9]/*
#IN_PATH=/user/cdpi/public/sada_cdpi_userflow/${DAY}/10/*
#OUT_PATH=private/judge_adsite/$DAY

${HPHOME}hadoop fs -test ${IN_PATH}
if [ $? -ne 0 ];then
${HPHOME}hadoop fs -rmr -skipTrash $OUT_PATH
fi

${HPHOME}hadoop jar $JAR_PACKEGE \
        -jobconf mapreduce.reduce.memory.mb=4048 \
        -jobconf mapreduce.reduce.java.opts=-Xmx4048m \
        -jobconf mapred.job.queue.name=Q_bcdata \
        -jobconf stream.recordreader.compression=gzip \
    	-jobconf stream.non.zero.exit.is.failure=false \
    	-numReduceTasks 100 \
        -input $IN_PATH \
        -output $OUT_PATH \
        -file $MAP \
        -file $REDUCE \
        -mapper $MAP \
        -reducer $REDUCE \
        -file $EXECPATH/esm.so \
        -file $EXECPATH/adsite.py \
        -file $EXECPATH/black_host 
#	-cacheArchive pkg/Python-2.5.4.tar.bz2#python
echo "Totally ${DAY} done!!"
DAY_FILE=adsite_${DAY}.txt
hadoop fs -text longtail/adsite/${DAY}/* > $EXECPATH/$DAY_FILE
IP=192.168.122.154
#ftp -i -n $IP <<FTPIT
ftp -i -n <<FTPIT
open $IP 2001
user guest guest!@#Q4
bin
passive
mkdir adsite
cd /adsite
put $EXECPATH/${DAY_FILE} /adsite/${DAY_FILE}
quit
FTPIT
exit 0
