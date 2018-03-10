#!/usr/bin/python3
import sys
import argparse
import re

parser = argparse.ArgumentParser(description='Reformats an xml-filename so tags and sub-trees below a given depth are on a single line')

parser.add_argument('--path', dest='path', type=str, default='',
                    help='output directory file')

parser.add_argument('inputfile', type=str, nargs='?', help='name of xml-file to parse')

parser.add_argument('--depth', dest='depth', type=int, default=2,
                    help='depth to nest xml tags (default: 2)')

args = parser.parse_args()

path = args.path
depth = args.depth

if path != '':
    path = path + '/'

fin = sys.stdin
fout = sys.stdout

inputfile = args.inputfile
if inputfile:
    fin = open(inputfile, 'r')
else:
    inputfile = 'STDIN'

root = []
stag = None
etag = None

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

    fout.write(line)

    if etag:
        qtag = root.pop()
        if etag != qtag:
            sys.stderr.write('Error: tag mismatch between "' + qtag + '" "' + etag + '" in file "' + inputfile + '"\n')
            sys.exit(1)

    if multiline and not etag:
        fout.write(' ')
    elif len(root) <= depth:
        fout.write('\n')
