#!/usr/bin/env python3

import pandas as pd
import json

fin_name = 'test/timetable-11.ndjson'

fin = open(fin_name, 'r', encoding='utf-8')
WTT = pd.DataFrame([json.loads(i) for i in fin])
WTT = WTT.fillna(value={'Origin': '00:00:00', 'Terminus': '00:00:00'})

def days_str(n):
    return '{:b}'.format(n).zfill(7)

def set_path1(this_path, this_id, this_bitmap):
    return {**this_path.to_dict(), **{'Actual': this_bitmap, 'Days': this_bitmap}}

def set_path2(this_path, this_id, this_bitmap):
    return {**this_path.to_dict(), **{'UID': this_id, 'Actual': this_bitmap, 'Days': this_bitmap}}

for (i, PATH) in WTT.iterrows():
    for j in range(0, 128):
        uid = 'T{}{}'.format(str(i+1).zfill(2), str(j).zfill(3))
        this_bitmap = days_str(j)
        print(json.dumps(set_path2(PATH, uid, this_bitmap)))


2/0

for (i, PATH) in WTT.iterrows():
    for (n, j) in enumerate([0] + [2 ** n for n in range(0, 7)]):
        uid = 'T{}{}'.format(str(i+1).zfill(2), str(j).zfill(3))
        this_bitmap = days_str(j)
        print(json.dumps(set_path2(PATH, uid, this_bitmap)))

1/0
