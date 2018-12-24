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


def update_db_tag_num():
    tag_num={2:111}
    conn = connect("192.168.6.13",3306,"bc","bc!@#Q4","rmc")
    sql_str = "update rmc_user_tag set coverage=%d where id=%d;" 
    cursor = conn.cursor()
    for tag in tag_num:
        sql = sql_str % (int(tag_num[tag]),int(tag))
        cursor.execute(sql)
    conn.commit()
    cursor.close()
    conn.close()

 
#update_db_tag_num() 


 
