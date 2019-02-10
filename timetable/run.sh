#!/bin/sh 

URL="https://networkrail.opendata.opentraintimes.com/mirror/schedule/cif/"

if [ ! -f tbody.html ]; then
    curl ${URL} | scrape -e 'tbody' > tbody.html
fi

if [ ! -f full-file-list.txt ]; then
    xml-to-json tbody.html | jq -cr '.tbody[] | .[].td[] | select(.a?.title?) | .a.title' > full-file-list.txt
fi

LINE=$(fgrep -n _full.gz full-file-list.txt | tail -1)

if [ ! -f file-list.txt ]; then
    N=$(echo ${LINE} | cut -d':' -f1)
    tail -n +${N} full-file-list.txt > file-list.txt
fi    

for DIRECTORY in data schedule storage
do
    if [ ! -d ${DIRECTORY} ]; then
        mkdir ${DIRECTORY}
    fi
done

for FILENAME in $(cat file-list.txt | sed 's/.gz$//')
do
    if [ ! -f data/${FILENAME} ]; then
        curl -o data/${FILENAME}.gz ${URL}/${FILENAME}.gz
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

DATESTRING=$(tail -1 file-list.txt | cut -d'_' -f1 | cut -d':' -f2 | cut -c1-8)
echo ${DATESTRING}

if [ ! -f timetable-${DATESTRING}.ndjson ]; then
    cat schedule/*-path | ./wtt-timetable2.py > timetable-${DATESTRING}.ndjson
fi

echo $(date +%Y%m%d)/$(date --date="tomorrow" +%Y%m%d)
if [ ! -f wtt-${DATESTRING}-0.ndjson ]; then

    ./filter.sh $(date +%Y%m%d)/$(date --date="tomorrow" +%Y%m%d)
fi
