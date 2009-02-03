
'''
Some default file publishers.  Output generated data to a file, etc.

@author: Michael Eddington
@version: $Id$
'''

#
# Copyright (c) 2005-2008 Michael Eddington
# Copyright (c) 2004-2005 IOActive Inc.
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

import os, sys, time
from Peach.Engine.engine import Engine
from Peach.publisher import Publisher

class FileWriter(Publisher):
	'''
	Publishes generated data to a file.  No concept of receaving data
	yet.
	'''
	
	def __init__(self, filename):
		'''
		@type	filename: string
		@param	filename: Filename to write to
		'''
		Publisher.__init__(self)
		self._filename = None
		self._fd = None
		self._state = 0	# 0 -stoped; 1 -started
		self.setFilename(filename)
	
	def getFilename(self):
		'''
		Get current filename.
		
		@rtype: string
		@return: current filename
		'''
		return self._filename
	def setFilename(self, filename):
		'''
		Set new filename.
		
		@type filename: string
		@param filename: Filename to set
		'''
		self._filename = filename
	
	def start(self):
		pass
	
	def connect(self):
		if self._state == 1:
			raise Exception('File::start(): Already started!')
		
		if self._fd != None:
			self._fd.close()
		
		self.mkdir()
		
		self._fd = open(self._filename, "w+b")
		self._state = 1
	
	def stop(self):
		self.close()
	
	def mkdir(self):
		# lets try and create the folder this file lives in
		delim = ""
		
		if self._filename.find("\\") != -1:
			delim = '\\'
		elif self._filename.find("/") != -1:
			delim = '/'
		else:
			return
		
		# strip filename
		try:
			path = self._filename[: self._filename.rfind(delim) ]
			os.mkdir(path)
		except:
			pass
		
	def close(self):
		if self._state == 0:
			return
		
		self._fd.close()
		self._fd = None
		self._state = 0
	
	def send(self, data):
		self._fd.write(data)
	
	def receive(self, size = None):
		if size != None:
			return self._fd.read(size)
		
		return self._fd.read()

class FileReader(Publisher):
	'''
	Publishes generated data to a file.  No concept of receaving data
	yet.
	'''
	
	def __init__(self, filename):
		'''
		@type	filename: string
		@param	filename: Filename to write to
		'''
		Publisher.__init__(self)
		self._filename = None
		self._fd = None
		self._state = 0	# 0 -stoped; 1 -started
	
		self.setFilename(filename)
	
	def getFilename(self):
		'''
		Get current filename.
		
		@rtype: string
		@return: current filename
		'''
		return self._filename
	def setFilename(self, filename):
		'''
		Set new filename.
		
		@type filename: string
		@param filename: Filename to set
		'''
		self._filename = filename
	
	def start(self):
		pass
	
	def connect(self):
		if self._state == 1:
			return
		
		if self._fd != None:
			self._fd.close()
		
		self._fd = open(self._filename, "r+b")
		self._state = 1
	
	def stop(self):
		self.close()
	
	def close(self):
		try:
			if self._state == 0:
				return
			
			self._fd.close()
			self._fd = None
			self._state = 0
		except:
			pass
	
	def send(self, data):
		self._fd.write(data)
	
	def receive(self, size = None):
		if size != None:
			return self._fd.read(size)
			
		return self._fd.read()


class FilePerIteration(FileWriter):
	'''
	This publisher differs from File in that each round
	will generate a new filename.  Very handy for generating
	bogus content (media files, etc).
	'''
	
	def __init__(self, filename):
		'''
		@type	filename: string
		@param	filename: Filename to write to should have a %d in it
		someplace :)
		'''
		FileWriter.__init__(self, filename)
		
		self._roundCount = 0
		self._origFilename = filename
		self.setFilename(filename % self._roundCount)
		self._closed = True
	
	def connect(self):
		FileWriter.connect(self)
		self._closed = False
	
	def stop(self):
		self.close()
	
	def close(self):
		FileWriter.close(self)
		if not self._closed:
			self._roundCount += 1
			self.setFilename(self._origFilename % self._roundCount)
			self._closed = True
	
	def send(self, data):
		FileWriter.send(self, data)

class FileWriterLauncher(Publisher):
	'''
	Writes a file to disk and then launches a program.
	
	To use, first use this publisher like the FileWriter
	stream publisher.  Close, than call a program (or two).
	'''
	
	def __init__(self, filename, debugger = "False", waitTime = 180):
		'''
		@type	filename: string
		@param	filename: Filename to write to
		@type	waitTime: integer
		@param	waitTime: Time in seconds to wait before killing process
		'''
		Publisher.__init__(self)
		self._filename = None
		self._fd = None
		self._state = 0	# 0 -stoped; 1 -started
		self.setFilename(filename)
		self.waitTime = float(waitTime)
		self.debugger = False
		if debugger.lower() == "true":
			self.debugger = True
	
	def getFilename(self):
		'''
		Get current filename.
		
		@rtype: string
		@return: current filename
		'''
		return self._filename
	def setFilename(self, filename):
		'''
		Set new filename.
		
		@type filename: string
		@param filename: Filename to set
		'''
		self._filename = filename
	
	def start(self):
		pass
	
	def connect(self):
		if self._state == 1:
			raise Exception('File::start(): Already started!')
		
		if self._fd != None:
			self._fd.close()
		
		self.mkdir()
		
		self._fd = open(self._filename, "w+b")
		self._state = 1
	
	def stop(self):
		self.close()
	
	def mkdir(self):
		# lets try and create the folder this file lives in
		delim = ""
		
		if self._filename.find("\\") != -1:
			delim = '\\'
		elif self._filename.find("/") != -1:
			delim = '/'
		else:
			return
		
		# strip filename
		try:
			path = self._filename[: self._filename.rfind(delim) ]
			os.mkdir(path)
		except:
			pass
		
	def close(self):
		if self._state == 0:
			return
		
		self._fd.close()
		self._fd = None
		self._state = 0
	
	def send(self, data):
		self._fd.write(data)
	
	def receive(self, size = None):
		if size != None:
			return self._fd.read(size)
		
		return self._fd.read()
	
	def call(self, method, args):
		'''
		Launch program to consume file
		
		@type	method: string
		@param	method: Command to execute
		@type	args: array of objects
		@param	args: Arguments to pass
		'''
		
		## Make sure we close the file first :)
		
		self.close()
		
		## Figure out how we are calling the program
		
		if self.debugger:
			# Launch via agent
			
			Engine.context.agent.OnPublisherCall(method)
		
		else:
			# Launch via spawn
			
			realArgs = [method, "/c", method]
			for a in args:
				realArgs.append(a)
			
			pid = os.spawnv(os.P_NOWAIT, os.path.join( os.getenv('SystemRoot'), 'system32','cmd.exe'), realArgs)
			
			# Give it some time before we KILL!
			for i in range(self.waitTime/0.25):
				if win32process.GetExitCodeProcess(pid) != win32con.STILL_ACTIVE:
					# Process exited already
					return
				
				time.sleep(0.25)
			
			try:
				# Kill application
				win32process.TerminateProcess(pid, 0)
			except:
				pass

try:
	import win32gui, win32con, win32process, win32event, win32api
	import sys,time, os, signal, subprocess, ctypes
	
	TH32CS_SNAPPROCESS = 0x00000002
	class PROCESSENTRY32(ctypes.Structure):
		_fields_ = [("dwSize", ctypes.c_ulong),
			("cntUsage", ctypes.c_ulong),
			("th32ProcessID", ctypes.c_ulong),
			("th32DefaultHeapID", ctypes.c_ulong),
			("th32ModuleID", ctypes.c_ulong),
			("cntThreads", ctypes.c_ulong),
			("th32ParentProcessID", ctypes.c_ulong),
			("pcPriClassBase", ctypes.c_ulong),
			("dwFlags", ctypes.c_ulong),
			("szExeFile", ctypes.c_char * 260)]
	
	class FileWriterLauncherGui(Publisher):
		'''
		Writes a file to disk and then launches a program.  After
		some defined amount of time we will try and close the GUI
		application by sending WM_CLOSE than kill it.
		
		To use, first use this publisher like the FileWriter
		stream publisher.  Close, than call a program (or two).
		'''
		
		def __init__(self, filename, windowname, debugger = "false", waitTime = 3):
			'''
			@type	filename: string
			@param	filename: Filename to write to
			@type   windowname: string
			@param  windowname: Partial window name to locate and kill
			'''
			Publisher.__init__(self)
			self._filename = None
			self._fd = None
			self._state = 0	# 0 -stoped; 1 -started
			self.setFilename(filename)
			self._windowName = windowname
			self.waitTime = float(waitTime)
			self.debugger = False
			if debugger.lower() == "true":
				self.debugger = True
		
		def getFilename(self):
			'''
			Get current filename.
			
			@rtype: string
			@return: current filename
			'''
			return self._filename
		
		def setFilename(self, filename):
			'''
			Set new filename.
			
			@type filename: string
			@param filename: Filename to set
			'''
			self._filename = filename
		
		def start(self):
			pass
		
		def connect(self):
			if self._state == 1:
				raise Exception('File::start(): Already started!')
			
			if self._fd != None:
				self._fd.close()
			
			self.mkdir()
			
			# First lets rename the old file if there is one
			
			try:
				try:
					os.unlink(self._filename + ".old.old")
				except:
					pass
				
				try:
					os.rename(self._filename + ".old", self._filename + ".old.old")
				except:
					pass
				
				os.rename(self._filename, self._filename + ".old")
				
			except:
				pass
			
			# If we can't open the file it might
			# still be open.  Lets retry a few times.
			for i in range(10):
				try:
					self._fd = open(self._filename, "w+b")
					break
				except:
					if i == 9:
						raise
				
				time.sleep(1)
			
			self._state = 1
		
		def stop(self):
			self.close()
		
		def mkdir(self):
			# lets try and create the folder this file lives in
			delim = ""
			
			if self._filename.find("\\") != -1:
				delim = '\\'
			elif self._filename.find("/") != -1:
				delim = '/'
			else:
				return
			
			# strip filename
			try:
				path = self._filename[: self._filename.rfind(delim) ]
				os.mkdir(path)
			except:
				pass
			
		def close(self):
			if self._state == 0:
				return
			
			self._fd.close()
			self._fd = None
			self._state = 0
		
		def send(self, data):
			self._fd.write(data)
		
		def receive(self, size = None):
			if size != None:
				return self._fd.read(size)
			
			return self._fd.read()
		
		def call(self, method, args):
			'''
			Launch program to consume file
			
			@type	method: string
			@param	method: Command to execute
			@type	args: array of objects
			@param	args: Arguments to pass
			'''
			
			proc = None
			if self.debugger:
				# Launch via agent
				
				Engine.context.agent.OnPublisherCall(method)
			
			else:
				realArgs = [method]
				for a in args:
					realArgs.append(a)
				
				proc = None
				try:
					proc = subprocess.Popen(realArgs, shell=True)
				
				except:
					print "Error: Exception thrown creating process"
					raise
			
			# Wait 5 seconds
			time.sleep(self.waitTime)
			
			self.closeApp(proc, self._windowName)
	
		def enumCallback(hwnd, args):
			'''
			Will get called by win32gui.EnumWindows, once for each
			top level application window.
			'''
			
			proc = args[0]
			windowName = args[1]
			
			try:
			
				# Get window title
				title = win32gui.GetWindowText(hwnd)
				
				# Is this our guy?
				if title.find(windowName) == -1:
					return
				
				# Send WM_CLOSE message
				win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
				win32gui.PostQuitMessage(hwnd)
			except:
				pass
		
		enumCallback = staticmethod(enumCallback)
		
		def genChildProcesses(self, proc):
			parentPid = proc.pid
			
			for p in self.genProcesses():
				if p.th32ParentProcessID == parentPid:
					yield p.th32ProcessID
		
		def genProcesses(self):
			
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
				yield pe32
				if Process32Next(hProcessSnap, ctypes.byref(pe32)) == win32con.FALSE:
					break
			
			CloseHandle(hProcessSnap)
		
		def closeApp(self, proc, title):
			'''
			Close Application by window title
			'''
			win32gui.EnumWindows(FileWriterLauncherGui.enumCallback, [proc, title])
			
			if proc:
				win32event.WaitForSingleObject(int(proc._handle), 5*1000)
				
				for pid in self.genChildProcesses(proc):
					try:
						handle = win32api.OpenProcess(1, False, pid)
						win32process.TerminateProcess(handle, -1)
						win32api.CloseHandle(handle)
					except:
						pass
		
except:
	pass

# end
