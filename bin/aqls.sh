#!/bin/sh

. ${HOME}/bin/ar-env.sh

CMD=`echo $@`
if [ $# = 0 ]; then
   CMD=`cat -`
fi

( ${NODE} | jq '.' ) <<- @EOF 
Database = require('arangojs').Database;
db = new Database({url: 'http://${ARUSR}:${ARPWD}@${ARSVR}:8529', databaseName: '${ARDBN}' });
db.query(\`${CMD}\`)
.then(cursor => { cursor.every(function(data) { console.log(JSON.stringify(data)); return cursor.hasNext();})}, err => console.error(err))
@EOF

