#!/usr/bin/python3
import sys
from pyArango.connection import *
import os
import requests
from operator import itemgetter
from datetime import datetime

ARUSR = os.environ['ARUSR']
ARPWD = os.environ['ARPWD']
ARSVR = os.environ['ARSVR']
ARDBN = os.environ['ARDBN']

connection = Connection(arangoURL='http://'+ARSVR+':8529', username=ARUSR, password=ARPWD)

db = connection[ARDBN] #all databases are loaded automatically into the connection and are accessible in this fashion

query = 'for i in fullfilternodes \
filter i.valid > @n \
let nodes = (for j in within(fullfilternodes, i.lat, i.lon, @n) \
filter i._key != j._key \
filter j.valid > @n \
return j._key) \
return {node: i._key, nodes: nodes, valid: i.valid}'

update = 'for i in @a update i.k with { "valid": i.v } in fullfilternodes'

print('\t'.join(['n','count', 'elapsed']))
n = 2
for k in range(22):
    s0 = datetime.now()
    results = db.AQLQuery(query, rawResults=True, bindVars={'n': n})

    node = {}
    sequence = []

    for i in results:
        m = len(i['nodes'])
        if m > 0:
            node[i["node"]] = {"nodes": i["nodes"], "valid": i["valid"] }
            sequence.append((i['node'], m))

    documents = {}
    for (i, _) in sorted(sequence, key=itemgetter(1), reverse=True):
        if (node[i]["valid"] > n):
            for j in node[i]["nodes"]:
                if j in node:
                    documents[j] = n // 2

    r = db.AQLQuery(update, bindVars={'a': [{'k': k, 'v': v} for k, v in documents.items()]})

    count = len(documents)
    s1 = datetime.now()

    print('\t'.join([str(i) for i in [n // 2, count, (s1 - s0).total_seconds()]]))

    if(count <= 1): break

    n = n * 2
