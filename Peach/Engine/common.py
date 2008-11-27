'''
Common functions and classes.

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

import types,os,sys

class Holder:
	'''
	Holds static stuff
	'''
	
	globals = None
	locals = None

class SoftException(Exception):
	'''
	Soft exceptions should end the current test
	iteration, but not the run.  They are "recoverable"
	or "try again" errors.
	'''
	pass

class HardException(Exception):
	'''
	Hard exceptions are non-recoverable and should
	end the fuzzing run.
	'''
	pass

class RedoTestException(SoftException):
	'''
	Indicate we should re-run the current test.  A recoverable error
	occured.  The main enging loop should only retry the test case 3
	times before turning this into a hard exception.
	'''
	pass

class PeachException(HardException):
	'''
	Peach exceptions are specialized hard exceptions.  The
	message contained in a PeachException is presentable to the
	user w/o any stack trace, etc.
	
	Examples would be:
	
		"Error: The DataModel element requires a name attribute."
	
	'''
	
	def __init__(self, msg, module = "Unknown"):
		Exception.__init__(self, msg)
		self.module = module
		self.msg = msg

def peachEval(code, environment = False):
	'''
	Eval using the Peach namespace stuffs
	'''
	
	return eval(code, Holder.globals, Holder.locals)

def GetClassesInModule(module):
	'''
	Return array of class names in module
	'''

	classes = []
	for item in dir(module):
		i = getattr(module, item)
		if type(i) == types.ClassType and item[0] != '_':
			classes.append(item)
		elif type(i) == types.MethodType and item[0] != '_':
			classes.append(item)
		elif type(i) == types.FunctionType and item[0] != '_':
			classes.append(item)

	return classes
	
def buildImports(node, g, l):
	
	root = node.getRoot()
	
	for child in root:

		if child.elementType == 'import':
			# Import module

			importStr = child.importStr
			fromStr = child.fromStr
			
			if fromStr != None:
				
				if importStr == "*":
					module = __import__(fromStr, globals(), locals(), [ importStr ], -1)

					try:
						# If we are a module with other modules in us then we have an __all__
						for item in module.__all__:
							g[item] = getattr(module, item)

					except:
						# Else we just have some classes in us with no __all__
						for item in GetClassesInModule(module):
							g[item] = getattr(module, item)

				else:
					module = __import__(fromStr, globals(), locals(), [ importStr ], -1)
					for item in importStr.split(','):
						item = item.strip()
						g[item] = getattr(module, item)

			else:
				g[importStr] = __import__(importStr, globals(), locals(), [], -1)
				
def evalEvent(code, environment, node = None):
	'''
	Eval python code returning result.
	
	code - String
	environment - Dictionary, keys are variables to place in local scope
	'''
	
	globalScope = {}
	localScope = {}
	
	if node != None:
		buildImports(node, globalScope, localScope)
	
	if Holder.globals != None:
		for k in Holder.globals:
			globalScope[k] = Holder.globals[k]
	
	if Holder.locals != None:
		for k in Holder.locals:
			localScope[k] = Holder.locals[k]
	
	for k in environment.keys():
		globalScope[k] = environment[k]
		localScope[k] = environment[k]
	
	try:
		ret = eval(code, globalScope, localScope)
	except:
		print "Code: [%s]" % code
		print "Environment:"
		for k in environment.keys():
			print "  [%s] = [%s]" % (k, repr(environment[k]))
		raise
	
	return ret

class _Getch:
    """Gets a single character from standard input.  Does not echo to the
screen."""
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            self.impl = _GetchUnix()

    def __call__(self): return self.impl()


class _GetchUnix:
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()


getch = _Getch()

class StreamBuffer:
	'''
	A Peach data stream.  Used when generating or cracking data.
	'''
	
	def __init__(self, data = None):
		
		#: Current position
		self.pos = 0
		#: Data buffer
		self.data = ""
		#: History of data locations
		self.positions = {}
		#: History of data length
		self.lengths = {}
		
		if data != None:
			self.data = data
	
	def getValue(self):
		'''
		Return the value created by this stream.
		'''
		return self.data
	
	def setValue(self, data):
		'''
		Set the internal buffer.
		'''
		self.data = data
	
	def peek(self, size = None):
		'''
		Read data with out changing position.
		'''
		if size == None:
			return self.data[self.pos:]
		
		if self.pos + size > len(self.data):
			raise Exception("StreamBuffer.peek(%d): Peeking passed end of buffer." % size)
		
		return self.data[self.pos:self.pos+size]
	
	def read(self, size = None):
		'''
		Read from current position.  If size
		isn't specified, read rest of stream.
		
		Read will shift the current position.
		'''
		
		if size == None:
			ret = self.data[self.pos:]
			self.pos = len(self.data)
			return ret
		
		if self.pos + size > len(self.data):
			raise Exception("StreamBuffer.read(%d): Reading passed end of buffer." % size)
		
		ret = self.data[self.pos:self.pos+size]
		self.pos += size
		return ret

	def storePosition(self, name):
		'''
		Store our position by name
		'''
		#print "Storing position of %s at %d" % (name, self.pos)
		self.positions[name] = self.pos
		return self.pos
	
	def getPosition(self, name):
		'''
		Retreave position by name
		'''
		if name not in self.positions:
			return None
		
		return self.positions[name]
	
	def write(self, data, name = None):
		'''
		Write a block of data at current position.
		Stream will expand if needed to support the
		written data.  Otherwise it will overright
		the existing data.
		
		@type	data: string
		@param	data: Data to write
		@type	name: string
		@param	name: Name to store position under [optional]
		'''
		
		if name != None:
			#print "write: %s: %s" % (name, repr(data))
			self.storePosition(name)
			self.lengths[name] = len(data)
		
		dataLen = len(data)
		ourDataLen = len(self.data)
		
		# Replace existing data
		if ourDataLen - self.pos > dataLen:
			ret = self.data[:self.pos]
			ret += data
			ret += self.data[self.pos+dataLen:]
			self.data = ret
		
		# Append new data
		elif self.pos == ourDataLen:
			self.data += data
		
		# Do both
		else:
			self.data = self.data[:self.pos] + data
		
		# Move position
		self.pos += dataLen

	def count(self):
		'''
		Get the current size in bytes of the data stream.
		'''
		return len(self.data)

	def tell(self):
		'''
		Return the current position in the data stream.
		'''
		return self.pos
	
	def seekFromCurrent(self, pos):
		'''
		Change current position in data.
		
		NOTE: If the position is past the end of the
		      existing stream data the data will be expanded
		      such that the position exists padded with '\0'
		'''
		
		newpos = self.pos + pos
		self.seekFromStart(newpos)
	
	def seekFromStart(self, pos):
		'''
		Change current position in data.
		
		NOTE: If the position is past the end of the
		      existing stream data the data will be expanded
		      such that the position exists padded with '\0'
		'''
		
		if pos < 0:
			raise Exception("StreamBuffer.seekFromStart(%d) results in negative position" % pos)
		
		# Should we expand buffer?
		if pos > len(self.data):
			self.data += '\0' * (pos - len(self.data))
		
		self.pos = pos
	
	def seekFromEnd(self, pos):
		'''
		Change current position in data.
		
		NOTE: If the position is past the end of the
		      existing stream data the data will be expanded
		      such that the position exists padded with '\0'
		'''
		
		newpos = len(self.data) + pos
		self.seekFromStart(newpos)


# end
