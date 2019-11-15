#!/bin/sh

CORENAMES=$@
CORENAMES=${CORENAMES:-PATH}

echo Check if Solr running

while ! (docker exec --user=solr solr-instance bin/solr status -p 8983)
do
    echo Solr is not running
    docker start solr-instance
    sleep 5
done

echo Solr is running
for CORENAME in ${CORENAMES}
do
    echo Create Solr core ${CORENAME}
    echo

    STATUS=$(curl -s -X POST 'http://localhost:8983/solr/admin/cores?STATUS&core='${CORENAME} | jq -r '.status.'${CORENAME}'.name')
    if [ "${STATUS}" = "${CORENAME}" ]; then
        docker exec --user=solr solr-instance bin/solr delete -c ${CORENAME}
    fi
    docker exec --user=solr solr-instance bin/solr create_core -c ${CORENAME}
    docker exec --user=solr solr-instance bin/solr config -c ${CORENAME} -p 8983 -action set-user-property -property update.autoCreateFields -value false
    echo Created ${CORENAME}
done
