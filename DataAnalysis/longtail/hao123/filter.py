import os 
import sys
import esm

black_engine = esm.Index()

adsite_domain=set([])
se_host=set([])

def load_host(files,host_set):
	with open(files) as f:
		for line in f:
			line = line.strip()
			segs = line.split()
			domain= segs[0]
			host_set.add(domain)


def load_black_host(files,engine):
	with open(files) as f:
		for line in f:
			line = line.strip()
			segs = line.split()
			if len(segs):
				domain= segs[0]
				engine.enter(domain)
	engine.fix()
	

load_host("se_host",se_host)
load_host("adsite_out",adsite_domain)

load_black_host("black_host",black_engine)

for line in sys.stdin:
	segs = line.strip().split()
	domain = segs[0]
	pv = int(segs[1])
	if domain in se_host:
		continue
	if black_engine.query(domain):
		continue
	if domain in adsite_domain and pv > 1000 and pv < 900000:
		print domain
