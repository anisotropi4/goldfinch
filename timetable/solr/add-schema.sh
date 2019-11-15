#!/bin/sh

CORENAME=$1
FIELDNAMES=$2
FIELDTYPE=${3:-string}
HOSTNAME=${4:-localhost}

echo Create or update fields: ${FIELDNAMES} type: ${FIELDTYPE} core: ${CORENAME}
COMMAND="add-field"

curl -s -X POST -H 'Content-type:application/json' -d '{'${COMMAND}':{"name":'"${FIELDNAME}"',"type":"'${FIELDTYPE}'","multiValued":false,"stored":true }}' http://${HOSTNAME}:8983/api/cores/${CORENAME}/schema
