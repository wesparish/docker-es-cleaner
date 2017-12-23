#!/bin/bash

HOSTNAME=$(curl -s rancher-metadata/latest/self/host/name | cut -d'.' -f1)
HOSTNAME=${HOSTNAME:-localhost}

CONTAINER_NAME=$(curl -s rancher-metadata/latest/self/container/name)
CONTAINER_NAME=${CONTAINER_NAME:-$HOSTNAME}

export HOSTNAME
export CONTAINER_NAME
export DOCKER_FQDN="$CONTAINER_NAME.$HOSTNAME"

env

exec "$@"
