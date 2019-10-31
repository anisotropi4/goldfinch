#!/usr/bin/env python3
import sys
import argparse
from datetime import datetime, date, timedelta, time, MINYEAR
import json
import pickle
from iso8601datetime.duration import duration_p, fromisoday_p, ISO8601_DATE, duration_f
from iso8601datetime.interval import interval_f, interval_p, repeat_pair
import pandas as pd

DAY = timedelta(days=1)
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

def week_p(week_str):
    if not isinstance(week_str, str):
        sys.stderr.write('Error: invalid week string ' + str(week_str))
        raise TypeError

    if len(week_str) != 7:
        sys.stderr.write('Error: invalid week bitmap ' + str(week_str))
        raise ValueError

    return int(week_str, 2)

TIMETABLE = {}

fp = open('storage/timetable.pkl', 'wb+')

for line in sys.stdin:
#for line in open('Schedule-sample-1'):
    N = N + 1
    object_json = json.loads(line)
    ID = object_json['ID']
    if ID != 'PA':
        continue

    pickle.dump(object_json, fp, pickle.HIGHEST_PROTOCOL)

    UID = object_json['UID']
    service_dates = object_json.get('Dates')

    (start_date, end_date) = interval_p(service_dates, return_duration=False)
    if start_date == end_date:
        end_date = end_date + DAY

    STP = object_json['STP']
    transaction = object_json['Transaction']
    this_interval = (start_date, end_date, (service_dates, STP, transaction))

    if UID in TIMETABLE:
        TIMETABLE[UID] = insert_interval(TIMETABLE[UID], this_interval)
    else:
        TIMETABLE[UID] = [this_interval]

SCHEDULE = {}
for (UID, services_object) in TIMETABLE.items():
    for (start_date, end_date, (service_dates, STP, transaction)) in services_object:
        if ACTIVE_SERVICES and STP == 'C':
            continue

        if ACTIVE_SERVICES and transaction == 'D':
            continue

        active_dates = interval_f(start_date, end_date, format=True)

        if UID in SCHEDULE:
            if service_dates in SCHEDULE[UID]:
                SCHEDULE[UID][service_dates].append(active_dates)
            else:
                SCHEDULE[UID][service_dates] = [active_dates]
            continue
        SCHEDULE[UID] = {service_dates: [active_dates]}

with open('storage/schedule.pkl', 'wb') as fp:
    pickle.dump(SCHEDULE, fp, pickle.HIGHEST_PROTOCOL)

with open('storage/timetable.pkl', 'rb') as fp:
    try:
        while True:
            object_json = pickle.load(fp)
            UID = object_json['UID']
            STP = object_json['STP']
            transaction = object_json['Transaction']
            service_dates = object_json.get('Dates')

            if ACTIVE_SERVICES and UID not in SCHEDULE:
                continue

            if service_dates not in SCHEDULE[UID]:
                if ACTIVE_SERVICES:
                    continue
                object_json['Active'] = 'E'
                print(json.dumps(object_json))
                continue

            if STP == 'C' or transaction == 'D':
                if ACTIVE_SERVICES:
                    continue
                for active_date in SCHEDULE[UID][service_dates]:
                    object_json['Active'] = active_date
                    print(json.dumps(object_json))
                continue

            (start_interval, _) = interval_p(object_json['Interval'])
            duration = duration_p(object_json['Duration'])
            start_time = start_interval.time()
            end_time = (start_interval + duration).time()

            for active_date in SCHEDULE[UID][service_dates]:
                object_json['Active'] = active_date
                (start_date, end_date) = interval_p(active_date, return_duration=False)
                start_date = datetime.combine(start_date.date(), start_time)
                end_date = datetime.combine(end_date.date(), end_time)
                object_json['Interval'] = interval_f(start_date, end_date)
                print(json.dumps(object_json))

    except EOFError:
        pass
