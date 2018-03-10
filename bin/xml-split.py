#!/usr/bin/python3
import xml.etree.cElementTree as ET
import xml.dom.minidom as md
import sys
import re
import gc

import argparse

parser = argparse.ArgumentParser(description='Iterate through an xml file \
removing namespace and outer xml-tags')

parser.add_argument('--depth', dest='depth', type=int, default=2,
                    help='depth to remove outer xml tags (default: 2)')

parser.add_argument('--stdout', dest='tostdout', action='store_true',
                    default=False,
                    help='output to STDOUT (default: False if depth > 0)')

parser.add_argument('--path', dest='path', type=str, default='output',
                    help='directory file for split files (default: ./output)')

parser.add_argument('inputfile', type=str, nargs='?',
                    help='name of file to parse')

parser.add_argument('--append', dest='append', action='store_true',
                    default=False,
                    help='append output to <xml-tag>.xml files')

args = parser.parse_args()

path = args.path
if path != '':
    path = path + '/'

fin = sys.stdin
inputfile = 'STDIN'
if args.inputfile:
    inputfile = args.inputfile
    fin = open(inputfile, 'r')


depth = args.depth

def strip_ns(tag, namespaces):
    for nk, nv in namespaces.items():
        if tag.startswith(nk+':'):
            return tag[len(nk)+1:]
        if tag.startswith('{'+nv+'}'):
            return tag[len(nv)+2:]
    return tag


namespaces = {}
document = ET.iterparse(fin, events=('start', 'end', 'start-ns', 'end-ns'))
root = None
v = {}
n = 0
s = {}
w = []
filename = None
f = None
flist = {}

re_strip = re.compile('>\s+<')
try:
    for event, e in document:
        if event == 'start-ns':
            (nk, nv) = e
            namespaces[nk] = nv
            continue

        if event == 'end-ns':
            namespaces.pop('key', None)
            continue

        if event == 'start':
            if n < depth:
                e.clear()
                e.tag = None
            n = n + 1

        if event == 'end':
            if n > depth:
                tag = strip_ns(e.tag, namespaces)
                u = ET.Element(tag, e.attrib)
                w.append(u)
                v[tag] = u
                u.text = e.text
                if tag in s:
                    s[tag].append(u)
                else:
                    s[tag] = [u]
                i = e.iter()
                r = strip_ns(next(i).tag, namespaces)
                for j in i:
                    k = strip_ns(j.tag, namespaces)
                    v[r].append(s[k].pop(0))
                root = r
                e.clear()
            else:
                e.clear()
                e.tag = None

            if n == (depth + 1) and root:
                t = v[root]            
                p = ET.tostring(t, method='xml').decode('UTF-8')
                (_, r) = md.parseString(p).toxml().replace('\n', '').split('>', 1)
                r = re.sub(re_strip, '><', r)
                if not args.tostdout:
                    if root in flist:
                        with open(path + root + '.xml', 'a') as f:
                            f.write(r + '\n')
                    else:
                        flist[root] = True
                        with open(path + root + '.xml', 'w') as f:
                            f.write(r + '\n')
                elif args.append:
                    with open(path + root + '.xml', 'a') as f:
                        f.write(r + '\n')
                    flist[root] = True                
                else:
                    print(r)

                root = None
                u.clear()
                u = None

                for i in w:
                    i.clear()
                    i.tag = None

                w = []
                v.clear()
                s.clear()
                t.clear()
                t = None
                e.clear()
                e.tag = None
            n = n - 1
except ET.ParseError:
    sys.stderr.write('Error: parse error in file "' + inputfile + '"\n')
    sys.exit(1)

if f and not f.closed:
    f.close()
