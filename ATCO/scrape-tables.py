#!/usr/bin/env python3

import argparse
import pandas as pd
from lxml import html, objectify
import requests

ARG_PARSER = argparse.ArgumentParser(description='Scrapes and extracts tables data from a URL')
ARG_PARSER.add_argument('URL', type=str, nargs='?',
                        help='URL to scrape tables',
                        default='https://www.gov.uk/government/publications/national-public-transport-access-node-schema/naptan-guide-for-data-managers')

ARGS = ARG_PARSER.parse_args()

PAGE = requests.get(ARGS.URL)

TREE = html.fromstring(PAGE.content)

DATA = TREE.xpath('//div[@class="main-content-container"]').pop()

TABLES = DATA.xpath('//table')

for i, j in enumerate(TABLES):
    header = j.xpath('thead/tr/th/text()')
    body = [k.xpath('td/text()') for k in j.xpath('tbody/tr')]
    df1 = pd.DataFrame(data=body)
    if len(header) < df1.shape[1]:
        header += list(df1.columns[len(header):])
    df1.columns = header
    df1.to_csv('table_{:02}.tsv'.format(i + 1), sep='\t', index=False)

