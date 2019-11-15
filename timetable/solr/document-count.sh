#!/bin/sh

HOSTNAME=localhost
CORES=$@

STATUS=$(curl -s http://${HOSTNAME}:8983/solr/admin/cores | jq '.status | keys[]')

if [ x"${STATUS}" = x ];  then
    for CORE in ${CORES}
    do
        echo "{\"${CORE}\": \"missing\"}"
    done
    exit 0
fi

for CORE in ${CORES}
do
    COUNT=$(curl -s "http://${HOSTNAME}:8983/solr/${CORE}/select?q=*%3A*" | jq -c '.response | .numFound' 2> /dev/null) || (echo "{\"${CORE}\": \"missing\"}")
    echo "{\"${CORE}\":"             
    echo ${COUNT}
   echo "}"
done | jq -c '.' 2> /dev/null
