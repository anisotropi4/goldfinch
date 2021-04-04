#!/usr/bin/env python3

import json
import pandas as pd
import sys

pd.set_option('display.max_columns', None)

DATA = []

for i, j in enumerate(sys.stdin):
    this_json = json.loads(j)
    data = [k for k in this_json]
    header = data[0]['th']
    body = [k['td'] for k in data[1:]]
    df1 = pd.DataFrame(data=body)
    if len(header) < df1.shape[1]:
        header += list(df1.columns[len(header):])
    df1.columns = header
    df1.to_csv('table_{:02}.tsv'.format(i + 1), sep='\t', index=False)
