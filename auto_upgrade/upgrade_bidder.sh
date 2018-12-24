#!/bin/sh

if [ $# -ne 1 ]; then
    echo "Usage: $0 <bidder_version>"
    exit -1
fi

version=$1
package_file=bidder_revision_${version}.tar.gz
bidder_file=bidder_release

echo ${package_file}
echo ${bidder_file}

if [ ! -f ${package_file} ]; then
    echo "Package file ${package_file} is not exist, Please copy the package file first"
    exit -2
fi

if [ -f ${bidder_file} ]; then
    unlink ${bidder_file}
fi

program_num=`ps -ef | grep bidder_release | grep -v grep | wc -l`
if [ $program_num -gt 0 ]; then
    killall ${bidder_file}
fi

tar -zxf bidder_revision_${version}.tar.gz;cp bidder_revision_${version}/bidder bidder_r${version};ln -s bidder_r${version}  ${bidder_file};/bin/sh runbidder.sh ${bidder_file}
