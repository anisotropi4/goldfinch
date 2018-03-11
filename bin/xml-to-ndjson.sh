#!/bin/bash
FILEPATH=$1
FILENAME=$(basename ${FILEPATH})

TAG=$2
TAG=${TAG:-$(${FILENAME} | sed 's/.xml$//')}
XTAG=$3
XTAG=${XTAG:-"_wrapper"}

< ${FILEPATH} mapfile -n 4

if [ ${#MAPFILE[@]} -gt 3 ]; then
    xml-to-json ${FILEPATH} | jq -c ".${XTAG}.${TAG}[]"
else
    xml-to-json ${FILEPATH} | jq -c ".${XTAG}.${TAG}"
fi

