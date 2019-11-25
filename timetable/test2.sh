#!/bin/sh

N=1
M=01

next () {
    N=$((${N} + 1))
    M=$(printf "%02d" ${N})
}

load () {
    ./set-schema.sh PA PA-schema.jsonl > /dev/null
    ./solr-post.py --core PA test2/timetable-${M}.ndjson
}

update () {
    echo ${M}
    cat test2/test-A${M}.jsonl | \
        jq --sort-keys -c 'del(.id) | del(.End_Date) | del(.Start_Date) | del(.Date_From) | del(.Date_To)' | \
        sed 's/T00:00:00Z//' > test2/test-${M}.jsonl
}

#01
echo Execute timetable test ${M} time match

load
./wtt-select5.py '2019-10-21T11:00:00/2019-10-21T12:00:00' > test2/test-A${M}.jsonl
update
diff test2/test-${M}.jsonl test2/output-${M}.jsonl
next

#jq -r '.UID' test2/output-01.jsonl > test2/output-02.jsonl

#02
echo Execute timetable test ${M} time/bitmap match

load
./wtt-select5.py '2019-10-17T11:00:00/2019-10-17T12:00:00' > test2/test-A${M}.jsonl
update
jq -r '.UID' test2/test-${M}.jsonl | sort -u > test2/test-${M}.txt
diff test2/test-${M}.txt test2/output-${M}.txt
next

#03
echo Execute timetable test ${M} bitmap match

load
./wtt-select5.py '2019-10-17T11:00:00/2019-10-17T12:00:00' > test2/test-A${M}.jsonl
update
diff test2/test-${M}.jsonl test2/output-${M}.jsonl
next

#04 
echo Execute timetable test ${M} date range match
load
./wtt-select5.py '2019-10-16/2019-10-17' > test2/test-A${M}.jsonl
update
diff test2/test-${M}.jsonl test2/output-${M}.jsonl
next

#05
echo Execute timetable test ${M} multiple day-range active day match
load
./wtt-select5.py '2019-10-16/2019-10-18' > test2/test-A${M}.jsonl
update
diff test2/test-${M}.jsonl test2/output-${M}.jsonl
next
#jq -r '.UID' test2/output-${M}.jsonl | sort -u > test2/output-${M}.txt

#06
echo Execute timetable test ${M} multiple day-range and all bitmap match
load
./wtt-select5.py '2019-10-16/2019-10-18' > test2/test-A${M}.jsonl
update
jq -r '.UID' test2/test-${M}.jsonl | sort -u > test2/test-${M}.txt

echo Match date-range
diff test2/test-${M}.txt test2/output-${M}.txt

echo Match bitmap-range
diff test2/test-${M}.jsonl test2/output-${M}.jsonl

next

#07
echo Execute timetable test ${M} many-day and bitmap match with varying active week
load
./wtt-select5.py '2019-10-16/2019-10-22' > test2/test-A${M}.jsonl
update
jq -r '.Date' test2/test-${M}.jsonl | sort -u > test2/test-${M}.txt

echo Match date-range
diff test2/test-${M}.txt test2/output-${M}.txt

echo Match bitmap-range
diff test2/test-${M}.jsonl test2/output-${M}.jsonl

next

#08
echo Execute timetable test ${M} bitmap match
load
./wtt-select5.py '2019-10-17/2019-10-22' > test2/test-A${M}.jsonl
update
jq -c '{Date, Days}' test2/test-${M}.jsonl | sort -u > test2/test-${M}.txt

echo Match bitmap/date-range
diff test2/test-${M}.txt test2/output-${M}.txt

echo Match date range
diff test2/test-${M}.jsonl test2/output-${M}.jsonl

next

#09
echo Execute timetable test ${M} date-range/time match
load
./wtt-select5.py '2019-10-16T11:00:00/2019-10-18T12:00:00' > test2/test-A${M}.jsonl
update
jq -c '{Date, Origin, Terminus, UID}' test2/test-${M}.jsonl | sort -n > test2/test-${M}.txt

echo Match date-range/time
diff test2/test-${M}.txt test2/output-${M}.txt

echo Match date-range
diff test2/test-${M}.jsonl test2/output-${M}.jsonl

next

#10
echo Execute timetable test ${M} overnight
load
./wtt-select5.py '2019-10-16T11:00:00/2019-10-18T12:00:00' > test2/test-A${M}.jsonl
update
jq -c '{Date, Origin, Terminus, Days, UID}' test2/test-${M}.jsonl | sort -n > test2/test-${M}.txt

echo Match date-range/time
diff test2/test-${M}.txt test2/output-${M}.txt

echo Match date-range
diff test2/test-${M}.jsonl test2/output-${M}.jsonl

next

#11
echo Execute timetable test ${M} over Weekend 2019-10-19/2019-10-20
load
./wtt-select5.py '2019-10-19/2019-10-20' > test2/test-A${M}.jsonl
update
jq -c '{UID, Date, Origin, Duration, Terminus,  Actual}' test2/test-${M}.jsonl | sort -n > test2/test-${M}.txt

echo Match date-range/time
diff test2/test-${M}.txt test2/output-${M}.txt

echo Match date-range
diff test2/test-${M}.jsonl test2/output-${M}.jsonl

next

#12
echo Execute timetable test ${M} over Weekend 2019-10-20/2019-10-21
load
./wtt-select5.py '2019-10-20/2019-10-21' > test2/test-A${M}.jsonl
update
jq -c '{UID, Date, Origin, Duration, Terminus,  Actual}' test2/test-${M}.jsonl | sort -n > test2/test-${M}.txt

echo Match date-range/time
diff test2/test-${M}.txt test2/output-${M}.txt

echo Match date-range
diff test2/test-${M}.jsonl test2/output-${M}.jsonl

for P in 11 12
do
    jq -c 'del(.Date)' test2/test-${P}.txt > test2/test-S${P}.txt
done

echo Match train services

diff test2/test-S11.txt test2/test-S12.txt

next

#13
echo Execute timetable test ${M} match week over Weekend 2019-10-21/2019-10-22 
load
./wtt-select5.py '2019-10-21/2019-10-22' > test2/test-A${M}.jsonl
update
jq -c '{UID, Date, Origin, Duration, Terminus,  Actual}' test2/test-${M}.jsonl | sort -n > test2/test-${M}.txt

echo Match date-range/time
diff test2/test-${M}.txt test2/output-${M}.txt

echo Match date-range
diff test2/test-${M}.jsonl test2/output-${M}.jsonl

next

#14
echo Execute timetable test ${M} match week over Sunday to Monday with timestamp 2019-10-20T14:00:00/2019-10-21T02:00:00
load
./wtt-select5.py '2019-10-20T14:00:00/2019-10-21T02:00:00' > test2/test-A${M}.jsonl
update
jq -c '{UID, Date, Origin, Duration, Terminus,  Actual}' test2/test-${M}.jsonl | sort -n > test2/test-${M}.txt

echo Match date-range/time
diff test2/test-${M}.txt test2/output-${M}.txt

echo Match date-range
diff test2/test-${M}.jsonl test2/output-${M}.jsonl

next

#15

echo Execute timetable test ${M} over Weekend 2019-10-20/2019-10-21 with bitmap
load
./wtt-select5.py '2019-10-20/2019-10-21' > test2/test-A${M}.jsonl
update

jq -c '{Date, UID, Origin, Duration, Terminus,  Actual}' test2/test-${M}.jsonl | sort -n > test2/test-${M}.txt

echo Match date-range/time
diff test2/test-${M}.txt test2/output-${M}.txt

echo Match date-range
diff test2/test-${M}.jsonl test2/output-${M}.jsonl

next

#16
echo Execute timetable test ${M} over Weekend 2019-10-21/2019-10-22 with bitmap day
load
./wtt-select5.py '2019-10-21/2019-10-22' > test2/test-A${M}.jsonl
update
jq -c '{UID, Date, Active, Origin, Duration, Actual}' test2/test-${M}.jsonl | sort -n > test2/test-${M}.txt

echo Match date-range/time
diff test2/test-${M}.txt test2/output-${M}.txt

echo Match date-range
diff test2/test-${M}.jsonl test2/output-${M}.jsonl

next

#17
echo Execute timetable test ${M} over Weekend 2019-10-21/2019-10-22 with weekend bitmap day
load
./wtt-select5.py '2019-10-21/2019-10-22' > test2/test-A${M}.jsonl
update
jq -c '{UID, Date, Active, Origin, Duration, Actual}' test2/test-${M}.jsonl | sort -n > test2/test-${M}.txt

echo Match date-range/time
diff test2/test-${M}.txt test2/output-${M}.txt

echo Match date-range
diff test2/test-${M}.jsonl test2/output-${M}.jsonl

next

#18
echo Execute timetable test ${M} over Weekend 2019-10-21/2019-10-22 with bitmap days
load
./wtt-select5.py '2019-10-21/2019-10-22' > test2/test-A${M}.jsonl
update
jq -c '{Date, UID, Active, Origin, Duration, Actual}' test2/test-${M}.jsonl | sort -n > test2/test-${M}.txt

echo Match date-range/time
diff test2/test-${M}.txt test2/output-${M}.txt

echo Match date-range
diff test2/test-${M}.jsonl test2/output-${M}.jsonl

next

#19
echo Execute timetable test ${M} over Weekend 2019-10-21T00:00:00/2019-10-21T06:00:00 with bitmap day
load
./wtt-select5.py '2019-10-21T00:00:00/2019-10-21T06:00:00' > test2/test-A${M}.jsonl
update
jq -c '{UID, Date, Active, Origin, Duration, Actual}' test2/test-${M}.jsonl | sort -n > test2/test-${M}.txt

echo Match date-range/time
diff test2/test-${M}.txt test2/output-${M}.txt

echo Match date-range
diff test2/test-${M}.jsonl test2/output-${M}.jsonl

next

#20
echo Execute timetable test ${M} over Weekend 2019-10-21T06:00:00/2019-10-21T12:00:00 with bitmap day
load
./wtt-select5.py '2019-10-21T06:00:00/2019-10-21T12:00:00' > test2/test-A${M}.jsonl
update
jq -c '{UID, Date, Active, Origin, Duration, Actual}' test2/test-${M}.jsonl | sort -n > test2/test-${M}.txt

echo Match date-range/time
diff test2/test-${M}.txt test2/output-${M}.txt

echo Match date-range
diff test2/test-${M}.jsonl test2/output-${M}.jsonl

next

#21
echo Execute timetable test ${M} over Weekend 2019-10-21T00:00:00/2019-10-21T06:00:00 with all bitmap days
load
./wtt-select5.py '2019-10-21T00:00:00/2019-10-21T06:00:00' > test2/test-A${M}.jsonl
update
jq -c '{UID, Date, Active, Origin, Duration, Actual}' test2/test-${M}.jsonl | sort -n > test2/test-${M}.txt

echo Match date-range/time
diff test2/test-${M}.txt test2/output-${M}.txt

echo Match date-range
diff test2/test-${M}.jsonl test2/output-${M}.jsonl
