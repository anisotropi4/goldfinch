# **ATCO**

These scripts scrape the [ATCO codes](https://www.gov.uk/government/publications/national-public-transport-access-node-schema/naptan-guide-for-data-managers) from the UK Government Department for Transport tables to provide a link between the three-numeric ATCO code used in the National Public Transport Access Nodes [NaPTAN](https://www.gov.uk/government/publications/national-public-transport-access-node-schema) dataset

## Background

This is to support matching railway stations to the local authority area in which a British railway station is located

## Data sources and processing

These scripts scrape HTML from the [ATCO codes](https://www.gov.uk/government/publications/national-public-transport-access-node-schema/naptan-guide-for-data-managers) from the UK Government Department for Transport (DfT) HTML tables, convert these to JSON, extract all the table data and output this into a series of 11 TSV format report

In the NaPTAN dataset the first three numbers denotes the authority responsible for the managing the data associate with the transport node. The fourth character is a 0 (zero). The remaining characters to a maximum of 8 are alpha-numeric determined locally. The first three to provide a link between the three-numeric ATCO code used in the National Public Transport Access Nodes [NaPTAN](https://www.gov.uk/government/publications/national-public-transport-access-node-schema) dataset.

For rail stations the ATCO code is managed centrally, however by linking the National Passenger Tranport Locality Code (NptgLocalityCode) it is possible in the majority of cases to link the stop-point ATCOCode for the station through common locality codes


## Software Components

The framework is built using [dash](http://gondor.apana.org.au/~herbert/dash/) (Debian Almquist shell) scripts and python to download, extract, transform and load data into a Apache Solr and zookeeper docker cluster 


## Pre-requisites

To extract and process the data requires the following software

### jq

The [jq](https://stedolan.github.io/jq/) JSON script tool is used in the to filter, map and transform structured data on the command line. To install `jq` on a Debian based Linux type
```console
    $ sudo apt-get install jq
```

### cURL

The [cURL](http://curl.haxx.se) command line tool is used to download HTML and data. To install `curl` on a Debian based Linux type
```console
    $ sudo apt-get install curl
```

## python modules

The `pandas`, `lxml` and `xmltodict` are used to manage docker container configuration and to process data. To manage [python](https://www.python.org/) module installation and dependencies create and active a python virtual environment in the `wagtail` directory type
```console
    $ virtualenv venv
    $ source venv/bin/activate
    $ pip install -r requirements
```

To exit the virtual environment type
```console
    $ deactivate
```

### pandas
python [pandas](https://pandas.pydata.org) is a fast, powerful, flexible and easy to use open source data analysis and manipulation tool, built on top of the Python

### lxml
python [lxml](https://lxml.de/)

### xmltodict
python [xmltodict](https://github.com/martinblech/xmltodict)

## Note and licensing

This software framework and scripts are released under an `MIT License` without  warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement

It is based on access and processing the data released by Network Rail Infrastructure Limited licensed under the following [licence](www.networkrail.co.uk/data-feeds/terms-and-conditions)

This implementation is based on access to the [opentraintimes](https://networkrail.opendata.opentraintimes.com/) mirror of the Network Rail open [datafeeds](https://datafeeds.networkrail.co.uk) for ease of access

I would like to thank both [Network Rail](https://www.networkrail.co.uk/) for making this data available and [Open Train Times](https://www.opentraintimes.com/) for their mirror of this data
