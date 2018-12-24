import os
import sys 
import MySQLdb


def connect(host,port,user,passwd,db=""):
    try:
        conn = MySQLdb.connect(host=host,port=int(port),user=user,passwd=passwd,db=db,charset="utf8")
    except Exception as e:
        print e
        exit(-1) 
    return conn

def test():
    conn = connect("192.168.6.13",3306,"bc","bc!@#Q4","rmc")
    cursor = conn.cursor()
    cursor.execute("show databases")
    ret = cursor.fetchall()
    for i in ret:
        print i
    
    cursor.close()    
    conn.close()

def load_tag_table():
    query_str = "select id,feq,sql_string from rmc_user_tag where enabled = 0"
    conn = connect("192.168.6.13",3306,"bc","bc!@#Q4","rmc")
    cursor = conn.cursor()
    cursor.execute(query_str) 
    res = cursor.fetchall()
    cursor.close()    
    conn.close()  

    for row in res:
        print row    
