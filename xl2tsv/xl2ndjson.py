#!/usr/bin/env python3

import pandas as pd
import argparse
import os
import sys

parser = argparse.ArgumentParser(description='Dump xls(x) files tab(s) to .tsv files, to the (default output) path')

parser.add_argument('inputfiles', type=str, nargs='*', help='name of xls-file to process')

tabgroup = parser.add_mutually_exclusive_group()

tabgroup.add_argument('--tabnames', dest='tabnames', action='store_true',
                    default=False, help='dump name of tabs')

tabgroup.add_argument('--tab', type=str, dest='tab', default=None,
                    help='name of tab to process')

filegroup = parser.add_mutually_exclusive_group()

filegroup.add_argument('--path', dest='path', type=str, default='output',
                    help='output directory file')

filegroup.add_argument('--stdout', dest='stdout', action='store_true',
                    default=False, help='dump a tab to stdout')

parser.add_argument('--sourcename', dest='sourcename', action='store_true',
                    default=False, help='prepend filename to output tab file')

parser.add_argument('--headers', type=str, dest='h_list', default=None,
                    help='list of header names')

parser.add_argument('--skip-rows', type=str, dest='skip', default=0,
                    help='skip rows')

args = parser.parse_args()

path = args.path

if not os.path.exists(path):
    os.makedirs(path)

if args.tabnames:
    for filename in args.inputfiles:
        if len(args.inputfiles) > 1:
            print(filename)
        df = pd.read_excel(filename, None)
        print('\t'.join(df.keys()))
    sys.exit(0)

for filename in args.inputfiles:    
    if args.tab:
        tab = args.tab
        filebase = ''
        if args.sourcename:
            filebase = filename + ':'
            if '.' in filename:
                filebase = filename.rsplit('.', 1)[0] + ':'
        try:
            header_list = None
            if args.h_list:
                header_list = [i.strip() for i in args.h_list.split(',')]
            if args.skip:
                skip_list = [int(i.strip()) for i in args.skip.split(',')]
            df = pd.read_excel(filename, tab, names=header_list, skiprows=skip_list).fillna('')
            if args.stdout:
                df.to_json(sys.stdout, orient='records', lines=True)
                print()
            else:
                df.to_json('{}/{}{}.ndjson'.format(path, filebase, tab), orient='records', lines=True)

        except KeyError:
            pass
    else:
        df = pd.read_excel(filename, None)
        filebase = ''
        if args.sourcename:
            filebase = filename + ':'
            if '.' in filename:
                filebase = filename.rsplit('.', 1)[0] + ':'
        for tab in df.keys():
            df[tab] = df[tab].fillna('')
            df[tab].to_json('{}/{}{}.ndjson'.format(path, filebase, tab), orient='records', lines=True)

