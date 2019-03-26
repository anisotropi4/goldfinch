#!/bin/sh

if [ ! -d archive ]; then
    mkdir archive
fi

if [ -f github-markdown.min.css ]; then
    mv github-markdown.min.css archive
fi

wget -nc https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/3.0.1/github-markdown.min.css
