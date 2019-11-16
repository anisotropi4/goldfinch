#!/usr/bin/env python3

import pysolr
import pandas as pd
from pandas.io.json import json_normalize
import json
import numpy as np
import sys
import datetime
from datetime import datetime, date, timedelta, time, MINYEAR

solr_service = pysolr.Solr('http://localhost:8983/solr/BS', timeout=10)
solr_path = pysolr.Solr('http://localhost:8983/solr/PATH', timeout=10)

locations = {}

def trim_f(this_object):
    v = this_object
    if not this_object:
        return v
    if type(this_object) is str:
        v = float(this_object)
    return float('{0:.4f}'.format(v))

## Decode GeoJson object:
# {"type": "FeatureCollection",
#  "name": "TIPLOC",
#  "crs": {
#    "type": "name",
#    "properties": {
#      "name": "urn:ogc:def:crs:OGC:1.3:CRS84"
#    }
#  },
#  "features": [...]}

with open('reference/TIPLOC_Eastings_and_Northings.json', 'rb') as fp:
    geoobject_json = json.load(fp)
    for this_object in geoobject_json['features']:
        properties = this_object['properties']
        (longitude, latitude) = this_object['geometry']['coordinates']
        locations[properties['TIPLOC']] = {'station': properties['NAME'], 'longitude': trim_f(longitude), 'latitude': trim_f(latitude)}

df1 = pd.read_csv('reference/TIPLOC-map.tsv', sep='\t')
tiploc_map = df1.set_index('NaPTAN').to_dict('index')

naptan = {}
with open('reference/NaPTAN-Rail.ndjson', 'rb') as fp:
    for line in fp:
        this_object = json.loads(line)
        (latitude, longitude) = (this_object['lat'], this_object['lon'])
        tiploc = this_object['TIPLOC']
        naptan[tiploc] = {'name': this_object['Name'], 'longitude': trim_f(longitude), 'latitude': trim_f(latitude)}
        if tiploc in tiploc_map:
            naptan[tiploc_map[tiploc]['TIPLOC']] = {'name': this_object['Name'], 'longitude': trim_f(longitude), 'latitude': trim_f(latitude), 'lookup': True}

osmdata = {}
with open('reference/osmnaptan-all.ndjson', 'rb') as fp:
    for line in fp:
        this_object = json.loads(line)
        (latitude, longitude) = (this_object['lat'], this_object['lon'])
        if 'name' not in this_object:
            sys.stderr.write('No name: {}\n'.format(json.dumps(this_object)))
            continue
        osmdata[this_object['TIPLOC']] = {'name': this_object['name'], 'longitude': trim_f(longitude), 'latitude': trim_f(latitude)}

def coordinates(location_str):
    this_object = {}
    if location_str in locations:
        this_object = locations[location_str]
    elif location_str in naptan:
        this_object = naptan[location_str]
    elif location_str in osmdata:
        this_object = osmdata[location_str]
    return (this_object.get('longitude', np.NaN), this_object.get('latitude', np.NaN))

def clean_query(this_object):
    del this_object['_version_']
    del this_object['id']
    return this_object

def get_query(solr, search_str, sort=''):
    v = solr.search(q=search_str, sort=sort, start=0, rows=1024)
    r = [clean_query(i) for i in v]
    for m in range(1024, v.hits, 1024):
        s = solr.search(q=search_str, sort=sort, start=m, rows=1024)
        r += [clean_query(i) for i in s]
    return r
    
def get_path(UUID):
    search_str = 'UUID:{}'.format(UUID)
    return get_query(solr_path, search_str, sort='Offset asc')

def get_service(UUID):
    search_str = 'id:{}'.format(UUID)
    return get_query(solr_service, search_str).pop(0)

DEBUG = True
fin = sys.stdin

if __name__ == '__main__':
    DEBUG = False

if DEBUG:
    fin = open('wtt-20191116-1.jsonl', 'r')
    pd.set_option('display.max_columns', None)
    INTERVAL='20191116/20191117'

DATA = pd.DataFrame([json.loads(line) for line in fin])
MISSING = []
for (i, PATH) in DATA.iterrows():
    UUID = PATH['UUID']
    STP = PATH['STP']
    if STP in ['C']:
        continue
    SERVICE = get_service(UUID)
    SCHEDULE = pd.DataFrame(get_path(UUID)).fillna('')
    
    SCHEDULE = SCHEDULE.rename(columns={'T': 'Event', 'Schedule': 'Time'})
    for k in ['UID', 'Date']:
        SCHEDULE[k] = PATH[k]

    if 'TIPLOC' not in SCHEDULE:
        sys.stderr.write('{}\n'.format(json.dumps(PATH.to_dict())))
        continue

    for k in ['Headcode', 'ATOC']:
        SCHEDULE[k] = SERVICE[k] if k in SERVICE else ''

    HEADCODE = SCHEDULE['Headcode']
    idx_loc = SCHEDULE['TIPLOC'] if 'TIPLOC' in SCHEDULE else 'missing'
    LOCATION = pd.DataFrame(data=np.array(idx_loc.map(coordinates).tolist()), index=idx_loc, columns=['lat', 'lon']).drop_duplicates()

    SCHEDULE = SCHEDULE.reset_index().set_index('TIPLOC').join(LOCATION).reset_index().set_index('index').sort_index()

    for i in SCHEDULE[['Time', 'UID', 'Headcode', 'ATOC', 'Date', 'Event', 'TIPLOC', 'lat', 'lon']].to_dict(orient='records'):
        print(json.dumps(i))
        if np.isnan(i['lat']):
            sys.stderr.write('\t'.join([i['TIPLOC'], i['Headcode'], i['UID'], UUID]))
            sys.stderr.write('\n')

