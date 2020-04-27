#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 18 15:32:31 2020

@author: kewilliams
"""

import mysql.connector
from mysql.connector import errorcode
import sys
import argparse


def createNewTable(cursor):
    cursor.execute('drop table findPhrase')
    cursor.execute('create table findPhrase (acronym varchar(20), phrase \
                    varchar(100),count mediumint,meshID varchar(10), unique \
                        (acronym, phrase, meshID))') 

def executeQuery(cursor, data, duplicateList):
    data[0] = ascii(data[0])
    data[1] = ascii(data[1])
    data[3] = ascii(data[3])
    info = (', ').join(data)
    query = 'insert into findPhrase(acronym, phrase, count, meshID) \
        values (' + info + ')'
    try:
        cursor.execute(query)
    except mysql.connector.Error as err:
        if err.errno == 1062: #duplicate entry code
            duplicateList.append(info)
        else:
            print(data[0])

def accessDatabase(userName, password, inFile, newTable):
    duplicateList = []
    try:
        cnx = mysql.connector.connect(user=userName, password=password,
                                      database='findphrasedb')
    except mysql.connector.Error as err:
        
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    else:
    
        cnx.autocommit = True
        cursor = cnx.cursor()
      
        if newTable:
            createNewTable(cursor)
        
        with open(inFile) as readFile:
            count = 0
            for line in readFile:
                count += 1
                executeQuery(cursor, line.strip('\n').split('\t'), duplicateList)
                if count % 100 == 0:
                    print(str(count) + ' rows added')
    
    cnx.close()
    return duplicateList
    
    
# main program
# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser(description='Add data to database')
ap.add_argument("username", help="findphrasedb username")
ap.add_argument("password", help="findphrasedb password")
ap.add_argument("inFile", help = "directory of input files")
ap.add_argument("newTable", nargs='?', help = "drop and create new table", default = False)

# print help if no arguments are provided
if len(sys.argv)==1:
    ap.print_help(sys.stderr)
    sys.exit(1)

args = vars(ap.parse_args())

userName = args['username']
password = args['password']
inFile = args['inFile']
newTable = args['newTable']

# inFile = '/home/kewilliams/Documents/Word_Embedding/updated_acronym_phrase_mesh.txt'

duplicates = accessDatabase(userName, password, inFile, newTable)
print(str(len(duplicates)) + ' duplicate records not written to DB')