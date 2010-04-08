
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
import tempfile
from subprocess import *
from threading import *
import popen2

def _MonitorSyslog(*args, **kargs):
	'''
	Watch syslog for Crash Reports
	'''
	
	try:
		
		#print "> _MonitorSyslog"
		
		eventStarted = kargs["EventStarted"]
		eventFormulating = kargs["EventFormulating"]
		eventCrashReport = kargs["EventCrashReport"]
		eventQuit = kargs["EventQuit"]
		crashReporter = kargs["Context"]
		
		reFormulating = r"Formulating crash report for process [^\\[]*\\\[(\d+)\\\]"
		reCrashReport = r"Saved crashreport to (.*) using"
		
		p = popen2.Popen4(
			"/usr/bin/syslog -w 1 -k Facility eq \"Crash Reporter\"")
		
		crashReporter.monitorPid = None
		crashReporter.monitorCrashReport = None
		
		if p.poll() != -1:
			raise Exception("Failed to run syslog")
		
		eventStarted.set()
		
		while (not eventQuit.isSet()) and p.poll() == -1:
			line = p.fromchild.readline()
			
			m = re.search(reFormulating, line)
			if m:
				print "CrashReporter: !!! FOUND FAULT !!!"
				crashReporter.monitorPid = int(m.group(1))
				eventFormulating.set()
				
				line = p.fromchild.readline()
				m = re.search(reCrashReport, line)
				if m:
					crashReporter.monitorCrashReport = m.group(1)
					eventCrashReport.set()
		
		if p.poll() == None:
			print "_MonitorSyslog: syslog exited!"
		
	except:
		print "_MonitorSyslog: Exception:", sys.exc_info()
		raise
	
	finally:
		eventStarted.clear()
	
	#print "< _MonitorSyslog"
	

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
		
		# Our name for this monitor
		self._name = "CrashReporter"
		
		self.eventCrashReport = Event()
		self.eventFormulating = Event()
		self.eventQuit = Event()
		self.eventStarted = Event()
		
		self.monitorPid = None
		self.monitorCrashReport = None
		
		self.thread = None
	
	def OnTestStarting(self):
		'''
		Called right before start of test case or variation
		'''
		
		if not self.thread or not self.thread.isAlive():
			if self.thread:
				self.thread.join()
			
			self.eventCrashReport.clear()
			self.eventFormulating.clear()
			self.eventQuit.clear()
			self.eventStarted.clear()
			
			self.thread = None
			self.thread = Thread(target=_MonitorSyslog, kwargs = {
				"EventStarted": self.eventStarted,
				"EventFormulating": self.eventFormulating,
				"EventCrashReport": self.eventCrashReport,
				"EventQuit" : self.eventQuit,
				"Context": self
				})
			self.thread.start()
			
			print "Waiting for eventStarted"
			self.eventStarted.wait()
			print "Done waiting..."
	
	def OnTestFinished(self):
		'''
		Called right after a test case or varation
		'''
		pass
	
	def GetMonitorData(self):
		'''
		Get any monitored data from a test case.
		'''
		
		if not self.eventFormulating.isSet():
			return None
		
		self.eventCrashReport.wait()
		
		fileName = self.monitorCrashReport
		
		self.monitorCrashReport = None
		self.monitorPid = None
		
		fd = open(fileName, "rb")
		data = fd.read()
		fd.close()
		
		self.eventFormulating.clear()
		self.eventCrashReport.clear()
		
		return {"CrashReport.txt": data}
	
	def DetectedFault(self):
		'''
		Check if a fault was detected.
		'''
		
		# Give crash reporter time to find the crash
		time.sleep(2)
		
		return self.eventFormulating.isSet()
	
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
		self.eventQuit.set()
		self.thread.join()
	
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


# end
