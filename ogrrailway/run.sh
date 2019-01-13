#!/bin/sh

REGION=great-britain

for directory in output archive
do
    if [ ! -d ${directory} ]; then
        mkdir ${directory}
    fi
done

if [ ! -f ${REGION}-latest.o5m ]; then
    osmconvert ${REGION}-latest.osm.pbf -o=${REGION}-latest.o5m 
fi

if [ ! -f ${REGION}-railway.osm ]; then
    osmfilter --keep="rail= train= railway=" --drop-version --drop-author ${REGION}-latest.o5m -o=${REGION}-railway.osm
fi

if [ ! -x ./xml-split4.py ]; then
    echo "Install xml-split.py from the 'bin' directory of (https://github.com/anisotropi4/goldfinch) into the local directory"
    exit 1
fi

if [ ! -f output/node.xml ] || [ ! -f output/way.xml ] || [ ! -f output/relation.xml ]
then
   touch output/node.xml output/way.xml output/relation.xml
   ./xml-split4.py ${REGION}-railway.osm --depth 1
fi

if [ ! -x ./xml-to-ndjson.sh ]; then
    echo "Install xml-to-ndjson.sh from the 'bin' directory of (https://github.com/anisotropi4/goldfinch) into the local directory"
    exit 1
fi

for XTAG in node way relation
do    
    if [ ! -f output/${XTAG}.ndjson ];
    then
        echo ${XTAG}
        < output/${XTAG}.xml parallel -j 1 --files --pipe -N1024 ./add-x-tag.sh | parallel -j 4 "./xml-to-ndjson.sh {} | ./tag-filter.sh; rm {}" > output/${XTAG}.ndjson
    fi
done
 
if [ ! -f output/nodeconvert.txt ];
then
   echo "yes" > output/nodeconvert.txt
   < output/node.ndjson jq -c '. + {lat: (.lat | tonumber), lon: (.lon | tonumber)}' > output/node.ndjson.$$
   mv output/node.ndjson archive
   mv output/node.ndjson.$$ output/node.ndjson
fi

if [ ! -f ${REGION}-railway.ndjson ];
then
    for i in node way relation
    do
        < output/${i}.ndjson jq -c '{"type": "'${i}'"} + .' 
    done > ${REGION}-railway.ndjson
fi

if [ ! -d visualisation ];
then
    mkdir visualisation
fi

if [ ! -d visualisation/raildata.json ];
then
    echo "creating ogrrailway arangodb"
    ./create-ogrdb.sh

    echo "dump nodes to 'raildata.json' file"
    ./report.sh
fi

