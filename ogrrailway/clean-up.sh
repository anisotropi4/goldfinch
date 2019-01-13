#!/bin/sh

REGION=great-britain

if [ -f ${REGION}-latest.o5m ]; then
    rm ${REGION}-latest.o5m 
fi

if [ -f ${REGION}-railway.osm ]; then
    rm ${REGION}-railway.osm
fi

if [ -f ${REGION}-railway.ndjson ]; then
    rm ${REGION}-railway.ndjson    
fi

for element in points multipolygons
do
    if [ -f geojson-rail-${element}.json ]; then
        rm geojson-rail-${element}.json 
    fi
done

if [ -f osmrail-all.ndjson ]; then
    rm osmrail-all.ndjson
fi

rm -f output/*.xml output/*.ndjson output/nodeconvert.txt

if [ -f visualisation/raildata.json ]; then
    rm visualisation/raildata.json
fi
