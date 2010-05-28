
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

# $Id: peach.py 1986 2010-03-05 07:19:57Z meddingt $

import struct, sys, time
from Peach.agent import Monitor
import os, re, pickle


class CrashReporter(Monitor):
	'''
	Monitor crash reporter for log files.
	'''
	def __init__(self, args):
		'''
		Constructor.  Arguments are supplied via the Peach XML
		file.
		
		@type	args: Dictionary
		@param	args: Dictionary of parameters
		'''
		
		if args.has_key('ProcessName'):
			self.ProcessName = str(args['ProcessName']).replace("'''", "")
		else:
			self.ProcessName = None
		
		if args.has_key('LogFolder'):
			self.logFolder = str(args['LogFolder']).replace("'''", "")
		else:
			self.logFolder = os.path.join(os.environ['HOME'], "Library/Logs/CrashReporter")
		
		if args.has_key('CrashWrangler') and str(args['CrashWrangler']).replace("'''", "").lower() == "false":
			self.crashWrangler = False
		else:
			self.crashWrangler = True
			
		# Our name for this monitor
		self._name = "CrashReporter"
		
		self.data = None
		self.startingFiles = None
	
	
	def OnTestStarting(self):
		'''
		Called right before start of test case or variation
		'''
		
		# Monitor folder
		self.startingFiles = os.listdir(self.logFolder)
	
	def OnTestFinished(self):
		'''
		Called right after a test case or varation
		'''
		pass
	
	def GetMonitorData(self):
		'''
		Get any monitored data from a test case.
		'''
		
		if self.data == None:
			return None
		
		return {"CrashReport.txt":self.data}
	
	def DetectedFault(self):
		'''
		Check if a fault was detected.
		'''
		
		try:
			# Give crash reporter time to find the crash
			time.sleep(0.25)
			time.sleep(0.25)
			
			#return self.eventFormulating.isSet()
			
			self.data = None
			for f in os.listdir(self.logFolder):
				if not f in self.startingFiles:
					fd = open(os.path.join(self.logFolder, f), "rb")
					self.data = fd.read()
					fd.close()
					
					return True
				
			
			return False
		
		except:
			print sys.exc_info()
		
		return False
	
	def OnFault(self):
		'''
		Called when a fault was detected.
		'''
		pass
	
	def OnShutdown(self):
		'''
		Called when Agent is shutting down, typically at end
		of a test run or when a Stop-Run occurs
		'''
		pass
	
	def StopRun(self):
		'''
		Return True to force test run to fail.  This
		should return True if an unrecoverable error
		occurs.
		'''
		return False
	
	def PublisherCall(self, method):
		'''
		Called when a call action is being performed.  Call
		actions are used to launch programs, this gives the
		monitor a chance to determin if it should be running
		the program under a debugger instead.
		
		Note: This is a bit of a hack to get this working
		'''
		pass


class CrashWrangler(Monitor):
	'''
	Use Apple Crash Wrangler to detect and sort crashes.
	'''
	
	def __init__(self, args):
		'''
		Constructor.  Arguments are supplied via the Peach XML
		file.
		
		@type	args: Dictionary
		@param	args: Dictionary of parameters
		'''
		
		if args.has_key('Command'):
			self.Command = str(args['Command']).replace("'''", "")
		else:
			raise PeachException("Error, CrashWrangler monitor requires 'Command' paramter.")
		
		if args.has_key('Arguments'):
			self.Arguments = str(args['Arguments']).replace("'''", "")
		else:
			self.Arguments = ""
		
		if args.has_key('StartOnCall'):
			self.StartOnCall = str(args['StartOnCall']).replace("'''", "")
		else:
			self.StartOnCall = None
		
		if args.has_key('UseDebugMalloc'):
			self.UseDebugMalloc = str(args['UseDebugMalloc']).replace("'''", "").lower() == 'true'
		else:
			self.UseDebugMalloc = False
		
		if args.has_key('ExecHandler'):
			self.ExecHandler = str(args['ExecHandler']).replace("'''", "")
		else:
			raise PeachException("Error, CrashWrangler monitor requires 'ExecHandler' parameter.")
		
		if args.has_key('ExploitableReads') and str(args['ExploitableReads']).replace("'''", "").lower() == "false":
			self.ExploitableReads = False
		else:
			self.ExploitableReads = True
		
		if args.has_key("NoCpuKill"):
			self.NoCpuKill = True
		else:
			self.NoCpuKill = False
			
		# Our name for this monitor
		self._name = "CrashWrangler"
		self.pid = None
	
	
	def OnTestStarting(self):
		'''
		Called right before start of test case or variation
		'''
		
		if not self.StartOnCall:
			if not self._IsRunning():
				self._StartProcess()
	
	def OnTestFinished(self):
		'''
		Called right after a test case or varation
		'''
		if self.StartOnCall and self._IsRunning():
			self._StopProcess()
	
	def GetMonitorData(self):
		'''
		Get any monitored data from a test case.
		'''

		if os.path.exists("cw.log"):
			fd = open("cw.log", "rb")
			data = fd.read()
			fd.close()
			
			bucket = "Unknown"
			
			if re.match(r".*:is_exploitable=\s*no\s*:.*", data):
				bucket = "NotExploitable"
			elif re.match(r".*:is_exploitable=\s*yes\s*:.*", data):
				bucket = "Exploitable"
			
			if data.find("exception=EXC_BAD_ACCESS:") > -1:
				bucket += "_BadAccess"
				
				if data.find(":access_type=read:") > -1:
					bucket += "_Read"
				elif data.find(":access_type=write:") > -1:
					bucket += "_Write"
				elif data.find(":access_type=exec:") > -1:
					bucket += "_Exec"
				elif data.find(":access_type=recursion:") > -1:
					bucket += "_Recursion"
				elif data.find(":access_type=unknown:") > -1:
					bucket += "_Unknown"
			
			elif data.find("exception=EXC_BAD_INSTRUCTION:") > -1:
				bucket += "_BadInstruction"
			elif data.find("exception=EXC_ARITHMETIC:") > -1:
				bucket += "_Arithmetic"
			elif data.find("exception=EXC_CRASH:") > -1:
				bucket += "_Crash"

			# Locate crashing address to help bucket duplicates
			try:
				threadId = re.search(r"Crashed Thread:\s+(\d+)", data).group(1)
				threadPos = data.find("Thread "+threadId+" Crashed:")
				crashAddress = re.search(r"(0x[0-9a-fA-F]+)", data[threadPos:]).group(1)
				
				bucket += "_" + crashAddress
			except:
				print sys.exc_info()
				
			try:
				os.unlink("cw.log")
				os.unlink("cw.lck")
			except:
				pass
			
			return {"CrashWrangler.txt":data, "Bucket":bucket}
		
		return None
	
	def DetectedFault(self):
		'''
		Check if a fault was detected.
		'''
		
		try:
			# Give crash wrangler time to find the crash
			time.sleep(0.25)
			time.sleep(0.25)
			
			return os.path.exists("cw.log")
		
		except:
			print sys.exc_info()
		
		return False
	
	def OnFault(self):
		'''
		Called when a fault was detected.
		'''
		pass
	
	def OnShutdown(self):
		'''
		Called when Agent is shutting down, typically at end
		of a test run or when a Stop-Run occurs
		'''
		self._StopProcess()
	
	def StopRun(self):
		'''
		Return True to force test run to fail.  This
		should return True if an unrecoverable error
		occurs.
		'''
		return False
	
	def PublisherCall(self, method):
		'''
		Called when a call action is being performed.  Call
		actions are used to launch programs, this gives the
		monitor a chance to determin if it should be running
		the program under a debugger instead.
		
		Note: This is a bit of a hack to get this working
		'''
		
		if self.StartOnCall:
			if self.StartOnCall == method:
				self._StartProcess()
			
			elif self.StartOnCall+"_isrunning" == method:
				if self._IsRunning():
					
					if not self.NoCpuKill:
						cpu = None
						try:
							os.system("ps -o pcpu %d > .cpu" % self.pid2)
							fd = open(".cpu", "rb")
							data = fd.read()
							fd.close()
							os.unlink(".cpu")
							
							cpu = re.search(r"\s*(\d+\.\d+)", data).group(1)
							
							if cpu.startswith("0.") and not os.path.exists("cw.lck"):
								
								time.sleep(0.25)
								
								# Check and see if crashwrangler is going
								if os.path.exists("cw.lck"):
									return True
								
								print "CrashWrangler: PCPU is low (%s), stopping process" % cpu
								self._StopProcess()
								return False
						
						except:
							print sys.exc_info()
					
					return True
				
				else:
					return False
					

		
		return None
		
		
	def _StartProcess(self):

		print ">> _StartProcess"
		
		if self._IsRunning():
			return

		args = ["/usr/bin/env", "CW_LOG_PATH=cw.log", "CW_PID_FILE=cw.pid"]
		
		if self.UseDebugMalloc:
			args.append("CW_USE_GMAL=1")
		if self.ExploitableReads:
			args.append("CW_EXPLOITABLE_READS=1")
		
		args.append(self.ExecHandler)
		args.append(self.Command)
		for a in self.Arguments.split(" "):
			args.append(a)
		
		print "CrashWrangler._StartProcess():", args

		# Remove any existing lock files
		try:
			os.unlink("cw.lck")
		except:
			pass
		
		# Remove any existing log files
		try:
			os.unlink("cw.lock")
		except:
			pass
		
		# Remove any existing pid files
		try:
			os.unlink("cw.pid")
		except:
			pass
		
		self.pid = os.spawnv(os.P_NOWAIT, "/usr/bin/env", args)
		
		while not os.path.exists("cw.pid"):
			time.sleep(0.15)
		
		fd = open("cw.pid", "rb")
		self.pid2 = int(fd.read())
		fd.close()
		
		print "_StartProcess(): Pid2: ", self.pid2
		
		try:
			os.unlink("cw.pid")
		except:
			pass
		
	
	def _StopProcess(self):
		print ">> _StopProcess"
		if self.pid:

			try:
				# Verify if process is still running
				(pid1, ret) = os.waitpid(self.pid, os.WNOHANG)
				if not (pid1 == 0 and ret == 0):
					self.pid = None
					return

				# Check for cw.lck before killing
				while os.path.exists("cw.lck"):
					
					time.sleep(0.25)
					
					(pid1, ret) = os.waitpid(self.pid, os.WNOHANG)
					if not (pid1 == 0 and ret == 0):
						self.pid = None
						return
			
			except:
				return
			
			try:
				# Kill process with signal
				import signal
				os.kill(self.pid2, signal.SIGTERM)
				time.sleep(0.25)
				os.kill(self.pid2, signal.SIGKILL)
			except:
				pass
			
			try:
				# Kill process with signal
				import signal
				os.kill(self.pid, signal.SIGTERM)
				time.sleep(0.25)
				os.kill(self.pid, signal.SIGKILL)
			except:
				pass
			
			# Prevent Zombies!
			os.wait()
			
			self.pid = None
	
	
	def _IsRunning(self):
		if self.pid:
			try:
				(pid1, ret) = os.waitpid(self.pid, os.WNOHANG)
				if pid1 == 0 and ret == 0:
					print "_IsRunning: True"
					return True
			except:
				pass
		
		print "_IsRunning: False"
		return False
	

# end
