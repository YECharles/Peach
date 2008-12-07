'''
Peach Logging System

This is the Peach logging sub-system.  To implement a new logging method
extend from Logger.

@author: Michael Eddington
@version: $Id$
'''

#
# Copyright (c) 2007-2008 Michael Eddington
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

from Engine.engine import EngineWatcher

class Logger(EngineWatcher):
	'''
	Parent class for all logger implementations.
	'''
	
	def OnRunStarting(self, run):
		'''
		Called when a run is starting.
		'''
		pass
	
	def OnRunFinished(self, run):
		'''
		Called when a run is finished.
		'''
		pass
	
	def OnTestStarting(self, run, test, totalVariations):
		'''
		Called on start of a test.  Each test has multiple variations.
		'''
		pass
	
	def OnTestFinished(self, run, test):
		'''
		Called on completion of a test.
		'''
		pass

	def OnTestCaseStarting(self, run, test, variationCount):
		'''
		Called on start of a test case.
		'''
		pass
	
	def OnTestCaseReceived(self, run, test, variationCount, value):
		'''
		Called when data is received from test case.
		'''
		pass
	
	def OnTestCaseException(self, run, test, variationCount, exception):
		'''
		Called when an exception occurs during a test case.
		'''
		pass
	
	def OnTestCaseFinished(self, run, test, variationCount, actionValues):
		'''
		Called when a test case has completed.
		'''
		pass
	
	def OnFault(self, run, test, variationCount, monitorData, value):
		pass
	
	def OnStopRun(self, run, test, variationCount, monitorData, value):
		pass

import os,uuid
from time import *

class Filesystem(Logger):
	'''
	A file system logger.
	'''
	
	def __init__(self, params):
		self.name = str(uuid.uuid1())
		self.elementType = 'logger'
		self.params = params
		self.heartBeat = 512
	
	def _writeMsg(self, line):
		self.file.write(asctime() + ": " + line + "\n")
		self.file.flush()
		
	def OnRunStarting(self, run):
		suppliedPath = eval(str(self.params['path']))
		
		self.path = os.path.join(suppliedPath, run.name + "_" + strftime("%Y_%b_%d_%H_%M_%S", gmtime()))
		self.faultPath = os.path.join(self.path, "Faults")
		try:
			os.mkdir(suppliedPath)
		except:
			pass
		try:
			os.mkdir(self.path)
		except:
			pass
		
		self.file = open(os.path.join(self.path,"status.txt"), "w")
		
		self.file.write("Peach 2.0 Fuzzer Run\n")
		self.file.write("====================\n\n")
		self.file.write("Date of run: " + asctime() + "\n")
		self.file.write("Run name: " + run.name + "\n\n")
	
	def OnRunFinished(self, run):
		self.file.write("\n\n== Run completed ==\n" + asctime() + "\n")
		self.file.close()
		self.file = None
	
	def OnTestStarting(self, run, test, totalVariations):
		self._writeMsg("")
		self._writeMsg("Test starting: " + test.name)
		#self._writeMsg("Test has %d variations" % totalVariations)
		self._writeMsg("")
	
	def OnTestFinished(self, run, test):
		self._writeMsg("")
		self._writeMsg("Test completed: " + test.name)
		self._writeMsg("")
	
	def OnTestCaseException(self, run, test, variationCount, exception):
		pass
	
	def OnFault(self, run, test, variationCount, monitorData, actionValues):
		self._writeMsg("Fault was detected on test %d" % variationCount)
		
		# Look for Bucket information
		bucketInfo = None
		for key in monitorData.keys():
			if key.find("_Bucket") > -1:
				bucketInfo = monitorData[key]
				break
		
		# Build folder structure
		try:
			os.mkdir(self.faultPath)
		except:
			pass
		
		if bucketInfo != None:
			print "BucketInfo:", bucketInfo
			
			try:
				path = os.path.join(self.faultPath,bucketInfo)
				os.mkdir(path)
			except:
				pass
			
			path = os.path.join(self.faultPath,bucketInfo,str(variationCount))
		else:
			try:
				path = os.path.join(self.faultPath,"Unknown")
				os.mkdir(path)
			except:
				pass
			
			path = os.path.join(self.faultPath,"Unknown",str(variationCount))
		
		try:
			os.mkdir(path)
		except:
			pass
		
		# Expand actionValues
		
		for i in range(len(actionValues)):
			fileName = os.path.join(path, "data_%d_%s_%s.txt" % (i, actionValues[i][1], actionValues[i][0]))
			
			if len(actionValues[i]) > 2:
				fout = open(fileName, "w+b")
				fout.write(actionValues[i][2])
				
				if len(actionValues[i]) > 3:
					fout.write(repr(actionValues[i][3]))
				
				fout.close()
		
		for key in monitorData.keys():
			if key.find("_Bucket") == -1:
				fout = open(os.path.join(path,key), "wb")
				fout.write(monitorData[key])
				fout.close()
	
	def OnStopRun(self, run, test, variationCount, monitorData, value):
		self._writeMsg("")
		self._writeMsg("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
		self._writeMsg("!!!! TEST ABORTING AT %d" % variationCount)
		self._writeMsg("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
		self._writeMsg("")
		
		
	def OnTestCaseStarting(self, run, test, variationCount):
		'''
		Called on start of a test case.
		'''
		if variationCount % self.heartBeat == 0:
			self._writeMsg("On test variation # %d" % variationCount)

# end
