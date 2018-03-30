#!/bin/bash
FILEPATH=$1
FILENAME=$(basename ${FILEPATH})

XTAG=$2
XTAG=${XTAG:-"_wrapper"}

< ${FILEPATH} mapfile -n 4

if [ ${#MAPFILE[@]} -gt 3 ]; then
    xml-to-json ${FILEPATH} | jq -c ".${XTAG} | to_entries[].value[]"
else
    xml-to-json ${FILEPATH} | jq -c ".${XTAG} | to_entries[].value"
fi

