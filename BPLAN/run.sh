#!/bin/sh

if [ ! -s Geography_current.txt ]; then
    URL=https://wiki.openraildata.com/images/0/00
    FILENAME=Geography_20201213_to_20210515_from_20201019.txt

    curl ${URL}/${FILENAME}.gz -o Geography_current.txt.gz
    gzip -d Geography_current.txt.gz
fi

FILENAME=output-stations.json
if [ ! -s ${FILENAME} ]; then
    URL=https://gist.githubusercontent.com/anisotropi4/54c29e6e6192cf758e12279e1981e889/raw/ceb3b8ae27511de7a0bbb2028055ad5dc8de20da
    curl ${URL}/${FILENAME} -o ${FILENAME}
fi

./bplan-split4.py
