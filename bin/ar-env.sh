#!/bin/sh

DEBUG=$-
set +x
# set arangodb connection string shell variables
# username      ARUSR default root
# password      ARPWD default lookup as key:pair from ~/.aqlpass file
# server-name   ARSVR default ar-server
# database-name ARDBN default testdb

# determine if node is installed
NODE=$(which node)
NODE=${NODE:-$(which nodejs)}

# Stop unless ~/.aqlpass file permissions are 0600
if [ "x"$(stat -c %a ${HOME}/.aqlpass) != "x600" ]
then
    echo "Set permission on ~/.pgpass to 0600 or nosuch file"
    exit 1
fi

ARUSR=${ARUSR:-aruser}
ARPWD=${ARPWD:-$(jq -r '.'${ARUSR}' | select(. != null)' ${HOME}/.aqlpass)}
if [ "x"${ARPWD} = "x" ]
then
    echo "No password set in the .aqlpass file for user ${ARUSR}"
    exit 1
fi

ARSVR=${ARSVR:-ar-server}
ARDBN=${ARDBN:-testdb}
ARPASSWORD=$(jq -r '.root | select(. != null)' ${HOME}/.aqlpass)
ARPASSWORD=${ARPASSWORD:-'pleasechangeme'}

if [ x"$DEBUG" != x ] && [ $(expr index "$DEBUG" 'x') != 0 ]
then
    set -x
fi

