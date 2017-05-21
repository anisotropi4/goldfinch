#!/bin/sh

. ${HOME}/bin/ar-env.sh

CMD=`echo $@`
if [ $# = 0 ]; then
   CMD=`cat -`
fi

( ${NODE} | jq -s '.' ) <<- @EOF 
Database = require('arangojs').Database;
db = new Database({url: 'http://${ARUSR}:${ARPWD}@${ARSVR}:8529', databaseName: '${ARDBN}' });
db.query(\`${CMD}\`).then(cursor => { 
  cursor.map(function(data) { 
    console.log(JSON.stringify(data));
  })
}, err => console.error(err))
@EOF

