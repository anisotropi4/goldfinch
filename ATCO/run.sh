#!/bin/sh

URL=https://www.gov.uk/government/publications/national-public-transport-access-node-schema/naptan-guide-for-data-managers

curl -s -L -G ${URL} | \
    ./htmltojson.py --depth 4 --stdout | \
    jq -c '.div[]? | select(.class == "govuk-grid-row sidebar-with-body")? | .div[] | select(.class == "main-content-container") | .div[] | select(.class)? | .div | .table[]' | \
    jq -c '[{"th": [.thead.tr.th[].value]}, .tbody.tr[]]' | \
    sed 's/null/""/g' | \
    ./scrape.py


