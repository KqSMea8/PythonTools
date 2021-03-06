#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018-12-18 10:59
# @Author  : yuxuecheng
# @Contact : yuxuecheng@xinluomed.com
# @Site    :
# @File    : clean_duplicate_data_in_mysql.py
# @Software: PyCharm
# @Description 清除mysql数据库中重复的数据

import os
import MySQLdb
import time
from commons.logger_utils import LogUtils

"""
def init_logging(filename):
    filename = os.path.join("logs", filename)
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)-8s %(filename)s:%(lineno)-4d: %(message)s",
                        datefmt="%m-%d %H:%M:%S",
                        filename=filename,
                        filemode="a")
"""


def connect_mysql(host='localhost', user='root', password='', database='', port=3306, charset='utf8'):
    """
    连接数据库
    :param host: 数据库主机
    :param user: 用户名
    :param password: 密码
    :param database: 数据库名
    :param port: 端口
    :param charset: 字符集
    :return: 数据库连接
    """
    db = MySQLdb.connect(host=host,
                         user=user,
                         passwd=password,
                         db=database,
                         port=port,
                         charset=charset,
                         init_command='show tables;')
    return db


def delete_record(conn, sql, table, hospital_id, patient_id):
    try:
        final_sql = sql.format(patient_id, hospital_id)
        logging.debug(final_sql)
        cursor = conn.cursor()
        cursor.execute(final_sql)
        cursor.close()
        logging.info("clean {0} for {1} success, effected rows: {2}, description: {3}"
                     .format(table, patient_id, cursor.rowcount, cursor.description))
        conn.commit()
    except MySQLdb.Error, e:
        logging.error("clean {0} for {1} failed".format(table, patient_id))
        logging.error(e.args)


def clean_demography(conn, hospital_id, patient_id):
    sql = '''
    DELETE td 
    FROM
        tqlh_demography td
        INNER JOIN tqlh_scene_inpatient tsi ON td.ID = tsi.DEMOGRAPHY_ID 
    WHERE
        tsi.id = "{0}" 
        AND tsi.HOSPITAL_ID = "{1}";
    '''
    delete_record(conn, sql, 'tqlh_demography', hospital_id=hospital_id, patient_id=patient_id)


def clean_symptom(conn, hospital_id, patient_id):
    sql = '''
    DELETE ts 
    FROM
        tqlh_symptom ts
        INNER JOIN tqlh_scene_inpatient tsi ON ts.ID = tsi.SYMPTOM_ID 
    WHERE
        tsi.id = "{0}" 
        AND tsi.HOSPITAL_ID = "{1}";
    '''
    delete_record(conn, sql, 'tqlh_symptom', hospital_id=hospital_id, patient_id=patient_id)


def clean_personal_history(conn, hospital_id, patient_id):
    sql = '''
    DELETE tph 
    FROM
        tqlh_personal_history tph
        INNER JOIN tqlh_scene_inpatient tsi ON tph.ID = tsi.PERSONAL_HISTORY_ID 
    WHERE
        tsi.id = "{0}" 
        AND tsi.HOSPITAL_ID = "{1}";
    '''
    delete_record(conn, sql, 'tqlh_personal_history', hospital_id=hospital_id, patient_id=patient_id)


def clean_physical_examination(conn, hospital_id, patient_id):
    sql = '''
    DELETE tpe 
    FROM
        tqlh_physical_examination tpe
        INNER JOIN tqlh_scene_inpatient tsi ON tpe.ID = tsi.PHYSICAL_EXAMINATION_ID 
    WHERE
        tsi.id = "{0}" 
        AND tsi.HOSPITAL_ID = "{1}";
    '''
    delete_record(conn, sql, 'tqlh_physical_examination', hospital_id=hospital_id, patient_id=patient_id)


def clean_cost(conn, hospital_id, patient_id):
    sql = '''
    DELETE tc 
    FROM
        tqlh_cost tc
        INNER JOIN tqlh_scene_inpatient tsi ON tc.ID = tsi.COST_ID 
    WHERE
        tsi.id = "{0}" 
        AND tsi.HOSPITAL_ID = "{1}";
    '''
    delete_record(conn, sql, 'tqlh_cost', hospital_id=hospital_id, patient_id=patient_id)


def clean_clinical_events(conn, hospital_id, patient_id):
    sql = '''
    DELETE tce 
    FROM
        tqlh_clinical_events tce
        INNER JOIN tqlh_scene_inpatient tsi ON tce.ID = tsi.CLINICAL_EVENTS_ID 
    WHERE
        tsi.id = "{0}" 
        AND tsi.HOSPITAL_ID = "{1}";
    '''
    delete_record(conn, sql, 'tqlh_clinical_events', hospital_id=hospital_id, patient_id=patient_id)


def clean_zrsxzqxzl(conn, hospital_id, patient_id):
    sql = '''
    DELETE tz 
    FROM
        tqlh_zrsxzqxzl tz
        INNER JOIN tqlh_scene_inpatient tsi ON tz.ID = tsi.zrsxzqxzl_id 
    WHERE
        tsi.id = "{0}" 
        AND tsi.HOSPITAL_ID = "{1}";
    '''
    delete_record(conn, sql, 'tqlh_zrsxzqxzl', hospital_id=hospital_id, patient_id=patient_id)


def clean_inpatient_has_bled(conn, hospital_id, patient_id):
    sql = '''
    DELETE tihb 
    FROM
        tqlh_inpatient_has_bled tihb
        INNER JOIN tqlh_scene_inpatient tsi ON tihb.SCENE_INPATIENT_ID = tsi.ID 
    WHERE
        tsi.id = "{0}" 
        AND tsi.HOSPITAL_ID = "{1}";
    '''
    delete_record(conn, sql, 'tqlh_inpatient_has_bled', hospital_id=hospital_id, patient_id=patient_id)


def clean_inpatient_chads_vas(conn, hospital_id, patient_id):
    sql = '''
    DELETE ticv 
    FROM
        tqlh_inpatient_chads_vas ticv
        INNER JOIN tqlh_scene_inpatient tsi ON ticv.SCENE_INPATIENT_ID = tsi.ID 
    WHERE
        tsi.id = "{0}" 
        AND tsi.HOSPITAL_ID = "{1}";
    '''
    delete_record(conn, sql, 'tqlh_inpatient_chads_vas', hospital_id=hospital_id, patient_id=patient_id)


def clean_checkout_result(conn, hospital_id, patient_id):
    sql = '''
    DELETE tcr 
    FROM
        tqlh_checkout_result tcr
        INNER JOIN (
        SELECT
            tisc.CHECKOUT_RESULT_ID 
        FROM
            tqlh_inpatient_result_ck tisc
            INNER JOIN tqlh_scene_inpatient tsi ON tisc.SCENE_INPATIENT_ID = tsi.ID 
        WHERE
            tsi.id = "{0}" 
            AND tsi.HOSPITAL_ID = "{1}" 
        ) t1 ON tcr.ID = t1.CHECKOUT_RESULT_ID;
    '''
    delete_record(conn, sql, 'tqlh_checkout_result', hospital_id=hospital_id, patient_id=patient_id)


def clean_examination_result(conn, hospital_id, patient_id):
    sql = '''
    DELETE ter 
    FROM
        tqlh_examination_result ter
        INNER JOIN (
        SELECT
            tise.EXAMINATION_RESULT_ID 
        FROM
            tqlh_inpatient_result_ex tise
            INNER JOIN tqlh_scene_inpatient tsi ON tise.SCENE_INPATIENT_ID = tsi.ID 
        WHERE
            tsi.id = "{0}" 
            AND tsi.HOSPITAL_ID = "{1}" 
        ) t1 ON ter.ID = t1.EXAMINATION_RESULT_ID;
    '''
    delete_record(conn, sql, 'tqlh_examination_result', hospital_id=hospital_id, patient_id=patient_id)


def clean_treatment_result(conn, hospital_id, patient_id):
    sql = '''
    DELETE ttr 
    FROM
        tqlh_treatment_result ttr
        INNER JOIN (
        SELECT
            tist.TREATMENT_RESULT_ID 
        FROM
            tqlh_inpatient_result_tm tist
            INNER JOIN tqlh_scene_inpatient tsi ON tist.SCENE_INPATIENT_ID = tsi.ID 
        WHERE
            tsi.id = "{0}" 
            AND tsi.HOSPITAL_ID = "{1}" 
        ) t1 ON ttr.ID = t1.TREATMENT_RESULT_ID;
    '''
    delete_record(conn, sql, 'tqlh_treatment_result', hospital_id=hospital_id, patient_id=patient_id)


def clean_inpatient_result_ck(conn, hospital_id, patient_id):
    sql = '''
    DELETE tisc 
    FROM
        tqlh_inpatient_result_ck tisc
        INNER JOIN tqlh_scene_inpatient tsi ON tisc.SCENE_INPATIENT_ID = tsi.ID 
    WHERE
        tsi.id = "{0}" 
        AND tsi.HOSPITAL_ID = "{1}";
    '''
    delete_record(conn, sql, 'tqlh_inpatient_result_ck', hospital_id=hospital_id, patient_id=patient_id)


def clean_inpatient_result_ex(conn, hospital_id, patient_id):
    sql = '''
    DELETE tise 
    FROM
        tqlh_inpatient_result_ex tise
        INNER JOIN tqlh_scene_inpatient tsi ON tise.SCENE_INPATIENT_ID = tsi.ID 
    WHERE
        tsi.id = "{0}" 
        AND tsi.HOSPITAL_ID = "{1}";
    '''
    delete_record(conn, sql, 'tqlh_inpatient_result_ex', hospital_id=hospital_id, patient_id=patient_id)


def clean_inpatient_result_tm(conn, hospital_id, patient_id):
    sql = '''
    DELETE tist 
    FROM
        tqlh_inpatient_result_tm tist
        INNER JOIN tqlh_scene_inpatient tsi ON tist.SCENE_INPATIENT_ID = tsi.ID 
    WHERE
        tsi.id = "{0}" 
        AND tsi.HOSPITAL_ID = "{1}";
    '''
    delete_record(conn, sql, 'tqlh_inpatient_result_tm', hospital_id=hospital_id, patient_id=patient_id)


def clean_scene_inpatient(conn, hospital_id, patient_id):
    sql = '''
    DELETE 
    FROM
        tqlh_scene_inpatient 
    WHERE
        ID = "{0}" 
        AND HOSPITAL_ID = "{1}";
    '''
    delete_record(conn, sql, 'tqlh_scene_inpatient', hospital_id=hospital_id, patient_id=patient_id)


def clean_data_by_id(conn, file_name):
    with open(file_name, mode='r') as fd:
        for line in fd:
            line = line.strip()
            logging.info(line)
            clean_demography(conn=conn, hospital_id="36", patient_id=line)
            clean_symptom(conn=conn, hospital_id="36", patient_id=line)
            clean_personal_history(conn=conn, hospital_id="36", patient_id=line)
            clean_physical_examination(conn=conn, hospital_id="36", patient_id=line)
            clean_cost(conn=conn, hospital_id="36", patient_id=line)
            clean_clinical_events(conn=conn, hospital_id="36", patient_id=line)
            clean_zrsxzqxzl(conn=conn, hospital_id="36", patient_id=line)
            clean_inpatient_has_bled(conn=conn, hospital_id="36", patient_id=line)
            clean_inpatient_chads_vas(conn=conn, hospital_id="36", patient_id=line)
            clean_checkout_result(conn=conn, hospital_id="36", patient_id=line)
            clean_examination_result(conn=conn, hospital_id="36", patient_id=line)
            clean_treatment_result(conn=conn, hospital_id="36", patient_id=line)
            clean_inpatient_result_ck(conn=conn, hospital_id="36", patient_id=line)
            clean_inpatient_result_ex(conn=conn, hospital_id="36", patient_id=line)
            clean_inpatient_result_tm(conn=conn, hospital_id="36", patient_id=line)
            clean_scene_inpatient(conn=conn, hospital_id="36", patient_id=line)


if __name__ == '__main__':
    # init_logging('clean_duplicate_data_in_mysql_{0}.log'.format(time.strftime('%Y%m%d%H%M%S')))
    logfile_prefix = 'clean_duplicate_data_in_mysql_{0}'.format(time.strftime('%Y%m%d%H%M%S'))
    # logfile_prefix = 'clean_duplicate_data_in_mysql_{0}'.format(time.strftime('%Y%m%d'))
    logging = LogUtils(file_name_prefix=logfile_prefix, include_low_level=False)
    host = 'localhost'
    port = 3306
    user_name = 'root'
    password = '123456'
    database = 'test'
    conn = connect_mysql(host=host, port=port, password=password, user=user_name, database=database)
    clean_data_by_id(conn, 'duplicate_zyh_inpatient_id_test.txt')
