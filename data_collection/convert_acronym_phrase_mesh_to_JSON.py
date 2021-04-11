#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 24 12:34:17 2020

@author: kewilliams

"""
import json
import requests
from collections import defaultdict
import sys
import argparse

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser(description='Convert phrase/mesh file to json dump')
ap.add_argument("inputFile", help = "acronym/mesh file")
ap.add_argument("outputFile", help = "file for json dump")

# print help if no arguments are provided
if len(sys.argv)==1:
    ap.print_help(sys.stderr)
    sys.exit(1)

args = vars(ap.parse_args())

inputFile = args['inputFile']
outFile = args['outputFile']

with open(inputFile) as inFile:
    myDict = defaultdict(list)
    i = 0
    for line in inFile:
        data = line.strip('\n').split('\t')
        myDict[data[0]].append({'phrase':data[1], 'count':data[2], 'meshID':data[3]})


data = json.dumps(myDict)
with open('json_dump_text.txt', 'w') as writeFile:
    writeFile.write(data)
