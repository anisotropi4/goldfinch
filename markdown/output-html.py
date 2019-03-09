#!/usr/bin/env python3

import sys
import argparse
import yaml
from jinja2 import Template
from mistune import Markdown

# Simple jinja2 template
this_template = """<html>
<head>
<title>{{ titletext }}</title>
</head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="github-markdown.min.css">
<style>
	.markdown-body {
		box-sizing: border-box;
		min-width: 200px;
		max-width: 980px;
		margin: 0 auto;
		padding: 45px;
	}

	@media (max-width: 767px) {
		.markdown-body {
			padding: 15px;
		}
	}
</style>
<article class="markdown-body">
{{ bodytext }}
</article>
</html>
"""

parser = argparse.ArgumentParser(description='Input a markdown file and output the corresponding html file. Also with yaml convertion')

parser.add_argument('--yaml', dest='yaml', action='store_true',
                    default=False, help='process yaml format markdown file')

parser.add_argument('--dumpmd', dest='dumpmd', action='store_true',
                    default=False, help='dump yaml file to markdown format')
                    
parser.add_argument('inputfile', type=str, nargs='?', help='name of markdown-file to process, default stdin')

parser.add_argument('outputfile', type=str, default='index.html', nargs='?', help='name of html-file to output, default index.html')

args = parser.parse_args()

fin = sys.stdin
if args.inputfile:
    fin = open(args.inputfile, 'r')

template = Template(this_template)
markdown = Markdown()
output_dict = {}

if args.yaml:
    yaml_text = yaml.safe_load(fin)
    output_dict['titletext'] = yaml_text['title']
    output_dict['bodytext'] = markdown(yaml_text['body'])
else:
    body_text = fin.read()
    output_dict['titletext'] = 'Title'
    if '\n' in body_text:
        """set an arbitrary limit to the title of 80 characters"""
        n = min(80, body_text.find('\n'))
        output_dict['titletext'] = body_text[:n]
    output_dict['bodytext'] = markdown(body_text)

if args.dumpmd:
    md_file = 'dump.md'
    if args.inputfile:
        md_file = '.'.join(args.inputfile.split('.')[:-1]) + '.md'
    with open(md_file, 'w') as fp:
        fp.write('\n'.join(yaml_text['body'].split('\n')))

with open(args.outputfile, 'w') as fp:
    fp.write(template.render(output_dict))
