#!/usr/bin/env python3

"""converts CIF specification timetable file to new-line delimited json
(ndjson) representation of the working timetable"""
import json
import sys
from uuid import uuid1
from datetime import datetime, timedelta, time
from iso8601datetime.duration import ISO8601_DATE, time_f, fromisoday_p, duration_f #, time_f

DAY = timedelta(days=1)
ZERO = timedelta(0)

def headerdate_p(date_str):
    """return datetime objectcorresponding in ddmmyy format from header record"""
    return datetime.strptime(date_str, '%d%m%y')

def datetime_f(object):
    """return string objectcorresponding in YYY-MM-SS<T>HH:MM:SS format from header record"""
    return datetime.strftime(object, '%Y-%m-%dT%H:%M:%S')

def interval_f(start_object, end_object):
    return '{}/{}'.format(date_f(start_object), date_f(end_object))
               
def date_f(object):
    """return string objectcorresponding in YYY-MM-SS<T>HH:MM:SS format from header record"""
    return datetime.strftime(object, '%Y-%m-%d')

def operationdate_p(date_str):
    """return datetime object corresponding to yymmyy format or empty string for general records"""
    try:
        datetime_object = datetime.strptime(date_str, '%y%m%d')
        return datetime_object
    except ValueError:
        pass
    return ''

def operation_p(time_str):
    """return datetime object corresponding to a 'HHMM' time string with 'H'
half-minute 30-second offset. starting from the ISO8601 start date
(1 January 1901)"""
    this_time = datetime.strptime(time_str[:4], '%H%M')
    if time_str[-1] == 'H':
        this_time = this_time + timedelta(seconds=30)
    return this_time

def operation_f(time_str):
    """return string object corresponding to a 'HHMM' time string with 'H'
half-minute 30-second offset"""
    try:
        time_object = operation_p(time_str)
        return time_f(time_object.time())
    except ValueError:
        return ''

def operation_duration(this_object):
    """return timedelta duration corresponding to a datetime object offset
from the ISO8601 start date (1 January 1901)"""
    if isinstance(this_object, datetime):
        return this_object - ISO8601_DATE
    return operation_p(this_object) - ISO8601_DATE

def tidy_keys(this_object):
    """Removes keys with empty values"""
    return {k: v for (k, v) in this_object.items() if v.strip() != ''}

def strip_keys(this_object):
    """Strips whitespace and removes keys with empty values"""
    return {k: v.strip() for (k, v) in this_object.items() if v.strip() != ''}

def public_time(time_str):
    """return a formatted public time string if time_str is not '0000'"""
    if time_str == '0000':
        return ''
    return time_f(operation_p(time_str).time())

def duration_value(start_object, end_object):
    """return timedelta for the time difference between the current event 
and last event allowing for events over midnight"""
    offset = fromisoday_p(end_object) - fromisoday_p(start_object)
    if offset >= timedelta(0):
        return offset
    return offset + DAY

def duration_str(start_object, end_object):
    """return duration string for the time difference between the current event 
and last event allowing for events over midnight"""
    offset = duration_value(start_object, end_object)
    return duration_f(offset)

def offset_value(event_object, last_event_object, headcode_str):
    """return timedelta object for the time difference between the current
event and last event allowing for events over midnight and bus journeys"""
    offset = event_object - last_event_object
    if offset >= timedelta(0):
        return offset
    if headcode_str == '0B00':
        if offset >= timedelta(hours=-1):
            return timedelta(0)
    return offset + timedelta(days=1)

def header_record(line):
    """process CIF file header record from 80-character line string"""
    this_object = {'ID': line[0:2],
                   'File Mainframe Identity': line[2:22],
                   'Date of Extract': line[22:28],
                   'Time of Extract' :line[28:32],
                   'Current-File-Ref': line[32:39],
                   'Last-File-Ref': line[39:46],
                   'Bleed-off Update Ind': line[46:47],
                   'Version': line[47:48],
                   'User Extract Start Date': line[48:54],
                   'User Extract End Date': line[54:60]}
    extract_time = operation_p(this_object['Time of Extract'])
    extract_date = headerdate_p(this_object['Date of Extract'])
    extract_datetime = extract_date + (extract_time - ISO8601_DATE)
    extract_start_date = headerdate_p(this_object['User Extract Start Date'])
    extract_end_date = headerdate_p(this_object['User Extract End Date'])
    this_object['Extract Datetime'] = datetime_f(extract_datetime)
    this_object['Extract Interval'] = interval_f(extract_start_date, extract_end_date)
    [this_object.pop(i, None) for i in ['Date of Extract',
                                        'Time of Extract',
                                        'User Extract Start Date',
                                        'User Extract End Date']]    
    return tidy_keys(this_object)


def tiploc_insert(line):
    """return CIF file TIPLOC insert object from 80-character line string"""
    this_object = {'ID': line[0:2],
                   'TIPLOC': line[2:9],
                   'Capitals Identification': line[9:11],
                   'Nalco': line[11:17],
                   'NLC check character': line[17:18],
                   'TPS Description': line[18:44],
                   'Stanox': line[44:49],
                   'PO MCP': line[49:53],
                   'CRS': line[53:56],
                   'Description': line[56:72]}
    return strip_keys(this_object)

def tiploc_amend(line):
    """return CIF file TIPLOC amend object from 80-character line string"""
    this_object = {'ID': line[0:2],
                   'TIPLOC': line[2:9],
                   'Capitals Identification': line[9:11],
                   'Nalco': line[11:17],
                   'NLC check character': line[17:18],
                   'TPS Description': line[18:44],
                   'Stanox': line[44:49],
                   'PO MCP': line[49:53],
                   'CRS': line[53:56],
                   'Description': line[56:72],
                   'New TIPLOC': line[72:79]}
    return strip_keys(this_object)

def tiploc_delete(line):
    """return CIF file TIPLOC delete object from 80-character line string"""
    this_object = {'ID': line[0:2],
                   'TIPLOC': line[2:9]}
    return strip_keys(this_object)

def association_record(line):
    """return CIF file train-association object from 80-character line string"""
    this_object = {'ID': line[0:2],
                   'Transaction': line[2:3],
                   'Main Train-UID': line[3:9],
                   'UID': line[9:15],
                   'Date From': line[15:21],
                   'Date To': line[21:27],
                   'Days': line[27:34],
                   'Category': line[34:36],
                   'Indicator': line[36:37],
                   'Location': line[37:44],
                   'Base-Suffix': line[44:45],
                   'Location-Suffix': line[45:46],
                   #deprecated 'Diagram Type': line[46:47],
                   'Type': line[47:48],
                   'STP': line[79:80]}
    this_object = tidy_keys(this_object)

    start_object = operationdate_p(this_object['Date From'])
    this_object.pop('Date From', None)
    if 'Date To' in this_object:
        end_object = operationdate_p(this_object['Date To'])
        this_object.pop('Date To', None)
        this_object['Dates'] = interval_f(start_object, end_object)
    else:
        this_object['Dates'] = date_f(start_object)
    return tidy_keys(this_object)

def basic_schedule(line):
    """return CIF file basic schedule object from 80-character line string"""
    this_path = {'ID': 'PA',
                 'Transaction': line[2:3],
                 'UID': line[3:9],
                 'Date From': line[9:15],
                 'Date To': line[15:21],
                 'Days': line[21:28],
                 'STP': line[79:80]}
    id = line[0:2]
    this_service = {'Bank Holiday Running': line[28:29],
                    'Train Status': line[29:30],
                    'Train Category': line[30:32],
                    'Headcode': line[32:36],
                    'NRS Headcode': line[36:40],
                    #deprecated 'Course Indicator': line[40:41],
                    'Train Service': line[41:49],
                    'Portion Id': line[49:50],
                    'Power Type': line[50:53],
                    'Timing Load': line[53:57],
                    'Speed': line[57:60],
                    'Characteristics': line[60:66],
                    'Seating Class': line[66:67],
                    'Sleepers': line[67:68],
                    'Reservations': line[68:69],
                    #deprecated 'Connection Indicator': line[69:70],
                    'Catering': line[70:74],
                    'Service Branding': line[74:78]}
    this_path = tidy_keys(this_path)
    this_service = tidy_keys(this_service)

    start_object = operationdate_p(this_path['Date From'])
    this_path.pop('Date From', None)
    if 'Date To' in this_path:
        end_object = operationdate_p(this_path['Date To'])
        this_path.pop('Date To', None)
        this_path['Dates'] = interval_f(start_object, end_object)
    else:
        this_path['Dates'] = date_f(start_object)

    if len(this_service) > 1:
        this_path['Service'] = {id: this_service}

    return this_path

def basic_schedule_extra(line):
    """return CIF file basic schedule extra object from 80-character line string"""
    id = line[0:2]
    this_object = {'UIC': line[6:11],
                   #deprecated 'Traction Class': line[2:6],
                   'ATOC': line[11:13],
                   'Applicable Timetable': line[13:14],
                   'RSID': line[14:22],
                   'Data Source': line[22:23]}

    return {id: tidy_keys(this_object)}

def origin_location(line):
    """return CIF file depart from origin object, updated last reported time and
train operation duration from 80-character line string, the last reported time
and the train operation duration"""
    this_object = {'ID': line[0:2],
                   'TIPLOC': line[2:9],
                   'Suffix': line[9:10],
                   'Schedule': line[10:15],
                   'Public Schedule': line[15:19],
                   'Platform': line[19:22],
                   'Line': line[22:25],
                   'Engineering Allowance': line[25:27],
                   'Pathing Allowance': line[27:29],
                   'Activity': line[29:41],
                   'Performance Allowance': line[41:43],
                   'Reserved': line[43:46]}
    this_object['Schedule'] = operation_f(this_object['Schedule'])
    public_departure = public_time(this_object['Public Schedule'])
    this_object.pop('Public Schedule', None)
    if public_departure:
        this_object['Public Schedule'] = public_departure
    this_object['T'] = 'OD'
    this_object['Offset'] = duration_f(ZERO)
    return strip_keys(this_object)

def intermediate_location(line):
    """return CIF file intermediate location object, updated last reported time
and train operation duration from 80-character line string, the last reported
time and the train operation duration"""
    this_object = {'ID': line[0:2],
               'TIPLOC': line[2:9],
               'Suffix': line[9:10],
               'Platform': line[33:36],
               'Line': line[36:39],
               'Path': line[39:42],
               'Activity': line[42:54],
               'Engineering Allowance': line[54:56],
               'Pathing Allowance': line[56:58],
               'Performance Allowance': line[58:60],
               'Reserved field': line[60:65]}
    this_arrival = {'Schedule': operation_f(line[10:15]),
                    'Public Schedule': public_time(line[25:29])}

    this_departure = {'Schedule': operation_f(line[15:20]),
                      'Public Schedule': public_time(line[29:33])}

    this_pass = {'Schedule': operation_f(line[20:25])}

    this_object = tidy_keys(this_object)
    this_arrival = strip_keys(this_arrival)
    this_departure = strip_keys(this_departure)
    this_pass = strip_keys(this_pass)

    if this_pass:
        this_object.update(this_pass)
        this_object['T'] = 'IP'
        return (strip_keys(this_object),)

    this_arrival_object = dict(this_object)
    this_arrival_object.update(this_arrival)
    this_arrival_object['T'] = 'IA'
    this_departure_object = dict(this_object)
    this_departure_object.update(this_departure)
    this_departure_object['T'] = 'ID'
    return (strip_keys(this_arrival_object), strip_keys(this_departure_object))

def termination_location(line):
    """return CIF file arrival at terminal location object, updated last
reported time and train operation duration from 80-character line string, the
last reported time and the train operation duration"""
    this_object = {'ID': line[0:2],
                   'TIPLOC': line[2:9],
                   'Suffix': line[9:10],
                   'Schedule': line[10:15],
                   'Public Schedule': line[15:19],
                   'Platform': line[19:22],
                   'Path': line[22:25],
                   'Activity': line[25:37],
                   'Reserved field': line[37:40]}
    this_object['Schedule'] = operation_f(this_object['Schedule'])
    public_arrival = public_time(this_object['Public Schedule'])
    this_object.pop('Public Schedule', None)
    if public_arrival:
        this_object['Public Schedule'] = public_arrival
    this_object['T'] = 'DA'
    return strip_keys(this_object)

def change_en_route(line):
    """return CIF file train change en route object from 80-character line string"""
    this_object = {#'ID': line[0:2],
                   'TIPLOC': line[2:9],
                   'Suffix': line[9:10],
                   'Train Category': line[10:12],
                   'Headcode': line[12:16],
                   'NRS Headcode': line[16:20],
                   #deprecated 'Course Indicator': line[20:21],
                   'Train Service': line[21:29],
                   'Portion Id': line[29:30],
                   'Power Type': line[30:33],
                   'Timing Load': line[33:37],
                   'Speed': line[37:40],
                   'Operating Characteristics': line[40:46],
                   'Seating Class': line[46:47],
                   'Sleepers': line[47:48],
                   'Reservations': line[48:49],
                   #deprecated 'Connection Indicator': line[49:50],
                   'Catering': line[50:54],
                   'Service Branding': line[54:58],
                   #deprecated 'Traction Class': line[58:62],
                   'UIC': line[62:67],
                   'Reserved field': line[67:75]}
    return strip_keys(this_object)

def notes(line):
    """return CIF file train notes object en route object from 80-character line string"""
    this_object = {'ID': line[0:2],
                   'Note Type': line[2:3],
                   'Note': line[3:80]}
    return this_object

def end_record(line):
    """return CIF file end-of-file record"""
    this_object = {'ID': line[0:2]}
    return this_object

def output_object(this_object):
    uuid = uuid1().hex
    this_object['UUID'] = uuid
    if this_object['ID'] != 'PA':
        print(json.dumps(this_object))
        return
    this_output = this_object.copy()
    this_service = this_output.pop('Service', None)
    these_schedules = this_output.pop('Schedule', None)
    print(json.dumps(this_output))
    if this_service:
        this_base = {'ID': 'BS'}
        this_base.update(this_service['BS'])
        this_base['UUID'] = uuid
        print(json.dumps(this_base))
        this_extra = {'ID': 'BX'}
        this_extra.update(this_service['BX'])
        this_extra['UUID'] = uuid
        print(json.dumps(this_extra))
    if these_schedules:
        for this_schedule in these_schedules:
            this_schedule['UUID'] = uuid
            print(json.dumps(this_schedule))

OUTPUT = {}
start_schedule = None
N = 0

fin = sys.stdin
#fin = open('data/201909200510_update', 'r')

for l in fin:
    N = N + 1
    ID = l[0:2]    
    if N == 1 and ID != 'HD':
        sys.stderr.write('Error: no CIF header\n' + l)
        sys.exit(1)

    if ID == 'HD':
        OUTPUT = header_record(l)
    if ID == 'TI':
        OUTPUT = tiploc_insert(l)
    if ID == 'TA':
        OUTPUT = tiploc_amend(l)
    if ID == 'TD':
        OUTPUT = tiploc_delete(l)
    if ID == 'AA':
        OUTPUT = association_record(l)
    if ID == 'BS':
        if len(OUTPUT) != 0:
            raise('Error: missed output\n{}'.format(json.dumps(OUTPUT)))
        OUTPUT = basic_schedule(l)
        if OUTPUT['Transaction'] != 'D'and OUTPUT['STP'] != 'C':
            continue
    if ID == 'BX':
        schedule = basic_schedule_extra(l)
        OUTPUT['Service'].update(schedule.copy())
        continue
    if ID == 'LO':
        start_schedule = origin_location(l)
        start_time = start_schedule['Schedule']
        OUTPUT['Schedule'] = [start_schedule.copy()]
        OUTPUT['Origin'] = start_time
        continue
    if ID == 'LI':
        s = intermediate_location(l)
        for i in s:
            i['Offset'] = duration_str(start_time, i['Schedule'])
            OUTPUT['Schedule'].append(i)
        continue
    if ID == 'CR':
        schedule = change_en_route(l)
        if 'Headcode' in schedule:
            headcode = schedule['Headcode']
        if 'CR' in OUTPUT['Service']:
            OUTPUT['Service']['CR'].append(schedule.copy())
        else:
            OUTPUT['Service']['CR'] = [schedule.copy()]
        continue
    if ID in ('LN', 'TN'):
        OUTPUT['Notes'] = notes(l)
    if ID == 'ZZ':
        OUTPUT = end_record(l)
    if ID == 'LT':
        end_schedule = termination_location(l)
        end_offset = duration_str(start_schedule['Schedule'], end_schedule['Schedule'])
        end_schedule['Offset'] = end_offset
        OUTPUT['Schedule'].append(end_schedule.copy())
        OUTPUT['Terminus'] = end_schedule['Schedule']
        OUTPUT['Duration'] = end_offset
    if not OUTPUT:
        sys.stderr.write('Error: unknown record type ' + l[0:2] + '\n' + l)
        sys.exit(1)
    output_object(OUTPUT)
    OUTPUT = {}
