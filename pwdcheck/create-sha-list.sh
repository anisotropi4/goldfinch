#!/bin/sh


if [ ! -f pwned-passwords-sha1-ordered-by-hash-??.txt ]; then
    if [ ! $(ls pwned-passwords-sha1-ordered-by-hash-??.7z 2> /dev/null) ]; then
        echo download SHA-1 ordered by hash from https://haveibeenpwned.com/Passwords
        exit 1
    fi
    p7zip -d pwned-passwords-sha1-ordered-by-hash-??.7z
fi

if [ ! -f pwned-passwords-sha1-ordered-by-hash-??.txt ]; then
    echo 
    echo file decompress failed
    exit 1
fi

if [ ! -d data ]; then
    mkdir data
fi

if [ $(ls data/x?? 2> /dev/null | wc -l) -ne 128 ]; then
    split --number=l/128 pwned-passwords-sha1-ordered-by-hash-??.txt 
    mv x?? data
fi

if [ ! -f sha-list.txt ]; then
   for i in data/x??
   do
       echo ${i}"\t"$(head -1 ${i} | sed 's/^\(....\).*/\1/')"\t"$(tail -1 ${i} | sed 's/^\(....\).*/\1/')
   done > sha-list.txt
fi
