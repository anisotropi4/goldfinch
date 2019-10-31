#!/bin/bash

CORENAMES=$@
CORENAMES=${CORENAMES:-PATH}
SOLRPATH=${HOME}/solr

export PATH=${PATH}:${SOLRPATH}/bin

echo Check if Solr running

if ! (solr status -p 8983)
then
    solr start -p 8983
fi

echo Started Solr

for CORENAME in ${CORENAMES}
do
    echo Create Solr core ${CORENAME}
    echo


    if [ -f ${SOLRPATH}/server/solr/${CORENAME}/conf/managed-schema ]; then
        echo Backup ${CORENAME} managed-schema
        cp ${SOLRPATH}/server/solr/${CORENAME}/conf/managed-schema managed-schema.${CORENAME}.bak
    fi


    if [ -d ${SOLRPATH}/server/solr/${CORENAME} ]; then
        solr delete -c ${CORENAME}
        echo Deleted ${CORENAME}
    fi

    solr create_core -c ${CORENAME}
    echo Created ${CORENAME}

    if [ -f managed-schema.${CORENAME} ]; then
        echo Install ${CORENAME} Schema
        cp managed-schema.${CORENAME} ${SOLRPATH}/server/solr/${CORENAME}/conf/managed-schema
    fi
done

echo Restart Solr
echo Stop Solr
solr stop -p 8983

echo Start Solr
solr start -p 8983

while ! (solr status -p 8983)
do
    echo Starting Solr
    sleep 5
done

echo Started Solr
