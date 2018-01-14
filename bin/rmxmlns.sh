#!/bin/sh

EXEDIR=$(dirname $0)

FLIST=`echo $@`
if [ $# = 0 ]; then
    FLIST=-
fi

for i in ${FLIST}
do
  xsltproc ${EXEDIR}/rmxmlns.xslt ${i}
done
