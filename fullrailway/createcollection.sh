#!/bin/sh
. ${HOME}/bin/ar-env.sh
COLLECTION=`echo $@`
if [ $# = 0 ]; then
   COLLECTION=`cat -`
fi

${NODE}  <<- @EOF 
Database = require('arangojs').Database;
db = new Database({url: 'http://${ARUSR}:${ARPWD}@${ARSVR}:8529', databaseName: '${ARDBN}' });

db.collection('${COLLECTION}').drop()
    .then(() => console.log("dropped ${COLLECTION}"),
          err => console.error("No ${COLLECTION}"))
    .then(() => {
        console.log("create ${COLLECTION}");
        db.collection('${COLLECTION}').create();
        console.log("created ${COLLECTION}");},
          err => console.error("cannot create ${COLLECTION}"));
@EOF

