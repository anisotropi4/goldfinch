# Markdown .md and .yaml helper and render scripts
## Overview
A set of python and shell scripts to locally process and convert between [Markdown](https://daringfireball.net/projects/markdown) `.md`, `.yaml` and `.html` format files using:
* [mistune](https://github.com/lepture/mistune) python markdown down parser
* [jinja2](http://jinja.pocoo.org/) python html template engine
* [wget](https://www.gnu.org/software/wget/) file retrieval package
* [github-markdown-css](https://github.com/sindresorhus/github-markdown-css) css style sheet


 The motivation for this is try and reduce my github edits (currently about 50%) being to fix typo and rendering in markdown README.md files

## Pre-requisites and setup:
The scripts assume the following:

1 The `mistune` and `jinja2` python libraries are installed


2 Download the `github-markdown.min.css` style sheet using the `update.sh` script:

    $ ./update.sh

Previous `.css` files are moved to the `archive` folder

## Execution:
Run the `output-html.py` file from the command line to convert a markdown file in `.md` or `.yaml` and output the corresponding html file, default name `index.html`

Example, create a `README.md` markdown and `README.html` html files in the local directory:
```
$ ./output-html.py --yaml --dumpmd README.yaml readme.html```

Options:
- `--yaml` process a yaml-format markdown file
- `--dumpmd` dump the the markdown from a yaml-format file, default-name `dump.md`
