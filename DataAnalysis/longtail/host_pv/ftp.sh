#!/usr/bin/bash

IP=192.168.122.154
#ftp -i -n $IP <<FTPIT
ftp -i -n <<FTPIT
open $IP 2001
user guest guest!@#Q4
bin
passive
cd /host_pv
put job.log
quit
FTPIT
