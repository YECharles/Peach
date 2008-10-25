
'''
Debugging monitor for Peach Agent.  Uses pydbgeng to monitor processes and
detect faults.  Would be nice to also eventually do other things like
"if we hit this method" or whatever.

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

try:
	import pydbg, win32process, win32api, win32pdhutil, win32con
	import struct, sys, time
	from threading import Thread, Event, Lock
	from Peach.agent import Monitor
	
	import struct, sys, time,os
	import comtypes
	from ctypes import *
	from comtypes import HRESULT, COMError
	from comtypes.client import CreateObject, GetEvents, PumpEvents#, ReleaseEvents
	from comtypes.hresult import S_OK, E_FAIL, E_UNEXPECTED, E_INVALIDARG
	from comtypes.automation import IID
	
	class WindowsAppVerifier(Monitor):
		'''
		Agent that uses the Microsoft AppVerifier tool to detect faults on
		running processes.  AppVerifier can be downloaded from Microsoft via
		the following url: http://www.microsoft.com/technet/prodtechnol/windows/appcompatibility/appverifier.mspx
		'''
		
		def __init__(self, args):
			self._image = str(args['Application']).replace("'''", "")
			
			self.checks = ["COM", "Exceptions", "Handles", "Heaps", "Locks", "Memory", "RPC", "Threadpool", "TLS"]
			self.stops = {}
			# self.stops = {"COM":["10","1032"]}
			
			if args.has_key("Checks"):
				self.checks = args["Checks"].replace("'''", "").split(",")
				for i in self.range(checks):
					self.checks[i] = self.checks[i].strip()
			
			if args.has_key("Stops"):
				checks = args["Stops"].replace("'''", "").split(";")
				for check in checks:
					check, stops = check.split(":")
					self.stops[check] = stops.split(",")
				
			print "WindowsAppVerifier: Enabling the following Checks:"
			for c in self.checks:
				print "WindowsAppVerifier: Check: %s" % c
			
			print "WindowsAppVerifier: Disabling the following Stops:"
			for c in self.stops:
				for s in self.stops[c]:
					print "%s: %s" % (c, s)
			
			self._appManager = CreateObject("{597c1ef7-fc28-451e-8273-417c6c9244ed}")
			
			self._RemoveImageLogs(self._image)
			self._DisableImage(self._image)
		
		def _EnableImage(self, image):
			'''
			Enables the default checks for an image (exe).
			'''
			image = self._appManager.Images.Add(image)
			for check in image.Checks:
				if check.Name in self.checks:
					check.Enabled = True
				else:
					check.Enabled = False
				
				if self.stops.has_key(check.Name):
					stops = self.stops[check.Name]
					for stop in check.Stops:
						if str(stop.StopCode) in stops:
							stop.Active = False
		
		def _DisableImage(self, image):
			try:
				self._appManager.Images.Remove(image)
			except:
				pass
		
		def _GetImageLogs(self, image):
			'''
			Get lof files for an image
			'''
			
			logFiles = []
			for log in self._appManager.Logs(image):
				
				try:
					os.unlink("appVerifierTmp.xml")
				except:
					pass
				
				try:
					log.SaveAsXML("appVerifierTmp.xml", "SRV*http://msdl.microsoft.com/download/symbols")
				except:
					pass
				
				fd = open("appVerifierTmp.xml","rb+")
				logFiles.append(fd.read())
				fd.close()
				os.unlink("appVerifierTmp.xml")
			
			return logFiles
		
		def _RemoveImageLogs(self, image):
			try:
				logs = self._appManager.Logs(image)
				for idx in range(logs.Count):
					try:
						logs.Remove(0)
					except:
						print "Warning: Caught error removing App Verifier logs."
						pass
			except:
				pass
			
		def OnTestStarting(self):
			'''
			Called right before start of test.
			'''
			self._EnableImage(self._image)
		
		def OnTestFinished(self):
			'''
			Called right after a test.
			'''
			self._DisableImage(self._image)
		
		def GetMonitorData(self):
			'''
			Get any monitored data.
			'''
			ret = {}
			count = 0
			logs = self.imageLogs
			
			#print "WindowsAppVerifier.GetMonitorData: Waiting for data to come in"
			#while logs == None or len(logs) < 1:
			#	time.sleep(0.25)
			#	logs = self.imageLogs = self._GetImageLogs(self._image)
			if logs == None:
				logs = self.imageLogs = self._GetImageLogs(self._image)
			
			self._RemoveImageLogs(self._image)
			
			for log in logs:
				count += 1
				ret["AppVerifier_%d.xml" % count] = log
			
			return ret
		
		def DetectedFault(self):
			'''
			Check if a fault was detected.
			'''
			
			time.sleep(0.15) # Pause a sec
			
			self.imageLogs = self._GetImageLogs(self._image)
			self._RemoveImageLogs(self._image)
			
			for log in self.imageLogs:
				if len(log) > 300:
					print "WindowsAppVerifier: Detected fault"
					return True
			
			self.imageLogs = None
			print "WindowsAppVerifier: Did not detect fault"
			return False
		
		def OnFault(self):
			'''
			Called when a fault was detected.
			'''
			pass
		
		def OnShutdown(self):
			'''
			Called when Agent is shutting down.
			'''
			try:
				self._DisableImage(self._image)
			except:
				pass
	
	
	def handleAccessViolation(dbg):
		#print "!!!!!!!!! AV !!!!!!!!!!!!!!!"
		crash_bin = crash_binning()
		crash_bin.record_crash(dbg)
		
		WindowsDebugger.lock.acquire()
		WindowsDebugger.crashInfo = crash_bin.crash_synopsis()
		WindowsDebugger.fault = True
		WindowsDebugger.lock.release()
		
		dbg.terminate_process()
	
	class WindowsDebuggerThread(Thread):
		def run(self):
			print "WindowsDebuggerThread: Starting process"
			self.dbg = pydbg.pydbg()
			self.dbg.set_callback(pydbg.EXCEPTION_ACCESS_VIOLATION, handleAccessViolation)
			
			if self._command != None:
				self.dbg.load(self._command, self._params)
			else:
				self.dbg.attach(self._pid)
			
			WindowsDebugger.started.set()
			self.dbg.debug_event_loop()
	
	class WindowsDebugger(Monitor, Thread):
		'''
		Windows debugger monitor.  Uses PaiMei pydbg module
		'''
		def __init__(self, args):
			Thread.__init__(self)
			
			self._stopRun = False
			WindowsDebugger.started = Event()
			WindowsDebugger.lock = Lock()
			WindowsDebugger.crashInfo = None
			WindowsDebugger.fault = False
			WindowsDebugger.started.clear()
			
			if args.has_key('Command'):
				self._command = str(args['Command']).replace("'''", "\"")
				self._params = str(args['Params']).replace("'''", "\"")
				self._pid = None
				print "Command: [%s]" % self._command
			
			elif args.has_key('ProcessName'):
				self._command = None
				self._params = None
				self._pid = self.GetProcessIdByName(str(args['ProcessName']).replace("'''", ""))
			
			else:
				raise Exception("Unable to create WindowsDebugger!  Error in params!")
			
			self._StartDebugger()
		
		def _StartDebugger(self):
			WindowsDebugger.crashInfo = None
			WindowsDebugger.fault = False
			WindowsDebugger.started.clear()
			
			self.thread = WindowsDebuggerThread()
			
			self.thread._command = self._command
			self.thread._params = self._params
			self.thread._pid = self._pid
			
			self.thread.start()
			WindowsDebugger.started.wait()
		
		def _StopDebugger(self):
			if self.thread.isAlive():
				try:
					win32process.TerminateProcess(self.thread.dbg.h_process, 0)
				except:
					pass
			
			self.thread.join()
		
		def GetProcessIdByName(self, str):
			'''
			Try and get pid for a process by name.
			'''
			
			try:
				win32pdhutil.GetPerformanceAttributes('Process','ID Process',str)
			except:
				sys.stdout.write("WindowsDebugger: Unable to locate process [%s]\n" % str)
				raise
			
			pids = win32pdhutil.FindPerformanceAttributesByName(str)
			
			# If _my_ pid in there, remove it!
			try:
				pids.remove(win32api.GetCurrentProcessId())
			except ValueError:
				pass
			
			return pids[0]
		
		def OnTestStarting(self):
			'''
			Called right before start of test.
			'''
			if not self.thread.isAlive():
				self.thread.join()
				self._StartDebugger()
		
		def OnTestFinished(self):
			'''
			Called right after a test.
			'''
			pass
		
		def GetMonitorData(self):
			'''
			Get any monitored data.
			'''
			WindowsDebugger.lock.acquire()
			if WindowsDebugger.crashInfo != None:
				ret = WindowsDebugger.crashInfo
				WindowsDebugger.crashInfo = None
				WindowsDebugger.lock.release()
				return { 'StackTrace.txt' : ret }
			
			WindowsDebugger.lock.release()
			return None
		
		def DetectedFault(self):
			'''
			Check if a fault was detected.
			'''
			time.sleep(0.1)
			WindowsDebugger.lock.acquire()
			if WindowsDebugger.fault or not self.thread.isAlive():
				print ">>>>>> RETURNING FAULT <<<<<<<<<"
				WindowsDebugger.fault = False
				WindowsDebugger.lock.release()
				return True
			
			WindowsDebugger.lock.release()
			return False
		
		def OnFault(self):
			'''
			Called when a fault was detected.
			'''
			self._StopDebugger()
			
			# If we are attaching we cannot restart
			if self._pid != None:
				self._stopRun = True
			
		def OnShutdown(self):
			'''
			Called when Agent is shutting down.
			'''
			self._StopDebugger()
			
		def StopRun(self):
			return self._stopRun
	
	## ############################################################################
	## ############################################################################
	## ############################################################################
	
	##
	## The following code from here 
	## is taken verbatum from PaiMei v1.1 rev122 and is licensed
	## using the GNU General Public License 2.0 or later
	##
	
	'''
	@author:       Pedram Amini
	@license:      GNU General Public License 2.0 or later
	@contact:      pedram.amini@gmail.com
	@organization: www.openrce.org
	'''
	
	class __crash_bin_struct__:
		exception_address   = 0
		write_violation     = 0
		violation_address   = 0
		violation_thread_id = 0
		context             = None
		context_dump        = None
		disasm              = None
		disasm_around       = []
		stack_unwind        = []
		seh_unwind          = []
		extra               = None
	
	
	class crash_binning:
		'''
		@todo: Add persistant data support (disk / MySQL)
		'''
	
		bins       = {}
		last_crash = None
		pydbg      = None
	
		####################################################################################################################
		def __init__ (self):
			'''
			'''
	
			self.bins       = {}
			self.last_crash = None
			self.pydbg      = None
	
	
		####################################################################################################################
		def record_crash (self, pydbg, extra=None):
			'''
			Given a PyDbg instantiation that at the current time is assumed to have "crashed" (access violation for example)
			record various details such as the disassemly around the violating address, the ID of the offending thread, the
			call stack and the SEH unwind. Store the recorded data in an internal dictionary, binning them by the exception
			address.
	
			@type  pydbg: pydbg
			@param pydbg: Instance of pydbg
			@type  extra: Mixed
			@param extra: (Optional, Def=None) Whatever extra data you want to store with this bin
			'''
	
			self.pydbg = pydbg
			crash = __crash_bin_struct__()
	
			crash.exception_address   = pydbg.dbg.u.Exception.ExceptionRecord.ExceptionAddress
			crash.write_violation     = pydbg.dbg.u.Exception.ExceptionRecord.ExceptionInformation[0]
			crash.violation_address   = pydbg.dbg.u.Exception.ExceptionRecord.ExceptionInformation[1]
			crash.violation_thread_id = pydbg.dbg.dwThreadId
			crash.context             = pydbg.context
			crash.context_dump        = pydbg.dump_context(pydbg.context, print_dots=False)
			crash.disasm              = pydbg.disasm(crash.exception_address)
			crash.disasm_around       = pydbg.disasm_around(crash.exception_address)
			crash.stack_unwind        = pydbg.stack_unwind()
			crash.seh_unwind          = pydbg.seh_unwind()
			crash.extra               = extra
	
			if not self.bins.has_key(crash.exception_address):
				self.bins[crash.exception_address] = []
	
			self.bins[crash.exception_address].append(crash)
			self.last_crash = crash
	
	
		####################################################################################################################
		def crash_synopsis (self):
			'''
			For the last recorded crash, generate and return a report containing the disassemly around the violating
			address, the ID of the offending thread, the call stack and the SEH unwind.
			'''
	
			if self.last_crash.write_violation:
				direction = "write to"
			else:
				direction = "read from"
	
			synopsis = "0x%08x %s from thread %d caused access violation\nwhen attempting to %s 0x%08x\n\n" % \
				(
					self.last_crash.exception_address,      \
					self.last_crash.disasm,                 \
					self.last_crash.violation_thread_id,    \
					direction,                              \
					self.last_crash.violation_address       \
				)
	
			synopsis += self.last_crash.context_dump
	
			synopsis += "\ndisasm around:\n"
			for (ea, inst) in self.last_crash.disasm_around:
				synopsis += "\t0x%08x %s\n" % (ea, inst)
	
			if len(self.last_crash.stack_unwind):
				synopsis += "\nstack unwind:\n"
				for addr in self.last_crash.stack_unwind:
					synopsis += "\t%08x\n" % addr
	
			if len(self.last_crash.seh_unwind):
				synopsis += "\nSEH unwind:\n"
				for (addr, handler) in self.last_crash.seh_unwind:
					try:
						disasm = self.pydbg.disasm(handler)
					except:
						disasm = "[INVALID]"
	
					synopsis +=  "\t%08x -> %08x: %s\n" % (addr, handler, disasm)
	
			return synopsis + "\n"

except:
	pass
	
try:
	
	# ###############################################################################################
	# ###############################################################################################
	# ###############################################################################################
	# ###############################################################################################

	import PyDbgEng
	import comtypes
	from ctypes import *
	from comtypes import HRESULT, COMError
	from comtypes.client import CreateObject, GetEvents, PumpEvents#, ReleaseEvents
	from comtypes.hresult import S_OK
	from comtypes.automation import IID
	from comtypes.gen import DbgEng

	class _DbgEventHandler(PyDbgEng.IDebugOutputCallbacksSink, PyDbgEng.IDebugEventCallbacksSink):
		
		buff = ''
		
		def Output(self, this, Mask, Text):
			#sys.stdout.write(Text)
			_DbgEventHandler.buff += Text
		
		def GetInterestMask(self):
			#sys.stdout.write("_DbgEventHandler::GetInterestMask\n")
			return PyDbgEng.DbgEng.DEBUG_EVENT_EXCEPTION | PyDbgEng.DbgEng.DEBUG_FILTER_INITIAL_BREAKPOINT
		
		def Exception(self, dbg, ExceptionCode, ExceptionFlags, ExceptionRecord,
				ExceptionAddress, NumberParameters, ExceptionInformation0, ExceptionInformation1,
				ExceptionInformation2, ExceptionInformation3, ExceptionInformation4,
				ExceptionInformation5, ExceptionInformation6, ExceptionInformation7,
				ExceptionInformation8, ExceptionInformation9, ExceptionInformation10,
				ExceptionInformation11, ExceptionInformation12, ExceptionInformation13,
				ExceptionInformation14, FirstChance):
			
			if WindowsDebugEngine.handlingFault.isSet() or WindowsDebugEngine.handledFault.isSet():
				# We are already handling, so skip
				#sys.stdout.write("_DbgEventHandler::Exception(): handlingFault set, skipping.\n")
				return DbgEng.DEBUG_STATUS_NO_CHANGE
			
			try:
				
				WindowsDebugEngine.handlingFault.set()
				
				# 1. Calculate no. of frames
				#sys.stdout.write("_DbgEventHandler::Exception(): 1\n")
				
				frames_filled = 0
				stack_frames = dbg.get_stack_trace(100)
				for i in range(100):
					eip = stack_frames[i].InstructionOffset
					if (eip == 0):
						break
					frames_filled += 1
				
				# 2. Output registers
				#sys.stdout.write("_DbgEventHandler::Exception(): 2\n")
				
				dbg.idebug_registers.OutputRegisters(DbgEng.DEBUG_OUTCTL_THIS_CLIENT, DbgEng.DEBUG_REGISTERS_ALL)
				_DbgEventHandler.buff += "\n\n"
				
				# 3. Ouput stack trace
				#sys.stdout.write("_DbgEventHandler::Exception(): 3\n")
				
				frames_count = 100
				frames_buffer = create_string_buffer( frames_count * sizeof(DbgEng._DEBUG_STACK_FRAME) )
				frames_buffer_ptr = cast(frames_buffer, POINTER(DbgEng._DEBUG_STACK_FRAME))
				
				dbg.idebug_control.GetStackTrace(0, 0, 0, frames_buffer_ptr, frames_count)
				dbg.idebug_control.OutputStackTrace(DbgEng.DEBUG_OUTCTL_THIS_CLIENT, frames_buffer_ptr, frames_filled,
					DbgEng.DEBUG_STACK_ARGUMENTS |
					DbgEng.DEBUG_STACK_FUNCTION_INFO |
					DbgEng.DEBUG_STACK_SOURCE_LINE |
					DbgEng.DEBUG_STACK_FRAME_ADDRESSES |
					DbgEng.DEBUG_STACK_COLUMN_NAMES |
					DbgEng.DEBUG_STACK_FRAME_NUMBERS |
					DbgEng.DEBUG_STACK_PARAMETERS )
				
				_DbgEventHandler.buff += "\n\n"
				
				# 4. Write dump file
				#sys.stdout.write("_DbgEventHandler::Exception(): 4\n")
				
				dbg.idebug_client.WriteDumpFile(c_char_p("dumpfile.core"), DbgEng.DEBUG_DUMP_SMALL)
				minidump = None
				
				try:
					f = open('dumpfile.core', 'rb+')
					minidump = f.read()
					f.close()
					
				except:
					pass
				
				# 5. !analyze -v
				
				#sys.stdout.write("_DbgEventHandler::Exception(): 5\n")
				handle = dbg.idebug_control.AddExtension(c_char_p("C:\\Program Files\\Debugging Tools for Windows\\winext\\ext.dll"), 0)
				try:
					dbg.idebug_control.Execute(DbgEng.DEBUG_OUTCTL_THIS_CLIENT, c_char_p("!analyze -v"), DbgEng.DEBUG_EXECUTE_ECHO)
				except:
					pass
				
				dbg.idebug_control.RemoveExtension(handle)
				
				WindowsDebugEngine.lock.acquire()
				
				if minidump:
					WindowsDebugEngine.crashInfo = { 'StackTrace.txt' : _DbgEventHandler.buff, 'MiniDump.dmp' : minidump }
				else:
					WindowsDebugEngine.crashInfo = { 'StackTrace.txt' : _DbgEventHandler.buff }
				
				WindowsDebugEngine.fault = True
				WindowsDebugEngine.lock.release()
				
			except:
				sys.stdout.write(repr(sys.exc_info()[0]) + "\n")
				raise
			
			WindowsDebugEngine.handledFault.set()
			
			#return DbgEng.DEBUG_STATUS_BREAK
			return DbgEng.DEBUG_STATUS_NO_CHANGE


	class WindowsDebugEngineThread(Thread):
		def run(self):
			WindowsDebugEngine.handlingFault.clear()
			
			# Hack for comtypes early version
			comtypes._ole32.CoInitializeEx(None, comtypes.COINIT_APARTMENTTHREADED)
			
			self._eventHandler = _DbgEventHandler()
			
			if self.KernelConnectionString:
				self.dbg = PyDbgEng.KernelAttacher(  connection_string = connection_string,
					follow_forks = True,
					event_callbacks_sink = self._eventHandler,
					output_callbacks_sink = self._eventHandler,
					symbols_path = self.SymbolsPath)
			
			elif self.CommandLine:
				self.dbg = PyDbgEng.ProcessCreator(command_line = self.CommandLine,
					follow_forks = True,
					event_callbacks_sink = self._eventHandler,
					output_callbacks_sink = self._eventHandler,
					symbols_path = self.SymbolsPath)
			
			elif self.ProcessName:
				self.dbg = PyDbgEng.ProcessAttacher(pid = self.GetProcessIdByName(self.ProcessName),
					event_callbacks_sink = self._eventHandler,
					output_callbacks_sink = self._eventHandler,
					symbols_path = self.SymbolsPath)
			
			else:
				raise Exception("Didn't find way to start debugger... bye bye!!")
			
			WindowsDebugEngineThread.Quit = Event()
			WindowsDebugEngine.started.set()
			
			self.dbg.event_loop_with_user_callback(self.Callback, 10)
			self.dbg.__del__()
		
		def Callback(self = None, stuff = None, stuff2 = None):
			PumpEvents(0.1)
			if WindowsDebugEngineThread.Quit.isSet():
				self.dbg.idebug_client.TerminateProcesses()
				return True
		
		def GetProcessIdByName(self, procname):
			'''
			Try and get pid for a process by name.
			'''
			
			ourPid = -1
			procname = procname.lower()
			
			try:
				ourPid = win32api.GetCurrentProcessId()
			
			except:
				pass
			
			pids = win32process.EnumProcesses()
			for pid in pids:
				if ourPid == pid:
					continue
				
			try:
				hPid = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ, 0, pid)
					
				try:
					mids = win32process.EnumProcessModules(hPid)
					for mid in mids:
						name = str(win32process.GetModuleFileNameEx(hPid, mid))
						#print "Filename: ", name
						if name.lower().find(procname) != -1:
							return pid
					
				finally:
					win32api.CloseHandle(hPid)
			except:
				pass
			
			return None
	
	class WindowsDebugEngine(Monitor, Thread):
		'''
		Windows debugger agent.  This debugger agent is based on the windbg engine and
		supports the following features:
			
			* User mode debugging
			* Kernel mode debugging
			* x86 and x64
			* Symbols and symbol server
		
		'''
		def __init__(self, args):
			Thread.__init__(self)
			WindowsDebugEngine.started = Event()
			
			# Set at start of exception handling
			WindowsDebugEngine.handlingFault = Event()
			# Set when collection finished
			WindowsDebugEngine.handledFault = Event()
			WindowsDebugEngine.lock = Lock()
			WindowsDebugEngine.crashInfo = None
			WindowsDebugEngine.fault = False
			self.thread = None
			
			if args.has_key('CommandLine'):
				self.CommandLine = str(args['CommandLine']).replace("'''", "")
			else:
				self.CommandLine = None
			
			if args.has_key('ProcessName'):
				self.ProcessName = str(args['ProcessName']).replace("'''", "")
			else:
				self.ProcessName = None
			
			if args.has_key('KernelConnectionString'):
				self.KernelConnectionString = str(args['KernelConnectionString']).replace("'''", "")
			else:
				self.KernelConnectionString = None
			
			if args.has_key('SymbolsPath'):
				self.SymbolsPath = str(args['SymbolsPath']).replace("'''", "")
			else:
				self.SymbolsPath = "SRV*http://msdl.microsoft.com/download/symbols"
			
			if self.CommandLine == None and self.ProcessName == None and self.KernelConnectionString == None:
				raise Exception("Unable to create WindowsDebugger Instance!!!!!")
			
		
		def _StartDebugger(self):
			
			# Need to reinitialize in another thread.
			# Note: This must occur on every PyDbgEng restart to properly
			#       clear out the old state.  A matching initialize call
			#       is performed in the created thread.
			comtypes._ole32.CoUninitialize()
			
			# Clear all our event handlers
			WindowsDebugEngine.started.clear()
			WindowsDebugEngine.handlingFault.clear()
			WindowsDebugEngine.handledFault.clear()
			
			self.thread = WindowsDebugEngineThread()
			
			self.thread.CommandLine = self.CommandLine
			self.thread.ProcessName = self.ProcessName
			self.thread.KernelConnectionString = self.KernelConnectionString
			self.thread.SymbolsPath = self.SymbolsPath
			
			# Kick off our thread:
			self.thread.start()
			
			# Wait it...!
			WindowsDebugEngine.started.wait()
			
			# Let things get spun up
			time.sleep(2)
		
		def _StopDebugger(self):
			print "_StopDebugger"
			if self.thread.isAlive():
				WindowsDebugEngineThread.Quit.set()
				WindowsDebugEngine.started.clear()
				self.thread.join()
				time.sleep(0.25) # Take a breath
		
		def _IsDebuggerAlive(self):
			return self.thread and self.thread.isAlive()
		
		def OnTestStarting(self):
			'''
			Called right before start of test.
			'''
			if not self._IsDebuggerAlive():
				self._StartDebugger()
		
		def GetMonitorData(self):
			'''
			Get any monitored data.
			'''
			WindowsDebugEngine.lock.acquire()
			if WindowsDebugEngine.crashInfo != None:
				ret = WindowsDebugEngine.crashInfo
				WindowsDebugEngine.crashInfo = None
				_DbgEventHandler.buff = ""
				WindowsDebugEngine.lock.release()
				return ret
			
			WindowsDebugEngine.lock.release()
			return None
		
		def DetectedFault(self):
			'''
			Check if a fault was detected.
			'''
			
			time.sleep(0.15)

			if not WindowsDebugEngine.handlingFault.isSet():
				return False
			
			WindowsDebugEngine.handledFault.wait()
			WindowsDebugEngine.lock.acquire()
			
			if WindowsDebugEngine.fault or not self.thread.isAlive():
				print ">>>>>> RETURNING FAULT <<<<<<<<<"
				WindowsDebugEngine.fault = False
				WindowsDebugEngine.lock.release()
				return True
			
			WindowsDebugEngine.lock.release()
			return False
		
		def OnFault(self):
			'''
			Called when a fault was detected.
			'''
			self._StopDebugger()
		
		def OnShutdown(self):
			'''
			Called when Agent is shutting down.
			'''
			self._StopDebugger()

except:
	pass
	#raise

try:
	
	from pygdb.mi import Gdb
	
	class _GdbThread(Thread):
		
		def __init__(self):
			Thread.__init__(self)
		
		def run(self):
			
			self.gdb = gdb = Gdb(None)
			gdb.file(self._command)
			#gdb.start(args=self._params).wait()
			gdb.run(self._params).wait()
			
			if UnixGdb.quit.isSet():
				return
			
			UnixGdb.handlingFault.set()
			
			buff = "Crash output from GDB\n"
			buff+= "=====================\n\n"
			buff+= "break: reason: %s, thread-id: %s\n\n" % (result.reason, result.thread_id)
			buff+= self._getLocals(gdb)
			buff+= "\n-------------------\n"
			buff+= self._getArguments(gdb)
			buff+= "\n-------------------\n"
			buff+= self._getStack(gdb)
			buff+= "\n-------------------\n"
			buff+= self._getRegisters(gdb)
			
			gdb.quit()
			
			UnixGdb.lock.acquire()
			UnixGdb.creashInfo = { 'DebuggerOutput.txt' : buff }
			UnixGdb.fault = True
			UnixGdb.lock.release()
			UnixGdb.handledFault.set()

		def _getLocals(self, gdb):
			buff = "Frame Locals:\n"
			try:
				result = gdb.stack_list_locals().wait()
				for local in resul.locals:
					buff += "\t%s = %s\n" % (local.name, local.value)
			except:
				pass
			
			return buff
		
		def _getArguments(self, gdb):
			buff = "Frame Arguments:\n"
			try:
				result = gdb.stack_list_arguments().wait()
				for frame in result.stack_args.frame:
					buff += "\tframe: " + frame.level + "\n"
					for arg in frame.args:
						buff += "\t\t%s = %s\n" % (arg.name, arg.value)
			except:
				pass
			
			return buff
		
		def _getStack(self, gdb):
			buff = "Stack:\n"
			try:
				result = gdb.stack_list_frames().wait()
				for frame in result.stack.frame:
					buff += "\t%s, at %s:%s\n" % (frame.func, frame.file, frame.line)
			except:
				pass
			
			return buff
		
		def _getRegisters(self, gdb):
			buff = "Registers:\n"
			try:
				names = gdb.data_list_register_names().wait()
				result = gdb.data_list_register_values(regno=registers).wait()
				for register in result.register_values:
					name = names.register_names[int(register.number)]
					buff += "\t%s: %s\n" % (name, register.value)
			except:
				pass
			
			return buff
	
	class UnixGdb(Monitor):
		'''
		Unix GDB monitor.  This debugger monitor uses the gdb
		debugger via pygdb wrapper.  Tested under Linux and OS X.
		
			* Collect core files
			* User mode debugging
			* Capturing stack trace, registers, etc
			* Symbols is available
		'''
		
		def __init__(self, args):
			
			UnixGdb.quit = Event()
			UnixGdb.started = Event()
			UnixGdb.handlingFault = Event()
			UnixGdb.handledFault = Event()
			UnixGdb.lock = Lock()
			UnixGdb.crashInfo = None
			UnixGdb.fault = False
			
			if args.has_key('Command'):
				self._command = str(args['Command']).replace("'''", "\"")
				self._params = str(args['Params']).replace("'''", "\"")
				self._pid = None
			
			elif args.has_key('ProcessName'):
				self._command = None
				self._params = None
				self._pid = self.GetProcessIdByName(str(args['ProcessName']).replace("'''", "\""))
			
			else:
				raise Exception("Unable to create UnixGdb!  Error in params!")
		
		def _StartDebugger(self):
			UnixGdb.quit.clear()
			UnixGdb.started.clear()
			UnixGdb.handlingFault.clear()
			UnixGdb.handledFault.clear()
			UnixGdb.fault = False
			UnixGdb.crashInfo = None
			
			self.thread = _GdbThread()
			self.thread._command = self._command
			self.thread._params = self._params
			self.thread._pid = self._pid
			
			self.thread.start()
			UnixGdb.started.wait()
			time.sleep(2)	# Let things spin up!
		
		def _StopDebugger(self):
			
			if self.thread.isAlive():
				UnixGdb.quit.set()
				UnixGdb.started.clear()
				self.thread.gdb.quit()
				self.thread.join()
				time.sleep(0.25)	# Take a breath
		
		def _IsDebuggerAlive(seld):
			return self.thread != None and self.thread.isAlive()
		
		def OnTestStarting(self):
			'''
			Called right before start of test.
			'''
			if not self._IsDebuggerAlive():
				self._StartDebugger()
		
		def GetMonitorData(self):
			'''
			Get any monitored data.
			'''
			UnixGdb.lock.acquire()
			if UnixGdb.crashInfo != None:
				ret = UnixGdb.crashInfo
				UnixGdb.crashInfo = None
				_GdbEventHandler.buff = ""
				UnixGdb.lock.release()
				return ret
			
			UnixGdb.lock.release()
			return None
		
		def DetectedFault(self):
			'''
			Check if a fault was detected.
			'''
			
			time.sleep(0.15)

			if not UnixGdb.handlingFault.isSet():
				return False
			
			UnixGdb.handledFault.wait()
			UnixGdb.lock.acquire()
			
			if UnixGdb.fault or not self.thread.isAlive():
				print ">>>>>> RETURNING FAULT <<<<<<<<<"
				UnixGdb.fault = False
				UnixGdb.lock.release()
				return True
			
			UnixGdb.lock.release()
			return False
		
		def OnFault(self):
			'''
			Called when a fault was detected.
			'''
			self._StopDebugger()
		
		def OnShutdown(self):
			'''
			Called when Agent is shutting down.
			'''
			self._StopDebugger()

except:
	pass

# end
