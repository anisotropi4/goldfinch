#!/bin/sh

KEY=$1
SCHEMA=${2:-schema.jsonl}

if [ ! -s ${SCHEMA} ]; then
    echo Error set-schema.sh: empty or missing ${SCHEMA} file
fi

./solr/create-core.sh ${KEY}

< ${SCHEMA} jq -c 'select(.'${KEY}') | .[][]' | \
    while read -r FIELD
    do
        ./solr/update-field.sh ${KEY} "${FIELD}"
    done

