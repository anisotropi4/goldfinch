#!/usr/bin/env python3

# requirement: a unique train for each given bitmap day and UID

import sys
from datetime import datetime, date, timedelta, time, MINYEAR
import json
from iso8601datetime.duration import duration_p, fromisoday_p, ISO8601_DATE, duration_f
from iso8601datetime.interval import interval_f, interval_p, repeat_pair
import pandas as pd
import numpy as np

DAY = timedelta(days=1)
SIXDAY = 6 * DAY
WEEK = 7 * DAY
N = 0

ACTIVE_SERVICES=False

def get_interval(this_interval):
    if isinstance(this_interval, tuple):
        return this_interval
    start = this_interval[0][0]
    end = this_interval[-1][1]
    return (start, end, this_interval)

def set_interval(this_interval):
    (interval_start, interval_end, interval_object) = this_interval
    if not isinstance(interval_object, list):
        return [this_interval]
    output_object = []
    for i in interval_object:
        (start, end, interval) = i
        if end <= interval_start:
            continue
        if start >= interval_end:
            continue
        output_object.append((max(interval_start, start), min(interval_end, end), interval))
    return output_object

def insert_interval(this_object, insert_object):
    (a1, a2, a) = get_interval(this_object)
    (b1, b2, b) = insert_object
    if a1 >= b1 and a2 <= b2:
        return [(b1, b2, b)]
    if a2 <= b1:
        return set_interval((a1, a2 - DAY, a)) + set_interval((b1, b2, b))
    if b2 <= a1:
        return set_interval((b1, b2, b)) + set_interval((a1 + DAY, a2, a))
    if a2 >= b1 and a2 <= b2:
        return set_interval((a1, b1 - DAY, a)) + set_interval((b1, b2, b))
    if a1 >= b1 and a1 <= b2:
        return set_interval((b1, b2 , b)) + set_interval((b2 + DAY, a2, a))
    return set_interval((a1, b1 - DAY, a)) + set_interval((b1, b2, b)) + set_interval((b2 + DAY, a2, a))

def day_bitmap(date_object):
    return 2 ** (6 - date_object.weekday())

def days_str(n):
    return '{:b}'.format(n).zfill(7)

def day_int(bitmap):
    return int(bitmap, 2)

def monday_offset(date_object):
    return date_object - timedelta(days=date_object.weekday())

def week_p(week_str):
    if not isinstance(week_str, str):
        sys.stderr.write('Error: invalid week string ' + str(week_str))
        raise TypeError

    if len(week_str) != 7:
        sys.stderr.write('Error: invalid week bitmap ' + str(week_str))
        raise ValueError

    return int(week_str, 2)

#INPUTDATA = sys.stdin.read()

try:
    with open('storage/schedule2.ndjson', 'r', encoding='utf-8') as fin:
        INPUTDATA = json.load(fin)
except FileNotFoundError:
    INPUTDATA = []
    with open('schedule/201908100520_full-path', 'r', encoding='utf-8') as fin:
        for line in fin:
            path = json.loads(line)
            path.pop('Schedule', None)
            path.pop('Service', None)
            INPUTDATA.append(path)
    with open('storage/schedule2.ndjson', 'w', encoding='utf-8') as fout:
        json.dump(INPUTDATA, fout)


#df1 = pd.read_json(INPUTDATA, orient='records', dtype={'Days': str}, lines=True, encoding='utf8')
df1 = pd.DataFrame(INPUTDATA)

df1 = df1.drop(df1[df1['ID'] != 'PA'].index).fillna(value={'Duration': 'PT00:00:00'})

df1['Start'] = pd.DataFrame(df1['Interval'].str.split('/').tolist(), columns=['start_dt', 1]).iloc[:, 0].str[10:]
df2 = pd.DataFrame(df1['Dates'].str.split('/').tolist(), columns=['start_date', 'end_date'])
df2['start_date'] = pd.to_datetime(df2['start_date'], format='%Y-%m-%d').apply(monday_offset)
df2['end_date'] = pd.to_datetime(df2['end_date'], format='%Y-%m-%d').apply(monday_offset) + SIXDAY
df1 = df1.join(df2)

df1['Act'] = df1['Days']
#Identify all unique UIDs in timetable
SCHEDULE = pd.DataFrame(df1[~df1['UID'].duplicated(keep=False)]).reset_index(drop=True)

DUPLICATES = df1[df1['UID'].duplicated(keep=False)]

# Identify all UIDs without date overlap in timetable
df2 = DUPLICATES[['UID', 'start_date', 'end_date']].sort_values(['UID', 'start_date']).reset_index(drop=True)
df3 = df2[['UID', 'start_date']].rename({'UID': 'UID2', 'start_date': 'overlap'}, axis=1).shift(-1)
df2 = df2.join(df3)
df3 = df2[df2['UID'] == df2['UID2']].drop('UID2', axis=1).set_index('UID')

df2 = DUPLICATES.set_index('UID', drop=False)
idx3 = df3[df3['end_date'] > df3['overlap']].index.unique()

UPDATE = df2.drop(idx3)
UPDATE = UPDATE.reset_index(drop=True)
SCHEDULE = SCHEDULE.append(UPDATE, ignore_index=True, sort=False)

# Identify all UIDs with same bitmap days and interleave
df2 = df2.loc[idx3] #.set_index('Days', append=True, drop=False)
df2['bit'] = df2['Days'].map(day_int)

def xand(v):
    import itertools as itt
    for i, j in itt.combinations(v, 2):
        if (i & j) != 0:
            return False
    return True

df3 = df2['bit'].groupby('UID').agg(list).apply(np.unique).apply(xand)
df2 = df2.drop('bit', axis=1)

UPDATE = []
for UID in df2.index.unique():
    this_schedule = None
    object_iter = df2.loc[UID].iterrows()
    for _, object_json in object_iter:
        start_date = object_json.pop('start_date')
        end_date = object_json.pop('end_date')
        this_interval = (start_date, end_date, dict(object_json))
        if this_schedule:
            this_schedule = insert_interval(this_schedule, this_interval)
        else:
            this_schedule = [this_interval]
    for start_date, end_date, this_object in this_schedule:
        UPDATE.append({**this_object, 'start_date': start_date, 'end_date': end_date})

UPDATE = pd.DataFrame(UPDATE)
SCHEDULE = SCHEDULE.append(UPDATE, ignore_index=True, sort=False)

def interval_overlap(start_date, end_date, this_object):
    return (start_date >= this_object['start_date']) and (end_date < this_object['end_date'])

# Identify all UIDs with overlapping bitmap days, interleave and set unique week bitmap
df2 = DUPLICATES.set_index('UID', drop=False)
df2 = df2.loc[df3[~df3].index]
df2['bit'] = df2['Days'].map(day_int)

UPDATE = []
for UID in df2.index.unique():
    this_schedule = None
    these_objects = df2.loc[UID]
    object_iter = these_objects.iterrows()
    for _, object_json in object_iter:
        start_date = object_json['start_date']
        end_date = object_json['end_date']
        this_interval = (start_date, end_date, dict(object_json))
        if this_schedule:
            this_schedule = insert_interval(this_schedule, this_interval)
        else:
            this_schedule = [this_interval]

    2/0
    for i, (start_date, end_date, object_json) in enumerate(this_schedule):
        object_bit = object_json['bit']
        for _, this_object in these_objects.iterrows():
            this_json = dict(this_object)
            if this_json == object_json:
                continue
            this_bit = this_json['bit']
            if not(object_bit ^ this_bit):
                continue
            if interval_overlap(start_date, end_date, this_object):
                4/0

    321/0
    for start_date, end_date, this_object in this_schedule:
        UPDATE.append({**this_object, 'start_date': start_date, 'end_date': end_date})


7531/0




UPDATE = []
for UID in df2.index.unique():
    this_schedule = None
    object_iter = df2.loc[UID].iterrows()
    for _, object_json in object_iter:
        start_date = object_json.pop('start_date')
        end_date = object_json.pop('end_date')
        this_interval = (start_date, end_date, dict(object_json))
        if this_schedule:
            this_schedule = insert_interval(this_schedule, this_interval)
        else:
            this_schedule = [this_interval]
    2/0
8642/0




UPDATE = df2.loc[df3[df3].index].reset_index(drop=True)
#df2.loc[df3[df3].index.unique()].to_csv('test-out3.tsv', sep='\t', index=False)
SCHEDULE = SCHEDULE.append(UPDATE, ignore_index=True, sort=False)

#df2.loc[df3[df3['end_date'] <= df3['overlap']].index]
#df2.loc[df3[df3['end_date'] <= df3['overlap']].index.unique()].to_csv('test-out1.tsv', sep='\t', index=False)


df3.iloc[-1] = df2[['UID', 'start_date']].iloc[-1]
df3['end_date'] = df2['end_date']
df3 = df3.reset_index(drop=True)


3/0
def overlap_p(rows):
    r = np.array(rows[['start_date', 'end_date']].values)
    return r

df2 = DUPLICATES.set_index(['UID', 'start_date'], drop=False).sort_index()

2/0
df2 = DUPLICATES.set_index(['UID', 'Days'], drop=False)

df2['v'] = 1
df3 = df2.loc[:, 'v'].groupby(['UID']).agg(sum)
df3.name = 'n'
df2 = df2.join(df3)
df3 = df2.loc[:, 'v'].groupby(['UID', 'Days']).agg(sum)
df3.name = 'm'
df2 = df2.join(df3)
print(df2.shape[0])

df3 = df2[df2['n'] == df2['m']].drop(['v', 'm', 'n'], axis=1)

UPDATE = []
for (UID, days) in df3.index.unique():
    this_schedule = None
    try:
        object_iter = df3.loc[UID].loc[days].iterrows()
    except AttributeError:
        object_iter = df3.loc[UID].iterrows()
    for _, object_json in object_iter:
        start_date = object_json.pop('start_date')
        end_date = object_json.pop('end_date')
        if start_date == end_date:
            end_date = end_date + DAY
        this_interval = (start_date, end_date, dict(object_json))
        if this_schedule:
            this_schedule = insert_interval(this_schedule, this_interval)
        else:
            this_schedule = [this_interval]
    for start_date, end_date, this_object in this_schedule:
        UPDATE.append({**this_object, 'start_date': start_date, 'end_date': end_date})

UPDATE = pd.DataFrame(UPDATE)
SCHEDULE = SCHEDULE.append(UPDATE, ignore_index=True, sort=False)

def xand(v):
    import itertools as itt
    for i, j in itt.combinations(v, 2):
        if (i & j) != 0:
            return False
    return True

df2 = df2.drop(df2[df2['n'] == df2['m']].index)
print(len(df2))

df2['bit'] = df2['Days'].map(day_int)
df3 = df2['bit'].groupby('UID').agg(list).apply(np.unique).apply(xand)

df3.name = 'xand'
df2 = df2.join(df3)

UPDATE = pd.DataFrame(df2[df2['xand']].drop(['v', 'm', 'n', 'bit', 'xand'], axis=1).reset_index(drop=True))
SCHEDULE = SCHEDULE.append(UPDATE, ignore_index=True, sort=False)

df3 = df2.drop(df2[df2['xand']].index)
print(df3.shape)
10/0


def xoverlap(v):
    import itertools as itt
    overlap = []
    for i, j in itt.combinations(v, 2):
        if (i & j) != 0:
            overlap.append((i, j))
    return overlap

df4.name = 'xand'
df3 = df3.join(df4)

UPDATE = pd.DataFrame(df3[df3['xand']].drop(['v', 'm', 'n', 'bit', 'and', 'xand'], axis=1).reset_index(drop=True))
SCHEDULE = SCHEDULE.append(UPDATE, ignore_index=True, sort=False)

this_schedule = None
UID = 'C00037'
object_iter = df3.loc[UID].iterrows()
for _, object_json in object_iter:
    start_date = object_json.pop('start_date')
    end_date = object_json.pop('end_date')
    if start_date == end_date:
        end_date = end_date + DAY
    this_interval = (start_date, end_date, object_json['Days'])
    if this_schedule:
        this_schedule = insert_interval(this_schedule, this_interval)
    else:
        this_schedule = [this_interval]

3/0

#df3.loc['C00037', 'bit']
#df3.loc['C00060', 'bit']
3/0
df4 = df3['bit'].groupby('UID').agg(list).apply(xand)
df4.name = 'xand2'
df3 = df3.join(df4)


2/0
UPDATE = df3[(df3['and'] == 0)]
1/0
SCHEDULE = SCHEDULE.append(UPDATE, ignore_index=True, sort=False)

df4 = df3[(df3['and'] == 0) & (df3['n'] > 2)]
5/0
df3['nbit'] = 127 - df3['bit']


#df4 = df3['bitmap'].groupby('UID').agg(list).apply(np.bitwise_xor.reduce)
#df4.name = 'xor'
#df3 = df3.join(df4)

df4 = df3['nbit'].groupby('UID').agg(list).apply(np.bitwise_and.reduce)
df4.name = 'nand'
df3 = df3.join(df4)

3/0
UPDATE = []
for (UID, bitmap) in df3.index.unique():
    this_schedule = None
    for _, object_json in df3.loc[UID].loc[bitmap].iterrows():
        service_dates = object_json.get('Dates')
        start_date = object_json.get('start_date')
        end_date = object_json.get('end_date')
        if start_date == end_date:
            end_date = end_date + DAY
        STP = object_json['STP']
        transaction = object_json['Transaction']
        this_interval = (start_date, end_date, dict(object_json))
        if this_schedule:
            this_schedule = insert_interval(this_schedule, this_interval)
            for start_date, end_date, this_object in this_schedule:
                this_object['start_date'] = start_date
                this_object['end_date'] = end_date
        else:
            this_schedule = [this_interval]
    for _, _, this_object in this_schedule:
        UPDATE.append(this_object)

UPDATE = pd.DataFrame(UPDATE).reset_index().drop(['bitmap', 'xor'], axis=1)
SCHEDULE = SCHEDULE.append(UPDATE, ignore_index=True, sort=False)

2/0
df2 = pd.DataFrame(df1[df1['UID'].duplicated(keep=False)])
df2 = df2.set_index(['UID', 'Dates'])
df2['bitmap'] = df2['Days'].map(day_int)

5/0
df3 = (df2.groupby('UID').apply(lambda v: np.bitwise_xor(v['bitmap'].values)) != 0)
df3.name = 'xor'
df2 = df2.join(df3)

XOR = df2[df2['xor']].drop(['Duration', 'ID', 'Interval', 'Start', 'xor', 'bitmap'], axis=1).reset_index()
XOR = XOR.set_index('UID', drop=False)

UPDATE = []
for UID in XOR.index.unique():
    this_schedule = None
    these_intervals = []
    for _, object_json in XOR.loc[UID].iterrows():
        service_dates = object_json.get('Dates')
        start_date = object_json.get('start_date')
        end_date = object_json.get('end_date')
        if start_date == end_date:
            end_date = end_date + DAY
        STP = object_json['STP']
        transaction = object_json['Transaction']
        this_interval = (start_date, end_date, dict(object_json))
        if this_schedule:
            this_schedule = insert_interval(this_schedule, this_interval)
            for start_date, end_date, this_object in this_schedule:
                this_object['start_date'] = start_date
                this_object['end_date'] = end_date
            for base_start_date, base_end_date, base_object in these_intervals:
                base_bitmap = base_object['Days']
                if base_start_date <= start_date and base_end_date >= end_date:
                    this_bitmap = this_interval[2]['Days']
                    n = days_str(day_int(this_bitmap) ^ day_int(base_bitmap))
                    if n:
                        5/0
        else:
            this_schedule = [this_interval]
        these_intervals.append(this_interval)
    523/0
    for _, _, this_object in this_schedule:
        UPDATE.append(this_object)

UPDATE = pd.DataFrame(UPDATE)

5/0
df3 = (df2.groupby('UID').apply(lambda v: np.bitwise_and.reduce(v['bitmap'].values)) != 0)
df3.name = 'and'
df2 = df2.join(df3)

try:
    XOR = df2[df2['xor']].drop(['and', 'xor', 'bitmap'], axis=1).reset_index()
    XOR = XOR.set_index(['UID', 'Days'], drop=False)

    UPDATE = []
    for (UID, bitmap) in XOR.index.unique():
        this_schedule = None
        for _, object_json in XOR.loc[UID].loc[bitmap].iterrows():
            service_dates = object_json.get('Dates')
            start_date = object_json.get('start_date')
            end_date = object_json.get('end_date')
            if start_date == end_date:
                end_date = end_date + DAY
            STP = object_json['STP']
            transaction = object_json['Transaction']
            this_interval = (start_date, end_date, dict(object_json))
            if this_schedule:
                this_schedule = insert_interval(this_schedule, this_interval)
                for start_date, end_date, this_object in this_schedule:
                    this_object['start_date'] = start_date
                    this_object['end_date'] = end_date
            else:
                this_schedule = [this_interval]
        for _, _, this_object in this_schedule:
            UPDATE.append(this_object)

    UPDATE = pd.DataFrame(UPDATE)
except KeyError:
    pass

SCHEDULE = SCHEDULE.append(UPDATE, ignore_index=True, sort=False)

try:
    UPDATE = df2[~df2['and']].drop(['and', 'xor', 'bitmap'], axis=1).reset_index()
    SCHEDULE = SCHEDULE.append(UPDATE, ignore_index=True, sort=False)
except KeyError:
    pass

A = set(df1['UID'].unique())
B = set(df1.loc[~df1['UID'].duplicated(keep=False), 'UID'].unique())

C = set(df1.loc[df1['UID'].duplicated(keep=False), 'UID'].unique())

A == (B | C)

D = set(df2[~df2['and']].index.unique())
C & D == D

E = set(df2[df2['xor']].index.unique())
C & E == E

5/0


5/0

OVERLAP = df2[df2['overlap']].drop(['overlap'], axis=1)


OVERLAP['Active'] = OVERLAP['start_date'].dt.strftime('%Y-%m-%d')  + '/' + OVERLAP['end_date'].dt.strftime('%Y-%m-%d')
OVERLAP = OVERLAP.drop(['Interval', 'start_date', 'end_date'], axis=1)

with open('storage/overlap.ndjson', 'w') as fp:
    for _, v in OVERLAP.iterrows():
        json.dump(v.to_dict(), fp)
        fp.write('\n')
2/0

df3 = df2[~df2['overlap']].drop(['overlap'], axis=1)

df3 = df3[df3[['UID', 'Days']].duplicated(keep=False)]
df3 = df3.set_index(['UID', 'Days'], drop=False)

UPDATE = []
for (UID, bitmap) in df3.index.unique():
    this_schedule = None
    for _, object_json in df3.loc[UID].loc[bitmap].iterrows():
        service_dates = object_json.get('Dates')
        start_date = object_json.get('start_date')
        end_date = object_json.get('end_date')
        if start_date == end_date:
            end_date = end_date + DAY
        STP = object_json['STP']
        transaction = object_json['Transaction']
        this_interval = (start_date, end_date, dict(object_json))
        if this_schedule:
            this_schedule = insert_interval(this_schedule, this_interval)
            for start_date, end_date, this_object in this_schedule:
                this_object['start_date'] = start_date
                this_object['end_date'] = end_date
        else:
            this_schedule = [this_interval]
    for _, _, this_object in this_schedule:
        UPDATE.append(this_object)

UPDATE = pd.DataFrame(UPDATE)
SCHEDULE = SCHEDULE.append(UPDATE, ignore_index=True, sort=False)

#TIMETABLE['Active'] = TIMETABLE['start_date'].dt.strftime('%Y-%m-%d')  + '/' + #TIMETABLE['end_date'].dt.strftime('%Y-%m-%d')
#TIMETABLE = TIMETABLE.drop(['Interval', 'start_date', 'end_date'], axis=1)

#with open('storage/timetable.ndjson', 'w') as fp:
#    for _, v in TIMETABLE.iterrows():
#        json.dump(v.to_dict(), fp)
#        fp.write('\n')


SCHEDULE['Active'] = SCHEDULE['start_date'].dt.strftime('%Y-%m-%d')  + '/' + SCHEDULE['end_date'].dt.strftime('%Y-%m-%d')
SCHEDULE = SCHEDULE.drop(['Interval', 'start_date', 'end_date'], axis=1)

#for _, v in SCHEDULE.iterrows():
#    print(json.dumps(v.to_dict()))

with open('storage/schedule.ndjson', 'w') as fp:
    for _, v in SCHEDULE.iterrows():
        json.dump(v.to_dict(), fp)
        fp.write('\n')
