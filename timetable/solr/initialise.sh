#!/bin/bash

FILENAME=timetable-20190922-path.jsonl

FILENAME=$1
CORENAME=$2
SOLRPATH=${HOME}/solr

echo Create Solr core ${CORENAME}
echo

export PATH=${PATH}:${SOLRPATH}/bin

if [ -f ${SOLRPATH}/server/solr/${CORENAME}/conf/managed-schema ]; then
    echo Backup ${CORENAME} managed-schema
    cp ${SOLRPATH}/server/solr/${CORENAME}/conf/managed-schema managed-schema.${CORENAME}.bak
fi

echo Check if Solr running

if ! (solr status -p 8983)
then
    solr start -p 8983
    echo Start Solr
fi

if [ -d ${SOLRPATH}/server/solr/${CORENAME} ]; then
    solr delete -c ${CORENAME}
    echo Deleted ${CORENAME}
fi

solr create_core -c ${CORENAME}
echo Created ${CORENAME}

if [ -f managed-schema.${CORENAME} ]; then
    echo Install ${CORENAME} Schema
    solr stop -p 8983
    cp managed-schema.${CORENAME} ${SOLRPATH}/server/solr/${CORENAME}/conf/managed-schema
    solr start -p 8983
fi

while ! (solr status -p 8983)
do
    echo Starting Solr
    sleep 5
done

post -p 8983 -c ${CORENAME} ${FILENAME}

if [ -f ${SOLRPATH}/server/solr/${CORENAME}/conf/managed-schema ]; then
    echo Backup ${CORENAME} managed-schema
    cp ${SOLRPATH}/server/solr/${CORENAME}/conf/managed-schema managed-schema.${CORENAME}.bak2
fi
