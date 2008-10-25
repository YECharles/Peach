#!/usr/bin/python

'''
MinSet Console Application

This is a quick tool that will perform code coverage of basic blocks in a
target app and select the smallest set of files that give the largest
coverage of the application.

Currently WinDbg is required along with pydbgeng and comtypes.

@author: Michael Eddington
@version: $Id$
'''

#
# Copyright (c) 2008 Michael Eddington
#
# Permission is hereby granted, free of charge, to any person obtaining a copy 
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights 
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell 
# copies of the Software, and to permit persons to whom the Software is 
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in	
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

# Authors:
#   Michael Eddington (mike@phed.org)

# $Id$

import sys, os, threading, glob, pydbg

print ""
print "] Peach Minset Finder v0.2"
print "] Copyright (c) Michael Eddington\n"

if len(sys.argv) < 4:
	print "Syntax: minset.py target.exe samples\\folder command.exe \"args %%s\""
	print ""
	print "  target.exe   The target executable or ddl that"
	print "               contains the core parser logic."
	print "  samples      The folder containing the sample files"
	print "               for which we will find the min."
	print "  command      The command line of the program to run."
	print "  args         The arguments for the command line, it "
	print "               MUST contain a %%s which will be substututed"
	print "               for the sample filename."
	print ""
	
	sys.exit(0)

# 1. Read in offsets

try:
	os.unlink("bblocks.txt")
except:
	pass

bbTarget = sys.argv[1]
samples = sys.argv[2]
commandLine = sys.argv[3]
commandArgs = sys.argv[4]

print "[*] Finding all basic blocks in [%s]" % bbTarget
os.system("BasicBlocks\\BasicBlocks\\bin\\Debug\\basicblocks.exe /in %s" % bbTarget)

fd = open("bblocks.txt", "rb+")
strOffsets = fd.read().split("\n")
offsets = []

try:
	os.unlink("bblocks.txt")
except:
	pass

for s in strOffsets:
	if len(s) < 2:
		continue
	offsets.append(int(s))

sampleFiles = []
for f in glob.glob(samples):
	if os.path.isdir(f):
		continue
	
	sampleFiles.append(f)

print "[*] Found %d basic blocks and %d sample files" % (len(offsets),len(sampleFiles))

def handleAccessViolation(dbg):
	if dbg.first_breakpoint:
		return pydbg.defines.DBG_CONTINUE

	addr = dbg.dbg.u.Exception.ExceptionRecord.ExceptionAddress
	if addr in dbg.peachOffsets and addr not in dbg.peachBlocks:
		dbg.peachBlocks.append(addr)
	
	return pydbg.defines.DBG_CONTINUE

#: Dictionary of lists, key is sampleFile
bblocks = {}
#: Most coverage
sampleFileMostCoverage = None
sampleFileMostCoverageCount = -1
#: Min set
minset = []

for sampleFile in sampleFiles:
	print "[*] Determining coverage with [%s]...." % sampleFile
	
	bblocks[sampleFile] = []
	
	dbg = pydbg.pydbg()
	dbg.set_callback(pydbg.EXCEPTION_BREAKPOINT, handleAccessViolation)
	dbg.load(commandLine, commandArgs % sampleFile)
	
	dbg.peachOffsets = offsets
	dbg.peachBlocks = bblocks[sampleFile]
	
	for addr in offsets:
		dbg.bp_set(addr)
	
	dbg.debug_event_loop()
	
	print "[-] %s hit %d blocks" % (sampleFile, len(bblocks[sampleFile]))
	

# Figure out who covered the most blocks
for sampleFile in sampleFiles:
	cnt = len(bblocks[sampleFile])
	if cnt > sampleFileMostCoverageCount:
		sampleFileMostCoverage = sampleFile
		sampleFileMostCoverageCount = cnt

minset.append(sampleFileMostCoverage)

print "[*] Master template is [%s] with a coverage of %d blocks" % (sampleFileMostCoverage, sampleFileMostCoverageCount)

def delta(list1, list2):
	'''
	Find the delta of two lists
	'''
	
	d = []
	
	for i in list1:
		if i not in list2:
			d.append(i)
	
	return d

coveredBlocks = []
for b in bblocks[sampleFileMostCoverage]:
	coveredBlocks.append(b)

for sampleFile in sampleFiles:
	d = delta(bblocks[sampleFile], coveredBlocks)
	
	if len(d) > 0:
		minset.append(sampleFile)
		for b in d:
			coveredBlocks.append(b)

print ""
print "[*] Minimum set is %d of %d files:" % (len(minset), len(sampleFiles))

for sampleFile in minset:
	print "[-]    %s" % sampleFile

print "\n"

# end
