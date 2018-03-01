#!/usr/bin/python3
import xml.etree.cElementTree as ET
import xml.dom.minidom as md
import sys
import re

import argparse

parser = argparse.ArgumentParser(description='Iterate through an xml file \
removing namespace and outer xml-tags')
parser.add_argument('--depth', dest='depth', type=int, default=2,
                    help='depth to remove outer xml tags (default: 2)')
parser.add_argument('--split', dest='split', action='store_true',
                    default=False,
                    help='split output into <xml-tag>.xml files')
parser.add_argument('--split-path', dest='path', type=str, default='output',
                    help='directory file for split files (default: ./output)')
parser.add_argument('inputfile', type=str, nargs='?',
                    help='name of file to parse')

args = parser.parse_args()

path = args.path
if path != '':
    path = path + '/'

fin = sys.stdin
if args.inputfile:
    fin = open(args.inputfile, 'r')


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
filename = None
f = None

re_strip = re.compile('>\s+<')

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
        n = n + 1

    if event == 'end':
        if n > depth:
            tag = strip_ns(e.tag, namespaces)
            u = ET.Element(tag, e.attrib)
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
        if n == (depth + 1) and root:
            t = v[root]
            
            p = ET.tostring(t, method='xml').decode('UTF-8')
            (_, r) = md.parseString(p).toxml().replace('\n', '').split('>', 1)
            r = re.sub(re_strip, '><', r)
            if args.split:
                if root != filename:
                    if f and not f.closed:
                        f.close()
                    filename = root
                    f = open(path + root + '.xml', 'w')
                f.write(r + '\n')
            else:
                print(r)
            root = None
            u.clear()
            u = None
            v.clear()
            s.clear()
            t.clear()
            t = None
            e.clear()
            e.tag = None

        n = n - 1

if f and not f.closed:
    f.close()
