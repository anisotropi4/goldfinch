#!/bin/sh 

DATESTRING=$(tail -1 file-list.txt | cut -d'_' -f1 | cut -d':' -f2 | cut -c1-8)
echo ${DATESTRING}

FILTER=20191208/20191209
FILTER=${1:-$FILTER}

while true
do
    echo ${FILTER}
    if [ ! -s wtt-${DATESTRING}-$#.jsonl ]; then
        ./wtt-select4.py PA-${DATESTRING}.jsonl ${FILTER} > wtt-${DATESTRING}-$#.jsonl
    fi

    if [ ! -s visualisation/output-all.json ]; then
        < wtt-${DATESTRING}-$#.jsonl ./wtt-map.py ${FILTER} > output-all.jsonl 2> missing-TIPLOC.tsv
        < output-all.jsonl sort -n | jq -sc '.' > visualistion/output-all.json
        echo "TIPLOC	HeadCode	count" > missing-report.tsv
        < missing-TIPLOC.tsv cut -f1-2 -d'	' | unip >> missing-report.tsv
    fi
    if [ $# -le 1 ]; then
        break
    fi
    shift
    FILTER=$1
done
