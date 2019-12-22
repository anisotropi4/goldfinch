#!/usr/bin/env python3

# requirement: a unique train for each given bitmap day and UID

import sys
import argparse
from datetime import datetime, date, timedelta, time, MINYEAR
import json
import pandas as pd
import numpy as np
from uuid import uuid1

DAY = timedelta(days=1)
#SIXDAY = 6 * DAY
WEEK = 7 * DAY
N = 0

ACTIVE_SERVICES=False

def days_str(n):
    return '{:b}'.format(n).zfill(7)

def day_int(bitmap):
    return int(bitmap, 2)

def monday_offset(date_object):
    return date_object - timedelta(days=date_object.weekday())

INPUTDATA = []

fin = sys.stdin

DEBUG = True
if __name__ == '__main__':
    DEBUG = False

if DEBUG:
    fin = open('schedule/PA-20191130.jsonl', 'r', encoding='utf-8')
    pd.set_option('display.max_columns', None)

with open('storage/schedule.ndjson', 'w', encoding='utf-8') as fout:
    for line in fin:
        path = json.loads(line)
        path.pop('Schedule', None)
        path.pop('Service', None)
        INPUTDATA.append(path)
        json.dump(path, fout)
        fout.write('\n')


#df1 = pd.read_json(INPUTDATA, orient='records', dtype={'Days': str}, lines=True, encoding='utf8')
df1 = pd.DataFrame(INPUTDATA)

df1 = df1.drop(df1[df1['ID'] != 'PA'].index).fillna(value={'Duration': 'PT00:00:00'})

df1['ID'] = 'PT'

#df2 = pd.DataFrame(df1['Dates'].str.split('/').tolist(), columns=['start_date', 'end_date'])
for KEY in ['Date_From', 'Date_To']:
    df1[KEY] = pd.to_datetime(df1[KEY], format='%Y-%m-%d')


df2 = df1[['Date_From', 'Date_To']].copy().rename(columns={'Date_From': 'Start_Date', 'Date_To': 'End_Date'})
df2['Start_Date'] = df2['Start_Date'].apply(monday_offset)
idx2 = df2['End_Date'].isnull()
df2.loc[idx2, 'End_Date'] = df2.loc[idx2, 'Start_Date']
df2['End_Date'] = df2['End_Date'].apply(monday_offset) + WEEK

df1 = df1.join(df2)
idx1 = df1['Days'].isna()
df1.loc[idx1, 'Days'] = '0000000'

df1['Actual'] = df1['Days']

#Identify all unique UIDs in timetable
idx1 = df1['UID'].duplicated(keep=False)
SCHEDULE = pd.DataFrame(df1[~idx1]).reset_index(drop=True)

DUPLICATES = df1[idx1]

# Identify all UIDs without date overlap in timetable
df2 = DUPLICATES[['UID', 'Start_Date', 'End_Date']].sort_values(['UID', 'Start_Date']).reset_index(drop=True)
df3 = df2[['UID', 'Start_Date']].rename({'UID': 'UID2', 'Start_Date': 'overlap'}, axis=1).shift(-1)
df2 = df2.join(df3)
df3 = df2[df2['UID'] == df2['UID2']].drop('UID2', axis=1).set_index('UID')

df2 = DUPLICATES.set_index('UID', drop=False)
idx3 = df3[df3['End_Date'] > df3['overlap']].index.unique()

UPDATE = df2.drop(idx3)
UPDATE = UPDATE.reset_index(drop=True)
SCHEDULE = SCHEDULE.append(UPDATE, ignore_index=True, sort=False)

# Identify all UIDs with date overlap and interleave
df2 = df2.loc[idx3]

def xor_bitmap(a, b):
    return b & (a ^ b)

def overlay_bits(b):
    v = list(b[::-1])
    for n in range(1, len(v)):
        v = v[:n] + [(xor_bitmap(v[n - 1], i)) for i in v[n:]]
    return tuple(v[::-1])

def interleave(these_objects):
    this_interval = [(j['Start_Date'], j['End_Date'], day_int(j['Days']), (j),) for j in these_objects]
    idx = sorted(set([j for i in this_interval for j in (i[0], i[1])]))
    all_paths = {}
    for i in this_interval:
        (m, n, bit, k) = i
        for j in range(idx.index(m), idx.index(n)):
            (k1, k2) = (idx[j], idx[j+1])
            try:
                all_paths[(k1, k2)] += ((bit, k),)
            except KeyError:
                all_paths[(k1, k2)] = ((bit, k),)
    this_schedule = []
    for (k1, k2), v in all_paths.items():
        (bits, paths) = zip(*v)
        bits = overlay_bits((bits))
        for bit, path in zip(bits, paths):
            if bit > 0:
                path = path.copy()
                path['Start_Date'] = k1
                path['End_Date'] = k2
                path['Actual'] = days_str(bit)
                this_schedule.append(path)
    return this_schedule

UPDATE = []
for UID in df2.index.unique():
    this_schedule = [i.to_dict() for _, i in df2.loc[UID].iterrows()]
    UPDATE += interleave(this_schedule)

UPDATE = pd.DataFrame(UPDATE)
SCHEDULE = SCHEDULE.append(UPDATE, ignore_index=True, sort=False)

SCHEDULE['Active'] = SCHEDULE['Start_Date'].dt.strftime('%Y-%m-%d')  + '.' + SCHEDULE['End_Date'].dt.strftime('%Y-%m-%d') + '.' + SCHEDULE['Actual'] + '.' + SCHEDULE['Op_Days']

SCHEDULE['id'] = SCHEDULE['id'] + '.' + SCHEDULE.groupby('id').cumcount().apply(str)

for KEY in ['Date_From', 'Date_To', 'Start_Date', 'End_Date']:
   SCHEDULE[KEY] = SCHEDULE[KEY].dt.strftime('%Y-%m-%dT%H:%M:%SZ')

SCHEDULE = SCHEDULE.fillna(value={'Origin': '', 'Terminus': ''})

OUTPUTDATA = [json.dumps({k: v for k, v in path.to_dict().items() if v}) for _, path in SCHEDULE.iterrows()]

print('\n'.join(OUTPUTDATA))

