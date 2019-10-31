#!/usr/bin/env python3

import sys
import json
import pysolr

solr_path = pysolr.Solr('http://localhost:8983/solr/PATH/', timeout=30, always_commit=True)
solr_bs = pysolr.Solr('http://localhost:8983/solr/BS/', timeout=10, always_commit=True)
solr_bx = pysolr.Solr('http://localhost:8983/solr/BX/', timeout=10, always_commit=True)

"""converts CIF specification json timetable file to new-line delimited json
(ndjson) representation of service and path elements"""

BS = []
BX = []
PATH = []

N = 0
for line in sys.stdin:
#for line in open('schedule/201910260520_full', 'r'):    
    object = json.loads(line)
    if object['ID'] in ['BS']:
        BS.append(object)
        continue
    if object['ID'] in ['BX']:
        BX.append(object)
        continue
    if object['ID'] in ['LO', 'LI', 'LT']:
        PATH.append(object)
    if object['ID'] == 'LT':
        if N > 4096:
            solr_bs.add(BS)
            solr_bx.add(BX)
            solr_path.add(PATH)
            N = 0
            BS = []
            BX = []
            PATH = []
        N += 1
        
