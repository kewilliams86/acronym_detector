#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 22 12:39:12 2020

@author: kewilliams

Read XML file with descriptor/supplemental terms.  Read all pubmed text files.  Extract acronyms and
associated phrases.  Link acronyms with phrases in the descriptor file.  Write the acronym, phrase, # of occurances, 
and the MESH ID if the phrase satisfies a set filtering threshold.

usage:
    detect_acronyms_with_supplemental.py supplementalFile descriptorFile pubmedFilesPath outputFile 
        [threshold (default = 100))]

"""

from os import listdir
from os.path import isfile, join
from collections import defaultdict
import timeit
import xml.etree.ElementTree as ET
import sys
import argparse
import re


# define dictionaries
termDict = defaultdict(list)
matchDict = defaultdict(set)
phraseDict = defaultdict(list)
phraseAcronymDict = defaultdict(set)
phraseAcronymDictCopy = defaultdict(set)
testSingle = defaultdict(list)
phraseDictCopy = defaultdict(list)


def xmlParse(inputFile, fileType):
    """

    Parameters
    ----------
    inputFile : XML file (desc2020.xml)
    fileType : descriptor or supplemental
    
    Returns
    -------
    TermDict
        Dictionary with phrases as key, MeSH ID as value.

    Read XML file and extract MeSH ID and the associated phrases

    """
    
      
    tree = ET.parse(inputFile)
    
    if fileType == "descriptor":
        print("Parsing descriptor XML file...")  
        recordString = "DescriptorRecord"
        recordUIString = "DescriptorUI"
        
    elif fileType == "supplemental":
        print("Parsing supplemental XML file...")  
        recordString = "SupplementalRecord"
        recordUIString = "SupplementalRecordUI"
    
    for record in tree.iter(recordString):
        descID = record.find(recordUIString).text
        concepts = record.find("ConceptList") #terms located in conceptList branch
        for concept in concepts:
            termList = concept.findall("TermList") #list of all TermList
            for term in termList:
                for i in range(len(term)): #iterate through all terms, write to file
                    x = term[i].find('String').text
                    if ',' not in x and '(' not in x:
                        termDict[x.lower()] = descID


def parseFiles (mypath):
    """

    parameters
    ----------
    path to all pubmed text files
    
    Iterate through all files line by line (each
    line is an article) and send line to function extracting acronyms and phrases

    """

    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))] # all files in directory
    
    articleCount = 0 #count of files
    
    print("Reading files...")
    
    if not mypath.endswith('/'):
        mypath += '/'
    
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
            
        # if articleCount == 100:
        #     break

    
def findPhrases(line):
    """
    take each line (title and abstract) and extract acronyms and associated phrases
    
    Parameters
    ----------
    line : String

    Returns
    -------
    None : Added to phrase dictionary without return

    """

    # acronym containing only letters, numbers, or dash
    # and 7 words before acroynm

    pattern ='\\b((?:\w+[ -]){,7})\(([a-zA-Z0-9-]+)\)'
    search = re.findall(pattern, line) # search[0] - 7 words : search[1] - acronym
    # acronym starts with capital or lowercase letter and followed by only lowercase
    # should detect full words over acronyms
    acronymCheckPattern = '\\b[A-Za-z](?:[a-z]+)\\b'
    
    for item in search:

        phrase = item[0]
        acronym = item[1]
            
        if acronym.endswith('s'): # detect / remove plurals
            acronym = acronym[:-1]
            
        ####### threshold for length of acronym and remove words
        if len(acronym) >= 3 and not re.findall(acronymCheckPattern, acronym):

            phrase = getPhraseRegex(phrase, acronym) # find phrase for acronym
            
            if phrase: # if phrase returned after regex search
                phrase = phrase.lower().rstrip()
                acronym = acronym.upper()
                if len(phrase) > 2:
                           
                    skipTermSet = {'cells', 'acid'} # skip specific single words
                    if phrase in termDict and phrase not in skipTermSet: # if phrase a MeSH term
                        phraseAcronymDict[phrase].add(acronym) # add to set of acronyms for the phrase
                        phraseToDict(phrase, acronym) # modify phraseDict
                        
                        
def getPhraseRegex (phrase, acronym):
    """
    performs two regex on inputs: (must use escape character on \b for regex)
        
    firstLetterPattern = '\\b([' + upperFirst + lowerFirst + ']\w*)\\b' :
    Takes uppercase and lowercase first letter of the acronym and retrieves all
    words in the parameter phrase starting with that letter
    
    phrasePattern = '(\\b' + beginTerm + '[ -](?:\w+[ -]){,' + backtrack + '}$)' :
    Go from end of phrase String backwards (length of acronym + 2) and get beginning
    term and everything after. [ -] captures both hyphenated words and words separated
    by whitespace

    Parameters
    ----------
    phrase : String
        7 words preceeding detected acronym
    acronym : String
        detected acronym in text

    Returns
    -------
    String
        phrase that matches acronym

    """
    # get upper and lowercase first letter of acronym for regex pattern
    upperFirst = acronym[0].upper()
    lowerFirst = acronym[0].lower()
    
    # capture all words starting with the first letter of acronym
    # '\\b([Ff]\w*)\\b'
    firstLetterPattern = '\\b([' + upperFirst + lowerFirst + ']\w*)\\b'
    terms = re.findall(firstLetterPattern, phrase)
    
    if terms:

        # get count of first letter in letter (i.e. AARP = 2, ART = 1 etc)
        index = acronym.lower().count(acronym[0].lower())
        
        # # of terms found minus number of instances of words starting with letter
        try:
            beginTerm = terms[len(terms) - index]
        except:
            beginTerm = terms[0]
                
        backtrack = str(len(acronym) + 2) # number of words to backtrack
        # '(\\bTERM(?:\w+[ -]){,BACKTRACK})
        # find terms
        
        # old - captures begin term and back track amount of words after
        # does not start at end of string, $ should force this
        phrasePattern = '(\\b' + beginTerm + '[ -](?:\w+[ -]){,' + backtrack + '}$)'
        # returns list with 1 index if found
        try: # find phrase
            phrase = re.findall(phrasePattern, phrase)[0]
        except: # if word out of range of backtrack
            return None

        return phrase[:-1] # remove whitespace at end of regex
    
    return None


#modify phraseDict
def phraseToDict(phrase, acronym):
    """
    Parameters
    ----------
    phrase : specific phrase
    acronym : acronym
    
    update phraseDict.  If acronym already in phraseDict keys, increase count if phrase already present, 
    otherwise add new phrase to acronym key and set count to one.  If new acronym, add key to dictionary 
    and add phrase with count 1
    """
    if acronym in phraseDict:
        found = False
        for i in range(0, len(phraseDict[acronym])):
            if phraseDict[acronym][i][0] == phrase:
                phraseDict[acronym][i][1] += 1
                found = True
                break
        if found != True:
            phraseDict[acronym].append([phrase, 1])
    else:
        phraseDict[acronym].append([phrase, 1])


# may not want to perform this
def reduceAcronym():
    """
    keep only the one most commonly used acronym for each phrase, remove potential
    mistakes in articles or uncommonly used variations

    """
    

    for key in phraseAcronymDict:
        vals = []
        count = 0
        keep = ''
        
        # may be redundant
        # possibly if len(phraseAcronymDict[key]) == 1: continue
        if len(phraseAcronymDict[key]) == 1: # if only one acronym keep
            for item in phraseAcronymDict[key]:
                keep = item
            phraseAcronymDict[key] = keep            
        
        else: # keep acronym with highest count
            for val in phraseAcronymDict[key]:
                for i in phraseDict[val]:
                    if i[0] == key:
                        vals.append([val, i[1]])
                for item in vals:
                    if item[1] > count:
                        count = item[1]
                        keep = item[0] 
                phraseAcronymDict[key] = keep

        
def joinSingleWordPhrase():
    """
    Some single words are matched to an acronym that are likely to be a portion of a
    longer phrase.  If 'HGH' gets matched to 'hormone' and 'human growth hormone',
    combine count and replace 'hormone' with 'human growth hormone'

    Returns
    -------
    None.

    """
    
    
    for key in phraseDict:
        if len(phraseDict[key]) > 1: # if more than one phrase for key
            removeItem = [] # potential value to remove
            removeFlag = False # flag if found
            temp = phraseDict[key]
            # iterate through list of words with nested for loop
            # if word is in phrase combine count and remove single word
            for i in range(len(temp)):
                for j in range(len(temp)):
                    if i == j: # if indices match skip comparison
                        continue
                    else:
                        # single word (only letters) and in larger phrase
                        if temp[i][0].isalpha() and temp[i][0] in temp[j][0]:
                            temp[j][1] += temp[i][1] # add single word count to phrase
                            removeItem.append(temp[i]) # single word to remove
                            removeFlag = True # set flag to true             
                            break
            if removeFlag: # if item(s) found to be removed
                for item in removeItem:
                    temp.remove(item)
                phraseDict[key] = temp # update phraseDict[key]
        

def reducePhrases():
    """
    MeSH IDs contain variations on the phrase spelling, wording, etc while still having the same meaning.
    Variations on phrases that have identical acronyms and MeSH IDs are combined with the most common variation
    being the end version
    """
    
    keySet= {key for key in phraseDict} #set of acronyms
    print("Reducing phrases...")
    for key in keySet:
        phrases = phraseDict[key] #list of phrases for an acronym
        tempDict = defaultdict(list) 
        for phrase in phrases:
            tempDict[termDict[phrase[0]]].append(phrase) #temp dictionary with MeSH ID as key, phrases linked to MeSH as val

        for item in tempDict: #iterate through tempDict
            if len(tempDict[item]) > 1:
                maxVal = (max([(v,i) for i,v in enumerate(tempDict[item])])) #identify phrase with highest count
                total = 0
                for val in tempDict[item]:
                    total += val[1] # add up count of all items per MeSH ID
                tempDict[item] = [[maxVal[0][0], total]] # replace duplicate phrases for a MeSH term w/ the most common one and total count
        
        phraseDict[key] = [tempDict[k][0] for k in tempDict] # overwrite list of phrases linked to acronym
    filterPhrases()
         

# sort phraseDict by count
# retain only top 10 phrases and remove all phrases occuring fewer than threshold
def filterPhrases():
    """
    sort phraseDict by count, retain only top 10 phrases and remove all phrases occuring fewer than 100 times
    remove acronyms that do not have any phrases that satisfy the threshold
    """
    print('Filtering phrases...')
    removeKeySet = set()
    for key in phraseDict:
        temp = phraseDict[key]
        temp.sort(key = lambda temp : temp[1], reverse = True) # reverse sort
        temp = [item for item in temp if item[1] >= threshold] # retain phrases occuring more than 100 times
        if temp: # if items in temp
            phraseDict[key] = temp[:10] # add only top 10 phrases
        else:
            removeKeySet.add(key)
    for key in removeKeySet:
        del phraseDict[key]
        
        
def findMatches():
    """
    create dictionary for matches of phrases linked to acronyms and terms    
    phrase is key for both termDict and phraseAcronymDict, if keys match, values paired in
    matchDict with key being acronym and value being MeSHID
    """
    print('Finding matches...')
    for key in termDict:
        if key.lower() in phraseAcronymDict: #
            matchDict[phraseAcronymDict[key]].add(termDict[key])
        
        
def writeToPhraseFile(outFile):
    """
    write acronym /t phrase /t count /t MeSHID /n to file
    """
    with open(outFile, 'w') as writeFile:
        for key in phraseDict:
            for phrase in phraseDict[key]:
                writeFile.write(key + '\t' + phrase[0] + '\t' + str(phrase[1]) + '\t' + termDict[phrase[0]] + '\n')
            

# main program
# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser(description='Extract article information from PubMed xml files')
ap.add_argument("supplementalFile", help = "xml file with supplemental terms")
ap.add_argument("descriptorFile", help = "xml file with descriptor terms")
ap.add_argument("pubmedFilesPath", help = "folder path containing pubmed text")
ap.add_argument("outputFile", help = "file to write data to")
ap.add_argument("threshold", nargs='?', type = int, help = "threshold for count of phrases to be kept (default 100)", default = 100)

# print help if no arguments are provided
if len(sys.argv)==1:
    ap.print_help(sys.stderr)
    sys.exit(1)

args = vars(ap.parse_args())

suppFile = args['supplementalFile']
descFile = args['descriptorFile']
mypath = args['pubmedFilesPath']
outFile = args['outputFile']
threshold = args['threshold']

xmlParse(descFile, 'descriptor')
xmlParse(suppFile, 'supplemental')
parseFiles(mypath)

reduceAcronym()
joinSingleWordPhrase()
reducePhrases()
findMatches()
writeToPhraseFile(outFile)
