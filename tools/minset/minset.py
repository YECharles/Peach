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

from optparse import OptionParser
import sys
import time
import os
import glob
import shutil
import tempfile
import win32api
import win32con
import win32process
import win32pdh
import ctypes

TH32CS_SNAPPROCESS = 0x00000002
class PROCESSENTRY32(ctypes.Structure):
	_fields_ = [
		("dwSize", ctypes.c_ulong),
		("cntUsage", ctypes.c_ulong),
		("th32ProcessID", ctypes.c_ulong),
		("th32DefaultHeapID", ctypes.c_ulong),
		("th32ModuleID", ctypes.c_ulong),
		("cntThreads", ctypes.c_ulong),
		("th32ParentProcessID", ctypes.c_ulong),
		("pcPriClassBase", ctypes.c_ulong),
		("dwFlags", ctypes.c_ulong),
		("szExeFile", ctypes.c_char * 260)]

class PeachCoverage:
	
	def __init__(self):
		self._traceFolderCleanup = True
		self._traceFolder = None
		if not self.isWindows():
			raise Exception("This tool only supports Windows for now.")
	
	def clean(self):
		if self._traceFolder != None and self._traceFolderCleanup:
			shutil.rmtree(self._traceFolder)
			self._traceFolder = None
		
		try:
			os.unlink("bblocks.out")
		except:
			pass
	
	def delta(self, list1, list2):
		'''
		Find the delta of two lists
		'''
		
		d = []
		
		for i in list1:
			if i not in list2:
				d.append(i)
		
		return d
	
	def stripPath(self, fileName):
		'''
		Strip the path from a filename
		'''
		
		indx = fileName.rfind(os.path.sep)
		
		if indx == -1:
			return fileName
		
		return fileName[indx+1:]
	
	def getProcessEntry(self, pid):
		'''
		Return the PROCESSENTRY32 struct for
		a process id.
		'''
		
		# See http://msdn2.microsoft.com/en-us/library/ms686701.aspx
		CreateToolhelp32Snapshot = ctypes.windll.kernel32.CreateToolhelp32Snapshot
		Process32First = ctypes.windll.kernel32.Process32First
		Process32Next = ctypes.windll.kernel32.Process32Next
		CloseHandle = ctypes.windll.kernel32.CloseHandle
		
		hProcessSnap = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
		
		pe32 = PROCESSENTRY32()
		pe32.dwSize = ctypes.sizeof(PROCESSENTRY32)
		
		if Process32First(hProcessSnap, ctypes.byref(pe32)) == win32con.FALSE:
			print >> sys.stderr, "Failed getting first process."
			return
		
		while True:
			if pe32.th32ProcessID == pid:
				break
			
			if Process32Next(hProcessSnap, ctypes.byref(pe32)) == win32con.FALSE:
				pe32 = None
				break
		
		CloseHandle(hProcessSnap)
		
		return pe32
	
	def process_list(self, parentId):
		'''
		Yield all child process ids
		'''
		
		# See http://msdn2.microsoft.com/en-us/library/ms686701.aspx
		CreateToolhelp32Snapshot = ctypes.windll.kernel32.CreateToolhelp32Snapshot
		Process32First = ctypes.windll.kernel32.Process32First
		Process32Next = ctypes.windll.kernel32.Process32Next
		CloseHandle = ctypes.windll.kernel32.CloseHandle
		
		hProcessSnap = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
		
		pe32 = PROCESSENTRY32()
		pe32.dwSize = ctypes.sizeof(PROCESSENTRY32)
		
		if Process32First(hProcessSnap, ctypes.byref(pe32)) == win32con.FALSE:
			print >> sys.stderr, "Failed getting first process."
			return
		
		while True:
			if pe32.th32ParentProcessID == parentId:
				yield pe32.th32ProcessID
			
			if Process32Next(hProcessSnap, ctypes.byref(pe32)) == win32con.FALSE:
				break
		
		CloseHandle(hProcessSnap)
	
	def isWindows(self):
		'''
		Is this a windows system?
		'''
		
		if sys.platform == 'win32':
			return True
		
		return False
	
	def getProcessCpuTime(self, pid):
		'''
		Get the current CPU processor time as a double based on a process
		instance (chrome#10).
		'''
	
		process = self.getProcessInstance(pid)
		
		try:
			if process == None:
				print "getProcessCpuTimeWindows: process is null"
				return None
			
			#if cpu_path == None:
			cpu_path = win32pdh.MakeCounterPath( (None, 'Process', process, None, 0, '% Processor Time') )
			
			#if cpu_hq == None:
			cpu_hq = win32pdh.OpenQuery()
			
			#if cpu_counter_handle == None:
			cpu_counter_handle = win32pdh.AddCounter(cpu_hq, cpu_path) #convert counter path to counter handle
			win32pdh.CollectQueryData(cpu_hq) #collects data for the counter
			time.sleep(0.25)
			
			win32pdh.CollectQueryData(cpu_hq) #collects data for the counter
			(v,cpu) = win32pdh.GetFormattedCounterValue(cpu_counter_handle, win32pdh.PDH_FMT_DOUBLE)
			return cpu
		
		except:
			print "getProcessCpuTimeWindows threw exception!"
			print sys.exc_info()
		
		return None
	
	def getProcessInstance(self, pid):
		'''
		Get the process instance name using pid.
		'''
		
		hq = None
		counter_handle = None
		
		try:
			
			win32pdh.EnumObjects(None, None, win32pdh.PERF_DETAIL_WIZARD)
			junk, instances = win32pdh.EnumObjectItems(None,None,'Process', win32pdh.PERF_DETAIL_WIZARD)
		
			proc_dict = {}
			for instance in instances:
				if proc_dict.has_key(instance):
					proc_dict[instance] = proc_dict[instance] + 1
				else:
					proc_dict[instance]=0
			
			proc_ids = []
			for instance, max_instances in proc_dict.items():
				for inum in xrange(max_instances+1):
					hq = win32pdh.OpenQuery() # initializes the query handle 
					try:
						path = win32pdh.MakeCounterPath( (None, 'Process', instance, None, inum, 'ID Process') )
						counter_handle=win32pdh.AddCounter(hq, path) #convert counter path to counter handle
						try:
							win32pdh.CollectQueryData(hq) #collects data for the counter 
							type, val = win32pdh.GetFormattedCounterValue(counter_handle, win32pdh.PDH_FMT_LONG)
							proc_ids.append((instance, val))
							
							if val == pid:
								return "%s#%d" % (instance, inum)
							
						except win32pdh.error, e:
							#print e
							pass
						
						win32pdh.RemoveCounter(counter_handle)
						counter_handle = None
					
					except win32pdh.error, e:
						#print e
						pass
					win32pdh.CloseQuery(hq)
					hq = None
		except:
			print "getProcessInstance thew exception"
			print sys.exc_info()
		
		finally:
			
			try:
				if counter_handle != None:
					win32pdh.RemoveCounter(counter_handle)
					counter_handle = None
				if hq != None:
					win32pdh.CloseQuery(hq)
					hq = None
			except:
				pass
		
		# SHouldn't get here...we hope!
		return None
	
	def fileLineCount(self, fname):
		f = open(fname)
		for i, l in enumerate(f):
			pass
		
		f.close()
		return i + 1
	
	def loadBlocks(self, sampleFile):
		bblocks = []
		f = open(os.path.join(self._traceFolder, self.stripPath(sampleFile)+".trace"))
		for i,l in enumerate(f):
			bblocks.append(l)
		
		f.close()
		
		return bblocks
	
	def getCoverage(self, cmd, sampleFile):
		'''
		Generates a trace into "sampleFile.trace" and returns
		the count of basic blocks hit.
		'''
		
		try:
			os.unlink("bblocks.out")
		except:
			pass
		
		if self._traceFolder == None:
			self._traceFolder = tempfile.mkdtemp()
		
		if self._needsKilling:
			
			if not self.isWindows():
				raise Exception("-gui only on Windows for now")
			
			hProcPin = os.spawnl(os.P_NOWAIT, 
				"pin-2.8-37300-msvc10-ia32_intel64-windows\\ia32\\bin\\pin.exe", 
				"pin-2.8-37300-msvc10-ia32_intel64-windows\\ia32\\bin\\pin.exe", 
				"-t", 
				"bblocks.dll", 
				"--", 
				cmd)
			
			time.sleep(2)
			
			pid = ctypes.windll.kernel32.GetProcessId(hProcPin)
			for childPid in self.process_list(pid):
				pass
			
			print "parentpid:", pid, "child pid:", childPid
			
			while True:
				cpu = self.getProcessCpuTime(childPid)
				if cpu == None:
					print "CPU IS None!"
					sys.exit(0)
				
				if cpu != None and cpu < 0.5:
					print "Kill due to CPU time"
					
					os.system("taskkill /pid %d" % (childPid))
					os.system("taskkill /f /pid %d" % (childPid))
					
					# Prevent Zombies!
					os.waitpid(hProcPin, 0)
					break
				
				time.sleep(0.50)
		else:
			pid = os.spawnl(os.P_WAIT, 
				"pin-2.8-37300-msvc10-ia32_intel64-windows\\ia32\\bin\\pin.exe", 
				"pin-2.8-37300-msvc10-ia32_intel64-windows\\ia32\\bin\\pin.exe", 
				"-t", 
				"bblocks.dll", 
				"--", 
				cmd)
		
		
		# For large traces we shouldn't try and keep offsets
		# in memory.  Lets just copy our trace to a temp file
		# for use later.
		
		bblCount = self.fileLineCount("bblocks.out")
		shutil.move("bblocks.out", os.path.join(self._traceFolder, self.stripPath(sampleFile)+".trace"))
		
		return bblCount
	
	def runTraces(self, command, sampleFiles, tracesPath, needsKilling):
		'''
		Just take coverage traces and place them in tracesPath
		'''
		
		try:
			self._needsKilling = needsKilling
			self._traceFolder = tracesPath
			
			# Most coverage
			sampleFileMostCoverage = None
			sampleFileMostCoverageCount = -1
			
			try:
				os.mkdir(self._traceFolder)
			except:
				pass
			
			print "[*] Performing code coverage traces with %d files" % len(sampleFiles)
			
			for sampleFile in sampleFiles:
				print "[*] Determining coverage with [%s]" % sampleFile
				
				cmd = command % sampleFile
				bbl = self.getCoverage(cmd, sampleFile)
				
				if bbl > sampleFileMostCoverageCount:
					sampleFileMostCoverage = sampleFile
					sampleFileMostCoverageCount = bbl
				
				print "[-] %s hit %d blocks" % (sampleFile, bbl)
				
			print ""
			print "[*] Master template is [%s] with a coverage of %d blocks" % (sampleFileMostCoverage, sampleFileMostCoverageCount)
			
			# Set _traceFolder to None if we don't want
			# cleanup to remove it
			if tracesPath != None:
				self._traceFolder = None
			
			return (sampleFileMostCoverage, sampleFileMostCoverageCount)
			
		finally:
			# Clean up after ourselvs
			self.clean()

	def runCoverage(self, command, sampleFiles, minsetPath, tracesPath, needsKilling):
		'''
		Main entry point
		'''
		
		try:
			
			# Do we already have traces, if not collect.
			if tracesPath == None:
				try:
					self._traceFolderCleanup = False
					(sampleFileMostCoverage, sampleFileMostCoverageCount ) = self.runTraces(command, sampleFiles, None, needsKilling)
				finally:
					self._traceFolderCleanup = True
			
			else:
				print "[*] Using existing coverage traces"
				
				sampleFileMostCoverageCount = -1
				sampleFileMostCoverage = None
				
				self._traceFolderCleanup = False
				self._traceFolder = tracesPath
				for sampleFile in sampleFiles:
					bbl = self.fileLineCount(os.path.join(self._traceFolder, self.stripPath(sampleFile)+".trace"))
					
					if bbl > sampleFileMostCoverageCount:
						sampleFileMostCoverage = sampleFile
						sampleFileMostCoverageCount = bbl
				
				print ""
				print "[*] Master template is [%s] with a coverage of %d blocks" % (sampleFileMostCoverage, sampleFileMostCoverageCount)
			
			# Start with file with most coverage
			minset = []
			minset.append(sampleFileMostCoverage)
			coveredBlocks = self.loadBlocks(sampleFileMostCoverage)
			
			for sampleFile in sampleFiles:
				
				# Don't repeat master file
				if sampleFile == sampleFileMostCoverage:
					continue
				
				bblTrace = self.loadBlocks(sampleFile)
				d = self.delta(bblTrace, coveredBlocks)
				bblTrace = None
				
				if len(d) > 0:
					minset.append(sampleFile)
					for b in d:
						coveredBlocks.append(b)
			
			# No longer need these
			coveredBlocks = None
			d = None
			
			print ""
			print "[*] Minimum set is %d of %d files:" % (len(minset), len(sampleFiles))
			
			try:
				os.mkdir(minsetPath)
			except:
				pass
			
			for sampleFile in minset:
				print "[-]    %s" % sampleFile
				shutil.copyfile(sampleFile, os.path.join(minsetPath, self.stripPath(sampleFile)))
			
			print "\n"
		
		finally:
			# Clean up after ourselvs
			self.clean()


print ""
print "] Peach Minset Finder v0.9"
print "] Copyright (c) Michael Eddington\n"

usage = """
  minset.py [-k] -s samples -m minset command.exe args %%s
  minset.py [-k] -s samples -t traces command.exe args %%s
  minset.py [-k] -s samples -t traces -m minset command.exe args %%s
  
Note:
  "%%s" will be replaced by sample filename.
"""

parser = OptionParser(usage)
parser.add_option("-k", "--kill", action="store_true", dest="needsKilling", default=False,
				  help="Kill command when CPU time nears 0")
parser.add_option("-t", "--traces", action="store", type="string", dest="tracesPath", default=None,
				  help="Only take traces and place them in this folder.")
parser.add_option("-s", "--samples", action="store", type="string", dest="samplesGlob",
				  help="Path and file glob to samples (e.g. smaples/*.jpg)")
parser.add_option("-m", "--minset", action="store", type="string", dest="minsetPath", default=None,
				  help="Path to place minset of files.")
(options, args) = parser.parse_args()

if len(args) == 0:
	parser.error("incorrect number of arguments")

command = ""
for a in args:
	command += '"' + a + '" '

sampleFiles = []
for f in glob.glob(options.samplesGlob):
	if os.path.isdir(f):
		continue
	
	sampleFiles.append(f)

coverage = PeachCoverage()

if options.minsetPath != None:
	coverage.runCoverage(
		command,
		sampleFiles,
		options.minsetPath,
		options.tracesPath,
		options.needsKilling)

else:
	coverage.runTraces(
		command,
		sampleFiles,
		options.tracesPath,
		options.needsKilling)

# end
