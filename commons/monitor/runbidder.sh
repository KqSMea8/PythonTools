#! /bin/sh
program=`basename $0`
if [ $# != 1 ]; then
    echo "Usage: ${program} <program_name> [kill], kill is optional argument"
    exit -1
fi

killall -q -9 $1
killall -q -9 spawn-fcgi

if [ "$2" = "kill" ];then
  exit 0
fi

#spawn-fcgi -p 12345 -F 1 -- /usr/bin/valgrind  --leak-check=full --show-reachable=yes --trace-children=yes --log-file=/tmp/valgrind.log ./bidder


# for formal use
#SPAWNFCGI=/usr/local/bin/spawn-fcgi
SPAWNFCGI=/usr/local/spawn-fcgi/bin/spawn-fcgi
EXEC=$1

sleep 0.1

$SPAWNFCGI -p 12300 -F 4 -- $EXEC
#$SPAWNFCGI -p 12345 -F 1 -- $EXEC
#$SPAWNFCGI -p 12395 -F 1 -- $EXEC

