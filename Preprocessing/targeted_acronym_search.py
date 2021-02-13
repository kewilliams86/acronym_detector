# -*- coding: utf-8 -*-
"""
Created on Sat Feb  6 15:35:36 2021

@author: kewilliams86
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 22 12:39:12 2020

@author: kewilliams

quick read of all files looking for a specific acronym for testing
"""

from os import listdir
from os.path import isfile, join
from collections import defaultdict
import timeit
import re

acronymGather = defaultdict(list)

mypath = 'D:/Pubmed/2021_pubmed/pubmed21_text/' # folder path
acronym = 'AGL'
backtrack = str(len(acronym) + 2)


def parseFiles (mypath):
    """
    parameters
    ----------
    path to all pubmed XML files
    
    track info for graphing and printing progress.  Iterate through all files line by line (each
    line is an article) and send line to function
    """

    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))] # all files in directory
    
    articleCount = 0 #count of files
    
    print("Reading files...")
    
    t0 = timeit.default_timer()
    for file in onlyfiles: #iterate through files
        with open(mypath + file) as inFile:
            
            for line in inFile: #call function find phrases in each line
                findPhrases(line)

        articleCount += 1

        if articleCount % 20 == 0: # print progress
            t1 = timeit.default_timer()
            time = t1 - t0
            t0 = timeit.default_timer()
            print(str(articleCount) + ' files read : time ' + str(time))
            
        # if articleCount == 20:
        #     break

    
def findPhrases(line):
    """
    take each line (title and abstract) and associated phrases for acronym
    """

    # acronym containing only letters, numbers, or dash
    # and 10 words before acroynm

    # old (faulty) - '\\b((?:\w+ |\w-){,7})\(([a-zA-Z0-9-]+)\)'
    acronymCheck = '\((?:' + acronym + '|' + acronym + 's)\)'
    check = re.findall(acronymCheck, line)
    if check:
        pattern ='\\b((?:\w+[ -]){,' + backtrack + '})\((?:' + acronym + '|' + acronym + 's)\)'
        search = re.findall(pattern, line) # search[0] - 7 words : search[1] - acronym
    
        for phrase in search:
            phrase = phrase.rstrip().lower()
            print(phrase)
            if phrase in acronymGather:
                acronymGather[phrase] += 1
            else:
                acronymGather[phrase] = 1
            
parseFiles(mypath)
