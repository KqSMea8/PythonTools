#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018-12-24 10:45
# @Author  : yuxuecheng
# @Contact : yuxuecheng@xinluomed.com
# @Site    : 
# @File    : excel_adaptor.py
# @Software: PyCharm
# @Description Excel接口类

import xlrd
import xlwt
import json
import sys


class ExcelAdaptor(object):
    def __init__(self):
        pass

    def excel_to_json(self, excel_file_name):
        excel_file = xlrd.open_workbook(excel_file_name)
        book_d = {}
        for sheet_name in excel_file._sheet_names:
            sheet = excel_file.sheet_by_name(sheet_name)
            sheed_d = {}
            for i in range(sheet.nrows):
                key = None
                try:
                    key = sheet.cell(colx=0, rowx=i).value
                    key = key.strip()
                    value = sheet.cell(colx=1, rowx=i).value
                except IndexError:
                    value = None
                if key is None:
                    sheed_d[key.strip()] = value
            else:
                book_d[sheet_name.strip()] = sheed_d
        return book_d

    def json_to_excel(self, excel_file_name, json_obj):
        workbook = xlwt.Workbook()
        for key, value_dict in json_obj.items():
            sheet = workbook.add_sheet(key)
            for index, (name, value) in enumerate(value_dict.items()):
                sheet.write(r=index, c=0, label=name)
                if value:
                    sheet.write(r=index, c=1, label=value)
        workbook.save(excel_file_name)


if __name__ == '__main__':
    adaptor = ExcelAdaptor()
    ss = json.dumps(adaptor.excel_to_json(sys.argv[1]), ensure_ascii=False, indent=2)
    print(ss)
    # adaptor.json_to_excel(excel_file_name='test.xls', json_obj=json.loads(ss, encoding='utf-8'))
