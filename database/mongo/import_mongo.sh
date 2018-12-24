#/bin/sh

dirname=$(pwd)

if [ ! -z $1 ]; then
    dirname=$1
fi

if [ ${dirname: -1} = '/' ]; then
    dirname=${dirname:0:-1}
    echo $dirname
fi

filelist=`ls ${dirname}`

for file in ${filelist}
do
    coll=${file%.*}
    extension=${file##*.}
    echo ${coll}
    echo ${extension}
    cmd="mongoimport -h 115.29.188.63 --port 10086 -d sdpp_4mp_exp -c ${coll} --file ${dirname}/${file}"
    echo ${cmd}
done

