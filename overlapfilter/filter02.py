#!/usr/bin/python3
import sys
from pyArango.connection import *
import os
import requests

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
let n = length(nodes) \
filter n > 0 \
sort n desc \
return {node: i._key, nodes: nodes, valid: i.valid}'

update = 'for i in @a update i.k with { "valid": i.v } in fullfilternodes'

n = 2

print("n	count")

for k in range(22):
    results = db.AQLQuery(query, rawResults=True, bindVars={'n': n})

    node = {}

    for i in results:
        node[i["node"]] = {"nodes": i["nodes"], "valid": i["valid"] }

    documents = {}
    for i in node.keys():
        if (node[i]["valid"] > n):
            for j in node[i]["nodes"]:
                if j in node:
                    documents[j] = n // 2

    count = len(documents)
    print(n // 2, '	', count)
    if(count <= 1):
        sys.exit()

    r = db.AQLQuery(update, bindVars={'a': [{'k': k, 'v': v} for k, v in documents.items()]})

    n = n * 2
