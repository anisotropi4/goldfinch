#!/usr/bin/env python

import pandas as pd
from app.solr import get_collections, get_connection, get_query, get_count, get_schema, set_schema
import requests
import json

DEBUG = True
if __name__ == '__main__':
    DEBUG = False

if DEBUG:
    pd.set_option('display.max_columns', None)

def get_bitmaps():
    from datetime import datetime
    #STARTYEAR = pd.offsets.YearBegin()
    WEEK = pd.offsets.Week()
    MONDAY = pd.offsets.Week(weekday=0)
    ZEROBITMAP = '0' * 7
    solr = get_connection('AA')
    r = get_query(solr, '*:*', limitrows=False, fq='{{!collapse field=Dates size={}}}'.format(get_count(solr)), fl='Dates, Date_From, Date_To, Days')
    solr = get_connection('PA')
    r += get_query(solr, '*:*', limitrows=False, fq='{{!collapse field=Dates size={}}}'.format(get_count(solr)), fl='Dates,Date_From,Date_To,Days')
    df1 = pd.DataFrame(r).drop_duplicates().set_index(['Dates'], drop=False)
    for KEY in ['Date_From', 'Date_To']:
        df1[KEY] = pd.to_datetime(df1[KEY])
    start_date = df1['Date_From'].min() + MONDAY
    end_date = df1['Date_From'].max() + MONDAY
    fullkey = '{}.{}.{}'.format(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'), ZEROBITMAP)
    df1.loc[fullkey] = {'Date_From': start_date, 'Date_To': end_date, 'Days': ZEROBITMAP, 'Dates': fullkey}    
    def bitmap_range(date_from, date_to, this_bitstring):
        range_idx = pd.date_range(date_from + MONDAY, date_to + MONDAY, freq=MONDAY)
        return pd.Series(index=range_idx, data=this_bitstring)
    def fill_bitmap(this_row):
        inverse_row = this_row['Days'][::-1]
        return bitmap_range(this_row['Date_From'], this_row['Date_To'], inverse_row)
    df1 = df1.transpose().apply(fill_bitmap).sort_index(ascending=False).fillna(ZEROBITMAP)
    df1 = df1.apply(lambda x: ''.join(x.values).lstrip('0'))
    df1.name = 'bitstring'
    df1 = df1.reset_index()
    return df1

if 'bitmap' not in get_collections():
    raise ValueError('Error "wtt-bitmap.py": no "bitmap" collection')

BITMAP = get_bitmaps()
BITMAP['id'] = BITMAP['Dates']
set_schema('bitmap', [{'name': 'Dates'}, {'name': 'bitstring'} ])
OUTPUTDATA = [r.to_dict() for _, r in BITMAP.iterrows()]
solr = get_connection('bitmap', always_commit=True)
solr.add(OUTPUTDATA)
