#!/usr/bin/env python3

import sys
import json
import argparse
import os.path as path
import pandas as pd
import numpy as np

DEBUG = True
filename = 'storage/PATH_004.jsonl'
filename = 'storage/PA_004.jsonl'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process trains services \
file to json')
    parser.add_argument('inputfile', type=str, help='name of working \
timetable file to parse')
    args = parser.parse_args()
    filename = args.inputfile
    DEBUG = False

filestub = path.basename(filename)

if DEBUG:
    pd.set_option('display.max_columns', None)
    print(filename)

M = filestub.split('_').pop(0)
M = M.split('-').pop(0)

fin = open(filename, 'r')
df1 = pd.DataFrame([json.loads(line.strip()) for line in fin])

KEYS = df1.columns.tolist()

DATEFIELDS = {}
for KEY in KEYS:
    DATEFIELDS[KEY] = 'string'
    try:
        df1[KEY] = pd.to_datetime(df1[KEY])
        DATEFIELDS[KEY] = 'pdate'
    except ValueError:
        pass

print(json.dumps({M: len(KEYS), 'keys': [{KEY: DATEFIELDS[KEY]} for KEY in KEYS if KEY != 'id']}))
