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

    if [ ! -s schema.jsonl ]; then
        echo Create Solr schema structure
        if [ ! -s id-file.jsonl ]; then
            echo Create id-file.jsonl
            ls storage/*_???.jsonl | parallel ./get-id-file.py > id-file.jsonl
        fi
        echo Created Solr schema structure
        ./get-schema.sh id-file.jsonl > schema.jsonl
        if [ ! -s schema.jsonl ]; then
            echo Error: empty schema.jsonl file
            exit 2
        fi
    fi

    echo Post ${DATESTRING} data to Solr

    for ID in AA BS CR HD PATH TR ZZ
    do
        if [ $(./solr/document-count.sh ${ID} | jq -r '.[]') = "missing" ]; then
            echo Create Solr ${ID} schema
            ./set-schema.sh ${ID} schema.jsonl
            echo Created Solr ${ID} schema
        fi
        if [ $(./solr/document-count.sh ${ID} | jq '.[]') = 0 ]; then
            echo Post ${ID} json files to Solr
            cat storage/${ID}_*.jsonl | parallel --block 8M --pipe --cat ./solr-post.py --core ${ID} {}
            echo Posted ${ID} json files to Solr
        fi
    done

    echo Create PA-${DATESTRING}.jsonl timetable file
    if [ ! -f PA-${DATESTRING}.jsonl ]; then
        < schedule/PA-${DATESTRING}.jsonl ./wtt-timetable5.py > PA-${DATESTRING}.jsonl
    fi

    echo Created PA-${DATESTRING} timetable file
    if [ ! -f PA-id-file.jsonl ]; then
        ./get-id-file.py PA-${DATESTRING}.jsonl > PA-id-file.jsonl
    fi

    if [ ! -f PA-schema.jsonl ]; then
        echo Create PA Solr core
        ./get-schema.sh PA-id-file.jsonl > PA-schema.jsonl
    fi

    if [ $(./solr/document-count.sh PA | jq -r '.[]') = "missing" ]; then
        ./set-schema.sh PA PA-schema.jsonl
    fi

    echo Post Solr PA-${DATESTRING} timetable file
    if [ $(./solr/document-count.sh PA | jq '.[]') = 0 ]; then
        cat PA-${DATESTRING}.jsonl | parallel --block 8M --pipe --cat ./solr-post.py --core PA {}
    fi

fi

echo filter $(date +%Y%m%d)/$(date --date="tomorrow" +%Y%m%d) dates
if [ ! -f wtt-${DATESTRING}-1.ndjson ]; then
    ./filter.sh $(date +%Y%m%d)/$(date --date="tomorrow" +%Y%m%d)
fi
