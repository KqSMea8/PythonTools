#! /usr/bin/env python
# __author__ = 'Xuecheng Yu'
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#  Copyright YXC
# CreateTime: 2016-07-12 10:49:33

class Person:
    # This is class contain static method and class method
    def __init__(self):
        print "init"

    @staticmethod
    def sayHello(hello):
        if not hello:
            hello = "hello"
        print "i will say %s" % hello

    @classmethod
    def introduce(clazz, hello):
        clazz.sayHello(hello)
        print "from introduce method"

    def hello(self, hello):
        self.sayHello(hello)
        print "from hello method"

def main():
    Person.sayHello("haha")
    Person.introduce("hello world")
    #Person.hello("self.hello") TypeError: unbound method hello() must be called with Person instance as first argument (got str instance instead)

    print "*" * 20
    p = Person()
    p.sayHello("haha")
    p.introduce("hello world")
    p.hello("self.hello")

if __name__ == '__main__':
    main()
