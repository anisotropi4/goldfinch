#!/bin/sh -x 

URL="https://networkrail.opendata.opentraintimes.com/mirror/schedule/cif/"
FILTER=20180925/20180926

if [ ! -f tbody.html ]; then
    curl ${URL} | scrape -e 'tbody' > tbody.html
fi

if [ ! -f file-list.txt ]; then
    xml-to-json tbody.html | jq -cr '.tbody[] | .[].td[] | select(.a?.title?) | .a.title' > full-file-list.txt
fi

if [ -f full-file-list.txt ]; then
    LINE=$(fgrep -n _full.gz full-file-list.txt | tail -1)
    DATESTRING=$(echo ${LINE} | cut -d'_' -f1 | cut -d':' -f2 | cut -c1-8)
    if [ ! -f file-list.txt ]; then
         N=$(echo ${LINE} | cut -d':' -f1)
         tail -n +${N} full-file-list.txt > file-list.txt
    fi    
fi

echo ${DATESTRING}

for FILENAME in $(cat file-list.txt | sed 's/.gz$//')
do
    if [ ! -f data/${FILENAME} ]; then
        curl -o data/${FILENAME} ${URL}/${FILENAME}
        gzip -d data/${FILENAME}.gz
    fi

    if [ ! -f schedule/${FILENAME} ]
    then
        < data/${FILENAME} ./wtt3.py > schedule/${FILENAME}
    fi

    if [ ! -f schedule/${FILENAME}-path ]; then
        < schedule/${FILENAME} jq -c 'select(.ID == "PA")' > schedule/${FILENAME}-path
    fi
done

if [ ! -f timetable-${DATESTRING}.ndjson ]; then
    cat schedule/*-path | ./wtt-timetable2.py > timetable-${DATESTRING}.ndjson
fi


if [ ! -f wtt-${DATESTRING}.ndjson ]; then
    < timetable-${DATESTRING}.ndjson ./wtt-select2.py ${FILTER} > wtt-${DATESTRING}.ndjson
fi

if [ ! -f output-all.json ]; then
    < wtt-${DATESTRING}.ndjson ./wtt-map.py > output-all.json 2> missing-TIPLOC.tsv
    < output-all.json sort -n | jq -sc '.' > /tmp/output-all.json.$$
    mv /tmp/output-all.json.$$ output-all.json
    echo "TIPLOC	HeadCode	count" > missing-report.tsv
    < missing-TIPLOC.tsv cut -f1-2 -d'	' | unip >> missing-report.tsv
fi
