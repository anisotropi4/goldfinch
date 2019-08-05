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
if [ ! -f tbody.html ]; then
    curl ${URL} | scrape -e 'tbody' > tbody.html
    xml-to-json tbody.html | jq -cr '.tbody[] | .[].td[] | select(.a?.title?) | .a.title' > full-file-list.txt
fi

LINE=$(fgrep -n _full.gz full-file-list.txt | tail -1)
if [ ! -f file-list.txt ]; then
    N=$(echo ${LINE} | cut -d':' -f1)
    tail -n +${N} full-file-list.txt > file-list.txt
fi    

for FILENAME in $(cat file-list.txt | sed 's/.gz$//')
do
    echo Download ${FILENAME} CIF file
    if [ ! -f data/${FILENAME} ]; then
        curl -o data/${FILENAME}.gz ${URL}/${FILENAME}.gz
        gzip -d data/${FILENAME}.gz
    fi

    echo Convert ${FILENAME} file to ndjson
    if [ ! -f schedule/${FILENAME} ]
    then
        < data/${FILENAME} ./wtt3.py > schedule/${FILENAME}
    fi

    if [ ! -f schedule/${FILENAME}-path ]; then
        < schedule/${FILENAME} jq -c 'select(.ID == "PA")' > schedule/${FILENAME}-path
    fi

    if [ ! -f schedule/${FILENAME}-loc ]; then
        < schedule/${FILENAME} jq -c 'select(.ID == "TI")' > schedule/${FILENAME}-loc
    fi

    if [ ! -f schedule/${FILENAME}-loc ]; then
        < schedule/${FILENAME} jq -c 'select(.ID == "TI")' > schedule/${FILENAME}-loc
    fi
done

DATESTRING=$(tail -1 file-list.txt | cut -d'_' -f1 | cut -d':' -f2 | cut -c1-8)
echo ${DATESTRING}

if [ ! -f timetable-${DATESTRING}-loc.ndjson ]; then
    for FILENAME in $(cat file-list.txt | sed 's/.gz$//')
    do
        cat schedule/${FILENAME}-loc 
    done > timetable-${DATESTRING}-loc.ndjson
fi

if [ ! -f timetable-${DATESTRING}.ndjson ]; then
    for FILENAME in $(cat file-list.txt | sed 's/.gz$//')
    do
        cat schedule/${FILENAME}-path 
    done | ./wtt-timetable2.py > timetable-${DATESTRING}.ndjson
fi

echo filter $(date +%Y%m%d)/$(date --date="tomorrow" +%Y%m%d) dates
if [ ! -f wtt-${DATESTRING}-0.ndjson ]; then
    ./filter.sh $(date +%Y%m%d)/$(date --date="tomorrow" +%Y%m%d)
fi
