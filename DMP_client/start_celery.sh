#!/bin/sh 
nohup celery -A tasks worker --loglevel=debug -c4 &

