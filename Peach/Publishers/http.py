
'''
Send something by HTTP.

@author: Michael Eddington
@version: $Id$
'''

#
# Copyright (c) 2008 Michael Eddington
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

import time, urllib2
from Peach.publisher import Publisher

class HttpDigestAuth(Publisher):
	'''
	A simple HTTP publisher.
	'''
	
	def __init__(self, url, realm, username, password, headers = None, timeout = 0.1):
		'''
		@type	host: string
		@param	host: Remote host
		@type	port: number
		@param	port: Remote port
		@type	timeout: number
		@param	timeout: How long to wait for reponse
		'''
		self._url = url
		self._realm = realm
		self._username = username
		self._password = password
		self._headers = headers
		self._timeout = float(timeout)
		self._fd = None
	
	def stop(self):
		'''
		Close connection if open.
		'''
		self.close()
	
	def connect(self):
		pass
	
	def close(self):
		if self._fd:
			self._fd.close()
			self._fd = None
		
	def send(self, data):
		'''
		Send data via sendall.
		
		@type	data: string
		@param	data: Data to send
		'''
		
		passmgr = urllib2.HTTPPasswordMgr()
		passmgr.add_password(self._realm, self._url, self._username, self._password)
		
		auth_handler = urllib2.HTTPDigestAuthHandler(passmgr)
		opener = urllib2.build_opener(auth_handler)
		urllib2.install_opener(opener)
		
		req = urllib2.Request(self._url, data, self._headers)
		
		try:
			self._fd = urllib2.urlopen(req)
		except:
			self._fd = None
	
	def receive(self, size = None):
		'''
		Receive upto 10000 bytes of data.
		
		@rtype: string
		@return: received data.
		'''
		if self._fd:
			if size != None:
				return self._fd.read(size)
			
			return self._fd.read()
		
		else:
			return ''

class HttpBasicAuth(Publisher):
	'''
	A simple HTTP publisher.
	'''
	
	def __init__(self, url, realm, username, password, headers = None, timeout = 0.1):
		'''
		@type	host: string
		@param	host: Remote host
		@type	port: number
		@param	port: Remote port
		@type	timeout: number
		@param	timeout: How long to wait for reponse
		'''
		self._url = url
		self._realm = realm
		self._username = username
		self._password = password
		self._headers = headers
		self._timeout = float(timeout)
		self._fd = None
		
	def start(self):
		'''
		Create connection.
		'''
		pass
	
	def stop(self):
		self.close()
	
	def close(self):
		'''
		Close connection if open.
		'''
		if self._fd:
			self._fd.close()
			self._fd = None
	
	def send(self, data):
		'''
		Send data via sendall.
		
		@type	data: string
		@param	data: Data to send
		'''
		
		passmgr = urllib2.HTTPPasswordMgr()
		passmgr.add_password(self._realm, self._url, self._username, self._password)
		
		auth_handler = urllib2.HTTPBasicAuthHandler(passmgr)
		opener = urllib2.build_opener(auth_handler)
		urllib2.install_opener(opener)
		
		req = urllib2.Request(self._url, data, self._headers)
		
		try:
			self._fd = urllib2.urlopen(req)
		except:
			self._fd = None
			
	
	def receive(self, size = None):
		'''
		Receive upto 10000 bytes of data.
		
		@rtype: string
		@return: received data.
		'''
		if self._fd:
			if size != None:
				return self._fd.read(size)
			
			return self._fd.read()
		
		else:
			return ''

# end

