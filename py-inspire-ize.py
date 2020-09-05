#A simple python CLI tool to convert bibtex references to the INSPIRE-HEP standard. Checks a .bib file for references not matching the INSPIRE-HEP standard, queries the INSPIRE-HEP database, and replaces the reference if the bibliographic information is found.

#Optionally replaces the old citation keys in a given .tex file

import optparse
import os
import bibtexparser
import re
import urllib.request

cwd = os.getcwd()

parser = optparse.OptionParser()

parser.add_option('-b', action="store", default="", help=".bib file")
parser.add_option('-t', action="store", default="", help=".tex file")

options_in, args = parser.parse_args()

options = vars(options_in)

inspire_key_pattern = '[a-z]+:[0-9]{4}[a-z]+'

def is_inspire_id(id):
    """
        checks if the id is in the standard INSPIREHEP format
    """

    return bool(re.match(inspire_key_pattern, id, re.IGNORECASE))

def replace_text_in_file(file_name, old, new):
    """
        replaces text in a file
    """

    data_file = open(file_name, "r")
    data = data_file.read()
    data_file.close()

    new_data = data.replace(old, new)

    data_file = open(file_name, "w")
    data_file.write(new_data)
    data_file.close()

if not os.path.isfile(os.path.join(cwd, options['b'])):
    print('Error : try running with the -b option, or make sure that the input .bib file exists.')
    
else:
    
    bib_file_name = os.path.join(cwd, options['b'])

    # read old .bib file
    old_bib_file = open(bib_file_name, 'r')
    old_bib_database = bibtexparser.bparser.BibTexParser(common_strings=True).parse_file(old_bib_file)
    old_bib_file.close()

    # copy old database
    old_bib_file = open(bib_file_name, 'r')
    new_bib_database = bibtexparser.bparser.BibTexParser(common_strings=True).parse_file(old_bib_file)
    old_bib_file.close()

    old_id_new_id_dict = {}
    remove_entry = []

    num_bad_entries = 0

    for entry in old_bib_database.entries:
        if not is_inspire_id(entry['ID']):
            num_bad_entries += 1

    print('Found '+str(num_bad_entries)+' bad entries in the .bib file.')
    print()
    print('Searching inspire-hep ...')
    print()

    for entry in old_bib_database.entries:

        # check if the entry is in inspire form
        if not is_inspire_id(entry['ID']):

            # check for arxiv or doi information to search inspire with
            entry_data = {}
            try:
                entry_data['doi'] = entry['doi'].split(',')[0].split(' ')[0]
            except:
                pass
            try:
                # remove surrounding link if there, and ignore version number
                entry_data['arxiv'] = entry['eprint'].split('/')[-1].split('v')[0]
            except:
                pass

            if entry_data != {}:

                inspire_search_str = 'https://inspirehep.net/api/'+\
                                    list(entry_data.keys())[0]+'/'+\
                                    entry_data[list(entry_data.keys())[0]]+\
                                    '?format=bibtex'

                try:
                    inspire_data = bibtexparser.loads(urllib.request.urlopen(inspire_search_str).read())
                    new_bib_database.entries.append(inspire_data.entries[0])
                    remove_entry.append(entry)

                    old_id_new_id_dict[entry['ID']] = inspire_data.entries[0]['ID']

                except:

                    print('\tCould not download data from inspire-hep for : ')
                    print()
                    print('\t\t'+entry['title'])
                    print()

            else:
                print('\tNo arXiv or doi number for : ')
                print()
                print('\t\t'+entry['title'])
                print()

    for entry in remove_entry:

        new_bib_database.entries.remove(entry)

    new_bib_file = open(bib_file_name, 'w')
    bibtexparser.dump(new_bib_database, new_bib_file)
    new_bib_file.close()

    if os.path.isfile(os.path.join(cwd, options['t'])):
        print('Replacing citation keys in '+options['t']+'...')

        for key in old_id_new_id_dict:

            replace_text_in_file(
                        os.path.join(cwd, options['t']),
                        key, 
                        old_id_new_id_dict[key]
                    )
