#!/bin/sh
#NOTE only creates a GeoIndex on the ['lat', 'lon'] fields
. ${HOME}/bin/ar-env.sh

COLLECTION=`echo $@`
if [ $# = 0 ]; then
   COLLECTION=`cat -`
fi

${NODE}  <<- @EOF 
arangojs = require('arangojs');
db = new arangojs.Database({url: 'http://${ARSVR}:8529'});
db.useBasicAuth("${ARUSR}", "${ARPWD}");
db.useDatabase("${ARDBN}");

db.collection('${COLLECTION}').createGeoIndex(['lat','lon'])
    .then(index => console.log("create geoindex ${COLLECTION}: ",index.id, index.fields),
	  err => console.error("No GeoIndex ${COLLECITON}"));
@EOF

