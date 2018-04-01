#!/bin/sh 
# Set database name and user
ARUSR=railway
ARDBN=fullrailway

export ARUSR ARDBN
. ${HOME}/bin/ar-env.sh

for i in fullfilternodes
do    
    ./createcollection.sh ${i}
done

for i in fullfilternodes.aql
do
    echo ${i}
    < ${i} ${HOME}/bin/aqlx.sh
done

for i in fullfilternodes
do
    ./creategeoindex.sh ${i}
    ./createindex.sh ${i} valid
done

export ARPWD ARSVR
./filter02.py

echo "dump nodes to 'raildata.json' file"
sh ./report.sh > visualisation/raildata.json
