#!/bin/sh
# set arangodb connection string shell variables
# username      ARUSR default root
# password      ARPWD default lookup as key:pair from .aqlpass file
# server-name   ARSVR default ar-server
# database-name ARDBN default _system

ARUSR=${ARUSER:-root}
ARPWD=${ARPWD:-$(jq -r .${ARUSR} ${HOME}/.aqlpass)}
ARSVR=${ARSVR:-ar-server}
ARDBN=${ARDBN:-_system}


