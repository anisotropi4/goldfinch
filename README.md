# goldfinch
A set of scripts for working with postgres and arangodb databases based on extending Jeroen Janssens 'Data Science on the Command Line' https://github.com/jeroenjanssens/data-science-at-the-command-line  

1) create_table.py: Based on column names in a tsv file-format this python3 script create a postgres import script 

   For the file called 'CORPUS.tsv' run the script to create the table create/import script 'table_CORPUS.sql':

`$ bin/create_table.py CORPUS.tsv`

   To import the file 'CORPUS.tsv'into the table table_corpus (database user 'finch' and postgres server 'raven') run:

`$ < table_CORPUS.sql psql -U finch -h raven` 

  * The tablename is lowercase 'table_corpus' 
  * All columns are varchar by default but can be changed in the import script ahead of the import
  * csv is also supported by editing the create_table.py script
