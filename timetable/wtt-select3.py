#!/usr/bin/env python3
import sys
import argparse
from datetime import datetime, timedelta
import json
from iso8601datetime.duration import duration_p, duration_f, fromisoday_p
from iso8601datetime.interval import interval_f, interval_p, repeat_pair


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

INTERVAL='20190810/20190811'

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
        this_bitmap.append(WEEK_BITMAP)
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

(START_INTERVAL, END_INTERVAL) = interval_p(INTERVAL, return_duration=False)

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

