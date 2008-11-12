
'''
Base Publisher object implementation.

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

from Peach.Engine.common import SoftException

class PublisherStartError(Exception):
	'''
	Exception thrown if error occurs during start call
	'''
	pass

class PublisherStopError(Exception):
	'''
	Exception thrown if error occurs during stop call
	'''
	pass

class PublisherSoftException(SoftException):
	'''
	Recoverable exception occured in the Publisher.
	'''
	pass

class Timeout(SoftException):
	def __init__(self, msg):
		self.msg = msg
	
	def __str__(self):
		return self.msg

class PublisherBuffer:
	'''
	An IO buffer.
	'''
	
	def __init__(self, publisher, data = None):
		
		#: Publisher associated with buffer
		self.publisher = publisher
		
		if self.publisher != None:
			self.publisher.publisherBuffer = self
		
		#: Data buffer of currently read bytes
		self.data = ""
		
		#: Do we have all the data?
		self.haveAllData = False
		
		if data != None:
			self.data = data
			self.haveAllData = True
	
	def read(self, size = 1):
		'''
		Read additional data into IO buffer.
		'''
		
		if self.haveAllData:
			return
		
		ret = ""
		timeout = False
		try:
			if size != None:
				while(len(ret) < size):
					try:
						ret += self.publisher.receive(size)
					
					except Timeout, e:
						# Retry after a timeout
						if timeout:
							raise
						
						timeout = True
						self.haveAllData = True
			else:
				try:
					self.haveAllData = True
					ret += self.publisher.receive(size)
					
				except Timeout, e:
					pass
		
		finally:
			self.data += ret
	
	def readAll(self):
		'''
		Read all data
		'''
		
		if self.haveAllData:
			return
		
		try:
			self.read(None)
		
		finally:
			self.haveAllData = True

class Publisher:
	'''
	The Publisher object(s) implement a way to send and/or receave
	data by some means.  This could be a TCP connection, a filehandle, or
	SQL, etc.
	
	There are two "types" of publishers, stream based and call based.  This
	base class supports both types.
	
	To support stream based publishing implement everything but "call".
	
	To support call based publishing implement start, stop, and call.
	
	Note: A publisher can support both stream and call based publishing.
	'''
	
	#: Indicates which method should be called.
	withNode = False
	
	def start(self):
		'''
		Change state such that send/receave will work.  For Tcp this
		could be connecting to a remote host
		'''
		pass
	
	def stop(self):
		'''
		Change state such that send/receave will not work.  For Tcp this
		could be closing a connection, for a file it might be closing the
		file handle.
		'''
		pass
	
	def send(self, data):
		'''
		Publish some data
		
		@type	data: string
		@param	data: Data to publish
		'''
		raise PeachException("Action 'send' not supported by publisher")
	
	def sendWithNode(self, data, dataNode):
		'''
		Publish some data
		
		@type	data: string
		@param	data: Data to publish
		@type   dataNode: DataElement
		@param  dataNode: Root of data model that produced data
		'''
		raise PeachException("Action 'send' not supported by publisher")
	
	def receive(self, size = None):
		'''
		Receive some data.
		
		@type	size: integer
		@param	size: Number of bytes to return
		@rtype: string
		@return: data received
		'''
		raise PeachException("Action 'receive' not supported by publisher")
	
	def call(self, method, args):
		'''
		Call a method using arguments.
		
		@type	method: string
		@param	method: Method to call
		@type	args: Array
		@param	args: Array of strings as arguments
		@rtype: string
		@return: data returned (if any)
		'''
		raise PeachException("Action 'call' not supported by publisher")

	def callWithNode(self, method, args, argNodes):
		'''
		Call a method using arguments.
		
		@type	method: string
		@param	method: Method to call
		@type	args: Array
		@param	args: Array of strings as arguments
		@type   argNodes: Array
		@param  argNodes: Array of DataElements
		@rtype: string
		@return: data returned (if any)
		'''
		raise PeachException("Action 'call' not supported by publisher")

	def property(self, property, value = None):
		'''
		Get or set property
		
		@type	property: string
		@param	property: Name of method to invoke
		@type	value: object
		@param	value: Value to set.  If None, return property instead
		'''
		raise PeachException("Action 'property' not supported by publisher")
	
	def propertyWithNode(self, property, value, valueNode):
		'''
		Get or set property
		
		@type	property: string
		@param	property: Name of method to invoke
		@type	value: object
		@param	value: Value to set.  If None, return property instead
		@type	valueNode: DataElement
		@param	valueNode: data model root node that produced value.
		'''
		raise PeachException("Action 'property' not supported by publisher")
	
	def accept(self):
		'''
		Accept incoming connection.  Blocks until incoming connection
		occurs.
		'''
		
		raise PeachException("Action 'accept' not supported by publisher")
	
	def close(self):
		'''
		Close current stream/connection.
		'''
		raise PeachException("Action 'close' not supported by publisher")


# end
