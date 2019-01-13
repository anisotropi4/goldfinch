#!/bin/sh

FILTER=$1
FILTER=${FILTER:-cat}
XTAG=$2
XTAG=${XTAG:-"_wrapper"}

(echo "<${XTAG}>"; cat - ;echo "</${XTAG}>") | ${FILTER}

