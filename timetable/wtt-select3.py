#!/usr/bin/env python3

import sys
import argparse
from datetime import datetime, timedelta
import json
import pandas as pd
import numpy as np
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
        return [(this_date, day_bitmap(start_date))]

    start_bitmap = week_bitmap(start_date)
    end_bitmap = week_bitmap(end_date) >> 1

    if same_week(start_date, end_date):
        return [(this_date, start_bitmap ^ end_bitmap)]

    this_bitmap = [(this_date, start_bitmap)]
    this_date = this_date + WEEK
    
    while this_date < monday_offset(end_date):
        this_bitmap.append((this_date, WEEK_BITMAP))
        this_date = this_date + WEEK
    this_bitmap.append((this_date, WEEK_BITMAP ^ end_bitmap))
    return this_bitmap

def get_date_dt(date_object):
    return datetime(date_object.year, date_object.month, date_object.day)

def get_time_td(time_object):    
    return timedelta(hours=time_object.hour, minutes=time_object.minute, seconds=time_object.second)

def get_dt(datetime_object):
    return (get_date_dt(datetime_object), get_time_td(datetime_object))


def set_schedule(these_paths, this_date):
    return [{**i.to_dict(), **{'Date': this_date}} for _, i in these_paths.iterrows()]


INTERVAL='20190515/20190516'
#INTERVAL='20190925T12:00:00/20190925T12:30:00'
#INTERVAL= '20190916T00:00:00/20190916T23:59:00'
#INTERVAL= '20191209T00:00:00/20191209T23:59:59'
#INTERVAL= '20191216T00:00:00/20191216T23:59:59'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Select trains services \
based on working timetable')

    #parser.add_argument('inputfile', type=str, nargs='?', help='name of \
#working timetable file to parse')

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

sunday_idx = ((df1['d0_bitmap'] & SUNDAY) == SUNDAY)
idx2 = sunday_idx & overlap_idx
df1.loc[idx2, 'end_date'] += DAY
df1['end_overlap'] = False
df1.loc[idx2, 'end_overlap'] = True

df1['d0_actual'] = df1['d0_bitmap'].apply(days_str)
df1['d1_actual'] = df1['d1_bitmap'].apply(days_str)

# Test case:
# W1 train service S1 runs 20h from 18:00 on Sunday (d0 bitmap 1 d1 bitmap 64)
# W2 train service S2 runs 10h from 10:00 on Monday (d0 bitmap 64 d1 bitmap 0)
# W2 train service S3 runs 20h from 18:00 on Sunday (d0 bitmap 1 d1 bitmap 64)
# W1 Sunday/Monday one service S1
# W2 Monday/Tuesday two services S1 S2
# W2 Tuesday/Saturday no service
# W2 Sunday one service S3

INTERVAL='20191015/20191016'

(START_INTERVAL, END_INTERVAL) = interval_p(INTERVAL, return_duration=False)
(START_DATE, START_OFFSET) = get_dt(START_INTERVAL)
(END_DATE, END_OFFSET) = get_dt(END_INTERVAL)

if END_OFFSET == timedelta(0):
    END_DATE = END_DATE - DAY
    END_OFFSET = DAY
    
# identify operating trains in interval between START_INTERVAL END_INTERVAL
date_idx = (START_DATE >= df1['start_date']) & (END_DATE < df1['end_date'])
these_bitmaps = interval_bitmaps(START_DATE, END_DATE)

SCHEDULE = []
for (this_week, this_bitmap) in these_bitmaps:
    #print(datetime.strftime(this_date, '%Y-%m-%d %a'), days_str(this_bitmap))
    prior_idx = (df1['d1_bitmap'] & this_bitmap) == this_bitmap
    day_idx = (df1['d0_bitmap'] & this_bitmap) == this_bitmap

    if START_DATE == END_DATE:
        this_date = (START_DATE - DAY).strftime('%Y-%m-%d')
        this_idx = (df1['terminus_offset'] >= START_OFFSET)
        SCHEDULE += set_schedule(WTT[date_idx & prior_idx & this_idx], this_date)
        this_date = START_DATE.strftime('%Y-%m-%d')
        this_idx = ~((df1['terminus_offset'] < START_OFFSET) | (df1['origin_offset'] >= END_OFFSET))
        SCHEDULE += set_schedule(WTT[date_idx & day_idx & this_idx], this_date)
    else:
        print('next')
        123/0

with open('boco.jsonl', 'w') as fout:
    for i in SCHEDULE:
        fout.write(json.dumps(i) + '\n')

#pd.DataFrame(SCHEDULE).to_json(sys.stdout, orient='records', lines=True)

2/0

idx2 = (START_OFFSET >= df1['origin_offset']) & (END_OFFSET <= df1['terminus_offset'])
idx3 = (END_OFFSET <= df1['terminus_offset'])

1231/0
fin = open('timetable-20190920-path.ndjson', 'r', encoding='utf-8')
INPUTDATA = [json.loads(i) for i in fin]


1/0
df2 = pd.DataFrame(df1['Active'].str.split('/').tolist(), columns=['start_date', 'end_date'])
df2['start_date'] = pd.to_datetime(df2['start_date'], format='%Y-%m-%d')
idx2 = df2['end_date'].isnull()
df2.loc[idx2, 'end_date'] = df2.loc[idx2, 'start_date']
df2['end_date'] = pd.to_datetime(df2['end_date'], format='%Y-%m-%d')
df1 = df1.join(df2)

idx1 = df1['Days'].isna()
df1.loc[idx1, 'Days'] = '0000000'
idx1 = (df1['start_date'] >= START_INTERVAL) & (df1['end_date'] <= END_INTERVAL)

5/0
def week_p(week_str):
    if not isinstance(week_str, str):
        sys.stderr.write('Error: invalid week string ' + str(week_str))
        raise TypeError

    if len(week_str) != 7:
        sys.stderr.write('Error: invalid week bitmap ' + str(week_str))
        raise ValueError

    return int(week_str, 2)

WEEK_BITMAP = int('1' * 7, 2)
WEEK = timedelta(days=7)
DAY = timedelta(days=1)

def week_f(week):
    if week > WEEK_BITMAP or week < 1:
        sys.stderr.write('Error: invalid weekday ' + str(week))
        raise ValueError
    return '{0:b}'.format(week).zfill(7)

def week_bitmap(date_object):
    return 2 ** (7 - date_object.weekday()) - 1

def day_bitmap(date_object):
    return 2 ** (6 - date_object.weekday())

def same_day(start_object, end_object):
    return start_object.date() == end_object.date()

def same_week(start_object, end_object):
    return same_day(monday_offset(start_object), monday_offset(end_object))

def monday_offset(date_object):
    return date_object - timedelta(days=date_object.weekday())

def interval_bitmap(start_date, end_date):
    if same_day(start_date, end_date):
        return [day_bitmap(start_date)]

    start_bitmap = week_bitmap(start_date)
    end_bitmap = week_bitmap(end_date) >> 1

    if same_week(start_date, end_date):
        return [start_bitmap ^ end_bitmap]

    this_bitmap = [start_bitmap]
    this_date = monday_offset(start_date) + 2 * WEEK
    while this_date.date() <= end_date.date():
        this_bitmap.append((this_date, WEEK_BITMAP))
        this_date = this_date + WEEK
    this_bitmap.append(WEEK_BITMAP ^ end_bitmap)
    return this_bitmap

def get_schedule(schedule_list):
    events = []
    for event in schedule_list:
        event_id = event['ID']
        event_type = event['T']
        this_event = event.copy()
        this_event.pop('T', None)        

        if event_type[1] == 'A':
            this_event['Event'] = {'LI': 'A', 'LT': 'T'}[event_id]
            events.append(this_event)

        if event_type[1] == 'D':
            this_event['Event'] = {'LI': 'D', 'LO': 'O'}[event_id]
            events.append(this_event)

        if event_type[1] == 'P':
            this_event['Event'] = 'P'
            events.append(this_event)
        
    return events

def filter_schedule(events, start_datetime):
    schedule = []
    operation_start = None
    operation_end = None

    for this_event in events:
        offset = timedelta(0)

        if 'Offset' in this_event:
            offset = duration_p(this_event['Offset'])

        this_datetime = start_datetime + offset

        if START_INTERVAL <= this_datetime < END_INTERVAL:
            schedule.append(this_event)
            operation_end = this_datetime
            if not operation_start:
                operation_start = this_datetime

    return (schedule, operation_start, operation_end)

N = 0
OUTPUT = {}

(START_INTERVAL, END_INTERVAL) = interval_p(INTERVAL)

for line in sys.stdin:
    N = N + 1

    object_json = json.loads(line)

    if object_json['ID'] != 'PA':
        continue

    active = object_json['Active']
    if active == 'E':
        continue

    STP = object_json['STP']
    transaction = object_json['Transaction']

    if STP == 'C':
        continue

    if transaction == 'D':
        continue

    (start_time, end_time) = interval_p(object_json['Interval'], return_duration=False)

    start_time = start_time.time()
    end_time = end_time.time()

    if 'Operation' in object_json:
        (start_active, end_active) = interval_p(object_json['Operation'], return_duration=False)
        if START_INTERVAL > end_active or END_INTERVAL <= start_active:
            continue

        start_active = fromisoday_p(object_json['Day']).date()
        start_service = datetime.combine(start_active, start_time)
        events = object_json['Schedule']

        (schedule, operation_start, operation_end) = filter_schedule(events, start_service)

        if not schedule:
            continue
        output_object = object_json.copy()
        output_object['Schedule'] = schedule
        output_object['Operation'] = interval_f(operation_start, operation_end)
        print(json.dumps(output_object))
        continue

    (start_active, end_active) = interval_p(object_json['Active'], return_duration=False)

    if START_INTERVAL > end_active or END_INTERVAL <= start_active:
        continue

    start_active = start_active.date()
    end_active = end_active.date()

    service_duration = timedelta(0)
    service_duration = duration_p(object_json['Duration'])

    days = object_json['Days']
    days_bitmap = week_p(days)

    start_datetime = datetime.combine(start_active, end_time) - service_duration
    end_datetime = datetime.combine(end_active, start_time) + service_duration
    
    for operation_datetime in repeat_pair(start_datetime, end_datetime):
        start_service = operation_datetime
        end_service = operation_datetime + service_duration
        if start_service >= END_INTERVAL or end_service < START_INTERVAL:
            continue
        if day_bitmap(start_service) & days_bitmap == 0:
            continue

        output_object = object_json.copy()
        output_object['Day'] = duration_f(operation_datetime.date())
        events = get_schedule(object_json.get('Schedule'))
        (schedule, operation_start, operation_end) = filter_schedule(events, start_service)

        if not schedule:
            continue

        output_object['Schedule'] = schedule

        output_object['Operation'] = interval_f(operation_start, operation_end)
        print(json.dumps(output_object))

