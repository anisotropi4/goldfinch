#!/bin/sh

CONTINENT=europe
REGION=great-britain

wget -nc http://download.geofabrik.de/${CONTINENT}/${REGION}-latest.osm.pbf

if [ ! -d archive ]; then
    mkdir archive
fi

osmupdate great-britain-latest.osm.pbf great-britain-update.osm.pbf -B=great-britain.poly --verbose --keep-tempfiles 

mv great-britain-latest.osm.pbf archive
mv great-britain-update.osm.pbf great-britain-latest.osm.pbf
