# goldfinch
A set of scripts for working with postgres and arangodb databases based on extending Jeroen Janssens 'Data Science on the Command Line' https://github.com/jeroenjanssens/data-science-at-the-command-line

## osmrailway

A set of query shell-scripts that extract railway data from an OpenStreetMap Overpass API server. An example docker build for OpenStreetMap Overpass API server under a Debian based Linux distribution can be found here. https://github.com/guidoeco/osm-overpass

More information about OpenStreetMap and Overpass API can be found here:
  * OpenStreetMap: http://www.openstreetmap.org
  * Overpass API: http://overpass-api.de

## testrailway

The scripts in **testrailway** will create a **testrailway** Arangodb database instance, import the railway data extracted from an OpenStreetMap Overpass API server in **osmrailway** and create a json report containing OSM node information which can then be viewed in the 'visualisation' sub-directory using a d3/leaflet mashup http://bl.ocks.org/anisotropi4/3452a4d2d7e848511feafe8a6c1bfaee

The **testrailway** dataset was used on a smaller North Yorkshire dataset based to prove the concept before moving to the British Isles due to issues with scaling the visualisation code.

The ArangoDB used is based on the ArangoDB server docker build scripts here https://github.com/guidoeco/docker in the arangodb directory.

The render uses a mash up of d3 (https://d3js.org) and leaflet (http://leafletjs.com).

## 'bin' directory scripts  

The 'bin' directory 'aql' scripts are used extensively in the 'goldfinch' and other projects and should be installed in the user-account `${HOME}/bin` directory:

### **create_table.py**

Based on column names in a tsv file-format this python3 script create a postgres import script. Run the script to create a table create/import script 'table_CORPUS.sql' that imports the file 'CORPUS.tsv':  
`$ bin/create_table.py CORPUS.tsv`

 To then import 'CORPUS.tsv' into the table table_corpus (database user 'finch' and postgres server 'raven') run the following:  
`$ < table_CORPUS.sql psql -U finch -h raven` 
 * The tablename is lowercase 'table_corpus'
 * All columns are varchar by default but can be changed in the import script ahead of the import  
 * csv is also supported by editing the create_table.py script

### **aqls.sh**  
A command-line wrapper script for arangodb that allows either readline quoted text or input file. Connection parameters are set in shell environment variables as follows:
* username      ARUSR default root
* password      ARPWD default lookup as key:pair from $HOME/.aqlpass file
* server-name   ARSVR default ar-server
* database-name ARDBN default _system

 For example, select five elements from the collection 'fullnodes':  
`$ aqlx.sh 'for i in fullnodes limit 5 return i'`  

 The same query using the script file 'test-script.aql':  
`$ cat test-script.aql`  
`for i in fullnodes`  
`limit 5`  
`return i`  
`$ < test-script.aql aql.sh`

The output is in json pretty-printed using the 'jq' command-line tool https://stedolan.github.io/jq

### **aqlx.sh**  
A command-line wrapper script for arangodb identical to 'aqls.sh' but without 'jq' pretty-print.  

### **ar-env.sh**  
A wrapper script to set the following shell environment parameters used by the aqls.sh and aqlx.sh arangodb wrapper scripts
* username      ARUSR default root  
* password      ARPWD default lookup as key:pair from $HOME/.aqlpass file  
* server-name   ARSVR default ar-server  
* database-name ARDBN default _system  

If the ARPWD password variable is not set, the script uses the 'jq' command-line tool https://stedolan.github.io/jq to lookup from a json format file in the $HOME/.aqlpass  
`$ cat ~/.aqlpass`  
`{"root": "dontbedaft", "nodeuser": "tryharder"}`  

Notes: The key element is the use of the quadtree function in the visiblenodes function to quickly find nodes and is based on at least:  
 * The excellent work of Mike Bostock in developing d3 (https://bost.ocks.org/mike/)  
 * Scott Murray's 'Interactive Data Visualization for the Web' (http://alignedleft.com/work/d3-book)  
 * The Sumbera implementation 'Many points with d3 and leaflet' here http://bl.ocks.org/sumbera/10463358  
 * OpenStreetMap data and maptiles (https://www.openstreetmap.org)  
 * Leaflet javascript library (http://leafletjs.com)  
