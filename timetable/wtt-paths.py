#!/usr/bin/env python3

import sys
import json
import pysolr

solr_path = pysolr.Solr('http://localhost:8983/solr/PATH', timeout=10)
solr_bs = pysolr.Solr('http://localhost:8983/solr/BS', timeout=10)
solr_bx = pysolr.Solr('http://localhost:8983/solr/BX', timeout=10)

"""converts CIF specification json timetable file to new-line delimited json
(ndjson) representation of service and path elements"""

parser = argparse.ArgumentParser(description='Extract service and path \
data based on on jsonl format working timetable')
parser.add_argument('outputfile', type=str, nargs='?', help='name of \
working timetable file to parse', default='timetable-test.ndjson')

args = parser.parse_args()
fout_name = args.outputfile
fout1 = open('{}-BS.jsonl'.format(fout_name), 'w')
fout2 = open('{}-BX.jsonl'.format(fout_name), 'w')
fout3 = open('{}-PATH.jsonl'.format(fout_name), 'w')

N = 0
for line in sys.stdin:
    object = json.loads(line)
    if object['ID'] in ['BS']:
        fout1.write(json.dumps(object) + '\n')
        continue
    if object['ID'] in ['BX']:
        fout2.write(json.dumps(object) + '\n')
        continue
    if object['ID'] in ['LO', 'LI', 'LT']:
        fout3.write(json.dumps(object) + '\n')
    
    if N > 1024:
        N = 0
