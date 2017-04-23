#!/bin/sh 
# Set database name and user
ARUSR=railway
ARDBN=fullrailway

export ARUSR ARDBN
. ${HOME}/bin/ar-env.sh

for i in fulledges
do    
    ./createedgecollection.sh ${i}
done

for i in fulledges.aql
do
    echo ${i}
    < ${i} ${HOME}/bin/aqlx.sh
done

sh ./reinstall.sh
