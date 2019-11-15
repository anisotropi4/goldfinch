#!/usr/bin/env python3

import sys
import json
import argparse
import os.path as path
import pandas as pd
import numpy as np

DEBUG = True
filename = 'storage/PATH_004.jsonl'

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
    print(filename)

M = filestub.split('_').pop(0)
M = M.split('-').pop(0)

fin = open(filename, 'r')

KEYS = pd.DataFrame([json.loads(line.strip()) for line in fin]).columns.tolist()
print(json.dumps({M: len(KEYS), 'keys': [KEY for KEY in KEYS if KEY != 'id']}))
