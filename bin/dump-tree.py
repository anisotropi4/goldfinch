#!/usr/bin/python3
import xml.etree.cElementTree as ET
import sys

import argparse

parser = argparse.ArgumentParser(description='Strip namespace and a list of xml-tags in a tsv format')
parser.add_argument('--path', dest='path', type=str, default='',
                    help='output directory file')

parser.add_argument('inputfile', type=str, nargs='?', help='name of xml-file to parse')
parser.add_argument('outputfile', type=str, nargs='?', help='name of output file')

args = parser.parse_args()

path = args.path
if path != '':
    path = path + '/'

fin = sys.stdin
if args.inputfile:
    fin = open(args.inputfile, 'r')
    
fout = sys.stdout
if args.outputfile:
    fout = open(path + args.outputfile, 'w')
    
def strip_ns(tag, namespaces):
    for nk, nv in namespaces.items():
        if tag.startswith(nk+':'):
            return tag[len(nk)+1:]
        if tag.startswith('{'+nv+'}'):
            return tag[len(nv)+2:]
    return tag

namespaces = {}

document = ET.iterparse(fin, events=('start', 'end', 'start-ns', 'end-ns'))

s = []

n = 0

for event, e in document:
    if event == 'start-ns':
        (nk, nv) = e
        namespaces[nk] = nv
        continue
    
    if event == 'end-ns':        
        namespaces.pop('key', None)
        continue
    
    if event == 'start':
        tag = strip_ns(e.tag, namespaces)
        s.append(tag)
        n = n + 1
        r = "\t".join(s + [str(n)])
        fout.write(r)
        fout.write('\n')
        e.clear()

        
    if event == 'end':
        s.pop()
        n = n - 1        

if fout is not sys.stdout:        
    fout.close()
