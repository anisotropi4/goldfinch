#!/usr/bin/env python3
import pandas as pd
import json
import numpy as np
import sys
import datetime
from datetime import datetime, date, timedelta, time, MINYEAR
from iso8601datetime.interval import interval_p
from iso8601datetime.duration import duration_f, duration_p, time_f, fromisoday_p

df1 = pd.read_json('TIPLOC_Eastings_and_Northings.json')

locations = {}
for index, row in df1.iterrows():
    locations[row['TIPLOC']] = {'station': row['NAME'], 'longitude': row['longitude'], 'latitude': row['latitude']}    


df1 = pd.read_csv('NaPTAN-Rail2.tsv', sep='\t')
naptan = {}

for index, row in df1.iterrows():
    if row['TiplocRef'] != '':
        naptan[row['TiplocRef']] = {'station': row['StationName'], 'longitude': row['Longitude'], 'latitude': row['Latitude']}

def trim_f(this_object):
    if this_object:
        return float('{0:.4f}'.format(this_object))
    return this_object

def coordinates(location_str):
    this_object = {}
    if location_str in locations:
        this_object = locations[location_str]
    if location_str in naptan:
        this_object = naptan[location_str]
    return (any(this_object), trim_f(this_object.get('longitude')),
            trim_f(this_object.get('latitude')))

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



