#!/bin/sh

echo Count the number of times a password is in a list of hacked sha1sum hash keys 
echo type in password:
while read TEXT
do
    KEY=$(echo -n ${TEXT} | sed 's/[\n\r]//g' | sha1sum | awk '{print $1}' | tr '[:lower:]' '[:upper:]')

    N=$(echo ${KEY} | cut -c1-4)
    
    FILES=$(awk '($2 <= "'${N}'" && $3 >= "'${N}'") { print $1 }' sha-list.txt)

    for FILE in ${FILES}
    do
        SEARCH=$(fgrep ${KEY} data/${FILE} || echo ${KEY}:"not found") 
        echo ${SEARCH} | sed 's/:/ count /'
    done
    echo type in password:
done
