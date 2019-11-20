#!/usr/bin/env python3

import sys
import argparse
from datetime import datetime, timedelta
import json
import pandas as pd
import numpy as np
import itertools as it
from dateutil.parser import parse

DAY = timedelta(days=1)
WEEK = 7 * DAY

def day_int(bitmap):
    return int(bitmap, 2)

SUNDAY = day_int('0000001')
WEEK_BITMAP = day_int('1' * 7)

def days_str(n):
    return '{:b}'.format(n).zfill(7)

def rotr_int(bitmap, n=7):
    """Rotate bitmap left"""
    bitmap = bitmap | ((bitmap & 1) << n)
    return bitmap >> 1

def rotl_int(bitmap, n=7):
    """Rotate bitmap right"""
    m = 2 ** n
    bitmap = (bitmap << 1)
    return (bitmap % m) + (bitmap // m)

def bitmap_rotl(bitmap):
    """Rotate bitmap right"""
    b0 = bitmap << 1
    b1 = b0 & WEEK_BITMAP
    b2 = (b0 ^ WEEK_BITMAP) >> 7
    return [b2, b1]

def same_day(start_object, end_object):
    return start_object.date() == end_object.date()

def same_week(start_object, end_object):
    return same_day(monday_offset(start_object), monday_offset(end_object))

def monday_offset(date_object):
    return date_object - timedelta(days=date_object.weekday())

def day_bitmap(date_object):
    return 2 ** (6 - date_object.weekday())

def week_bitmap(date_object):
    return 2 ** (7 - date_object.weekday()) - 1

def interval_bitmaps(start_date, end_date):
    this_date = monday_offset(start_date)
    if same_day(start_date, end_date):
        return iter([(this_date, day_bitmap(start_date))])

    start_bitmap = week_bitmap(start_date)
    end_bitmap = week_bitmap(end_date) >> 1

    if same_week(start_date, end_date):
        return iter([(this_date, start_bitmap ^ end_bitmap)])

    this_bitmap = [(this_date, start_bitmap)]
    this_date = this_date + WEEK
    
    while this_date < monday_offset(end_date):
        this_bitmap.append((this_date, WEEK_BITMAP))
        this_date = this_date + WEEK
    this_bitmap.append((this_date, WEEK_BITMAP ^ end_bitmap))
    return iter(this_bitmap)

def get_date_dt(date_object):
    return datetime(date_object.year, date_object.month, date_object.day)

def get_time_td(time_object):    
    return timedelta(hours=time_object.hour, minutes=time_object.minute, seconds=time_object.second)

def get_dt(datetime_object):
    return (get_date_dt(datetime_object), get_time_td(datetime_object))

def set_schedule(these_paths, this_date):
    return [{**i.to_dict(), **{'Date': this_date}} for _, i in these_paths.iterrows()]

def repeat_this(start_object, duration_object, repeat):
    this = []

    for i in range(repeat):
        this.append(start_object)
        start_object = start_object + duration_object        
    return this

def repeat_pair(start_object, end_object, duration_object=DAY):
    this = []
    if isinstance(end_object, timedelta):
        end_object = start_object + end_object
    repeat = int((end_object - start_object) / duration_object) + 1
    return repeat_this(start_object, duration_object, repeat)

#INTERVAL='20190515/20190516'
#INTERVAL='20190925T12:00:00/20190925T12:30:00'
#INTERVAL= '20190916T00:00:00/20190916T23:59:00'
#INTERVAL= '20191209T00:00:00/20191209T23:59:59'
#INTERVAL= '20191216T00:00:00/20191216T23:59:59'
#INTERVAL = '20191016/20191018'

fout_name = None

DEBUG = True

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Select trains services \
based on working timetable')
    parser.add_argument('inputfile', type=str, nargs='?', help='name of \
working timetable file to parse', default='timetable-test.ndjson')
    parser.add_argument('interval', type=str, nargs='?', help='train operating \
interval', default='2019-10-21T10:00:00/2019-10-21T12:00:00')
    parser.add_argument('outputfile', type=str, nargs='?', help='name of \
output file', default=None)
    args = parser.parse_args()
    fin_name = args.inputfile
    fout_name = args.outputfile
    INTERVAL = args.interval
    DEBUG = False

if DEBUG:
    pd.set_option('display.max_columns', None)
    #fin_name = 'timetable-20190920.ndjson'
    #fin_name = 'test/A'
    #fin_name = 'test/timetable-02.ndjson'
    fin_name = 'PA-20191117.jsonl'
    #INTERVAL = '2019-10-21T11:00:00/2019-10-21T12:00:00'
    #INTERVAL = '2019-10-16T11:00:00/2019-10-18T12:00:00'
    INTERVAL = '20191112/20191113'

fin = open(fin_name, 'r', encoding='utf-8')
WTT = pd.DataFrame([json.loads(i) for i in fin])
WTT = WTT.fillna(value={'Origin': '00:00:00', 'Terminus': '00:00:00'})

df1 = pd.DataFrame(WTT['Active'].str.split('/').tolist(), columns=['start_date', 'end_date'])
df1['start_date'] = pd.to_datetime(df1['start_date'], format='%Y-%m-%d')
df1['end_date'] = pd.to_datetime(df1['end_date'], format='%Y-%m-%d')
df1['origin_offset'] = pd.to_timedelta(WTT['Origin'])
df1['terminus_offset'] = df1['origin_offset'] + pd.to_timedelta(WTT['Duration'].str.replace('PT', ''))

df1['d0_bitmap'] = WTT['Actual'].apply(day_int)

ds1 = df1['terminus_offset'] > 2 * DAY
if ds1.any():
    fout = sys.stderr
    fout.write('Error: PATH terminus offset greater than two days\n') 
    for (n, j) in WTT[ds1].iterrows():
        fout.write(json.dumps(j.to_dict()) + '\n')
    sys.exit(1)

overlap_idx = df1['terminus_offset'] > DAY
df1['d1_bitmap'] = 0
df1.loc[overlap_idx, 'd1_bitmap'] = df1.loc[overlap_idx, 'd0_bitmap'].apply(rotr_int)

sunday_idx = ((df1['d0_bitmap'] & SUNDAY) == SUNDAY)
idx2 = sunday_idx & overlap_idx
#df1.loc[idx2, 'end_date'] += DAY
df1['end_overlap'] = False
df1.loc[idx2, 'end_overlap'] = True

df1['d0_actual'] = df1['d0_bitmap'].apply(days_str)
df1['d1_actual'] = df1['d1_bitmap'].apply(days_str)

def get_interval(interval):
    return (parse(i) for i in interval.split('/'))

(START_INTERVAL, END_INTERVAL) = get_interval(INTERVAL)
(START_DATE, START_OFFSET) = get_dt(START_INTERVAL)
(END_DATE, END_OFFSET) = get_dt(END_INTERVAL)

# identify operating trains in interval between START_INTERVAL and END_INTERVAL
this_day = (START_DATE - DAY)
this_date = this_day.strftime('%Y-%m-%d')
date_idx = (this_day >= df1['start_date']) & (this_day < df1['end_date'])
this_bitmap = day_bitmap(START_DATE)
bitmap_idx = (df1['d1_bitmap'] & this_bitmap) == this_bitmap
this_idx = (df1['terminus_offset'] - DAY) >= START_OFFSET
SCHEDULE = set_schedule(WTT[date_idx & bitmap_idx & this_idx], this_date)

this_day = START_DATE
this_date = this_day.strftime('%Y-%m-%d')
date_idx = (this_day >= df1['start_date']) & (this_day < df1['end_date'])
this_bitmap = day_bitmap(this_day)
day_idx = (df1['d0_bitmap'] & this_bitmap) == this_bitmap

if START_DATE == END_DATE:
    this_idx = ~((df1['terminus_offset'] < START_OFFSET) | (df1['origin_offset'] > END_OFFSET))
    SCHEDULE += set_schedule(WTT[date_idx & day_idx & this_idx], this_date)
else:
    this_idx = (df1['terminus_offset'] >= START_OFFSET) | (df1['origin_offset'] >= START_OFFSET)
    SCHEDULE += set_schedule(WTT[date_idx & day_idx & this_idx], this_date)
    for this_day in repeat_pair(START_DATE + DAY, END_DATE - DAY):
        this_date = this_day.strftime('%Y-%m-%d')
        date_idx = (this_day >= df1['start_date']) & (this_day < df1['end_date'])
        this_bitmap = day_bitmap(this_day)
        day_idx = (df1['d0_bitmap'] & this_bitmap) == this_bitmap
        SCHEDULE += set_schedule(WTT[date_idx & day_idx], this_date)
    this_day = END_DATE
    this_date = this_day.strftime('%Y-%m-%d')
    this_bitmap = day_bitmap(this_day)
    day_idx = (df1['d0_bitmap'] & this_bitmap) == this_bitmap
    this_idx = (df1['origin_offset'] < END_OFFSET)
    SCHEDULE += set_schedule(WTT[date_idx & day_idx & this_idx], this_date)

fout = sys.stdout
if fout_name:
    fout = open(fout_name, 'w')

for i in SCHEDULE:
    fout.write(json.dumps(i) + '\n')
