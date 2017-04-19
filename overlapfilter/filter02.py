#!/usr/bin/python
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

n = 2

for k in range(22):
    results = db.AQLQuery(query, rawResults=True, bindVars={'n': n})

    #print(results)
    sequence = []
    node = {}

    for i in results:
        sequence.append(i["node"])
        node[i["node"]] = {"nodes": i["nodes"], "valid": i["valid"] }

        #print(i["node"],i["nodes"],i["valid"])

    for i in sequence:
        if (node[i]["valid"] > n):
            nodes = node[i]["nodes"]
            for j in nodes:
                if j in node:
                    node[j]["valid"] = n / 2
                    
    count = 0
    for i in sequence:
        if node[i]["valid"] < n:
            count=count+1
    print(n / 2, count)    
            
    collection = db.collections["fullfilternodes"]
    for i in sequence:
        if node[i]["valid"] < n:
            document = collection[i]
            document["valid"] = node[i]["valid"]
            document.patch()
            
    if(count <= 1):
        sys.exit()

    n = n * 2
