#!/bin/sh

FILES=$@

echo ${FILES} | parallel ./get-schema.py  | unip -r 

