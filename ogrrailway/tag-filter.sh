#!/bin/sh
jq -c '(. | del(.tag)) as $this | if .tag then ($this + ({tags: [([.tag?] | flatten | .[] | {(.k): .v})] | add})) else $this end'
