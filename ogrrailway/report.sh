#!/bin/sh
# Set database name and user
ARUSR=railway
ARDBN=ogrrailway

PATH=${PATH}:./bin

export ARUSR ARDBN
. bin/ar-env.sh

< report.aql aqlx.sh | jq -sc '.' > visualisation/raildata.json
