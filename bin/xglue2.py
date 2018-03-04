#!/usr/bin/python3
import sys
import argparse
import re

parser = argparse.ArgumentParser(description='Reformats an xml-filename so tags and sub-trees below a given depth are on a single line')

parser.add_argument('--path', dest='path', type=str, default='',
                    help='output directory file')

parser.add_argument('--depth', dest='depth', type=int, default=3,
                    help='depth to remove outer xml tags (default: 3)')

args = parser.parse_args()

path = args.path
if path != '':
    path = path + '/'

fin = sys.stdin
fout = sys.stdout

inputfile = 'STDIN'

if args.depth:
    depth = args.depth

root = []
this = None
etag = None
first = True
end = False
newline = False

n = 0
m = 0

for line in fin:
    line = line.rstrip('\n')
    line = re.sub('>\s+<','><', line)
    line = line.rstrip().lstrip()
    if 'xml ' in line:
        continue

    tags = re.split(r'[<\s>]+', line)
    if len(tags) < 2:
        continue

    tag = tags[1]

    etag = None
    if len(tags) > 3:
        etag = tags[-2]
        
    if tag == this or etag == this:
        x = root.pop()
        n = n - 1

        if n < 0:
            sys.exit(1)

        if end and not newline:
            fout.write('\n')
            newline = True
        fout.write(line)
        newline = False
        end = True

        this = None
        if len(root) > 0:
            this = '/' + root[-1]

        continue
        
    if n < depth:
        root.append(tag)
        this = '/' + tag
        n = n + 1
        if not first and not newline:
            fout.write('\n')        
            newline = True
            
    fout.write(line)
    newline = False
    
    if line[-2:] == '/>':
        #fout.write(':' + tag + ':' + this + ':')
        if '/' + tag == this:
            fout.write('\n')
            newline = True

    first = False
    end = False
        
fout.write('\n')    
