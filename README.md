# py-inspire-ize

A simple python CLI tool to convert bibtex references to the INSPIRE-HEP standard. Checks a .bib file for references not matching the INSPIRE-HEP standard, queries the INSPIRE-HEP database, and replaces the reference if the bibliographic information is found.

Optionally replaces the old citation keys in a given .tex file

## Use

    - Place py-inspire-ize.py in the directory of the .bib file
    - `python py-inspire-ize.py -b (.bib file name)`
    
    ### Optional
    
    - add `-t (.tex file name)` to replace the citation keys in the tex file with the new INSPIRE-HEP keys
    
## Help

    - `python py-inspire-ize.py -h [--help]`


