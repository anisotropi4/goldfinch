#!/usr/bin/python3
import sys
import argparse
import re

parser = argparse.ArgumentParser(description='Reformats an xml-filename so tags and sub-trees below a given depth are on a single line')

parser.add_argument('--depth', dest='depth', type=int, default=3,
                    help='depth to remove outer xml tags (default: 3)')

parser.add_argument('--stdout', dest='tostdout', action='store_true',
                    default=False,
                    help='output to STDOUT (default: False if depth > 0)')

parser.add_argument('--path', dest='path', type=str, default='output',
                    help='output directory file')

parser.add_argument('inputfile', type=str, nargs='?', help='name of xml-file to parse')

args = parser.parse_args()

path = args.path
depth = args.depth

if path != '':
    path = path + '/'

fin = sys.stdin

tostdout = args.tostdout

if depth == 0:
    tostdout = True

fout = sys.stdout
outputfile = 'STDOUT'

inputfile = args.inputfile
if inputfile:
    fin = open(inputfile, 'r')
else:
    inputfile = 'STDIN'

root = []
rtag = None
stag = None
etag = None
nl = True

m = 0
n = 0

spacematch = re.compile(r'>\s+<')
tagsplit = re.compile(r'[>\s]')

for line in fin:
    line = line.rstrip('\n')
    line = re.sub(spacematch, '><', line)
    line = line.rstrip().lstrip()

    if 'xml ' in line[:10]:
        continue

    multiline = False
    stag = None
    etag = None    
    
    (tag, _) = re.split(tagsplit, line[1:], 1)

    if tag[0] == '/':
        etag = tag[1:-1]
    elif line[0] == '<':
        stag = tag

    if line[-2:] == '/>':
        etag = tag
    elif '</' in line:
        (etag, _) = line[::-1][1:].split('/<', 1)        
        etag = etag[::-1]

    multiline = None

    if stag and not etag:
        if line[(len(stag) + 2):] != '':
            multiline = True

    if not stag and etag:
        if line[:-(len(etag) + 3)] != '':
            multiline = True

    if not stag and not etag:
        multiline = True

    if stag:
        root.append(stag)

    if len(root) == (depth + 1) and not tostdout:
        if stag and stag != rtag:
            rtag = stag

            if fout and not fout.closed and fout is not sys.stdout:        
                fout.close()
            outputfile = rtag + '.xml'
            fout = open(path + outputfile, 'a')

    if len(root) > depth:
        fout.write(line)
        nl = False

    if etag:
        qtag = root.pop()
        if etag != qtag:
            sys.stderr.write('Error: tag mismatch between "' + qtag + '" "' + etag + '" in file "' + inputfile + '"\n')
            sys.exit(1)
    
    if multiline and not etag and len(root) > depth:
        fout.write(' ')
    elif len(root) == depth and not nl:
        fout.write('\n')
        nl = True

#fout.write('\n')
