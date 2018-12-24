#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#  Copyright © YXC
# CreateTime: 2016-03-09 10:39:23

"""
Example of generate unique ID
"""

import uuid
import hmac, hashlib

if __name__ == "__main__":
    #using uuid1 to generate a unique ID
    print(uuid.uuid1())

    KEY = '1'
    DATA = 'a'
    print(hmac.new(KEY, DATA, hashlib.sha256).hexdigest())

    MSHA = hashlib.sha1()
    MSHA.update("The quick brown fox jumps over the lazy dog")
    print MSHA.hexdigest()
