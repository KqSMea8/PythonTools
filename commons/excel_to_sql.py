#! /usr/bin/env python3
# __author__ = 'Xuecheng Yu'
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#  Copyright YXC
# CreateTime: 2016-08-25 13:10:35
#encoding=utf-8

import xlrd
import xlwt
import pymysql
import sys


def connect(host,port,user,passwd,db=""):
    try:
        conn = pymysql.Connect(host=host,port=int(port),user=user,passwd=passwd,db=db,charset="utf8")
    except Exception as e:
        print(e)
        exit(-1)
    return conn


class ExcelAdaptor(object):
    def __init__(self):
        pass

    def insert_record_from_excel(self, excel_file_name, conn):
        xlrd.Book.encoding = "utf-8"
        excel_file = xlrd.open_workbook(excel_file_name)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM rmc_mp_media_position;")
        for sheet_name in excel_file._sheet_names:
            #if sheet_name == "Base" or sheet_name=="Location":
            if sheet_name != "Base" and sheet_name != "Location":
                print(sheet_name)
                continue;
            sheet = excel_file.sheet_by_name(sheet_name)
            for i in range(sheet.nrows):
                if i == 0:
                    continue
                try:
                    label_name = sheet.cell(colx=0, rowx=i).value
                    label_level = sheet.cell(colx=2, rowx=i).value
                    label_id = sheet.cell(colx=3, rowx=i).value
                    parent_id = sheet.cell(colx=4, rowx=i).value
                except IndexError:
                    continue
                try:
                    label_name = label_name.strip()
                    if label_name.find("'") != 0:
                        string_arr = label_name.split("'")
                        label_name = "\\'".join(string_arr)
                    label_level = int(label_level)
                    label_id = label_id.strip()
                    parent_id = parent_id.strip()
                except Exception as e:
                    print(label_level)
                    print(label_id)
                    print(parent_id)
                    sys.exit(-2)
                if label_name:
                    #sheed_d[key.strip()] = value
                    sql = "INSERT INTO rmc_mp_media_position VALUES ({0},'{1}',{2},{3});".format(label_id, label_name, label_level, parent_id)
                    print(sql)
                    cursor.execute(sql)
        return

    def json_to_excel(self, excel_file_name, json_obj):
        workbook = xlwt.Workbook()
        for key, value_dict in json_obj.iteritems():
            sheet = workbook.add_sheet(key)
            for index, (name, value) in enumerate(value_dict.iteritems()):
                sheet.write(r=index, c=0, label=name)
                if value:
                    sheet.write(r=index, c=1, label=value)
        workbook.save(excel_file_name)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: {0} <file_name>".format(sys.argv[0]))
        sys.exit(-1)
    adaptor = ExcelAdaptor()
    conn = connect("192.168.56.103",3306,"root","Linus_dev!@#123","rmc")
    adaptor.insert_record_from_excel(sys.argv[1], conn)
    # ss = json.dumps(adaptor.excel_to_json(sys.argv[1]), ensure_ascii=False, indent=2)
    # print ss
    # adaptor.json_to_excel(excel_file_name='test.xls', json_obj=json.loads(ss, encoding='utf-8'))
