#!/usr/bin/env python

import json
import os
from elasticsearch import Elasticsearch
from datetime import datetime
import socket
import logging
import sys
import signal
import time

class GracefulKiller:
  kill_now = False
  def __init__(self):
    signal.signal(signal.SIGINT, self.exit_gracefully)
    signal.signal(signal.SIGTERM, self.exit_gracefully)

  def exit_gracefully(self,signum, frame):
    self.kill_now = True

if __name__ == '__main__':
  killer = GracefulKiller()
  es = Elasticsearch(os.environ.get("ES_HOSTS","172.16.1.17:9200").split(","))
  logging.basicConfig(stream=sys.stdout,
                      level=os.environ.get("LOG_LEVEL","WARN").upper())

  index_list = os.environ.get("INDEX_LIST", "gpu-sensor*,logstash*,metricbeat*").split(",")

  logging.warn("%s starting..." % (os.path.basename(__file__)))
  while True:
    # Probe any available AMD cards
    try:
      for index_to_clean in index_list:
        indices = es.indices.get(index=index_to_clean)
        for index in indices:
          logging.info("Found index: %s" % (index))
    except Exception as inst:
      logging.error("Caught exception: %s, %s" % (type(inst), inst))
    finally:
      pass

    if killer.kill_now:
      break
    time.sleep(float(os.environ.get("SLEEP_TIME", 60)))

  logging.warn("%s exiting gracefully..." % (os.path.basename(__file__)))

