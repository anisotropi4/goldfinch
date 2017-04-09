# goldfinch
A set of scripts for working with postgres and arangodb databases based on extending Jeroen Janssens 'Data Science on the Command Line' https://github.com/jeroenjanssens/data-science-at-the-command-line  

1) create_table.py: Based on column names in a tsv file-format this python3 script create a postgres import script for the file called table_<filename-in-lower-cast>. 

To import the file 'CORPUS.tsv' with user 'finch' on the postgres server 'raven' run:

`$ < table_CORPUS.sql psql -U finch -h raven` 

The table created will be called table_corpus. 
All columns are varchar by default but can be modified ahead of import.
Edit the import script as indentified in the script to supports csv rather than tsv import. 
