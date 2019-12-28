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
done

DATESTRING=$(tail -1 file-list.txt | cut -d'_' -f1 | cut -d':' -f2 | cut -c1-8)
echo ${DATESTRING}

if [ ! -s timetable-${DATESTRING}.jsonl ]
then
    echo Create timetable for ${DATESTRING}
    echo Split CIF files
    if [ ! -f output/HD_001 ]; then
        if [ -d output ]; then
            rm -rf output
        fi
        mkdir output
        for FILENAME in $(cat file-list.txt | sed 's/.gz$//')
        do
            cat data/${FILENAME}
        done | ./wtt-split.py
    fi

    echo Convert ${DATESTRING} CIF files to jsonl
    if [ ! -s storage/HD_001.jsonl ]; then
        echo Create ${DATESTRING} jsonl files
        ls output/*_??? | parallel ./wtt9.py
    fi
    echo Converted timetable-${DATESTRING} CIF files to jsonl

    echo Create PA schedule PA-${DATESTRING}.jsonl file
    if [ ! -s schedule/PA-${DATESTRING}.jsonl ]; then
        cat storage/PA_???.jsonl > schedule/PA-${DATESTRING}.jsonl
    fi

    for ID in AA BS CR HD PA PATH TR ZZ
    do
        if [ $(./solr/document-count.sh ${ID} | jq -r '.[]') = "missing" ]; then
            echo Create Solr ${ID} core
            ./solr/create-core.sh ${ID}
            echo Created Solr ${ID} core
            echo Create Solr ${ID} schema
            ./set-schema.py storage/${ID}_???.jsonl
            echo Created Solr ${ID} schema
        fi
    done
    for ID in AA BS CR HD PA PATH TR ZZ
    do
        if [ $(./solr/document-count.sh ${ID} | jq '.[]') = 0 ]; then
            echo Post ${ID} json files to Solr
            cat storage/${ID}_*.jsonl | parallel --block 8M --pipe --cat ./solr/post.py --core ${ID} {}
            echo Posted ${ID} json files to Solr
        fi
    done

    echo Create PT-${DATESTRING}-7.jsonl timetable file
    if [ ! -f PT-${DATESTRING}-7.jsonl ]; then
        < schedule/PA-${DATESTRING}.jsonl ./wtt-timetable7.py > PT-${DATESTRING}-7.jsonl
    fi
    echo Created PT-${DATESTRING}-7.jsonl timetable file
    
    ID=PT
    if [ $(./solr/document-count.sh ${ID} | jq -r '.[]') = "missing" ]; then
        echo Create Solr ${ID} core
        ./solr/create-core.sh ${ID}
        echo Created Solr ${ID} core
        echo Create Solr ${ID} schema
        ./set-schema.py PT-${DATESTRING}-7.jsonl
        echo Created Solr ${ID} schema
    fi

    if [ $(./solr/document-count.sh ${ID} | jq '.[]') = 0 ]; then
        echo Post ${ID} json files to Solr
        cat PT-${DATESTRING}-7.jsonl | parallel --block 8M --pipe --cat ./solr/post.py --core ${ID} {}
        echo Posted ${ID} json files to Solr
    fi
fi

exit 7
echo filter $(date +%Y%m%d)/$(date --date="tomorrow" +%Y%m%d) dates
if [ ! -f wtt-${DATESTRING}-1.ndjson ]; then
    ./filter.sh $(date +%Y%m%d)/$(date --date="tomorrow" +%Y%m%d)
fi
