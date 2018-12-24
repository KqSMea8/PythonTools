#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: ‘yuxuecheng‘
@contact: yuxuecheng@baicdata.com
@software: PyCharm Community Edition
@file: wordcount_test.py
@time: 2017/4/1 下午3:08
"""

import os
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from pysqlite2 import dbapi2 as sqlite
from PIL import Image
import numpy as np


"""
This is the tool to generate the word cloud from the result of document classify.
"""


def get_feature_count(db, cat):
    frequencies = dict()
    res = db.execute(
        'select feature, count from fc where category="%s" order by count desc limit 20'
        % (cat)).fetchall()
    if res is None:
        return {0:0.0}
    else:
        for record in res:
            frequencies[record[0]] = record[1]

    return frequencies

if __name__ == "__main__":
    #FONT_PATH = os.environ.get("FONT_PATH", os.path.join(os.path.dirname(__file__),
    #                                                     "simhei.ttf"))
    # read the mask image
    # taken from
    # http://www.stencilry.org/stencils/movies/alice%20in%20wonderland/255fk.jpg
    alice_mask = np.array(Image.open(os.path.join(os.path.dirname(__file__), "alice_mask.png")))
    path = os.path.join(os.path.dirname(__file__), "simhei.ttf")
    fc = {"hello": 2.2, "world": 1.5, "test": 0.5}
    saved_dir = "longtail_pic"
    db = sqlite.connect("longtail")
    cur = db.execute('select category from cc')
    categories = [d[0] for d in cur]
    for category in categories:
        freq = get_feature_count(db, category)
        wc = WordCloud(max_font_size=100, relative_scaling=.5, font_path=path, margin=5, width=1800, height=800, mask=alice_mask).fit_words(freq)
        plt.axis("off")
        category = category.replace("/", "_")
        pic_name = "%s.png" % category
        plt.imsave(os.path.join(saved_dir, pic_name), wc)