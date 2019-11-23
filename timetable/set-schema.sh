#!/bin/sh

KEY=$1
SCHEMA=${2:-schema.jsonl}

if [ ! -s ${SCHEMA} ]; then
    echo Error set-schema.sh: empty or missing ${SCHEMA} file
fi

./solr/create-core.sh ${KEY}

< ${SCHEMA} jq -c 'select(.'${KEY}') | .[][]' | \
    while read -r JSON
    do
        FIELD=$(echo "${JSON}" | jq 'keys[]')
        TYPE=$(echo "${JSON}" | jq '. | to_entries[] | .value')
        echo ${KEY} "${FIELD}" "${TYPE}" 
        ./solr/update-field.sh ${KEY} "${FIELD}" "${TYPE}"
    done
