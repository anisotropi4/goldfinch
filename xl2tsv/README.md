# Dump spreadsheet content `xl2tsv.py`

The `xl2tsv.py` script dumps the content of xls(x) files to a `[<source-filename>:]<tabname>.tsv` files in the (default) `output` directory. Command line parameters:

+   --tabnames to dump the names of the tabs in the file(s) and stop  
+   --path (optional) set the output directory path (default) output  
+   --tab (optional) set the name of the tab to process  
+   --filename (optional) append file name to 

The `xl2ndjson.py` script dumps the same tab data to a `.ndjson` (New-line Delimited JSON file).

## Dependencies

The `xl2tsv.py` is a simple wrapper script based on the python [xlrd](https://pypi.org/project/xlrd) and [pandas](https://pandas.pydata.org) libraries. To install these libraries:

``` 
 $ pip install xlrd pandas
```

## Usage Examples

### Basic usage
Dump the `Airports`, `Junctions`, `RailStations` and `VariableDefinitions` tab data from the `connectivity-statistics-destination-lists.xls` into `.tsv` files in the `output` directory:

```
  $ ./xl2tsv.py connectivity-statistics-destination-lists.xls 
  $ ls output
Airports.tsv  Junctions.tsv  RailStations.tsv  VariableDefinitions.tsv
```

### All tabs in a file
Dump the names of the tabs from the `connectivity-statistics-destination-lists.xls` file:

```
$ ./xl2tsv.py --tabnames connectivity-statistics-destination-lists.xls 
VariableDefinitions	Airports	RailStations	Junctions
```

### One tab into a given directory
Dump the `Junctions` tab data into the `connectivity` directory:

```
  $ ./xl2tsv.py --tab Junctions --path connectivity  connectivity-statistics-destination-lists.xls 
  $ ls connectivity
Junctions.tsv
```

### All tabs from multiple-files into multiple `.tsv` files named source-filename

Dump all the tab data from the `connectivity-statistics.xls` and `US gun crime.xlsx` files into the `output` directory with filenames `<filename>:<tab>.tsv`:

```
  $ ./xl2tsv.py --filename connectivity-statistics.xls 'US gun crime.xlsx' 
  $ ls output
 connectivity-statistics:Airports.tsv
 connectivity-statistics:Junctions.tsv
 connectivity-statistics:RailStations.tsv
 connectivity-statistics:VariableDefinitions.tsv
'US gun crime:2010 SUMMARY.tsv'
'US gun crime:2011 MURDER.tsv'
'US gun crime:ASSAULT 2009.tsv'
'US gun crime:ASSAULT 2010.tsv'
'US gun crime:ASSAULT 2011.tsv'
'US gun crime:CHART TRENDS.tsv'
'US gun crime:MURDER 2009.tsv'
'US gun crime:MURDER 2010.tsv'
'US gun crime:MURDER TRENDS.tsv'
'US gun crime:POPULATION DATA.tsv'
'US gun crime:ROBBERY 2009.tsv'
'US gun crime:ROBBERY 2010.tsv'
'US gun crime:ROBBERY 2011.tsv'
'US gun crime:SUMMARY 2011.tsv'
```
