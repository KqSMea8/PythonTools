##!/bin/sh
#
#es_server=127.0.0.1:9200
#
#tag=`date -d "11 min ago" "+%Y%m%d%H%M"`
#tag2=`date -d "12 min ago" "+%Y%m%d%H%M"`
#tag3=`date -d "13 min ago" "+%Y%m%d%H%M"`
#tag4=`date -d "14 min ago" "+%Y%m%d%H%M"`
#tag5=`date -d "15 min ago" "+%Y%m%d%H%M"`
#
#day=${tag:0:8}
#log_dir=/data1/sys
#
##/usr/bin/python parse_log_files.py  -s ${es_server} -f ${log_dir}/$day/rtb_log_crit_$tag.log -f ${log_dir}/$day/rtb_log_crit_$tag2.log -f ${log_dir}/$day/rtb_log_crit_$tag3.log -f ${log_dir}/$day/rtb_log_crit_$tag4.log -f ${log_dir}/$day/rtb_log_crit_$tag5.log -f ${log_dir}/$day/rtb_log_notice_$tag.log -f ${log_dir}/$day/rtb_log_notice_$tag2.log -f ${log_dir}/$day/rtb_log_notice_$tag3.log -f ${log_dir}/$day/rtb_log_notice_$tag4.log -f ${log_dir}/$day/rtb_log_notice_$tag5.log
#/usr/bin/python parse_log_files.py  -s ${es_server} -f ${log_dir}/$day/rtb_log_crit_$tag.log -f ${log_dir}/$day/rtb_log_crit_$tag2.log -f ${log_dir}/$day/rtb_log_crit_$tag3.log -f ${log_dir}/$day/rtb_log_crit_$tag4.log -f ${log_dir}/$day/rtb_log_crit_$tag5.log
##/usr/bin/python parse_log_files.py  -s ${es_server} -f /data1/sys/20170609/rtb_log_crit_201706090942.log

#!/bin/sh

if [ $# -eq 1 ]; then
    day=${1}
else
	day=`date -d "1 day ago" "+%Y%m%d"`
fi

es_server=10.54.8.71:9200
log_dir=/data/logs/sys

echo ${log_dir}
echo ${day}

/usr/bin/python logstats.py -s ${es_server} -d ${log_dir} -t ${day} &