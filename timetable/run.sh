#!/bin/sh

export PYTHONUNBUFFERED=1
for DIRECTORY in data schedule storage
do
    if [ ! -d ${DIRECTORY} ]; then
        mkdir ${DIRECTORY}
    fi
done

URL="https://networkrail.opendata.opentraintimes.com/mirror/schedule/cif/"

echo Download CIF files
echo Get file list
if [ ! -f full-file-list.html ]; then
    curl ${URL} | scrape -e 'tbody' > full-file-list.html
    xml-to-json full-file-list.html | jq -cr '.tbody[] | .[].td[] | select(.a?.title?) | .a.title' > full-file-list.txt
fi

LINE=$(fgrep -n _full.gz full-file-list.txt | tail -1)
if [ ! -f file-list.txt ]; then
    N=$(echo ${LINE} | cut -d':' -f1)
    tail -n +${N} full-file-list.txt > file-list.txt
fi

for FILENAME in $(cat file-list.txt | sed 's/.gz$//')
do
    echo Process ${FILENAME} CIF file
    if [ ! -f data/${FILENAME} ]; then
        echo Download ${FILENAME} CIF file
        curl -o data/${FILENAME}.gz ${URL}/${FILENAME}.gz
        gzip -d data/${FILENAME}.gz
    fi

    if [ ! -f schedule/${FILENAME} ]
    then
        echo Convert ${FILENAME} file to ndjson
        < data/${FILENAME} ./wtt6.py > schedule/${FILENAME}
    fi

    if [ ! -f storage/${FILENAME}-path ]; then
        echo Extract Paths ${FILENAME} file to ndjson
        < schedule/${FILENAME} jq -c 'select(.ID == "PA")' > storage/${FILENAME}-path
    fi

    if [ ! -f storage/${FILENAME}-loc ]; then
        echo Extract Locations ${FILENAME} file to ndjson
        < schedule/${FILENAME} jq -c 'select(.ID == "TI")' > storage/${FILENAME}-loc
    fi
done

DATESTRING=$(tail -1 file-list.txt | cut -d'_' -f1 | cut -d':' -f2 | cut -c1-8)
echo Creating WTT for ${DATESTRING}

if [ ! -f timetable-${DATESTRING}-loc.ndjson ]; then
    echo Create timetable-${DATESTRING}-loc.ndjson file
    for FILENAME in $(cat file-list.txt | sed 's/.gz$//')
    do
        cat storage/${FILENAME}-loc
    done > timetable-${DATESTRING}-loc.ndjson
fi

if [ ! -f timetable-${DATESTRING}.ndjson ]; then
    echo Create timetable-${DATESTRING}.ndjson file
    for FILENAME in $(cat file-list.txt | sed 's/.gz$//')
    do
        cat storage/${FILENAME}-path
    done | ./wtt-timetable5.py > timetable-${DATESTRING}.ndjson
fi

if [ ! -f timetable-${DATESTRING}-PATH ]; then
    echo Create timetable-${DATESTRING} service files and post to Solr
    for FILENAME in $(cat file-list.txt | sed 's/.gz$//')
    do
        cat schedule/${FILENAME}
    done | ./wtt-paths2.py
    touch timetable-${DATESTRING}-PATH
fi

echo filter $(date +%Y%m%d)/$(date --date="tomorrow" +%Y%m%d) dates
if [ ! -f wtt-${DATESTRING}-1.ndjson ]; then
    ./filter.sh $(date +%Y%m%d)/$(date --date="tomorrow" +%Y%m%d)
fi
