#!/bin/sh 
# Set database name and user
ARUSR=test
ARDBN=testrailway

export ARUSR ARDBN
. ${HOME}/bin/ar-env.sh

sh ./createdb.sh

jq -c '.elements' ./railway.json | arangoimp --file - --type json --batch-size 134217728 --progress true --server.username ${ARUSR} --server.authentication true --server.database ${ARDBN} --server.endpoint "tcp://"${ARSVR}":8529" --server.password "${ARPWD}" --collection fullosm2 --create-collection true --overwrite true

for i in fullnodes fullways fullrelations 
do    
    ./createcollection.sh ${i}
done

for i in fullnodes.aql fullways.aql fullrelations.aql 
do
    echo ${i}
    < ${i} ${HOME}/bin/aqlx.sh
done

./creategeoindex.sh fullnodes

echo "dump nodes to 'raildata.json' file"
sh ./report.sh > visualisation/raildata.json
