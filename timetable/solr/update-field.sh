#!/bin/sh

CORENAME=$1
FIELDNAME=$2
FIELDTYPE=${3:-string}
HOSTNAME=${4:-localhost}

echo Create or update field: ${FIELDNAME} type: ${FIELDTYPE} core: ${CORENAME}
COMMAND="add-field"

STATUS=$(curl -s -X GET http://${HOSTNAME}:8983/api/cores/${CORENAME}/schema/fields | jq '.fields[] | select(.name == '"${FIELDNAME}"') | .name')
if [ "${STATUS}" = "${FIELDNAME}" ]; then
    COMMAND="replace-field"
fi

curl -s -X POST -H 'Content-type:application/json' -d '{'${COMMAND}':{"name":'"${FIELDNAME}"',"type":"'${FIELDTYPE}'","multiValued":false,"stored":true }}' http://${HOSTNAME}:8983/api/cores/${CORENAME}/schema

