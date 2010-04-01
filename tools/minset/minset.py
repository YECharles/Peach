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
# Copyright (c) Michael Eddington
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

import sys, os, threading, glob, re
import PyDbgEng
from comtypes.gen import DbgEng

class _DbgEventHandler(PyDbgEng.IDebugOutputCallbacksSink, PyDbgEng.IDebugEventCallbacksSink):
	
	bps = False
	mainOffset = 0
	
	def Output(self, this, Mask, Text):
		if self.mainOffset == 0 and Text.find("ModLoad") > -1:
			m = re.search("ModLoad:\s*([^ ]*) ", Text)
			self.mainOffset = int(m.group(1), 16)
	
	def LoadModule(self, this, ImageFileHandle, BaseOffset, ModuleSize, ModuleName,
				   ImageName, CheckSum, TimeDateStamp):
		
		if self.bps == False:
			self.bps = True
			
			try:
				for offset in self.peachOffsets:
					bp_params = this.idebug_control.AddBreakpoint(Type = DbgEng.DEBUG_BREAKPOINT_CODE, DesiredId = DbgEng.DEBUG_ANY_ID)
					flags = DbgEng.DEBUG_BREAKPOINT_ENABLED | DbgEng.DEBUG_BREAKPOINT_ONE_SHOT
					bp_params.AddFlags(flags)
					bp_params.SetOffset(self.mainOffset + offset)
			except:
				print sys.exc_info()
		
		return DbgEng.DEBUG_STATUS_NO_CHANGE
	
	def GetInterestMask(self):
		#print "GetInterestMask"
		return DbgEng.DEBUG_EVENT_BREAKPOINT | \
			DbgEng.DEBUG_EVENT_LOAD_MODULE | DbgEng.DEBUG_ENGOPT_INITIAL_BREAK |\
			DbgEng.DEBUG_FILTER_INITIAL_BREAKPOINT
	
	def ExitProcess(self, dbg, ExitCode):
		#print "ExitProcess"
		return DbgEng.DEBUG_STATUS_NO_CHANGE
	
	def Breakpoint(self, this, Offset, Id, BreakType, ProcType, Flags, DataSize,
				   DataAccessType, PassCount, CurrentPassCount, MatchThread,
				   CommandSize, OffsetExpressionSize):
		
		#print "Breakpoint", Offset - self.mainOffset
		addr = Offset - self.mainOffset
		if not (addr in self.peachBlocks):
			self.peachBlocks.append(addr)
		
		return DbgEng.DEBUG_STATUS_NO_CHANGE

print ""
print "] Peach Minset Finder v0.5"
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

# Locate the base path of this executable/script
p = None
if not (hasattr(sys,"frozen") and sys.frozen == "console_exe"):
	p = __file__[:-9]

else:
	p = os.path.dirname(os.path.abspath(sys.executable))

if len(p) == 0:
	p = "."

# Locate and run basicblock finding program
if os.path.exists(os.path.join(p,"BasicBlocks")):
	os.system(os.path.join(p,"BasicBlocks\\BasicBlocks\\bin\\release\\basicblocks.exe /in %s" % bbTarget))
elif os.path.exists(os.path.join(p,"bin\\basicblocks.exe")):
	os.system(os.path.join(p,"bin\\basicblocks.exe /in %s" % bbTarget))
elif os.path.exists(os.path.join(p,"basicblocks.exe")):
	os.system(os.path.join(p,"basicblocks.exe /in %s" % bbTarget))
elif os.path.exists(os.path.join(p,"tools")):
	os.system(os.path.join(p,"tools\\minset\\BasicBlocks\\BasicBlocks\\bin\\release\\basicblocks.exe /in %s" % bbTarget))
else:
	print "ERROR: Unable to locate basicblocks.exe"
	sys.exit(0)

fd = open("bblocks.txt", "rb+")
strOffsets = fd.read().split("\n")
offsets = []
fd.close()

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

#: Dictionary of lists, key is sampleFile
bblocks = {}
#: Most coverage
sampleFileMostCoverage = None
sampleFileMostCoverageCount = -1
#: Min set
minset = []

class DuhEvent:
	def is_set(self):
		return False

for sampleFile in sampleFiles:
	print "[*] Determining coverage with [%s]...." % sampleFile
	
	bblocks[sampleFile] = []
	
	_eventHandler = _DbgEventHandler()
	_eventHandler.peachOffsets = offsets
	_eventHandler.peachBlocks = bblocks[sampleFile]
	
	dbg = PyDbgEng.ProcessCreator(command_line = "%s %s" % (commandLine, commandArgs % sampleFile),
		follow_forks = True,
		event_callbacks_sink = _eventHandler,
		output_callbacks_sink = _eventHandler)
	
	dbg.event_loop_with_quit_event(DuhEvent())
	_eventHandler.peachBlocks = None
	
	print "[-] %s hit %d blocks" % (sampleFile, len(bblocks[sampleFile]))
	

# Figure out who covered the most blocks
for sampleFile in sampleFiles:
	cnt = len(bblocks[sampleFile])
	if cnt > sampleFileMostCoverageCount:
		sampleFileMostCoverage = sampleFile
		sampleFileMostCoverageCount = cnt

minset.append(sampleFileMostCoverage)

print ""
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
