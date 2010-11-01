
'''
Networking monitor for peach agent.  Uses pylibpcap to perform network
captures which can be reported back and logged.

Todo:

 Implement! http://pylibpcap.sourceforge.net/

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


import sys, threading, os, time, thread, re, socket
from Peach.agent import Monitor

try:
	def search_file(filename):
		"""
		Find a file in a search path
		"""
		
		search_path = os.getenv("path")
		paths = search_path.split(os.path.pathsep)
		for path in paths:
			if os.path.exists(os.path.join(path, filename)):
				return True
		
		return False
	
	if sys.platform == 'win32' and search_file("wpcap.dll"):
		import pcap
	
	elif sys.platform != 'win32':
		import pcap
	
	else:
		print "Warning: pypcap not found, disabling network monitor."

except:
	#print "Warning: pypcap not found, disabling network monitor."
	pass


class PingMonitor(Monitor):
	'''
	This monitor will report a fault if it cannot ping
	the specified hostname.
	'''
	
	def __init__(self, args):
		'''
		Constructor.  Arguments are supplied via the Peach XML
		file.
		
		@type	args: Dictionary
		@param	args: Dictionary of parameters
		'''
		
		# Our name for this monitor
		self.hostname = str(args['hostname']).replace("'''", "")
		self._name = "PingMonitor"
	
	def DetectedFault(self):
		'''
		Check if a fault was detected.
		'''
		
		if sys.platform == "win32":
				ping_send_command = "ping -n 2 "
				ping_send_command3 = "ping -n 3 "
				ping_reply_regex = r"Reply from \d+\.\d+\.\d+\.\d+: bytes="
		elif sys.platform == "linux2":
				ping_send_command = "ping -c 2 "
				ping_send_command3 = "ping -c 3 "
				ping_reply_regex = r"64 bytes from \d+\.\d+\.\d+\.\d+:"
		else:
				raise Exception("PingAgent running on unsupported platform %s" % sys.platform)
		
		pipe = os.popen(ping_send_command + self.hostname)
		buff = pipe.read()
		pipe.close()
		
		if re.compile(ping_reply_regex, re.M).search(buff) != None:
			return False
		
		# If we didn't see a ping, lets try again with 3 pings just to make sure
		
		pipe = os.popen(ping_send_command3 + self.hostname)
		buff = pipe.read()
		pipe.close()
		
		if re.compile(ping_reply_regex, re.M).search(buff) != None:
			return False
		
		return True


class UdpThread(threading.Thread):
	'''
	Thread class for UdpMonitor
	'''
	
	def __init__(self, parent, host, port):
		threading.Thread.__init__(self)
		threading.Thread.setDaemon(self, True)
		
		self._host = host
		self._port = port
		self.stopEvent = threading.Event()
		self.stopEvent.clear()
		self.receivedPacket = threading.Event()
		self.receivedPacket.clear()
		self.packets = []
	
	def run(self):
		print "UdpThread(): Starting up UDP listener"
		
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.bind((self._host,int(self._port)))
		sock.setblocking(false)
		
		while not self.stopEvent.isSet():
			try:
				data = None
				data,self.addr = self._socket.recvfrom(65565)
				if data != None and len(data) > 0:
					print "UdpThread: Received packet from ", self.addr
					self.packets.append(data)
					self.receivedPacket.set()
					
			except socket.error:
				# Thrown if non-blocking and no packet
				# available to receive.
				pass
		
		print "UdpThread: Shutting down"
		sock.close()

class UdpMonitor(Monitor):
	'''
	Watches for incoming packets on a UDP port.  If packet
	received will trigger fault saving data from packet.
	'''
	
	def __init__(self, args):
		Monitor.__init__(self)
		
		self.host = str(args['host']).replace("'''", "")
		self.port = str(args['port']).replace("'''", "")
		self._name = "UdpMonitor"
		self.thread = None
		
	def OnTestStarting(self):
		self.thread = PcapThread(self, self.host, self.port)
		self.thread.start()
	
	def OnTestFinished(self):
		if self.thread != None and self.thread.isAlive():
			self.thread.stopEvent.set()
			self.thread.join()
			
		self.thread = None
	
	def GetMonitorData(self):
		
		data = None
		for d in self.thread.packets:
			data += d
		
		self.thread.packets = []
		self.thread.receivedPackets.clear()
		
		return { 'UdpMonitor.txt' : data }
	
	def OnShutdown(self):
		if self.thread != None and self.thread.isAlive():
			self.thread.stopEvent.set()
			self.thread.join()
		
		self.thread = None
	
	def DetectedFault(self):
		return self.thread.receivedPacket.isSet()


class PcapThread(threading.Thread):
	def __init__(self, parent, device, filter, pcapFile):
		threading.Thread.__init__(self)
		threading.Thread.setDaemon(self, True)
		
		self._device = device
		self._filter = filter
		self._pcapFile = pcapFile
		self.stopEvent = threading.Event()
		self.stopEvent.clear()
		self.dumpClosed = threading.Event()
		self.dumpClosed.clear()
		self._packets = []
	
	def run(self):
		print "PcapThread(): Starting up pcap"
		
		pc = pcap.pcap(self._device)
		pc.dumpopen(self._pcapFile)
		
		if self._filter != None:
			pc.setfilter(self._filter)
		
		pc.setnonblock()
		
		print "PcapThread(): Packet capture loop"
		while not self.stopEvent.isSet():
			# Do not remove print.  For some reason packets
			# are only captures when it's there!!!
			print "."
			pc.readpkts()
		
		pc.dumpclose()
		self.dumpClosed.set()


class PcapMonitor(Monitor):
	'''
	Monitor network using pcap library.
	'''
	
	def __init__(self, args):
		try:
			self.device = str(args['device']).replace("'''", "")
			if len(self.device) < 1:
				self.device = pcap.getDefaultName()
			
		except:
			self.device = pcap.getDefaultName()
		
		self.filter = str(args['filter']).replace("'''", "")
		self.data = None
		self.tempFile = os.tmpnam()
		self.thread = None
	
	def OnTestStarting(self):
		self.thread = PcapThread(self, self.device, self.filter, self.tempFile)
		self.thread.start()
		self.data = None
		print "PcapMonitor: OnTestStarting done"
	
	def OnTestFinished(self):
		# Stop thread
		
		self.data = None
		if self.thread != None and self.thread.isAlive():
			self.thread.stopEvent.set()
			self.thread.join()
			self.thread.dumpClosed.wait()
			
			# Read dump
			f = open(self.tempFile, "rb")
			self.data = f.read()
			f.close()
			
			print "PcapMonitor: Thread joined, dump saved"
			
		self.thread = None
	
	def GetMonitorData(self):
		return { 'Capture.pcap' : self.data }
	
	def OnShutdown(self):
		if self.thread != None and self.thread.isAlive():
			self.thread.stopEvent.set()
			self.thread.join()

# end
