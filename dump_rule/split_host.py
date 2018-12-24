#!/usr/bin/env python
import os
import sys


seg_num = int(sys.argv[1])

for line in sys.stdin:
	line = line.strip()
	segs = line.split('.')
	if len(segs) <= seg_num:
		print line


