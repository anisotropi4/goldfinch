#!/bin/sh

M=0
HOSTNAME=joseph
CORES=$@
while true
do
    M=$((M+1))
    echo Cycle"	"${M}
    for CORE in ${CORES}
    do
        echo -n ${CORE}"	"
        curl -s http://${HOSTNAME}:8983/solr/${CORE}/select?q=*%3A* | jq -c '.response | .numFound'        
    done
    sleep 10
done

