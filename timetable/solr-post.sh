#!/bin/bash

CORENAME=PATH
SOLRPATH=${HOME}/solr

export PATH=${PATH}:${SOLRPATH}/bin

FILENAME=$1

echo Check if Solr running

if ! (solr status -p 8983)
then
    solr start -p 8983
    echo Started Solr
fi


if [ ! -f  ${SOLRPATH}/server/solr/${CORENAME}/conf/managed-schema ]; then
    echo No ${CORENAME} core instance
    exit 1
fi

while ! (solr status -p 8983)
do
    echo Starting Solr
    sleep 5
done

post -p 8983 -c ${CORENAME} ${FILENAME}
