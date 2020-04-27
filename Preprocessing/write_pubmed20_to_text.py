# -*- coding: utf-8 -*-
"""
@author kewilliams

modified write_full_pubmed_to_text.py from CPP_setup GitHub repository

Usage:

  write_pubmed20_to_text.py [-h] inputDirectory outputDirectory

Extract dcast article information from PubMed xml files

positional arguments:
  inputDirectory   directory of input files
  outputDirectory  directory of output files

simplified sample XML file format (Relevant Data Only):
PubmedArticle
    MedlineCitation
        PMID - text contains PMID
        Article
            ArticleTitle - Title of Article
            Abstract
                AbstractText - text contains abstract, if multiple tags can contain info
    
"""

import shutil #move file location
import timeit
import mysql.connector
from mysql.connector import errorcode
from lxml import etree #slightly faster than xml.etree.ElementTree, also no need to unzip

import sys
import argparse
import glob
import os


#retrieve PMID
def getPmid(medline):
    
    pmid = medline.find('PMID')
    if pmid is not None:
        pmid = pmid.text
    else:
        pmid = ''
    return pmid


#retrieve article title
def getTitle(article):

    title = article.find('ArticleTitle')    
    if title is not None:
        title = title.text
    else:
        title = ''
    return title


#retrieve abstract
def getAbstract(article):
    
    if article.find('Abstract/AbstractText') is not None:
        abstracts = article.findall('Abstract/AbstractText')
        if len(abstracts) == 1: #if one abstract, ignore tags and get text
            abstractText = abstracts[0].text
        elif len(abstracts) > 1:
            abstractText = ''
            #multiple abstracts typically come with hidden headings in tags
            #tags typically have a NlmCategory attribute, if not that then Label attribute
            for abstract in abstracts:
                abText = abstract.text
                if abText is None :
                    abText = ''
                #print("abstract.txt:", abstract.text)
                #print("Nlm:", abstract.attrib.get('NlmCategory','null'))
                #print("Label:", abstract.attrib.get('Label','null'))

                nlm = abstract.attrib.get('NlmCategory')
                if nlm :
                    abstractText += nlm + ' ' + abText + ' ' 
                    continue
                label = abstract.attrib.get('Label')
                if label :
                    abstractText += label + ' ' + abText + ' '
                    continue
                abstractText += abText + ' '
            abstractText = abstractText[:-1] #remove trailing ' '
        else:
            abstractText = ''
    #if Abstract/AbstractText is None, abstract text may be out of place in Abstract child        
    elif article.find('Abstract') is not None:
        abstractText = article.find('Abstract').text
    else:
        abstractText = ''
    return abstractText 


# takes set of pmids and checks each pmid against set
def createTxtFromXML(filePath):

    #t2 = timeit.default_timer() #begin timer for whole program
    
    errorStr = "" #for try / catch
    
    # get all xml.gz files in specified directory
    files = sorted(glob.glob(filePath +"/*.xml.gz"))
    print("Number of *.xml.gz files found in directory '", filePath, "': ", len(files), sep = "")

    # create outputDirectory if it does not exist
    if not os.path.exists(outputDirectory):
        os.makedirs(outputDirectory)

    errorCount = 0

    for inFile in files:
        t0 = timeit.default_timer()
        
        try:
            pubTree = etree.parse(inFile)
        
        except :            
            if not os.path.exists(outputDirectory + ("/ERRORS/")): #create folder for failed file
                os.makedirs(outputDirectory + ("/ERRORS/"))
            shutil.copy(inFile, outputDirectory + "/ERRORS/" + os.path.basename(inFile)) #move to ERROR folder
            errorStr = os.path.basename(inFile) + " - " + str(sys.exc_info()[0])
            print(errorStr)
            f = open(outputDirectory + "/ERRORS/log.txt", "a")
            f.write(errorStr + "\n")
            f.close()
            errorCount += 1
            continue #skip to next file
        
             
        outFile = outputDirectory + "/extracted_" + os.path.basename(inFile).replace(".xml.gz", ".txt")
        
        writeFile = open(outFile, 'w') #open file for data transfer
        
        for pubmedArticle in pubTree.getiterator('PubmedArticle'):
            writeToFile(pubmedArticle, writeFile)
            pubmedArticle.clear() #clearing nodes slightly increases speed
        t1 = timeit.default_timer()
        print("Successful Write : " + outFile + " : " + str(t1 - t0))   
    
    #t3 = timeit.default_timer() #end time for whole program
    #print("\nTotal time of execution: " + str(t3 - t2))
    if errorCount is not 0 :
        print("\nWarning:", errorCount, "files could not written. See", outputDirectory + "/ERRORS/log.txt for more information")


def writeToFile (pubmedArticle, writeFile):
    
    medline = pubmedArticle.find('MedlineCitation')
    article = medline.find('Article')
    title = getTitle(article)
    abstract = getAbstract(article)
  
    
    # make sure not to output None 
    if title is None :
        title = ''
    elif title.startswith('RETRACTED:'): #skip retracted
        return
    if abstract is None :
        abstract = ''


    writeFile.write(ascii(title) + '\t' + ascii(abstract) + '\n')
    
    

# main program
# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser(description='Extract article information from PubMed xml files')
ap.add_argument("inputDirectory", help = "directory of input files")
ap.add_argument("outputDirectory", help = "directory of output files")

# print help if no arguments are provided
if len(sys.argv)==1:
    ap.print_help(sys.stderr)
    sys.exit(1)

args = vars(ap.parse_args())

inputDirectory = args['inputDirectory']
outputDirectory = args['outputDirectory']

createTxtFromXML(inputDirectory)