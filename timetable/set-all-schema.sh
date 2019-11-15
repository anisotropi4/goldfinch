#!/bin/sh

SCHEMA=${1:-schema.jsonl}

if [ ! -s ${SCHEMA} ]; then
    echo Error set-schema.sh: empty or missing ${SCHEMA} file
fi

./solr/create-cores.sh $(< ${SCHEMA} jq -r 'keys[0]' | sort -u)

for KEY in $(< ${SCHEMA} jq -r 'keys[0]' | sort -u)
do
    < ${SCHEMA} jq -c 'select(.'${KEY}') | .[][]' | \
        while read -r FIELD
        do
            ./solr/update-field.sh ${KEY} "${FIELD}"            
        done 
done
