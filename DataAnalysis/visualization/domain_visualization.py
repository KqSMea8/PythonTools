#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: ‘yuxuecheng‘
@contact: yuxuecheng@baicdata.com
@software: PyCharm Community Edition
@file: domain_visualization.py
@time: 2017/4/14 上午9:04
"""

import sys
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import traceback
import glob

site_set = set()
time_set = set()
domain_set = set()
with open("sites.txt") as fd:
    for line in fd:
        line = line.strip()
        site_set.add(line)

with open("times.txt") as fd:
    for line in fd:
        line = line.strip()
        time_set.add(line)

with open("domains.txt") as fd:
    for line in fd:
        line = line.strip()
        domain_set.add(line)


def analysis_one_domain(data_files):
    """
    Analysis one domain flow for several site and several day
    :param data_files: 
    :return: 
    """
    global site_set
    global time_set
    global domain_set
    for full_file_name in data_files:
        print full_file_name
        base_name = os.path.basename(full_file_name)
        # print base_name
        file_name, extension = os.path.splitext(base_name)
        _, site, time = file_name.split('_')
        print site, time
        if site in site_set and time in time_set:
            print full_dirname
            with open(full_file_name) as fd:
                for line in fd:
                    line = line.strip()
                    try:
                        domain, pv, uv, ipv = line.split("\t")
                        if domain not in domain_set:
                            continue

                        print domain
                        if site in data:
                            site_dict = data[site]
                            site_dict[time] = int(pv)
                        else:
                            site_dict = dict()
                            site_dict[time] = int(pv)
                            data[site] = site_dict
                    except KeyError as ke:
                        traceback.print_exc()
                        print(line)
                        pass
                    except ValueError as ve:
                        traceback.print_exc()
                        print(line)
                        pass

    print data.keys()
    site_dict = data["hangzhou-jingfang"]
    f = pd.DataFrame(data, index=site_dict.keys().sort(), columns=data.keys().sort())
    f.replace(to_replace=np.nan, value=0, inplace=True)
    # f.dropna()
    plt.figure(figsize=(1280, 800))
    f.plot()
    picture_name = "_".join(domain_set) + ".png"
    excel_name = "_".join(domain_set) + "流量分析.xlsx"
    if os.path.exists(picture_name):
        os.remove(picture_name)
    if os.path.exists(excel_name):
        os.remove(excel_name)
    plt.savefig(picture_name)
    f.to_excel(excel_writer=excel_name, sheet_name=u"流量分析")


def analysis_one_site(data_files):
    """
    Analysis one site flow for several domain and several day
    :param data_files: 
    :return: 
    """
    global site_set
    global time_set
    global domain_set
    for full_file_name in data_files:
        print full_file_name
        base_name = os.path.basename(full_file_name)
        # print base_name
        file_name, extension = os.path.splitext(base_name)
        _, site, time = file_name.split('_')
        print site, time
        if site in site_set and time in time_set:
            print full_dirname
            with open(full_file_name) as fd:
                for line in fd:
                    line = line.strip()
                    try:
                        domain, pv, uv, ipv = line.split("\t")
                        if domain not in domain_set:
                            continue

                        print domain
                        if domain in data:
                            domain_dict = data[domain]
                            domain_dict[time] = int(pv)
                        else:
                            domain_dict = dict()
                            domain_dict[time] = int(pv)
                            data[domain] = domain_dict
                    except KeyError as ke:
                        traceback.print_exc()
                        print(line)
                        pass
                    except ValueError as ve:
                        traceback.print_exc()
                        print(line)
                        pass

    print data.keys()
    domain_dict = data[list(domain_set)[0]]
    f = pd.DataFrame(data, index=domain_dict.keys().sort(), columns=data.keys().sort())
    f.replace(to_replace=np.nan, value=0, inplace=True)
    # f.dropna()
    plt.figure(figsize=(1280, 800))
    f.plot()
    picture_name = "_".join(domain_set) + ".png"
    excel_name = "_".join(domain_set) + "流量分析.xlsx"
    if os.path.exists(picture_name):
        os.remove(picture_name)
    if os.path.exists(excel_name):
        os.remove(excel_name)
    plt.savefig(picture_name)
    f.to_excel(excel_writer=excel_name, sheet_name=u"流量分析")


if __name__ == "__main__":
    print(len(sys.argv))
    if len(sys.argv) < 2:
        print("Usage: python {0} <data_file_dir>".format(sys.argv[0]))
    dirname = sys.argv[1]
    full_dirname = os.path.split(os.path.realpath(__file__))[0] + os.path.sep + dirname
    print("Absolute directory is: {0}".format(full_dirname))
    data = dict()
    data_files = glob.glob(full_dirname + "/*")
    print site_set
    print time_set
    print domain_set
    if len(domain_set) == 1:
        analysis_one_domain(data_files)
    elif len(site_set) == 1:
        analysis_one_site(data_files)
    """
    for full_file_name in data_files:
        print full_file_name
        base_name = os.path.basename(full_file_name)
        #print base_name
        file_name, extension = os.path.splitext(base_name)
        _, site, time = file_name.split('_')
        print site, time
        if site in site_set and time in time_set:
            print full_dirname
            with open(full_file_name) as fd:
                for line in fd:
                    line = line.strip()
                    try:
                        domain,pv,uv,ipv = line.split("\t")
                        if domain not in domain_set:
                            continue

                        print domain
                        if site in data:
                            site_dict = data[site]
                            site_dict[time] = int(pv)
                        else:
                            site_dict = dict()
                            site_dict[time] = int(pv)
                            data[site] = site_dict
                    except KeyError as ke:
                        traceback.print_exc()
                        print(line)
                        pass
                    except ValueError as ve:
                        traceback.print_exc()
                        print(line)
                        pass

    print data.keys()
    site_dict = data["hangzhou-jingfang"]
    f = pd.DataFrame(data, index=site_dict.keys().sort(), columns=data.keys().sort())
    f.replace(to_replace=np.nan, value=0, inplace=True)
    #f.dropna()
    plt.figure(figsize=(1280, 800))
    f.plot()
    if os.path.exists("hao123_2.png"):
        os.remove("hao123_2.png")
    if os.path.exists("流量分析2.xlsx"):
        os.remove("流量分析2.xlsx")
    plt.savefig("_".join(domain_set) + ".png")
    f.to_excel(excel_writer="_".join(domain_set) + "流量分析.xlsx", sheet_name=u"流量分析")
    """


