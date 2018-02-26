#!/bin/sh
FILEPATH=$1
FILENAME=$(basename ${FILEPATH})

TAG=$2
TAG=${TAG:-$(${FILENAME} | sed 's/.xml$//')}
XTAG=$3
XTAG=${XTAG:-"_wrapper"}

xml-to-json ${FILEPATH} | jq -c ".${XTAG}.${TAG}[]"

