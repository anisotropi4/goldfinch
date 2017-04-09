# goldfinch
A set of scripts for working with postgres and arangodb databases based on extending Jeroen Janssens 'Data Science on the Command Line' https://github.com/jeroenjanssens/data-science-at-the-command-line  

1) create_table.py: Based on column names in a tsv file-format this python3 script create a postgres import script 

For the file called 'CORPUS.tsv' run the script to creates the import script 'table_CORPUS.sql':
`$ bin/create_table.py CORPUS.tsv`

To import the file 'CORPUS.tsv' with user 'finch' on the postgres server 'raven' run into the table table_corpus:

`$ < table_CORPUS.sql psql -U finch -h raven` 

The table created will be lowercase 'table_corpus' 
All columns are varchar by default but can be edited in the import script
Edit the create_table.py script as indentified in the script to supports csv rather than tsv import
