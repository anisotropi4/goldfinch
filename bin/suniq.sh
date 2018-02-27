#!/bin/sh
# suniq.sh: A pipeline script that sorts, counts, orders and puts the count as the final tab-delimited column

sort - | uniq -c | sort -rn | sed 's/^ *\([0-9][0-9]*\) \(.*\)$/\2\t\1/'
