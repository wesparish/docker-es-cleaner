FROM ubuntu:16.04

RUN apt-get update && \
    apt-get install python python-pip vim curl -y && \
    pip install elasticsearch5 && \
    pip install python-dateutil && \
    apt-get remove python-pip -y && \
    apt-get autoremove -y && \
    apt-get clean

ENV ES_HOSTS="elasticsearch.weshouse:9200" \
    LOG_LEVEL="WARN" \
    SLEEP_TIME=3600 \
    INDEX_LIST="logstash*,gpu-sensor*,metricbeat*,heartbeat*" \
    RETENTION_DAYS=3


COPY es-cleaner.py /es-cleaner.py
RUN chown root:root /es-cleaner.py

COPY docker-entrypoint.sh /docker-entrypoint.sh
ENTRYPOINT ["/docker-entrypoint.sh"]

CMD ["/es-cleaner.py"]
