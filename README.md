<<<<<<< HEAD
# acronym_detector
Detect acronyms on PubMed and suggests phrases

preprocessing: see -h/--help for positional arguments in code execution
4 scripts run in order get acronym, phrase, count, and MeSHID into database

pubMedRetrieval.py : (on first run a couple downloads may be unable to complete, may need to reexecute code)
extracts zipped xml data from PubMed ftp server

write_pubmed21_to_text.py :
parses xml files and extracts titles and abstracts and writes to files

detect_acronyms_with_supplemental.py :
detects acronyms matching descriptor or supplemental MeSH terms in previous files
and writes "acronym, phrase, count, meshID" to new file 
REQUIRES: supplemental and descriptor MeSH data (supp2021.xml & desc2021.xml)
from https://www.nlm.nih.gov/databases/download/mesh.html

write_data_to_db.py :
takes data from previous text file and writes to database
REQUIRES: mysql database
=======
# acronym_detector ![pubmed_test](https://github.com/gdancik/acronym_detector/workflows/pubmed_test/badge.svg)
Detect acronyms on PubMed and suggest phrases
>>>>>>> 42ef86b6522ee323d98c9b7623032fe4c924db03
