#!/usr/bin/env python3
import pandas as pd
from pandas.io.json import json_normalize
import json
import numpy as np
import sys
import datetime
from datetime import datetime, date, timedelta, time, MINYEAR
from iso8601datetime.interval import interval_p
from iso8601datetime.duration import duration_f, duration_p, time_f, fromisoday_p

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

with open('TIPLOC_Eastings_and_Northings.json', 'rb') as fp:
    geoobject_json = json.load(fp)
    for this_object in geoobject_json['features']:
        properties = this_object['properties']
        (longitude, latitude) = this_object['geometry']['coordinates']
        locations[properties['TIPLOC']] = {'station': properties['NAME'], 'longitude': trim_f(longitude), 'latitude': trim_f(latitude)}

df1 = pd.read_csv('TIPLOC-map.tsv', sep='\t')
tiploc_map = df1.set_index('NaPTAN').to_dict('index')

naptan = {}
with open('NaPTAN-Rail.ndjson', 'rb') as fp:
    for line in fp:
        this_object = json.loads(line)
        (longitude, latitude) = (this_object['lat'], this_object['lon'])
        tiploc = this_object['TIPLOC']
        naptan[tiploc] = {'name': this_object['Name'], 'longitude': trim_f(longitude), 'latitude': trim_f(latitude)}
        if tiploc in tiploc_map:
            naptan[tiploc_map[tiploc]['TIPLOC']] = {'name': this_object['Name'], 'longitude': trim_f(longitude), 'latitude': trim_f(latitude), 'lookup': True}

osmdata = {}
with open('osmnaptan-all.ndjson', 'rb') as fp:
    for line in fp:
        this_object = json.loads(line)
        (longitude, latitude) = (this_object['lat'], this_object['lon'])
        if 'name' not in this_object:
            sys.stderr.write('No name: {}\n'.format(json.dumps(this_object)))
            continue
        osmdata[this_object['TIPLOC']] = {'name': this_object['name'], 'longitude': trim_f(longitude), 'latitude': trim_f(latitude)}

#df1 = pd.read_csv('NaPTAN-Rail2.tsv', sep='\t')
#for index, row in df1.iterrows():
#    if row['TiplocRef'] != '':
#        naptan[row['TiplocRef']] = {'station': row['StationName'], 'longitude': row['Longitude'], 'latitude': row['Latitude']}

def coordinates(location_str):
    this_object = {}
    if location_str in locations:
        this_object = locations[location_str]
    elif location_str in naptan:
        this_object = naptan[location_str]
    elif location_str in osmdata:
        this_object = osmdata[location_str]
    return (any(this_object), this_object.get('longitude'), this_object.get('latitude'))

for line in sys.stdin:
    object_json = json.loads(line)
    UID = object_json['UID']
    headcode = object_json.get('Service').get('BS').get('Headcode')
    schedule = object_json['Schedule']
    (start_interval, end_interval) = interval_p(object_json['Interval'], return_duration=False)
    operation_date = object_json['Day']
    start_service = datetime.combine(fromisoday_p(operation_date).date(), start_interval.time())

    for event_object in schedule:
        TIPLOC = event_object['TIPLOC']
        event = event_object['ID']
        event_type = event_object['Event']
        offset = duration_p(event_object['Offset'])
        (found, lon, lat) = coordinates(TIPLOC)
        if not found:
            sys.stderr.write('{0}\t{1}\t{2}\t{3}\n'.format(TIPLOC, headcode, UID, operation_date))
            continue
        this_datetime = duration_f(start_service + offset, day_format=False)
        output_object = {'Time': this_datetime,
                         'UID': UID,
                         'Date': operation_date,
                         'Event': event_type,
                         'TIPLOC': TIPLOC,
                         'lon': lon,
                         'lat': lat}

        print(json.dumps(output_object))
