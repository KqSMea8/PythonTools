# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re

from django.http import HttpResponse

import config
import parse_rtb_log


# Create your views here.


def index(request):
    return HttpResponse("Hello, world. You're at the retargeting index.")


def get_click_user(request):
    day = request.GET.get("day")
    ad_id = request.GET.get("adid")
    label = request.GET.get("label")
    ad_click_user_map = parse_rtb_log.get_click_user(".", day, ["rtb_log_crit"])
    print("enter get_click_user view, day %s, ad_id %s" % (day, ad_id))
    redis_host = config.get_value("redis_server", "host")
    redis_port = config.get_int_value("redis_server", "port")
    redis_password = config.get_value("redis_server", "password")
    label_user_index = config.get_int_value("redis_server", "label_user_index")
    user_label_index = config.get_int_value("redis_server", "user_label_index")

    redis_client_label_user = parse_rtb_log.connect_redis(host=redis_host, port=redis_port, db_index=label_user_index,
                                                          password=redis_password)
    redis_client_user_label = parse_rtb_log.connect_redis(host=redis_host, port=redis_port, db_index=user_label_index,
                                                          password=redis_password)
    user_id_set = ad_click_user_map[ad_id]
    print(",".join(user_id_set))
    for user_id in user_id_set:
        redis_client_label_user.sadd(label, user_id)
        old_label = redis_client_user_label.get(user_id)
        new_label = label
        if old_label is not None:
            old_label_set = set(re.split(",|:|;", old_label))
            old_label_set.add(label)
            new_label = ",".join(old_label_set)
        redis_client_user_label.set(user_id, new_label)
    return HttpResponse("Hello welcome to use get_click_user")


def get_click_domain(request):
    day = request.GET.get("day")
    ad_id = request.GET.get("adid")
    ad_click_domain_map = parse_rtb_log.get_click_domain(".", day, ad_id, ["rtb_log_crit"])
    print("enter get_click_domain view")
    redis_client = parse_rtb_log.connect_redis(host="127.0.0.1", port=63791, db_index=2, password='yxc')
    for adid in ad_click_domain_map.keys():
        print(adid)
        domain_set = ad_click_domain_map[adid]
        for domain in domain_set:
            redis_client.sadd(adid, domain)
    return HttpResponse("Hello welcome to use get_click_domain")


def get_click_pos(request):
    day = request.GET.get("day")
    ad_id = request.GET.get("adid")
    ad_click_pos_map = parse_rtb_log.get_click_pos(".", day, ad_id, ["rtb_log_crit"])
    print("enter get_click_pos view")
    redis_client = parse_rtb_log.connect_redis(host="127.0.0.1", port=63791, db_index=3, password='yxc')
    for adid in ad_click_pos_map.keys():
        print(adid)
        pos_id_set = ad_click_pos_map[adid]
        for pos_id in pos_id_set:
            redis_client.sadd(adid, pos_id)
    return HttpResponse("Hello welcome to use get_click_pos")
