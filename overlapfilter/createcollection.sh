#!/bin/sh
. ${HOME}/bin/ar-env.sh
COLLECTION=`echo $@`
if [ $# = 0 ]; then
   COLLECTION=`cat -`
fi

${NODE}  <<- @EOF 
const arangojs = require('arangojs');
const db = new arangojs.Database({url: 'http://ar-server:8529'});
db.useBasicAuth("${ARUSR}", "${ARPWD}");
db.useDatabase("${ARDBN}");

db.collection('${COLLECTION}').drop()
    .then(() => console.log('dropped ${COLLECTION}'),
          err => console.error('No ${COLLECTION}'))
    .then(() => {
        console.log('create ${COLLECTION}');
        db.collection('${COLLECTION}').create();
        console.log('created ${COLLECTION}');},
          err => console.error("cannot create ${COLLECTION}"))
@EOF

