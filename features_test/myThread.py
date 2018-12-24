#!/usr/bin/env python

from __future__ import print_function

import threading
from time import sleep,ctime

class MyThread(threading.Thread):
    def __init__(self, func, args, name=""):
        threading.Thread.__init__(self)
        self.name = name
        self.func = func
        self.args = args

    def run(self):
        print("starting %s at: %s" % (self.name, ctime()))
        self.res = self.func(*self.args)
        print("finished %s at: %s" % (self.name, ctime()))

    def getResult(self):
        return self.res

def loop(nloop, nsec):
    print("start loop %d at: %s" % (nloop, ctime()))
    sleep(nsec)
    print("loop %d done at: %s" % (nloop, ctime()))

def main():
    print("starting at:" + ctime())
    threads = []
    loops = [1, 2, 3, 4, 5];
    nloops = range(len(loops))

    for i in nloops:
        t = MyThread(loop, (i, loops[i]), loop.__name__)
        threads.append(t)

    for i in nloops:
        threads[i].start()

    for i in nloops:
        threads[i].join()

    print("all done at:" + ctime())

if __name__ == "__main__":
    main()
