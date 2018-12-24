#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018-12-24 12:38
# @Author  : yuxuecheng
# @Contact : yuxuecheng@xinluomed.com
# @Site    : 
# @File    : excel_writer.py
# @Software: PyCharm
# @Description 写Excel工具类

import xlwt


class ExcelWriter(object):
    def __init__(self):
        self.workbook = xlwt.Workbook(encoding='utf-8')
        self.sheet_row_index = {}

    def sheet(self, sheet_name):
        new_sheet = self.workbook.add_sheet(sheet_name, cell_overwrite_ok=False)
        return new_sheet

    def add_row(self, sheet, iter_item):
        for col_index, content in enumerate(iter_item):
            # sheet = xlwt.Worksheet()
            sheet.write(r = self.sheet_row_index[sheet], c = col_index, label=content)
        else:
            self.sheet_row_index[sheet] += 1

    def save(self, filename):
        self.workbook.save(filename)
