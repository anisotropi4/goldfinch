# goldfinch
A set of scripts for working with postgres and arangodb databases based on extending Jeroen Janssens 'Data Science on the Command Line' https://github.com/jeroenjanssens/data-science-at-the-command-line  

1) **create_table.py** 

Based on column names in a tsv file-format this python3 script create a postgres import script 

   Run the script to create a table create/import script 'table_CORPUS.sql' that imports the file 'CORPUS.tsv':

`$ bin/create_table.py CORPUS.tsv`

   To then import 'CORPUS.tsv' into the table table_corpus (database user 'finch' and postgres server 'raven') run the following:

`$ < table_CORPUS.sql psql -U finch -h raven` 

  * The tablename is lowercase 'table_corpus' 
  * All columns are varchar by default but can be changed in the import script ahead of the import  
  * csv is also supported by editing the create_table.py script

2.1) **aqls.sh** 

A command-line wrapper script for arangodb that allows either readline quoted text or input file. Connection parameters are set in shell environment variables as follows:  
  * username      ARUSR default root  
  * password      ARPWD default lookup as key:pair from $HOME/.aqlpass file  
  * server-name   ARSVR default ar-server  
  * database-name ARDBN default _system  

   Select five elements from the collection 'fullnodes':  
`$ aqlx.sh 'for i in fullnodes limit 5 return i'`  

   The same query run from the script file 'test-script.aql':  
`$ cat test-script.aql  

for i in fullnodes  

limit 5  

return i  

$ < test-script.aql aql.sh`  

   The output is in json pretty-printed using the 'jq' command-line tool https://stedolan.github.io/jq

2.2) **aqlx.sh** 

A command-line wrapper script for arangodb identical to aqls.sh but without 'jq' pretty-print.  

2.3) **ar-env.sh** 

A wrapper script to set the following shell environment parameters used by the aqls.sh and aqlx.sh arangodb wrapper scripts   
  * username      ARUSR default root  
  * password      ARPWD default lookup as key:pair from $HOME/.aqlpass file  
  * server-name   ARSVR default ar-server  
  * database-name ARDBN default _system  

   If the ARPWD password variable is not set, the script uses the 'jq' command-line tool https://stedolan.github.io/jq to lookup from a json format file in the $HOME/.aqlpass  
`$ cat ~/.aqlpass  
{"root": "dontbedaft", "nodeuser": "tryagain"}`  