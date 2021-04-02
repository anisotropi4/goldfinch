# **BPLAN**

These scripts calculate about 3,031,953 minimum connections times for the approximately 2,462 on the heavy-rail British network. These calculations use a mirrored copy of the British Rail BPLAN Geography file. 

## Background

Following a request on #Twitter for travel times between rail stations, it became clear that an easily available resource was not obviously available.

## Data sources and processing

The example data are from the [Network Rail](https://www.networkrail.co.uk/) [open-data](https://www.networkrail.co.uk/who-we-are/transparency-and-ethics/transparency/open-data-feeds/) Infrastructure BPLAN Geography dataset. 

License information for this data is given at the bottom of this document

## Software Components

The framework is built using [dash](http://gondor.apana.org.au/~herbert/dash/) (Debian Almquist shell) scripts and python to download, extract, transform and create the reports

## Pre-requisites

To extract and process the data requires the following software

### cURL

The [cURL](http://curl.haxx.se) command line tool is used to download HTML and data. To install `curl` on a Debian based Linux type
```console
    $ sudo apt-get install curl
```

## python modules

The `pandas`, `networkx` and `scipy` modules are used to to process data. To manage [python](https://www.python.org/) module installation and dependencies create and active a python virtual environment in the `BPLAN` directory type
```console
    $ virtualenv venv
    $ source venv/bin/activate
    $ pip install -r requirements.txt
```

To exit the virtual environment type
```console
    $ deactivate
```

### pandas
python [pandas](https://pandas.pydata.org) is a fast, powerful, flexible and easy to use open source data analysis and manipulation tool, built on top of the Python

### GeoPandas
python [geopandas](https://geopandas.org/) makes working with geospatial data in python easier by extending the datatypes used by pandas to allow spatial operations on geometric types

### SciPy
python [scipy](https://www.scipy.org/) provides efficient numerical routines, such as routines for numerical integration, interpolation, optimization, linear algebra, and statistics include graph and network analysis

### networkx
python [networkx](https://networkx.org/) is a Python package for the creation, manipulation, and study of the structure, dynamics, and functions of complex networks

## Create connection time report files

To create the BPLAN-timing split into five TSV files:
```console
$ ./run.sh
```

## Note and licensing

This software framework and scripts are released under an `MIT License` without  warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement

It is based on access and processing the data released by Network Rail Infrastructure Limited licensed under the following [licence](www.networkrail.co.uk/data-feeds/terms-and-conditions)

This implementation is based on access to the [opentraintimes](https://networkrail.opendata.opentraintimes.com/) mirror of the Network Rail open [datafeeds](https://datafeeds.networkrail.co.uk) for ease of access

I would like to thank both [Network Rail](https://www.networkrail.co.uk/) for making this data available and [Open Train Times](https://www.opentraintimes.com/) for their mirror of this data
