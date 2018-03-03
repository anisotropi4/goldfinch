#!/usr/bin/python3
import sys
import argparse
import re

parser = argparse.ArgumentParser(description='Strip namespace and dump a list xml-tag numbers and xml-tags in key file both in a tsv format')
parser.add_argument('--path', dest='path', type=str, default='',
                    help='output directory file')

parser.add_argument('inputfile', type=str, nargs='?', help='name of xml-file to parse')

parser.add_argument('--depth', dest='depth', type=int, default=2,
                    help='depth to remove outer xml tags (default: 2)')

parser.add_argument('--lines', dest='lines', type=int, default=None,
                    help='number of lines per output file (default: 1)')

parser.add_argument('--stdout', dest='tostdout', action='store_true',
                    default=False,
                    help='output to STDOUT (default: False)')

args = parser.parse_args()

path = args.path
if path != '':
    path = path + '/'

fin = sys.stdin
fout = sys.stdout

inputfile = args.inputfile

if inputfile:
    fin = open(inputfile, 'r')
else:
    inputfile = 'STDIN'
    
depth = args.depth
lines = args.lines
tostdout = args.tostdout

def strip_ns(tag, namespaces):
    for nk, nv in namespaces.items():
        if tag.startswith(nk+':'):
            return tag[len(nk)+1:]
        if tag.startswith('{'+nv+'}'):
            return tag[len(nv)+2:]
    return tag

namespaces = {}

root = []
this = None
rtag = None
etag = None

n = 0
m = 0

start = True
tagend = False

for line in fin:
    line = line.rstrip('\n').rstrip()
    if 'xml ' in line:
        continue
    (_, tag, rest) = re.split(r'[<\s>]+', line, maxsplit=2)
    #print(tag, tagend)
    
    if len(root) < depth:
        if tag == etag:
            continue
        root.append((tag, line))
        rtag = tag
        etag = '/' + tag
        this = False
        continue

    if start:
        if rtag == tag:
            sys.stderr.write('error: ' + inputfile + ' depth ' + str(depth) + '\n')
            sys.exit(2)

        m = m + 1
        if fout and not fout.closed and fout is not sys.stdout:        
            fout.close()
        if not tostdout:
            fout = open(path + 'x' + str(m).zfill(4)+ '-' + tag + '.xml', 'w')

        for (u, v) in root:
            fout.write(v + '\n')
        start = False

    if tag == etag:
        for (u, v) in root[::-1]:
            fout.write('</' + u + '>\n')
        root.pop()
        if len(root) > 0:
            (u, v) = root[::-1][0]
        etag = '/' + u
        start = True
        n = 0
        continue

    if (this and tag != this) or (lines and n >= lines):
        if not tagend:
            sys.stderr.write('error: ' + inputfile + ' depth ' + str(depth) + '\n')
            sys.exit(2)
            
        for (u, v) in root[::-1]:
            fout.write('</' + u + '>\n')

        m = m + 1

        if fout and not fout.closed and fout is not sys.stdout:        
            fout.close()

        if not tostdout:            
            fout = open(path + 'x' + str(m).zfill(4)+ '-' + tag + '.xml', 'w')

        for (u, v) in root:
            fout.write(v + '\n')
        n = 0

    tagend = ('/' + tag + '>' in line[-(len(tag)+2):]) or ('/>' == line[-2:])
    this = tag
    fout.write(line + '\n')
    n = n + 1

if m == 0 and n == 0:
    sys.stderr.write('error: ' + inputfile + ' depth ' + str(depth) + '\n')
    sys.exit(2)
    
if fout and not fout.closed and fout is not sys.stdout:        
    fout.close()
