#!/usr/bin/env python3

import sys
import argparse
from datetime import datetime, timedelta
import json
import pandas as pd
import numpy as np
import itertools as it
from iso8601datetime.duration import duration_p, duration_f, fromisoday_p
from iso8601datetime.interval import interval_f, interval_p, repeat_pair, ISO8601_DATE

pd.set_option('display.max_columns', None)

DAY = timedelta(days=1)
WEEK = 7 * DAY

def day_int(bitmap):
    return int(bitmap, 2)

SUNDAY = day_int('0000001')
MONDAY = day_int('1000000')
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

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Select trains services \
based on working timetable')

    parser.add_argument('interval', type=str, nargs='?', help='train operating \
interval', default='2018-06-21T08:00:00/2018-06-21T12:00:00')

    args = parser.parse_args()

    #file_name = args.inputfile
    INTERVAL = args.interval

try:
    if fin: pass
except NameError:
    fin = open('timetable-20190920.ndjson', 'r', encoding='utf-8')
    WTT = pd.DataFrame([json.loads(i) for i in fin])
    WTT = WTT.fillna(value={'Origin': '00:00:00', 'Terminus': '00:00:00'})

df1 = pd.DataFrame(WTT['Active'].str.split('/').tolist(), columns=['start_date', 'end_date'])
df1['start_date'] = pd.to_datetime(df1['start_date'], format='%Y-%m-%d')
df1['end_date'] = pd.to_datetime(df1['end_date'], format='%Y-%m-%d')
df1['origin_offset'] = pd.to_timedelta(WTT['Origin'])
df1['terminus_offset'] = pd.to_timedelta(WTT['Terminus'])

df1['d0_bitmap'] = WTT['Actual'].apply(day_int)
ds1 = df1['origin_offset'] + pd.to_timedelta(WTT['Duration'].str.replace('PT', ''))

if (ds1 > 2 * DAY).any():
    print(WTT[ds1 > 2 * DAY])
    999/0

overlap_idx = ds1 > DAY
df1['d1_bitmap'] = 0
df1.loc[overlap_idx, 'd1_bitmap'] = df1.loc[overlap_idx, 'd0_bitmap'].apply(rotr_int)

df1['d0_actual'] = df1['d0_bitmap'].apply(days_str)
##df1['d1_actual'] = df1['d1_bitmap'].apply(days_str)

##sunday_idx = ((df1['d0_bitmap'] & SUNDAY) == SUNDAY)
##idx2 = sunday_idx & overlap_idx
##df1.loc[idx2, 'end_date'] += DAY
#df1['end_overlap'] = False
#df1.loc[idx2, 'end_overlap'] = True

START_DATE = np.min(df1['start_date'])
END_DATE = np.max(df1['end_date'])

fout = open('boco.jsonl', 'w')

#this_day = START_DATE - DAY
#date_idx = (this_day >= df1['start_date']) & (this_day < df1['end_date'])

#prior_bitmap = day_bitmap(this_day)
#prior_idx = (df1['d1_bitmap'] & prior_bitmap) == prior_bitmap
#this_date = (this_day - DAY).strftime('%Y-%m-%d')
#SCHEDULE = set_schedule(WTT[date_idx & prior_idx], this_date)

for this_day in repeat_pair(START_DATE, END_DATE + DAY):
    SCHEDULE = []
    date_idx = (this_day >= df1['start_date']) & (this_day < df1['end_date'])
    this_bitmap = day_bitmap(this_day)
    day_idx = (df1['d0_bitmap'] & this_bitmap) == this_bitmap
    this_date = this_day.strftime('%Y-%m-%d')
    SCHEDULE += set_schedule(WTT[date_idx & day_idx], this_date)
    for i in SCHEDULE:
        fout.write(json.dumps(i) + '\n')
