#!/bin/sh

FILENAME=$1
TAG=$2
XTAG=$3
XTAG=${XTAG:-"_wrapper"}

xml-to-json ${FILENAME} | jq -c ".${XTAG}.${TAG}[]"

