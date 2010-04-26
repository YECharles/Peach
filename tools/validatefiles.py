'''
This script will validate a DataModel against an collection of
input files.  It will verify they are able to be parsed correctly.
'''

import os, sys, time, glob

sys.path.append("c:/peach")

print """
]] Peach Validate Multiple Files
]] Copyright (c) Michael Eddington

"""

if len(sys.argv) < 3:
	print """
This program will crack a series of files against a selected
data model and verify the output matches the input.  This allows
for build validation of data models.

Syntax: validatefiles <Peach PIT> <Data Model> <Input Files>

  Peach PIT   - The Peach XML file containing the data model
  Data Model  - Name of the data model to crack against
  Input Files - The path to a folder or a UNIX style Glob

"""
	sys.exit(0)

from Peach.Engine import *
from Peach.Engine.incoming import DataCracker
from Peach.publisher import *

inputFiles = []
inputFilesPath = sys.argv[2]
dataModelName = sys.argv[1]
xmlFile = sys.argv[0]

inputFiles = glob.glob(inputFilesPath)

for file in inputFiles:
	self.peach = Analyzer.DefaultParser().asParser("file:"+file)
	
	fd = open(file, "rb")
	data = fd.read()
	fd.close()
	
	buff = PublisherBuffer(None, data, True)
	
	cracker = DataCracker(self.peach)
	cracker.optmizeModelForCracking(self.peach, True)
	cracker.crackData(dataModel, buff)
	
	if dataModel.getValue() == data:
		print "Cracking of file '"+file+"' passed."
	else:
		print "Cracking of file '"+file+"' failed."

print "Done\n"

# end
