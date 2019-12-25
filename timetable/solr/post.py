#!/usr/bin/env python

import pysolr
import json
from os import path
import argparse

parser = argparse.ArgumentParser(description='Extract service and path \
data based on on jsonl format working timetable')

parser.add_argument('--core', dest='key', type=str, default=None,
                    help='Solr core default is filename')

parser.add_argument('inputfile', type=str, nargs='?', help='name of \
working timetable file to parse', default='PA-20191031.jsonl')

args = parser.parse_args()
KEY = args.key
fin_name = args.inputfile

if not KEY:
    KEY = path.basename(fin_name).split('_').pop(0)
    KEY = KEY.split('-').pop(0)

SOLR_CONNECTION = pysolr.Solr('http://localhost:8983/solr/{}/'.format(KEY), timeout=30, always_commit=True)

with open(fin_name, 'r') as fin:
    N = 0
    DATA = []
    for line in fin:
        DATA.append(json.loads(line))
        if len(DATA) > 1048576:        
            SOLR_CONNECTION.add(DATA)
            DATA = []
    SOLR_CONNECTION.add(DATA)
