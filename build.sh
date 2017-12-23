#!/bin/bash

docker build -t wesparish/es-cleaner . && \
  docker push wesparish/es-cleaner
