#!/bin/bash

SOLRPATH=${HOME}/solr

export PATH=${PATH}:${SOLRPATH}/bin

FILENAME=$1
CORENAME=$2

echo Check if Solr running
while ! (solr status -p 8983)
do
    echo Starting Solr
    docker start solr-instance
    sleep 5
done

echo Post ${FILENAME} to ${CORENAME}
post -p 8983 -c ${CORENAME} ${FILENAME}
