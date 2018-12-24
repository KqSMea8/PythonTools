#!/bin/sh
startday=`date -d "-1 day" "+%Y%m%d"`
startday=`date  +"%Y%m%d" -d  "-1 day"`
endday=`date  +"%Y%m%d" -d  "-1 day"`
if [[ $# -eq 1 ]];then
    startday=$1
elif [[ $# -eq 2 ]]; then
    startday=$1
    endday=$2    
fi


while [ $startday -le $endday ]
do
    echo "BeginDeal Day = "$startday
    sh job.sh $startday
    echo "EndDeal   Day = "$startday
    startday=$(date +%Y%m%d -d "tomorrow $startday")    
done
