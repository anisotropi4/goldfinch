#!/bin/bash

FILENAME=$1
CORENAME=$2

echo Check if Solr running

echo Check if Solr running

while ! (docker exec --user=solr solr-instance bin/solr status -p 8983)
do
    echo Solr is not running
    docker start solr-instance
    sleep 5
done

curl -X POST 'http://localhost:8983/solr/'${CORENAME}'/update?commit=true' --data-binary @${FILENAME} -H 'Content-type:text/json; charset=utf-8'

