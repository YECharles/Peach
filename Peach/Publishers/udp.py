
'''
Default UDP publishers.

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

import socket, time
from Peach.publisher import *
import Peach

def Debug(msg):
	if Peach.Engine.engine.Engine.debug:
		print msg

class Udp(Publisher):
	'''
	A simple UDP publisher.
	'''
	
	def __init__(self, host, port, timeout = None):
		'''
		@type	host: string
		@param	host: Remote hostname
		@type	port: number
		@param	port: Remote port
		'''
		self._host = host
		self._port = port
		self._timeout = timeout
		
		if self._timeout == None:
			self._timeout = 2
		
		else:
			self._timeout = timeout
		
		self._socket = None
		self.buff = ""
		self.pos = 0
	
	def stop(self):
		'''Close connection if open'''
		self.close()
	
	def close(self):
		if self._socket != None:
			self._socket.close()
			self._socket = None
		self.buff = ""
		self.pos = 0
	
	def connect(self):
		if self._socket != None:
			# Close out old socket first
			self._socket.close()
		self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self._socket.connect((self._host,int(self._port)))
		self.buff = ""
		self.pos = 0
	
	def send(self, data):
		'''
		Send data via sendall.
		
		@type	data: string
		@param	data: Data to send
		'''
		self._socket.sendall(data)
	
	def _receiveBySize(self, size):
		'''
		This is now a buffered receiver.
		
		@rtype: string
		@return: received data.
		'''
		
		# Do we already a have it?
		if size+self.pos < len(self.buff):
			ret = self.buff[self.pos:self.pos+size]
			self.pos += size
			return ret
		
		# Only ask for the diff of what we don't already have
		diffSize = (self.pos+size) - len(self.buff)
		
		try:
			self._socket.settimeout(float(self._timeout))
			ret = self._socket.recv(65507)
			
			Debug("udp.Udp.receive we got:")
			Debug(repr(ret))
			
			if not ret:
				# Socket was closed
				raise PublisherSoftException("Socket is closed")
			
			self.buff += ret
			
		except socket.error, e:
			if str(e).find('The socket operation could not complete without blocking') == -1:
				raise Timeout("Timed out waiting for data [%d:%d:%d:%d]" % (len(self.buff), (size+self.pos), size, diffSize))
			
			else:
				raise PublisherSoftException("recv failed: " + str(sys.exc_info()[1]))
		
		finally:
			self._socket.settimeout(None)
		
		ret = self.buff[self.pos:]
		self.pos = len(self.buff)
		return ret
	
	def _receiveByAvailable(self):
		'''
		Receive as much as possible prior to timeout.
		
		@rtype: string
		@return: received data.
		'''
		self._socket.settimeout(float(self._timeout))
		
		try:
			ret = self._socket.recv(65507)
			
			Debug("udp.Udp.receive we got:")
			Debug(repr(ret))
			
			if not ret:
				raise PublisherSoftException("Socket is closed")
			
			self.buff += ret
			
		except socket.error, e:
			if str(e).find('The socket operation could not complete without blocking') == -1:
				pass
			
			else:
				raise PublisherSoftException("recv failed: " + str(sys.exc_info()[1]))
		
		self._socket.settimeout(None)
		
		ret = self.buff[self.pos:]
		self.pos = len(self.buff)
		return ret
	
	def receive(self, size = None):
		
		if size == None:
			return self._receiveByAvailable()
		else:
			return self._receiveBySize(size)
		
# end
