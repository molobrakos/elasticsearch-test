# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import os
import sys
import time
import logging
import json

_LOGGER = logging.getLogger(__name__)

def db_create():
    from elasticsearch import Elasticsearch
    db_uri = os.environ["DB_URI"]
    es = Elasticsearch([db_uri],
                       retry_on_timeout=True)

    _LOGGER.info("waiting for db ...")
    logging.getLogger("elasticsearch").setLevel(logging.CRITICAL)
    while True:
        try:
            if not es.ping():
                raise ConnectionRefusedError("ping failed")
            info = es.info()
            for k, v in info.items():
                _LOGGER.info("info %s = %s", k, v)
            info = es.cluster.health(wait_for_status="green")
            for k, v in info.items():
                _LOGGER.info("health %s = %s", k, v)
            logging.getLogger("elasticsearch").setLevel(logging.WARN)
            _LOGGER.info("... db is up!")
            return es
        except Exception as e:
            _LOGGER.info("... db not up yet: %s", e)
            time.sleep(1)
   

def db_index(es, item, idx):
    if "url" not in item:
        _LOGGER.error("could not handle item %s", item)
        return
        
    if "product" in item["url"]:
        index = "product"
    elif "substance" in item["url"]:
        index = "substance"
    else:
        _LOGGER.error("could not handle item %s", item)
        return

    id = item["id"]
    
    es.index(index=index,
             body=item)

    _LOGGER.info("Indexed item %d: %20s (%s)",
                 idx, id, index)


def db_search(es, index, search):
    _LOGGER.info("Serching in index %s for %s ...", index, search)
    result = es.search(index=index,
                       body=search)
    _LOGGER.info("... got %d matches", result["hits"]["total"])


def main():
    logging.basicConfig(level=logging.INFO) 
    _LOGGER.info("welcome!")
    
    es = db_create()

    if es.indices.exists(index="product"):
        count = es.count(index="product")
        _LOGGER.info("Index already exists with %d items", count)
    else:
        for idx, line in enumerate(sys.stdin):
            item = json.loads(line)
            db_index(es, item, idx)

    _LOGGER.info("All item indexed")

    db_search(es, "product", dict(query=dict(match=dict(atc="A02BC01"))))
    db_search(es, "product", dict(query=dict(match=dict(name="Omeprazol"))))
    db_search(es, "product", dict(query=dict(match=dict(text="yrsel"))))

        
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        _LOGGER.exception(e)
