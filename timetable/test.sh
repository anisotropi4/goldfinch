#!/bin/sh

N=1
M=01

next () {
    N=$((${N} + 1))
    M=$(printf "%02d" ${N})
}

#01
echo Execute timetable test ${M} time match
./wtt-select4.py test/timetable-${M}.ndjson '2019-10-21T11:00:00/2019-10-21T12:00:00' > test/test-${M}.jsonl

diff test/test-${M}.jsonl test/output-${M}.jsonl

#jq -r '.UID' test/output-01.jsonl > test/output-02.jsonl

next

#02
echo Execute timetable test ${M} time/bitmap match

./wtt-select4.py test/timetable-${M}.ndjson '2019-10-17T11:00:00/2019-10-17T12:00:00' > test/test-${M}.jsonl

jq -r '.UID' test/test-${M}.jsonl | sort -u > test/test-${M}.txt

diff test/test-${M}.txt test/output-${M}.txt

next

#03
echo Execute timetable test ${M} bitmap match
./wtt-select4.py test/timetable-${M}.ndjson '2019-10-17T11:00:00/2019-10-17T12:00:00' > test/test-${M}.jsonl

diff test/test-${M}.jsonl test/output-${M}.jsonl

next

#04 
echo Execute timetable test ${M} date range match
./wtt-select4.py test/timetable-${M}.ndjson '2019-10-16/2019-10-17' > test/test-${M}.jsonl

diff test/test-${M}.jsonl test/output-${M}.jsonl

next

#05
echo Execute timetable test ${M} multiple day-range active day match
./wtt-select4.py test/timetable-${M}.ndjson '2019-10-16/2019-10-18' > test/test-${M}.jsonl

diff test/test-${M}.jsonl test/output-${M}.jsonl

#jq -r '.UID' test/output-${M}.jsonl | sort -u > test/output-${M}.txt

next

#06
echo Execute timetable test ${M} multiple day-range and all bitmap match
./wtt-select4.py test/timetable-${M}.ndjson '2019-10-16/2019-10-18' > test/test-${M}.jsonl

jq -r '.UID' test/test-${M}.jsonl | sort -u > test/test-${M}.txt

echo Match date-range
diff test/test-${M}.txt test/output-${M}.txt

echo Match bitmap-range
diff test/test-${M}.jsonl test/output-${M}.jsonl

next

#07
echo Execute timetable test ${M} many-day and bitmap match with varying active wek
./wtt-select4.py test/timetable-${M}.ndjson '2019-10-16/2019-10-22' > test/test-${M}.jsonl

jq -r '.Date' test/test-${M}.jsonl | sort -u > test/test-${M}.txt

echo Match date-range
diff test/test-${M}.txt test/output-${M}.txt

echo Match bitmap-range
diff test/test-${M}.jsonl test/output-${M}.jsonl

next

#08
echo Execute timetable test ${M} bitmap match
./wtt-select4.py test/timetable-${M}.ndjson '2019-10-17/2019-10-22' > test/test-${M}.jsonl

jq -c '{Date, Days}' test/test-${M}.jsonl | sort -u > test/test-${M}.txt

echo Match bitmap/date-range
diff test/test-${M}.txt test/output-${M}.txt

echo Match date range
diff test/test-${M}.jsonl test/output-${M}.jsonl

next

#09
echo Execute timetable test ${M} date-range/time match
./wtt-select4.py test/timetable-${M}.ndjson '2019-10-16T11:00:00/2019-10-18T12:00:00' > test/test-${M}.jsonl

jq -c '{Date, Origin, Terminus, UID}' test/test-${M}.jsonl | sort -n > test/test-${M}.txt

echo Match date-range/time
diff test/test-${M}.txt test/output-${M}.txt

echo Match date-range
diff test/test-${M}.jsonl test/output-${M}.jsonl

next

#10
echo Execute timetable test ${M} overnight
./wtt-select4.py test/timetable-${M}.ndjson '2019-10-16T11:00:00/2019-10-18T12:00:00' > test/test-${M}.jsonl

jq -c '{Date, Origin, Terminus, Days, UID}' test/test-${M}.jsonl | sort -n > test/test-${M}.txt

echo Match date-range/time
diff test/test-${M}.txt test/output-${M}.txt

echo Match date-range
diff test/test-${M}.jsonl test/output-${M}.jsonl

next

#11
echo Execute timetable test ${M} over Weekend 2019-10-19/2019-10-20

./wtt-select4.py test/timetable-${M}.ndjson '2019-10-19/2019-10-20' > test/test-${M}.jsonl

jq -c '{UID, Date, Origin, Duration, Terminus,  Actual}' test/test-${M}.jsonl | sort -n > test/test-${M}.txt

echo Match date-range/time
diff test/test-${M}.txt test/output-${M}.txt

echo Match date-range
diff test/test-${M}.jsonl test/output-${M}.jsonl

next

#12
echo Execute timetable test ${M} over Weekend 2019-10-20/2019-10-21

./wtt-select4.py test/timetable-${M}.ndjson '2019-10-20/2019-10-21' > test/test-${M}.jsonl

jq -c '{UID, Date, Origin, Duration, Terminus,  Actual}' test/test-${M}.jsonl | sort -n > test/test-${M}.txt

echo Match date-range/time
diff test/test-${M}.txt test/output-${M}.txt

echo Match date-range
diff test/test-${M}.jsonl test/output-${M}.jsonl

for P in 11 12
do
    jq -c 'del(.Date)' test/test-${P}.txt > test/test-S${P}.txt
done

echo Match train services

diff test/test-S11.txt test/test-S12.txt

next

#13
echo Execute timetable test ${M} match week over Weekend 2019-10-21/2019-10-22 

./wtt-select4.py test/timetable-${M}.ndjson '2019-10-21/2019-10-22' > test/test-${M}.jsonl

jq -c '{UID, Date, Origin, Duration, Terminus,  Actual}' test/test-${M}.jsonl | sort -n > test/test-${M}.txt

echo Match date-range/time
diff test/test-${M}.txt test/output-${M}.txt

echo Match date-range
diff test/test-${M}.jsonl test/output-${M}.jsonl

next

#14
echo Execute timetable test ${M} match week over Sunday to Monday with timestamp 2019-10-20T14:00:00/2019-10-21T02:00:00

./wtt-select4.py test/timetable-${M}.ndjson '2019-10-20T14:00:00/2019-10-21T02:00:00' > test/test-${M}.jsonl

jq -c '{UID, Date, Origin, Duration, Terminus,  Actual}' test/test-${M}.jsonl | sort -n > test/test-${M}.txt

echo Match date-range/time
diff test/test-${M}.txt test/output-${M}.txt

echo Match date-range
diff test/test-${M}.jsonl test/output-${M}.jsonl

next

#15

echo Execute timetable test ${M} over Weekend 2019-10-20/2019-10-21 with bitmap

./wtt-select4.py test/timetable-${M}.ndjson '2019-10-20/2019-10-21' > test/test-${M}.jsonl

jq -c '{Date, UID, Origin, Duration, Terminus,  Actual}' test/test-${M}.jsonl | sort -n > test/test-${M}.txt

echo Match date-range/time
diff test/test-${M}.txt test/output-${M}.txt

echo Match date-range
diff test/test-${M}.jsonl test/output-${M}.jsonl

next

#16
echo Execute timetable test ${M} over Weekend 2019-10-21/2019-10-22 with bitmap day

./wtt-select4.py test/timetable-${M}.ndjson '2019-10-21/2019-10-22' > test/test-${M}.jsonl

jq -c '{UID, Date, Active, Origin, Duration, Actual}' test/test-${M}.jsonl | sort -n > test/test-${M}.txt

echo Match date-range/time
diff test/test-${M}.txt test/output-${M}.txt

echo Match date-range
diff test/test-${M}.jsonl test/output-${M}.jsonl

next

#17
echo Execute timetable test ${M} over Weekend 2019-10-21/2019-10-22 with weekend bitmap day

./wtt-select4.py test/timetable-${M}.ndjson '2019-10-21/2019-10-22' > test/test-${M}.jsonl

jq -c '{UID, Date, Active, Origin, Duration, Actual}' test/test-${M}.jsonl | sort -n > test/test-${M}.txt

echo Match date-range/time
diff test/test-${M}.txt test/output-${M}.txt

echo Match date-range
diff test/test-${M}.jsonl test/output-${M}.jsonl

next

#18
echo Execute timetable test ${M} over Weekend 2019-10-21/2019-10-22 with bitmap days

./wtt-select4.py test/timetable-${M}.ndjson '2019-10-21/2019-10-22' > test/test-${M}.jsonl

jq -c '{Date, UID, Active, Origin, Duration, Actual}' test/test-${M}.jsonl | sort -n > test/test-${M}.txt

echo Match date-range/time
diff test/test-${M}.txt test/output-${M}.txt

echo Match date-range
diff test/test-${M}.jsonl test/output-${M}.jsonl

next

#19
echo Execute timetable test ${M} over Weekend 2019-10-21T00:00:00/2019-10-21T06:00:00 with bitmap day

./wtt-select4.py test/timetable-${M}.ndjson '2019-10-21T00:00:00/2019-10-21T06:00:00' > test/test-${M}.jsonl

jq -c '{UID, Date, Active, Origin, Duration, Actual}' test/test-${M}.jsonl | sort -n > test/test-${M}.txt

echo Match date-range/time
diff test/test-${M}.txt test/output-${M}.txt

echo Match date-range
diff test/test-${M}.jsonl test/output-${M}.jsonl

next

#20
echo Execute timetable test ${M} over Weekend 2019-10-21T06:00:00/2019-10-21T12:00:00 with bitmap day

./wtt-select4.py test/timetable-${M}.ndjson '2019-10-21T06:00:00/2019-10-21T12:00:00' > test/test-${M}.jsonl

jq -c '{UID, Date, Active, Origin, Duration, Actual}' test/test-${M}.jsonl | sort -n > test/test-${M}.txt

echo Match date-range/time
diff test/test-${M}.txt test/output-${M}.txt

echo Match date-range
diff test/test-${M}.jsonl test/output-${M}.jsonl

next

#21
echo Execute timetable test ${M} over Weekend 2019-10-21T00:00:00/2019-10-21T06:00:00 with all bitmap days

./wtt-select4.py test/timetable-${M}.ndjson '2019-10-21T00:00:00/2019-10-21T06:00:00' > test/test-${M}.jsonl

jq -c '{UID, Date, Active, Origin, Duration, Actual}' test/test-${M}.jsonl | sort -n > test/test-${M}.txt

echo Match date-range/time
diff test/test-${M}.txt test/output-${M}.txt

echo Match date-range
diff test/test-${M}.jsonl test/output-${M}.jsonl
