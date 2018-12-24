#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#  Copyright © YXC
# CreateTime: 2016-03-09 10:47:47

"""
Example for serialize the content
"""

import pickle
import json

def orig_serialize():
    """
    Use the original Python serialize method
    """
    variable = ['hello', 42, [1, 'two'], 'apple']

    #serialize content
    with open("serial.txt", "w") as write_fd:
        serialize_obj = pickle.dumps(variable)
        write_fd.write(serialize_obj)
        print(serialize_obj)

    #unserialize to produce original content
    with open("serial.txt", "r") as read_fd:
        my_obj = pickle.load(read_fd)
        print(my_obj)

def json_serialize():
    """
    use json tools to serizlize content
    """
    variable = ['hello', 42, [1, 'two'], 'apple']
    print("Original {0} - {1}".format(variable, type(variable)))

    #encoding
    encode = json.dumps(variable)
    print("Encoded {0} - {1}".format(encode, type(encode)))

    #decoding
    decoded = json.loads(encode)
    print("Decoded {0} - {1}".format(decoded, type(decoded)))


if __name__ == "__main__":
    orig_serialize()
    json_serialize()
