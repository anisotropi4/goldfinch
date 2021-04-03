#!/usr/bin/env python3

import pandas as pd
from io import StringIO
import datetime

import json
import geopandas as gp

pd.set_option('display.max_columns', None)

HEADER = {
    'LOC': ['Reference',
            'Action Code',
            'Location Code',
            'Name',
            'Start',
            'End',
            'Easting',
            'Northing',
            'Timing Point',
            'Zone',
            'STANOX',
            'Off-Network indicator',
            'Force LPB',],
    'NWK': ['Record',
            'Action Code',
            'Origin',
            'Destination',
            'Running Line Code',
            'Running Line Description',
            'Start',
            'End',
            'Initial direction',
            'Final direction',
            'Distance',
            'DOO (Passenger)',
            'DOO (Non-Passenger)',
            'RETB',
            'Zone',
            'Reversible line',
            'Power supply type',
            'RA',
            'Maximum train length',
    ],
    'PIF': ['Type',
            'Version',
            'Source',
            'TOC ID',
            'Start',
            'End',
            'Cycle type',
            'Cycle stage',
            'Creation',],
    'PIT': ['Record',
            'REF Record',
            'REF Addition',
            'REF Change',
            'REF Delete',
            'TLD Record',
            'TLD Addition',
            'TLD Change',
            'TLD Delete',
            'LOC Record',
            'LOC Addition',
            'LOC Change',
            'LOC Delete',
            'PLT Record',
            'PLT Addition',
            'PLT Change',
            'PLT Delete',
            'NWK Record',
            'NWK Addition',
            'NWK Change',
            'NWK Delete',
            'TLK Record',
            'TLK Count'
    ],
    'PLT': ['Record',
            'Action Code',
            'Location Code',
            'Platform ID',
            'Start date',
            'End date',
            'Platform/Siding length',
            'Power supply type',
            'DOO (Passenger)',
            'DOO (Non-Passenger)',
    ],
    'REF': ['Record',
            'Action',
            'Reference type',
            'Reference',
            'Description',],
    'TLD': ['Record Type',
            'Action Code',
            'Traction type',
            'Trailing Load',
            'Speed',
            'RA/Gauge',
            'Description',
            'ITPS Power Type',
            'ITPS Load',
            'Limiting Speed',],
    'TLK': ['Record',
            'Action Code',
            'Origin',
            'Destination',
            'Running Line Code',
            'Traction Type',
            'Trailing Load',
            'Speed',
            'RA/Gauge',
            'Entry speed',
            'Exit speed',
            'Start',
            'End',
            'Sectional Running Time',
            'Description',
    ],
}

print('Load Geography\t{}'.format(datetime.datetime.now()))
FILENAME = 'Geography_current.txt'
COLS = [(0, 3), (4, 80)]
DF0 = pd.read_fwf(FILENAME, colspecs=COLS, header=None, index_col=False)

RECORDS = list(HEADER.keys())
DATA = {}

for i in RECORDS:
    data = [[i] + j.split('\t') for j in DF0[DF0[0] == i][1]]
    DATA[i] = pd.DataFrame(data)
    if i in HEADER:
        DATA[i].columns = HEADER[i]

DF1 = DATA['TLK']
NAMES = DATA['LOC'][['Location Code', 'Name']].set_index('Location Code')

def get_timedelta(this_df):
    df1 = this_df.str.split('\'', expand=True)
    for i in range(2):
        df1[i] = pd.to_numeric(df1[i], errors='coerce').fillna(0.0)
    ds1 = pd.to_timedelta(df1[0] * 60.0 + df1[1], unit='s')
    ds1.name = 'Time Delta'
    return ds1

print('Calculate Timing Links')
DS1 = get_timedelta(DF1[HEADER['TLK'][-2]])

ALLCOLS = ['Origin', 'Destination', 'Running Line Code', 'Action Code', 'Sectional Running Time', 'Time Delta']
DF1 = DF1.join(DS1)
DF1 = DF1.sort_values(ALLCOLS)

#COLUMNS = ['Origin', 'Destination', 'Running Line Code', 'Action Code']
COLUMNS = ['Origin', 'Destination']

DF2 = DF1.drop_duplicates(COLUMNS)
ALLCOLS = ['Origin', 'Destination', 'Time Delta']
DF2 = DF2[ALLCOLS].reset_index(drop=True)
DF2['Duration'] = DF2['Time Delta'].dt.total_seconds()

DATA = None
DF0 = None
DF1 = None
DS1 = None

print('Create Network')
import networkx as nx
from scipy.sparse.csgraph import dijkstra
EDGES = [tuple(i) for i in DF2[['Origin', 'Destination', 'Duration']].values]

DG = nx.DiGraph()
DG.add_weighted_edges_from(EDGES)

DF2 = None
EDGES = None

# Based on "Examples for search graph using scipy" from stackoverflow/53074847
NODES = list(DG.nodes())

def _nodes():
    return {j: i for i, j in enumerate(NODES)}

def get_indices(origin, destination, node = _nodes()):
    return (node[origin], node[destination])

START = datetime.datetime.now() 
print('Calculate Timing\t{}'.format(START))

A = nx.to_scipy_sparse_matrix(DG)
R, P = dijkstra(A, return_predecessors=True)

def get_path_index(p, i, j):
    r = [j]
    k = j
    while p[i, k] != -9999:
        r.append(p[i, k])
        k = p[i, k]
    return r[::-1]

def get_path(origin, destination, p=P):
    (i, j) = get_indices(origin, destination)
    return [NODES[k] for k in get_path_index(p, i, j)]

def get_duration(origin, destination, r=R):
    return r[get_indices(origin, destination)]

print('Load Stations')
GP1 = gp.read_file('output-stations.json')
GP2 = GP1[(GP1['Type'] == 'RLY') &
          (GP1['CRS_code'] != '-') &
          (GP1['Status'] == 'active')]
STATIONS = GP2['TIPLOC'].unique()

GP1 = None
GP2 = None

from itertools import accumulate, combinations, chain

EDGES = list(combinations(STATIONS, 2))
TIMINGS = pd.DataFrame(index=pd.MultiIndex.from_tuples(EDGES), data=EDGES, columns=['Origin', 'Destination'])
TIMINGS = TIMINGS.join(NAMES, on='Origin').rename(columns={'Name': 'Origin Name'})
TIMINGS = TIMINGS.join(NAMES, on='Destination').rename(columns={'Name': 'Destination Name'})
TIMINGS = TIMINGS.dropna()
TIMINGS['Duration'] = pd.NaT

STATIONS = TIMINGS['Origin'].unique()

DS2 = pd.Series(index=TIMINGS.index, data=pd.NA)

for i, e in enumerate(TIMINGS.index):
    if i % 65536 == 0:
        DELTA = datetime.datetime.now() - START
        print('{:8}\t{:8}\t{:8}\t{}'.format(i, *e, str(DELTA)))
    try:
        DS2[e] = get_duration(*e)
    except KeyError:
        pass

COLUMNS = ['Origin Name', 'Destination Name', 'Origin', 'Destination', 'Duration']

TIMINGS['Duration'] = DS2
TIMINGS = TIMINGS.dropna()
IDX1 = TIMINGS['Duration'] != 0.0
TIMINGS = TIMINGS[IDX1]
TIMINGS['Duration'] = pd.to_datetime(TIMINGS['Duration'], unit='s').dt.strftime('%H:%M:%S')
TIMINGS = TIMINGS[COLUMNS]

END = datetime.datetime.now() 
print('Write Timing\t{}'.format(END))


START = 0
END = 0
CHUNK = 524288
while END < TIMINGS.shape[0]:
    START = END
    END += CHUNK
    n = END // CHUNK
    TIMINGS[START:END].to_csv('BPLAN-timing-{:02}.tsv'.format(n),
                              sep='\t',
                              index=False)

TIMINGS = TIMINGS.sort_values('Duration', ascending=False)

START = 0
END = 0
CHUNK = 524288
while END < TIMINGS.shape[0]:
    START = END
    END += CHUNK
    n = END // CHUNK
    TIMINGS[START:END].to_csv('BPLAN-timing-sort-{:02}.tsv'.format(n),
                              sep='\t',
                              index=False)
