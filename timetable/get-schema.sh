#!/bin/sh

IDFILE=${1:-id-file.jsonl}

for KEY in $(< ${IDFILE}  jq -r 'keys[0]' | sort -u)
do
    (echo -n {\"${KEY}\": [
    < ${IDFILE} jq -c 'select(.'${KEY}') | .keys[]' | \
        sort -u | \
        while read -r FIELD
        do
            echo -n "${FIELD}",
        done | sed 's/,$//'
    echo ]}) 
done
