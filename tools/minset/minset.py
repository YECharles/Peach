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

import sys
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
		self._traceFolder = None
		if not self.isWindows():
			raise Exception("This tool only supports Windows for now.")
	
	def clean(self):
		if self._traceFolder != None:
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
		
		if needsKilling:
			
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
			for childPid in process_list(pid):
				pass
			
			print "parentpid:", pid, "child pid:", childPid
			
			while True:
				cpu = getProcessCpuTime(childPid)
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
		
	
	def runCoverage(self, command, samplesGlob, minsetPath, needsKilling):
		'''
		Main entry point
		'''
		
		try:
			
			print "[*] Finding all basic blocks"
			
			sampleFiles = []
			for f in glob.glob(samplesGlob):
				if os.path.isdir(f):
					continue
				
				sampleFiles.append(f)
			
			print "[*] Found %d sample files" % len(sampleFiles)
			
			#: Dictionary of lists, key is sampleFile
			bblocks = {}
			#: Most coverage
			sampleFileMostCoverage = None
			sampleFileMostCoverageCount = -1
			#: Min set
			minset = []
			
			for sampleFile in sampleFiles:
				print "[*] Determining coverage with [%s]...." % sampleFile
				
				cmd = command % sampleFile
				bblocks[sampleFile] = self.getCoverage(cmd, sampleFile)
				
				print "[-] %s hit %d blocks" % (sampleFile, bblocks[sampleFile])
				
			
			# Figure out who covered the most blocks
			for sampleFile in sampleFiles:
				cnt = bblocks[sampleFile]
				if cnt > sampleFileMostCoverageCount:
					sampleFileMostCoverage = sampleFile
					sampleFileMostCoverageCount = cnt
			
			minset.append(sampleFileMostCoverage)
			
			print ""
			print "[*] Master template is [%s] with a coverage of %d blocks" % (sampleFileMostCoverage, sampleFileMostCoverageCount)
			
			# Start with file with most coverage
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

if len(sys.argv) < 4:
	print "Syntax: minset.py [-gui] samples minset \"command.exe\" \"args %%s\""
	print ""
	print "  -gui         Optional parameter indicating program will"
	print "               not close on it's own and needs killing"
	print "  samples      The folder containing the sample files"
	print "               for which we will find the min."
	print "  minset       Folder to place the min set of required files."
	print "  command      The command line of the program to run."
	print "               MUST contain a %%s which will be substututed"
	print "               for the sample filename."
	print ""
	
	sys.exit(0)

needsKilling = False
if sys.argv[1] == "-gui":
	needsKilling = True
	samplesGlob = sys.argv[2]
	minsetPath = sys.argv[3]
	command = sys.argv[4]
	if len(sys.argv) > 5:
		command = '"' + command + '" ' + sys.argv[5]
else:
	samplesGlob = sys.argv[1]
	minsetPath = sys.argv[2]
	command = sys.argv[3]
	if len(sys.argv) > 4:
		command = '"' + command + '" ' + sys.argv[4]

coverage = PeachCoverage()
coverage.runCoverage(command, samplesGlob, minsetPath, needsKilling)

# end
