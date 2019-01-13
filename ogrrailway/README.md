# A set of query scripts to generate railway .ndjson reports for Great Britain using Open Street Map data and `osmctools`

## Open Street Map (OSM)
Open Street Map data is used under the Open Street Map license https://www.opens
treetmap.org/copyright

Data for the analysis is from http://www.geofabrik.de/ using the download hostin
g service http://download.geofabrik.de/

## Pre-requisites

To extract and process the data is dependant on the following tools:

  * python3 (https://python.org) 
  * wget (https://www.gnu.org/software/wget/)
  * parallel (https://www.gnu.org/software/parallel/)
  * `xml-split4.py`, `add-x-tag.sh` and `xml-to-ndjson.sh`scripts from `bin` directory of (https://github.com/anisotropi4/goldfinch) in the local directory
  * jq (https://stedolan.github.io/jq)
  * xml-to-json (https://hackage.haskell.org/package/xml-to-json)
  * osmctools apt repository (https://gitlab.com/osm-c-tools/osmctools)
  * npm nodejs installation (https://www.npmjs.com/)
  * arangoimp arangodb import tool (https://www.arangodb.com/download-major/ubuntu)
  * d3 (https://d3js.org) and leaflet (http://leafletjs.com)

### For ease of python dependency management python3 miniconda (https://conda.io/miniconda.html) is recomended 

## Obtain, convert and filter OSM data

This an attempt to apply the OSEMN model (Obtain, Scrub, Explore, Model, and iNterpret) on OSM data on the British rail-network

### Get an up-to-date copy of OSM data

The `create-update.sh` script updates the `great-britain-update.osm.pbf` data file or downloads the data if not present

$ ./create-update.sh

The `REGION` parameter in the `create-update.sh` script identifies the OSM region to process

The `create-update.sh` script archives the last `great-britain-lastest.osm.pbf` in the `archive` directory

### Extract and manipulate OSM data

This uses a simple pipeline to extract and manipulate OpenStreetMap data extracted from Overpass API using ArangoDB and then rendered using a d3/leaflet interactive map

1) Using the `run.sh` script

$ ./run.sh

This then:

* Converts the `.osm.pbf` file to a `.o5m` format file
* Extracts elements associated with tags 'rail', 'railway' or 'train' to a `.osm` format
* Extracts nodes, ways and relations into `.xml` files in the output directory
* Converts the node, way and relation `.xml` data into Newline Delimited JSON`.ndjson`and tag values from `{"k": key, "v": value}` format to `key: value` pairs
* Combines the node, way and relation files into a `great-britain-railway.ndjson` file
* Creates an `ogrrailway` arangodb database and uploads the `node`, `way` and `relationship` data
* Exports railway data into the `visualisation` directory to be visualised in an javascript based interactive webpage

The resulting 'raildata.json' file is visualised in an interactive webpage, using an d3 and OpenStreetMap Leaflet javascript framework, by running a simple webserver on a random port, say 8273, in the `visualisation` directory

$ python3 -m http.server 8273

Then browsing to http://localhost:8273

## Notes:

### Data file management

The `run.sh` only creates if a file with the same name does not exist

To delete all files processed by the `run.sh` script run the `clean-up.sh`. As the execute permission bit is not set `clean-up.sh` script 

$ sh ./clean-up.sh

### Set up of an arangodb database

Information and scripts to install and configure an arangodb docker installation on a Debian based Linux system is detailed here https://github.com/guidoeco/docker

### Visualisation References

The key element is the use of the quadtree function in the visiblenodes functionto quickly find nodes and is based on at least:
* The excellent work of Mike Bostock in developing d3 (https://bost.ocks.org/mike/)
* Scott Murray's 'Interactive Data Visualization for the Web' (http://alignedleft.com/work/d3-book)
* The Sumbera implementation 'Many points with d3 and leaflet' here http://bl.ocks.org/sumbera/10463358
* OpenStreetMap data and maptiles (https://www.openstreetmap.org)
* The Leaflet javascript library (http://leafletjs.com)
* parallel (https://doi.org/10.5281/zenodo.1146014)
* The OSEMN approach is set out by the Dataists (http://www.dataists.com/tag/osemn) and is based on the work of Jeroen Janssens in 'Data Science at the Command Line' https://github.com/jeroenjanssens/data-science-at-the-command-line  
