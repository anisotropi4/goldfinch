#!/usr/bin/env python3

import sys
import json
import argparse
import os.path as path
import pandas as pd
import numpy as np
import pandas.api.types as pd_types
from app.solr import get_schema, set_schema

DEBUG = True
filename = 'storage/PATH_004.jsonl'
filename = 'storage/PA_004.jsonl'
filename = 'storage/HD_001.jsonl'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process trains services \
file to create JSONL schema')
    parser.add_argument('inputfiles', nargs='+', \
                        help='name of JSONL files to parse')
    args = parser.parse_args()
    filenames = args.inputfiles
    DEBUG = False

if DEBUG:
    pd.set_option('display.max_columns', None)
    filenames = [filename]

for filename in filenames:
    filestub = path.basename(filename)
    M = filestub.split('_').pop(0)
    M = M.split('-').pop(0)

    df1 = pd.read_json(filename, lines=True)
    KEYS = df1.columns.tolist()

    SCHEMA = set(get_schema(M))

    DATAFIELDS = {}
    for KEY in KEYS:
        if KEY in SCHEMA:
            continue
        DATAFIELDS[KEY] = 'string'
        if pd_types.is_datetime64_any_dtype(df1[KEY]):
            DATAFIELDS[KEY] = 'pdate'
            continue
        if pd_types.is_string_dtype(df1[KEY]):
            if np.max(df1[KEY].fillna('').apply(len)) < 10:
                continue
            if df1[KEY].str.contains('/').any():
                continue
            try:
                df1[KEY] = pd.to_datetime(df1[KEY])
                DATAFIELDS[KEY] = 'pdate'
            except ValueError:
                pass

    print(json.dumps({'core': M, 'file': filestub, 'field_update': [{KEY: DATAFIELDS[KEY]} for KEY in DATAFIELDS if KEY != 'id']}))
    schema = [{'name': KEY, 'type': DATAFIELDS[KEY]} for KEY in DATAFIELDS if KEY != 'id']
    if schema:
        set_schema(M, schema)
