#!/bin/sh 
ARDBN=fullrailway
. ${HOME}/bin/ar-env.sh

foxx-manager --server.database ${ARDBN} --server.endpoint "tcp://ar-server:8529" --server.password "${ARPASSWORD}" uninstall /volpe
foxx-manager --server.database fullrailway --server.endpoint "tcp://ar-server:8529" --server.password "${ARPASSWORD}" install . /volpe

