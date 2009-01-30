
'''
Process control agent.  This agent is able to start, stop, and monitor
if a process is running.  If the process exits early a fault will be
issued to the fuzzer.

@author: Michael Eddington
@version: $Id$
'''

#
# Copyright (c) 2007 Michael Eddington
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

import sys, time
sys.path.append("..")
sys.path.append("../..")
import os

try:
	import win32con
	from win32process import *
except:
	print "Warning: win32 extensions not found, disabing variouse process monitors."

from Peach.agent import Monitor

class PageHeap(Monitor):
	'''
	A monitor that will enable/disable pageheap on an executable.
	'''
	
	def __init__(self, args):
		'''
		Params: Path, Executable
		'''
		
		try:
			self._path = args['Path'].replace("'''", "") + "\\gflags.exe"
			
		except:
			self._path = 'c:\\Program Files\\Debugging Tools for Windows\\gflags.exe'
		
		self._exe = args['Executable'].replace("'''", "")
		
		self._onParams = [ 'gflags.exe', '/p', '/full', '/enable', self._exe ]
		self._offParams = [ 'gflags.exe', '/p', '/disable', self._exe ]
		
		os.spawnv(os.P_WAIT, self._path, self._onParams )
	
	def OnShutdown(self):
		os.spawnv(os.P_WAIT, self._path, self._offParams )


class Process(Monitor):
	'''
	Process control agent.  This agent is able to start, stop, and monitor
	if a process is running.  If the process exits early a fault will be
	issued to the fuzzer.
	'''
	
	def __init__(self, args):
		if args.has_key('RestartOnEachTest'):
			if args['RestartOnEachTest'].lower() == 'true':
				self.restartOnTest = True
			else:
				self.restartOnTest = False
		else:
			self.restartOnTest = False
		
		if args.has_key('FaultOnEarlyExit'):
			if args['FaultOnEarlyExit'].lower() == 'true':
				self.faultOnEarlyExit = True
			else:
				self.faultOnEarlyExit = False
		else:
			self.faultOnEarlyExit = True
		
		self.strangeExit = False
		self.command = args["Command"].replace("'''", "")
		self.args = None
		self.pid = None
		self.hProcess = None
		self.hThread = None
		self.dwProcessId = None
		self.dwThreadId = None
	
	def _StopProcess(self):
		
		if self.hProcess == None:
			return
		
		if self._IsProcessRunning():
			TerminateProcess(self.hProcess, 0)
		
		self.hProcess = None
		self.hThread = None
		self.dwProcessId = None
		self.dwThreadId = None
	
	def _StartProcess(self):
		if self.hProcess != None:
			self._StopProcess()
		
		(hProcess, hThread, dwProcessId, dwThreadId) = CreateProcess(None, self.command,
			None, None, 0, 0, None, None, STARTUPINFO())
		
		self.hProcess = hProcess
		self.hThread = hThread
		self.dwProcessId = dwProcessId
		self.dwThreadId = dwThreadId
	
	def _IsProcessRunning(self):
		if self.hProcess == None:
			return False
		
		ret = GetExitCodeProcess(self.hProcess)
		if ret != win32con.STILL_ACTIVE:
			return False
		
		ret = GetExitCodeThread(self.hThread)
		if ret != win32con.STILL_ACTIVE:
			return False
		
		return True
	
	def OnTestStarting(self):
		'''
		Called right before start of test.
		'''
		self.strangeExit = False
		if self.restartOnTest or not self._IsProcessRunning():
			self._StopProcess()
			self._StartProcess()
	
	def OnTestFinished(self):
		'''
		Called right after a test.
		'''
		if not self._IsProcessRunning():
			self.strangeExit = True
			
		if self.restartOnTest:
			self._StopProcess()
	
	def GetMonitorData(self):
		'''
		Get any monitored data.
		'''
		if self.strangeExit:
			return "Process exited early"
		
		return None
	
	def DetectedFault(self):
		'''
		Check if a fault was detected.  If the process exits
		with out our help we will report it as a fault.
		'''
		if self.faultOnEarlyExit:
			return not self._IsProcessRunning()
		
		else:
			return False
	
	def OnFault(self):
		'''
		Called when a fault was detected.
		'''
		self._StopProcess()
	
	def OnShutdown(self):
		'''
		Called when Agent is shutting down.
		'''
		self._StopProcess()

try:
	import win32serviceutils
except:
	pass

class WindowsService(Monitor):
	'''
	Controls a windows service making sure it's started,
	optionally restarting, etc.
	'''
	
	def __init__(self, args):
		if args.has_key('RestartOnEachTest'):
			if args['RestartOnEachTest'].lower() == 'true':
				self.restartOnTest = True
			else:
				self.restartOnTest = False
		else:
			self.restartOnTest = False
		
		if args.has_key('FaultOnEarlyExit'):
			if args['FaultOnEarlyExit'].lower() == 'true':
				self.faultOnEarlyExit = True
			else:
				self.faultOnEarlyExit = False
		else:
			self.faultOnEarlyExit = True
		
		self.strangeExit = False
		self.service = args["Service"].replace("'''", "")
		
		if args.has_key("Machine"):
			self.machine = args["Machine"].replace("'''", "")
		else:
			self.machine = None
	
	def _StopProcess(self):
		win32serviceutil.StopService(self.service, self.machine)
		
		while win32serviceutil.QueryServiceStatus(self.service, self.machine)[1] == 3:
			time.sleep(0.25)
		
		if win32serviceutil.QueryServiceStatus(self.service, self.machine)[1] != 1:
			raise Exception("WindowsService: Unable to stop service!")
	
	def _StartProcess(self):
		if self._IsProcessRunning():
			return
		
		win32serviceutil.StartService(self.service, self.machine)
		
		while win32serviceutil.QueryServiceStatus(self.service, self.machine)[1] == 2:
			time.sleep(0.25)
			
		if win32serviceutil.QueryServiceStatus(self.service, self.machine)[1] == 4:
			raise Exception("WindowsService: Unable to start service!")
		
	def _IsProcessRunning(self):
		if win32serviceutil.QueryServiceStatus(self.service, self.machine)[1] == 4:
			return True
		
		return False
	
	def OnTestStarting(self):
		'''
		Called right before start of test.
		'''
		self.strangeExit = False
		if self.restartOnTest or not self._IsProcessRunning():
			self._StopProcess()
			self._StartProcess()
	
	def OnTestFinished(self):
		'''
		Called right after a test.
		'''
		if not self._IsProcessRunning():
			self.strangeExit = True
		
		if self.restartOnTest:
			self._StopProcess()
	
	def GetMonitorData(self):
		'''
		Get any monitored data.
		'''
		if self.strangeExit:
			return "Process exited early"
		
		return None
	
	def DetectedFault(self):
		'''
		Check if a fault was detected.  If the process exits
		with out our help we will report it as a fault.
		'''
		if self.faultOnEarlyExit:
			return not self._IsProcessRunning()
		
		else:
			return False
	
	def OnFault(self):
		'''
		Called when a fault was detected.
		'''
		self._StopProcess()
	
	def OnShutdown(self):
		'''
		Called when Agent is shutting down.
		'''
		#self._StopProcess()
		pass

# end
