#!/bin/sh

PATH=${PATH}:$(dirname ${0})

M=0
HOSTNAME=localhost
CORES=$@
while true
do
    M=$((M+1))
    echo Cycle"	"${M}
    for CORE in ${CORES}
    do
        echo -n "${CORE}\t"
        document-count.sh ${CORE} | jq '.[]'
    done
    sleep 10
done

