#!/usr/bin/env python

import pysolr
import pandas as pd

solr = pysolr.Solr('http://localhost:8983/solr/PATH', timeout=10)

def clean_query(this_object):
    del this_object['_version_']
    del this_object['id']
    return this_object
    
def get_query(search_str, sort=''):
    v = solr.search(q=search_str, sort=sort, start=0, rows=1024)
    r = [clean_query(i) for i in v]
    for m in range(1024, v.hits, 1024):
        s = solr.search(q=search_str, sort=sort, start=m, rows=1024)
        r += [clean_query(i) for i in s]
    return r

#z = get_query('UUID:0064d474dd5111e9a21ff0def1d95ed1')
#z = get_query('TIPLOC:LLGMMRW')
z = get_query('UUID:08b85600dd4d11e9a21ff0def1d95ed1')
y = pd.DataFrame(z).fillna('').sort_values(by=['Schedule', 'ID', 'Offset'])
3/0
    
print("Saw {} result(s).".format(len(results)))

for result in results:
    print("The name is '{0}'.".format(result['name']))

solr = pysolr.Solr('http://localhost:8983/solr/core0', timeout=10)
results = solr.search(q='*:*', fq='{!geofilt}', pt='53.958333,-1.080278', d=10, sfield='gps')

results = solr.search(q='*:*', fq='{!geofilt cache=False}', pt='53.958333,-1.080278', d=10, sfield='gps', sort='geodist() asc', fl='*,geodist()')

results = solr.search(q='{!func}geodist()', pt='53.958333,-1.080278', sfield='gps', sort='score asc', fl='*,score')

#&pt=53.958333%2C-1.080278&q=*%3A*&sfield=gps
4/0
solr.add([
    {
        "id": "doc_1",
        "title": "A test document",
    },
    {
        "id": "doc_2",
        "title": "The Banana: Tasty or Dangerous?",
        "_doc": [
            { "id": "child_doc_1", "title": "peel" },
            { "id": "child_doc_2", "title": "seed" },
        ]
    },
])
