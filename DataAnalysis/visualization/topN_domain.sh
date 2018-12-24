#!/bin/sh

file=hao123_hangzhou-jingfang_20170318.txt
if [ $# -eq 2 ]; then
	file=$1
	topN=$2
else
	echo "Usage " $0 " <data_file> <topN>"
	exit 0
fi

#echo ${file}

echo "top " ${topN} " domain in file " ${file} " is: "
cat ${file} | awk '{print $2,$1}' | sort -nr | head -n ${topN}
