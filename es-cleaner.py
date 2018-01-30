#!/usr/bin/env python

import json
import os
from elasticsearch import Elasticsearch
import datetime
import socket
import logging
import sys
import signal
import time
from dateutil.parser import parse as parse_date

class GracefulKiller:
  kill_now = False
  def __init__(self):
    signal.signal(signal.SIGINT, self.exit_gracefully)
    signal.signal(signal.SIGTERM, self.exit_gracefully)

  def exit_gracefully(self,signum, frame):
    self.kill_now = True

if __name__ == '__main__':
  killer = GracefulKiller()
  es = Elasticsearch(os.environ.get("ES_HOSTS","elasticsearch.weshouse:9200").split(","))
  logging.basicConfig(stream=sys.stdout,
                      level=os.environ.get("LOG_LEVEL","WARN").upper())

  index_list = os.environ.get("INDEX_LIST", "logstash*,gpu-sensor*,metricbeat*").split(",")
  retention_days = int(os.environ.get("RETENTION_DAYS", 3))

  logging.warn("%s starting..." % (os.path.basename(__file__)))
  while not killer.kill_now:
    # Probe any available AMD cards
    try:
      for index_to_clean in index_list:
        indices = es.indices.get(index=index_to_clean)
        for index in indices:
          logging.info("Found index: %s" % (index))
          newest_document = es.search(index=index,
                                      filter_path=['hits.hits._source.@timestamp'],
                                      body=\
                      {
                        'query': {
                          'match_all': {}
                        },
                        'size': 1,
                        'sort': [
                          {
                            '_timestamp': {
                              'order': 'desc'
                            }
                          }
                        ]
                      })
          if newest_document.get("hits", False):
            newest_timestamp = parse_date(newest_document['hits']['hits'][0]['_source']['@timestamp'])
            logging.info("Newest timestamp: %s" % (newest_timestamp))

            if newest_timestamp.replace(tzinfo=None) < (datetime.datetime.utcnow() - 
                                                        datetime.timedelta(days=retention_days)):
              logging.warn("Deleting index: %s" % (index))
              es.indices.delete(index=index)
            else:
              logging.info("Not deleting index: %s" % (index))

    except Exception as inst:
      logging.error("Caught exception: %s, %s" % (type(inst), inst))
    finally:
      pass

    if killer.kill_now:
      break
    time.sleep(float(os.environ.get("SLEEP_TIME", 60)))

  logging.warn("%s exiting gracefully..." % (os.path.basename(__file__)))

