import pysolr
import requests
import json
import os

CONNECTIONS = {}
SOLRHOST = os.environ.get('SOLRHOST', 'localhost')

def clean_query(this_object):
    this_object.pop('_version_', None)
    return this_object

def get_count(solr, search_str='*:*', **rest):
    v = solr.search(q=search_str, start=0, nrows=0, **rest)
    return v.hits

def raw_query(solr, search_str='*:*', nrows=10, **rest):
    if not nrows:
        nrows = get_count(solr) + 10
    v = solr.search(q=search_str, start=0, rows=nrows, **rest)
    return v.docs

def get_query(solr, search_str, sort='id asc', limitrows=False, nrows=10, **rest):
    v = solr.search(q=search_str, sort=sort, start=0, rows=nrows, **rest)
    r = [clean_query(i) for i in v]
    if limitrows:
        return r
    for m in range(nrows, v.hits, 1024):
        s = solr.search(q=search_str, sort=sort, start=m, rows=1024, **rest)
        r += [clean_query(i) for i in s]
    return r

def get_connection(ID, hostname=SOLRHOST, timeout=10, always_commit=False):
    if ID not in COLLECTIONS:
        raise ValueError('Not a Solr collection ID {}'.format(ID))
    if ID not in CONNECTIONS:
        CONNECTIONS[ID] = pysolr.Solr('http://{}:8983/solr/{}'.format(SOLRHOST, ID), timeout=timeout, always_commit=always_commit)
    return CONNECTIONS[ID]

def get_cores():
    r = requests.get('http://{}:8983/solr/admin/cores'.format(SOLRHOST)).json()
    return {'collections': [i for i in r['status']]}

def get_collections():
    return get_cores()['collections']

def get_schema(ID):
    if ID not in COLLECTIONS:
        raise ValueError('ID {} not a Solr collection'.format(ID))
    r = requests.get('http://{}:8983/solr/{}/schema/fields'.format(SOLRHOST, ID)).json()
    del r['responseHeader']
    return [i['name'] for i in r['fields'] if i.get('stored')]

def solr_field(name=None, type='string', multiValued=False, stored=True):
    if not name:
        raise TypeError('solar() missing 1 required positional argument: "name"')
    lookup_bool = {True: 'true', False: 'false'}
    return {'name': name, 'type': type, 'multiValued': lookup_bool[multiValued], 'stored': lookup_bool[stored]}

def set_schema(ID, *v):
    fields = []
    for i in v:
        if isinstance(i, list):
            fields += i
        else:
            fields.append(i)
    schema_fields = None
    try:
        schema_fields = get_schema(ID)
    except ValueError:
        pass
    data = {'add-field': [], 'replace-field': []}
    for field in fields:
        if field['name'] in schema_fields:
            data['replace-field'].append(solr_field(**field))
            continue
        data['add-field'].append(solr_field(**field))
    r = requests.post('http://{}:8983/api/cores/{}/schema'.format(SOLRHOST, ID), json.dumps(data))

COLLECTIONS = get_collections()
