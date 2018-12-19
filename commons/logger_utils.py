#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018-12-19 09:35
# @Author  : yuxuecheng
# @Contact : yuxuecheng@xinluomed.com
# @Site    : 
# @File    : logger_utils.py
# @Software: PyCharm
# @Description 日志打印工具类

"""
该日志类可以把不同级别的日志输出到不同的日志文件中
"""

import os
import time
import logging
import inspect
from collections import Iterable


# 加载模块时创建全局变量
# create_handlers("")


class LogUtils(object):
    def __init__(self,
                 file_name_prefix,
                 file_path = "logs",
                 mode='a',
                 include_low_level=False,
                 time_format='%Y-%m-%d %H:%M:%S',
                 level=None):
        self.__loggers = {}
        self.file_path = file_path
        self.file_name_prefix = file_name_prefix
        self.log_level_file_map = {logging.NOTSET: "{0}/{1}-notset.log",
                                   logging.DEBUG: "{0}/{1}-debug.log",
                                   logging.INFO: "{0}/{1}-info.log",
                                   logging.WARNING: "{0}/{1}-warning.log",
                                   logging.ERROR: "{0}/{1}-error.log",
                                   logging.CRITICAL: "{0}/{1}-critical.log"}
        self.time_format = time_format
        self.include_low_level = include_low_level
        self.mode = mode
        self.log_levels = set()
        if level is not None:
            if isinstance(level, int):
                self.log_levels.add(level)
            elif isinstance(level, Iterable):
                self.log_levels.update(level)
        else:
            self.log_levels = self.log_level_file_map.keys()
        self.create_handlers()

    def current_time_str(self):
        return time.strftime(self.time_format, time.localtime())

    def create_handlers(self):
        for level in self.log_levels:
            path = os.path.abspath(self.log_level_file_map[level].format(self.file_path, self.file_name_prefix))
            logger = logging.getLogger(str(level))
            logger.addHandler(logging.FileHandler(path, self.mode))
            logger.setLevel(level)
            self.__loggers.update({level: logger})

    def get_log_message(self, level, message):
        frame, filename, lineNo, functionName, code, unknowField = inspect.stack()[2]
        '''日志格式：[时间] [类型] [记录代码] 信息'''
        return "[%s] [%s] [%s - %s - %s] %s" % (self.current_time_str(), level, filename, lineNo, functionName, message)

    def debug_raw(self, message):
        self.__loggers[logging.DEBUG].debug(message)
        if self.include_low_level:
            self.info_raw(message)

    def debug(self, message):
        message = self.get_log_message("debug", message)
        self.__loggers[logging.DEBUG].debug(message)
        if self.include_low_level:
            self.info_raw(message)

    def info_raw(self, message):
        self.__loggers[logging.INFO].info(message)
        if self.include_low_level:
            self.warning_raw(message)

    def info(self, message):
        message = self.get_log_message("info", message)
        self.__loggers[logging.INFO].info(message)
        if self.include_low_level:
            self.warning_raw(message)

    def warning_raw(self, message):
        self.__loggers[logging.WARNING].warning(message)
        if self.include_low_level:
            self.error_raw(message)

    def warning(self, message):
        message = self.get_log_message("warning", message)
        self.__loggers[logging.WARNING].warning(message)
        if self.include_low_level:
            self.error_raw(message)

    def error_raw(self, message):
        self.__loggers[logging.ERROR].error(message)
        if self.include_low_level:
            self.critical_raw(message)

    def error(self, message):
        message = self.get_log_message("error", message)
        self.__loggers[logging.ERROR].error(message)
        if self.include_low_level:
            self.critical_raw(message)

    def critical_raw(self, message):
        self.__loggers[logging.CRITICAL].critical(message)

    def critical(self, message):
        message = self.get_log_message("critical", message)
        self.__loggers[logging.CRITICAL].critical(message)


if __name__ == "__main__":
    logfile_prefix = 'clean_duplicate_data_in_mysql_{0}'.format(time.strftime('%Y%m%d%H%M%S'))
    logger = LogUtils(file_name_prefix=logfile_prefix, file_path='../logs', include_low_level=True)
    logger.debug("debug")
    # logger = TNLog()
    logger.info("info")
    # logger = TNLog()
    logger.warning("warning")
    # logger = TNLog()
    logger.error("error")
    # logger = TNLog()
    logger.critical("critical")
