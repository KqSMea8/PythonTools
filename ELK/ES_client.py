#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@author: ‘yuxuecheng‘
@contact: yuxuecheng@baicdata.com
@software: PyCharm Community Edition
@file: ES_client.py.py
@time: 22/08/2017 14:58
"""

import json
import logging
import traceback

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk


def add_user_label_data( esclient, filename ):
    type = "user_tag_type"
    with open(name=filename, mode='r') as fd:
        actions = list()
        bulk_num = 0
        for line in fd:
            line = line.strip()
            segs = line.split(None, 1)
            adsl = segs[0].strip()
            label_datas = segs[1].strip().split(",")
            labels = list()
            for label_data in label_datas:
                label_id, times = label_data.split(":")
                label = {"id": label_id.strip(), "number": int(times.strip())}
                labels.append(label)
            data = dict()
            user = dict()
            user["adsl"] = adsl
            user["label"] = labels
            data["user"] = user
            action = {"_index": "user_tag", "_type": type, "_source": data, "_id": adsl}
            actions.append(action)
            bulk_num += 1
            if bulk_num >= 100:
                try:
                    bulk(esclient, actions, raise_on_error=True)
                    bulk_num = 0
                    actions = []
                except:
                    # info = sys.exc_info()
                    # logging.error("{0} : {1}".format(info[0], info[1]))
                    logging.error(traceback.print_exc())
        if bulk_num >= 0:
            try:
                bulk(esclient, actions, raise_on_error=True)
                bulk_num = 0
                actions = []
            except:
                # info = sys.exc_info()
                # logging.error("{0} : {1}".format(info[0], info[1]))
                logging.error(traceback.print_exc())


def simple_search( esclient ):
    body = {
        "query": {
            "nested": {
                "path": "user.label",
                "query": {
                    "bool": {
                        "must": [
                            {
                                "match": {
                                    "user.label.id": "X001010000"
                                }
                            }
                        ]
                    }
                }
            }
        }
    }
    res = esclient.search(index="user_tag", doc_type="user_tag_type", body=body, size=20)
    print(json.dumps(res, indent=2))
    for hit in res['hits']['hits']:
        print(json.dumps(hit["_source"], indent=2))


def simple_search2( esclient ):
    """
    queries for user has label X001010000 and the number of this label is greater than or equal to 5.
    :param esclient: 
    :return: 
    
    the return example:
    {
      "user": {
        "adsl": "8617328805805", 
        "label": [
          {
            "id": "X001010000", 
            "number": 6
          }
        ]
      }
    }
    {
      "user": {
        "adsl": "8613385772285", 
        "label": [
          {
            "id": "X001010000", 
            "number": 5
          }
        ]
      }
    }
    {
      "user": {
        "adsl": "8617767112898", 
        "label": [
          {
            "id": "X001008000", 
            "number": 14
          }, 
          {
            "id": "X001010000", 
            "number": 14
          }, 
          {
            "id": "X001006001", 
            "number": 3
          }, 
          {
            "id": "X001005012", 
            "number": 3
          }, 
          {
            "id": "X001003112", 
            "number": 3
          }, 
          {
            "id": "X001002003", 
            "number": 3
          }, 
          {
            "id": "X001004003", 
            "number": 3
          }, 
          {
            "id": "X001001003", 
            "number": 3
          }
        ]
      }
    }
    {
      "user": {
        "adsl": "8618005899559", 
        "label": [
          {
            "id": "X001010000", 
            "number": 30
          }, 
          {
            "id": "X001005009", 
            "number": 18
          }, 
          {
            "id": "X001006002", 
            "number": 18
          }, 
          {
            "id": "X001002001", 
            "number": 18
          }, 
          {
            "id": "X001002002", 
            "number": 18
          }, 
          {
            "id": "X001004003", 
            "number": 18
          }, 
          {
            "id": "X001001008", 
            "number": 18
          }, 
          {
            "id": "X001003063", 
            "number": 18
          }, 
          {
            "id": "X001008000", 
            "number": 1
          }
        ]
      }
    }
    """
    body = {
        "query": {
            "nested": {
                "path": "user.label",
                "query": {
                    "bool": {
                        "must": [
                            {
                                "match": {
                                    "user.label.id": "X001010000"
                                }
                            },
                            {
                                "range": {
                                    "user.label.number": {
                                        "gte": 5
                                    }
                                }
                            }
                        ]
                    }
                }
            }
        }
    }
    res = esclient.search(index="user_tag", doc_type="user_tag_type", body=body, size=20)
    # print(json.dumps(res, indent=2))
    for hit in res['hits']['hits']:
        print(json.dumps(hit["_source"], indent=2))


def search_and_aggs( esclient ):
    """
    获取符合条件的用户数量，用户具有标签X001010000，并且该标签数量大于等于5
    :param esclient: 
    :return: 
    """
    body = {
        "query": {
            "nested": {
                "path": "user.label",
                "query": {
                    "bool": {
                        "must": [
                            {
                                "bool": {
                                    "must": [
                                        {
                                            "match": {
                                                "user.label.id": "X001010000"
                                            }
                                        },
                                        {
                                            "range": {
                                                "user.label.number": {
                                                    "gte": 5
                                                }
                                            }
                                        }
                                    ]
                                }
                            },
                            {
                                "bool": {
                                    "must": [
                                        {
                                            "match": {
                                                "user.label.id": "X001001008"
                                            }
                                        }

                                    ]

                                }
                            }

                        ]
                    }
                }
            }
        },
        "aggs": {
            "user_count": {
                "cardinality": {
                    "field": "user.adsl.raw"
                }
            }
        }
    }
    res = esclient.search(index="user_tag", doc_type="user_tag_type", body=body, size=20)
    # print(json.dumps(res, indent=2))
    print(json.dumps(res["aggregations"], indent=2))
    for hit in res['hits']['hits']:
        print(json.dumps(hit["_source"], indent=2))


def simple_aggs( esclient ):
    body = {
        "aggs": {
            "user_count": {
                "cardinality": {
                    "field": "user.adsl.raw"
                }
            }
        }
    }
    res = esclient.search(index="user_tag", doc_type="user_tag_type", body=body, size=20)
    # print(json.dumps(res["aggregations"], indent=2))
    adsl_set = set()
    for hit in res['hits']['hits']:
        adsl_set.add(hit["_source"]["user"]["adsl"])

    print(len(adsl_set))
    print("\t".join(adsl_set))


if __name__ == "__main__":
    esclient = Elasticsearch(['218.95.37.247:9200'])
    # simple_search(esclient)
    # simple_search2(esclient)
    # simple_aggs(esclient)
    search_and_aggs(esclient)
    add_user_label_data(esclient, "user_label_data.txt")
