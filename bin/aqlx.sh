#!/bin/sh
. ${HOME}/bin/ar-env.sh

CMD=`echo $@`
if [ $# = 0 ]; then
   CMD=`cat -`
fi

${NODE} <<- @EOF 
const arangojs = require('arangojs');
const db = new arangojs.Database({url: 'http://${ARSVR}:8529'});
db.useBasicAuth("${ARUSR}", "${ARPWD}");
db.useDatabase("${ARDBN}");
db.query(\`${CMD}\`).then(cursor => { 
  cursor.map(function(data) { 
    console.log(JSON.stringify(data));
  })
}, err => console.error(err))
@EOF

