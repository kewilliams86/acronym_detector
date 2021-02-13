# Taken from CPP_setup GitHub repository

#########################################################
# Downloads 2018 PubMed baseline data, which includes
#     pubmed18n0001.xml.gz - pubmed18n0929.xml.gz
#########################################################

import ftputil
import sys
import os
import glob
import argparse

# Note: consider using pubrunner for this

ap = argparse.ArgumentParser(description="Retrieve PubMed XML files. Note: a file will not be downloaded if it already exists")
ap.add_argument("pubmedDirectory", help="pubmed directory, either 'baseline' or 'updatefiles'")
ap.add_argument("outputDirectory", help = "directory of output files")
ap.add_argument("email", help = "e-mail requested for FTP access")

if len(sys.argv)== 0:
    ap.print_help(sys.stderr)
    sys.exit(1)

print(sys.argv)

args = vars(ap.parse_args())

# get arguments
pubmedDirectory = args['pubmedDirectory']
directory = args['outputDirectory']
email = args['email']

# connect to ftp and get files
host = ftputil.FTPHost('ftp.ncbi.nlm.nih.gov', 'anonymous', email)
path = 'pubmed/' + pubmedDirectory 
host.chdir(path)
files = host.listdir('.')

# keep only *.xml.gz files
files = [f for f in files if f.endswith("xml.gz")]


if not os.path.exists(directory):
        os.makedirs(directory)

print("Files will be saved to the following directory:", directory)

for fileName in files :

  outFile = directory + '/' + fileName
  if os.path.exists(outFile) :
      print("File already exists and will not be downloaded: " + fileName)
      continue

  print("retrieving file:", fileName)

  try :
    host.download(fileName, outFile)
  except :
    print("Warning: " + fileName + " could not be downloaded\n")      
