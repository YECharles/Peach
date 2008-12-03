
'''
Output to STDOUT stuffs.

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


from Peach.publisher import Publisher
import sys

class Stdout(Publisher):
	'''
	Basic stdout publisher.  All data is written to stdout.  No input
	is available from this publisher.  Excelent for testing.
	'''
	
	def accept(self):
		pass
	
	def connect(self):
		pass
	
	def close(self):
		pass
	
	def send(self, data):
		print data
	
	def receive(self, size = None):
		return ''
	
	def call(self, method, args):
		str = ""
		for a in args:
			str += "%s, " % repr(a)
		
		print "%s(%s)" % (method, str[:-2])
		
		return ''

class Null(Publisher):
	'''
	Basic stdout publisher.  All data is written to stdout.  No input
	is available from this publisher.  Excelent for testing.
	'''
	
	def accept(self):
		pass
	
	def connect(self):
		pass
	
	def close(self):
		pass
	
	def send(self, data):
		pass
	
	def receive(self):
		return ''
	
	def call(self, method, args):
		return ''

class StdoutCtypes(Publisher):
	'''
	
	'''
	
	#: Indicates which method should be called.
	withNode = True
	
	def connect(self):
		pass
	
	def sendWithNode(self, data, dataNode):
		'''
		Publish some data
		
		@type	data: string
		@param	data: Data to publish
		@type   dataNode: DataElement
		@param  dataNode: Root of data model that produced data
		'''
		value = dataNode.asCType()
		print value
		print dir(value)
	
	def close(self):
		'''
		Close current stream/connection.
		'''
		pass

# end
