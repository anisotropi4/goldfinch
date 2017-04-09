#!/bin/sh

. ${HOME}/bin/ar-env.sh

CMD=`echo $@`
if [ $# = 0 ]; then
   CMD=`cat -`
fi

node <<- @EOF 
Database = require('arangojs').Database;
db = new Database({url: 'http://${ARUSR}:${ARPWD}@${ARSVR}:8529', databaseName: '${ARDBN}' });
db.query(\`${CMD}\`)
.then(cursor => cursor.all(), err => console.error(err))
.then((data) => console.log(JSON.stringify(data)))
@EOF

