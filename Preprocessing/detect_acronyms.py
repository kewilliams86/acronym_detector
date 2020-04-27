#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 22 12:39:12 2020

@author: kewilliams

Read XML file with descriptor/supplemental terms.  Read all pubmed XML files.  Extract acronyms and
associated phrases.  Link acronyms with phrases in the descriptor file.  Write the acronym, phrase, # of occurances, 
and the MESH ID if the phrase satisfies a set filtering threshold.
"""

# import operator
import string
from nltk.corpus import stopwords
from os import listdir
from os.path import isfile, join
from collections import defaultdict
import timeit
import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET
import sys
import argparse


punct = string.punctuation.replace('-', '').replace('\'', '')
stopWordSet = {word for word in stopwords.words('english')} # set of stop words
skipStopSet = {'with', 'the', 'a', 'an', 'of', 'and'} #words not part of acronym when backtracking

# define dictionaries
termDict = {}
matchDict = defaultdict(set)
phraseDict = defaultdict(list)
phraseAcronymDict = defaultdict(set)


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
    
    print("Parsing XML file...")    
    tree = ET.parse(inputFile)
    
    if fileType == "descriptor":
        recordString = "DescriptorRecord"
        recordUIString = "DescriptorUI"
        
    elif fileType == "supplementary":
        recordString = "SupplementalRecord"
        recordUIString = "SupplementalRecordUI"
    
    for record in tree.getiterator(recordString):
        descID = record.find(recordUIString).text
        concepts = record.find("ConceptList") #terms located in conceptList branch
        for concept in concepts:
            termList = concept.findall("TermList") #list of all TermList
            for term in termList:
                for i in range(len(term)): #iterate through all terms, write to file
                    x = term[i].find('String').text
                    if ',' not in x and '-' not in x:
                        termDict[term[i].find("String").text.lower()] = descID
    return termDict

#modify phraseDict
def phraseToDict(phrase, acronym):
    """
    Parameters
    ----------
    phrase : specific phrase
    acronym : acronym
    
    update phraseDict.  If acronym already in phraseDict keys, increase count of phrase if already present, otherwise
    add new phrase to acronym key and set count to one.  If new acronym, add key to dictionary and add phrase with count 1
    to value
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
        
    
    
def findPhrases(line):
    """
    take each line (title and abstract) and extract acronyms and associated phrases
    """
       
    data = line.split('\t') #split list into list of title and abstract
    
    title = data[0]
    abstract = data[1]
    
    # pad parantheses with whitespace and create list of words.
    title = eval(title).translate(str.maketrans({key: " {0} ".format(key) for key in punct})).split()
    abstract = eval(abstract).translate(str.maketrans({key: " {0} ".format(key) for key in punct})).split()
    
    text = [*title, *abstract]

    threshold = 7 #number of words to capture before acronym     
    start = 0
    end = 0
    index = 0
    
    for item in text:
        if item == '(': # start point for potential acronym
            start = index + 1
        elif item == ')': # end point for potential acronym
            end = index
            # only one word, only capital letters, more than 2 letters
            if end - start == 1 and text[start:end][0].isupper() and len(text[start:end][0]) > 2:
                
                acronym = text[start : end] # get acronym
                
                # start at index zero or threshold
                if start - threshold < 0:
                    phrase = text[0 : start - 1]
                else:
                    phrase = text[start - threshold : start - 1] # get words before acronym
                
                addPhrase = []
                start = False #track start point for phrase
                duplicate = acronym[0][0] in acronym[0][1:] #check if first letter is repeated
                
                for item in phrase:
                    item = item.lower()
                    # find first word that matches the first letter in the acronym
                    if item in punct or item in stopWordSet: # reset phrase capture if stopword or punctuation
                        addPhrase = []
                        start = False
                    #if owrd begins with first acronym letter and word not a stopword being skipped
                    elif item.lower().startswith(acronym[0][0:1].lower()) and item.lower() not in skipStopSet:
                        if not duplicate: #no repeated first letter in acronym
                            addPhrase = [item] # set word to addphrase
                        else:    
                            addPhrase.append(item) #append due to multiple occurances of letter
                        start = True #set start point 
                    elif start == True: # if start point
                        addPhrase.append(item)

                #create new list replacing '-' with ' '
                addPhrase = (' ').join(addPhrase).replace('-', ' ').split()
                if len(addPhrase) <= 1: # skip if phrase one word
                    continue
                
                if duplicate: # if multiple occurances of first letter for acronyms
                    firstLetter = acronym[0][0]
                    count = acronym[0].count(firstLetter) # count number of occurances (ex AARP count = 2 (A))

                    for i in range(len(addPhrase) - 1, 0, -1): # reverse for loop
                        if addPhrase[i].lower().startswith(firstLetter.lower()) and addPhrase[i].lower() not in skipStopSet:
                            count -= 1
                            if count <= 0: # when number of letters occurs count times break
                                addPhrase = addPhrase[i:len(addPhrase)]
                                break
                
                phrase = (' ').join(addPhrase)
                # add acronym and all words after the first letter
                
                if phrase in termDict: # if phrase a MeSH term
                    
                    phraseAcronymDict[phrase].add(acronym[0]) # add to set of acronyms for the phrase
                    phraseToDict(phrase, acronym[0]) # modify phraseDict
                    
        index += 1
    
    
def parseFiles (mypath):
    """
    parameters
    ----------
    path to all pubmed XML files
    
    track info for graphing and printing progress.  Iterate through all files line by line (each
    line is an article) and send line to function extracted acronyms and phrases
    """

    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))] # all files in directory
        
    for word in skipStopSet: # set of stopword exluding specific ones (i.e. and, to, ...)
        stopWordSet.remove(word)
    
    articleCount = 0 #count of files
    phraseSize = [0] #track for graph
    numArticleList = [0] #track for graph
    
    print("Reading files...")
    
    for file in onlyfiles: #iterate through files
        t0 = timeit.default_timer()
    
        with open(mypath + file) as inFile:
            
            for line in inFile: #call function find phrases in each link
                findPhrases(line)

        articleCount += 1
        if articleCount % 5 == 0: # update graph data
            phraseSize.append(len(phraseDict))
            numArticleList.append(articleCount)
        if articleCount % 20 == 0: # print progress
            t1 = timeit.default_timer()
            time = t1 - t0
            t0 = timeit.default_timer()
            print(str(articleCount) + ' files read : time ' + str(time))
    
        if articleCount == 10:
            break
            
    plt.plot(numArticleList, phraseSize)        
    plt.xlabel('# of articles')
    plt.ylabel('# of phrases')


def reduceAcronym():
    """
    keep only the one most commonly used acronym for each phrase, remove potential
    mistakes in articles or uncommonly used variations

    """
    for key in phraseAcronymDict:
        vals = []
        count = 0
        keep = ''
        
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
        
        
# sort phraseDict by count
# retain only top 10 phrases and remove all phrases occuring fewer than 5 times
def filterPhrases():
    """
    sort phraseDict by count, retain only top 10 phrases and remove all phrases occuring fewer than 5 times
    remove acronyms that do not have any phrases that satisfy the threshold
    """
    print('Filtering phrases...')
    removeKeySet = set()
    for key in phraseDict:
        temp = phraseDict[key]
        temp.sort(key = lambda temp : temp[1], reverse = True) # reverse sort
        temp = [item for item in temp if item[1] >= 5] # retain phrases occuring more than 5 times
        if temp: # if items in temp
            phraseDict[key] = temp[:10] # add only top 10 phrases
        else:
            removeKeySet.add(key)
    for key in removeKeySet:
        del phraseDict[key]
        

def writeToPhraseFile(outFile):
    """
    write acronym /t phrase /t count /t MeSHID /n to file
    """
    with open(outFile, 'w') as writeFile:
        for key in phraseDict:
            for phrase in phraseDict[key]:
                writeFile.write(key + '\t' + phrase[0] + '\t' + str(phrase[1]) + '\t' + termDict[phrase[0]] + '\n')


def writeToMatchFile(matchFile):
    """
    broken, need to fix
    """
    
    with open(matchFile, 'w') as writeFile:
        for key in matchDict:
            writeFile.write(key + '\t')
            for item in matchDict[key]:
                writeFile.write(item + '\t')
            writeFile.write('\n')
                

# inputFile = '/home/kewilliams/Documents/GitHub/CPP_setup/download/completed/desc2019.xml'
# fileType = 'descriptor'
# mypath = '/home/kewilliams/Documents/Pubmed/2020_pubmed/pubmed20_text/' # folder path
# outFile = '/home/kewilliams/Documents/Word_Embedding/acronym_phrase_mesh_all_sample.txt'
# #matchFile = '/home/kewilliams/Documents/Word_Embedding/acronym_mesh.txt'

# main program
# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser(description='Extract article information from PubMed xml files')
ap.add_argument("inputFile", help = "xml file with descriptor/supplemental terms")
ap.add_argument("fileType", help = "descriptor or supplemental file")
ap.add_argument("mypath", help = "folder path containing pubmed text")
ap.add_argument("outputFile", help = "file to write data to")
#ap.add_argument("matchFile", help = "file to write matches to")

# print help if no arguments are provided
if len(sys.argv)==1:
    ap.print_help(sys.stderr)
    sys.exit(1)

args = vars(ap.parse_args())

inputFile = args['inputFile']
fileType = args['fileType']
mypath = args['mypath']
outFile = args['outputFile']
#matchFile = args['matchFile']


# execute methods
xmlParse(inputFile, fileType)
parseFiles(mypath)
reduceAcronym()
reducePhrases()
findMatches()
writeToPhraseFile(outFile)
#writeToMatchFile(matchFile)


# #function to find phrase / phrase count / mesh term
# def findPhrase(acronym):
#     for i in range(len(phraseDict[acronym])):
#         if phraseDict[acronym][i][0] in termDict:
#             print(phraseDict[acronym][i][0] + ' : ' + str(phraseDict[acronym][i][1]) + ' : ' + termDict[phraseDict[acronym][i][0]])