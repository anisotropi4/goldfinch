#!/bin/sh
FILENAME=$1
FILENAME=$(echo ${FILENAME} | sed 's/.xml$//')
TAG=$2
TAG=${TAG:-${FILENAME}}
XTAG=$3
XTAG=${XTAG:-"_wrapper"}

xml-to-json ${FILENAME}.xml | jq -c ".${XTAG}.${TAG}[]"

