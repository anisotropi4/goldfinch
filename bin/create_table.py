#!/usr/bin/python3

import csv
import sys
import os
import re

filename = sys.argv[1]

tablename = filename
#tablename = re.sub(r'\.csv$', '', tablename)
tablename = re.sub(r'\.tsv$', '', tablename)
tablename = re.sub(r'[ \.()\/\-]', '_', tablename)
tablename = re.sub(r'^', 'table_', tablename)

instances = {}
attributes = []
unique = True

s1_re = re.compile('[ ()\/\-\\%\]\[]+')
s2_re = re.compile('[\.:\?%]')
s3_re = re.compile('#')
s4_re = re.compile('£')
s5_re = re.compile('^_+')
s6_re = re.compile('_+$')

print(tablename)
with open(filename) as csvfile:
    #reader = csv.reader(csvfile, delimiter=',', quotechar='"')
    reader = csv.reader(csvfile, delimiter='\t', quotechar='"')
    for fields in reader:
        count = 0
        for field in fields:
            field = s1_re.sub('_',field.lower())
            field = s2_re.sub('',field)
            field = s3_re.sub('n',field)
            field = s4_re.sub('GBP',field)
            field = s5_re.sub('',field)
            field = s6_re.sub('',field)
            if field == "":
                field = "empty_"+str(len(attributes))

            if field in instances:
                unique = False
                instances[field] += 1
            else:
                instances[field] = 1
            attributes.append(field)
        break


if unique:
    with open(tablename+'.sql','w+') as sqlfile:
        sqlfile.write('drop table {} cascade;\n'.format(tablename))
        sqlfile.write('create table {} ('.format(tablename))
        sqlfile.write(' varchar, '.join(attributes)+' varchar);\n')
        #sqlfile.write("\\copy {0} from '{1}/{2}' csv header\n".format(tablename,os.getcwd(),filename))
        sqlfile.write("\\copy {0} from '{1}/{2}' delimiter as '	' csv header\n".format(tablename,os.getcwd(),filename))
else:
    print('**duplicate fields')

for field in attributes:
    print('{0},{1}'.format(field,instances[field]))

print('')
