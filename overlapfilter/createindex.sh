#!/bin/sh
. ${HOME}/bin/ar-env.sh

if [ $# -lt 2 ]; then
    echo "createindex.sh: <collection name> <field(s)>"
    exit 1
fi

COLLECTION=$1
shift
FIELDS=\'$1\'
shift

while [ $# -gt 0 ]; do
    FIELDS=${FIELDS}","\'$1\'
    shift
done

echo "create skiplist index ${COLLECTION} [${FIELDS}]"

${NODE}  <<- @EOF 
const arangojs = require('arangojs');
const db = new arangojs.Database({url: 'http://${ARSVR}:8529'});
db.useBasicAuth("${ARUSR}", "${ARPWD}");
db.useDatabase("${ARDBN}");

var collection = db.collection("${COLLECTION}");
collection.createSkipList([${FIELDS}])
    .then(index => console.log("create index ${COLLECTION}: ", index.id, index.fields),
	  err => console.error("No Index ${COLLECTION} ${FIELDS}"));
@EOF
