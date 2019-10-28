#!/bin/sh

DATESTRING=$(tail -1 file-list.txt | cut -d'_' -f1 | cut -d':' -f2 | cut -c1-8)
echo ${DATESTRING}

FILTER=20191208/20181209
FILTER=${1:-$FILTER}

while true
do
    echo ${FILTER}
    if [ ! -f wtt-${DATESTRING}-$#.ndjson ]; then
        < timetable-${DATESTRING}.ndjson ./wtt-select4.py ${FILTER} > wtt-${DATESTRING}-$#.ndjson
    fi

    if [ ! -f output-all.json ]; then
        < wtt-${DATESTRING}-$#.ndjson ./wtt-map.py > output-all.json 2> missing-TIPLOC.tsv
        < output-all.json sort -n | jq -sc '.' > /tmp/output-all.json.$$
        mv /tmp/output-all.json.$$ output-all.json
        echo "TIPLOC	HeadCode	count" > missing-report.tsv
        < missing-TIPLOC.tsv cut -f1-2 -d'	' | unip >> missing-report.tsv
    fi
    if [ $# -le 1 ]; then
        break
    fi
    shift
    FILTER=$1
done
