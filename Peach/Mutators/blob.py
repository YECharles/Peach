
'''
Mutators that operate on blob types.

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

import sys, os, time, struct
from Peach.mutator import *
from Peach.group import *
from Peach.Engine.common import *

class DWORDSliderMutator(Mutator):
	'''
	Slides a DWORD through the blob.
	
	@author Chris Clark
	'''
	
	def __init__(self, peach, node):
		Mutator.__init__(self)
		#: Weight to be chosen randomly
		self.weight = 2
		
		self.isFinite = True
		
		self.name = "DWORDSliderMutator"
		self._peach = peach
		self._curPos = 0
		
		self._len = len(node.getValue())
		self._position = 0		
		self._dword = 0xFFFFFFFF
		self._counts = 0
	
	def next(self):
		self._position += 1
		if self._position >= self._len:
			raise MutatorCompleted()
		
	def getCount(self):
		return self._len

	def supportedDataElement(e):
		if isinstance(e, Blob) and e.isMutable:
			for child in e:
				if isinstance(child, Hint) and child.name == 'DWORDSliderMutator' and child.value == 'off':
					return False
			
			return True
		
		return False
	supportedDataElement = staticmethod(supportedDataElement)
	
	def sequencialMutation(self, node):
		self._performMutation(node, self._position)
	
	def randomMutation(self, node):
		count = self._random.randint(0, self._len-1)
		self._performMutation(node, count)

	def _performMutation(self, node, position):
		
		data = node.getValue()
		length = len(data)
		
		if position >= length:
			return
		
		inject = ''
		remaining = length - position
		
		if remaining == 1:
			inject = struct.pack('B', self._dword & 0x000000FF)
		
		elif remaining == 2:
			inject = struct.pack('H', self._dword & 0x0000FFFF) #ushort
		
		elif remaining == 3: 
			inject = struct.pack('B', (self._dword & 0x00FF0000) >> 16) + \
				struct.pack('>H', self._dword & 0xFFFF)
		
		else:
			inject = struct.pack('L', self._dword)
		
		node.currentValue = data[:position] + inject + data[position + len(inject):]


class BitFlipperMutator(Mutator):
	'''
	Flip a % of total bits in blob.  Default % is 20.
	'''
	
	def __init__(self, peach, node):
		Mutator.__init__(self)
		#: Weight to be chosen randomly
		self.weight = 3
		
		self.isFinite = True
		self.name = "BitFlipperMutator"
		self._peach = peach
		self._n = self._getN(node, None)
		self._current = 0
		self._len = len(node.getValue())
		
		if self._n != None:
			self._count = self._n
		
		else:
			self._count = long((len(node.getValue())*8) * 0.2)
	
	def _getN(self, node, n):
		for c in node._children:
			if isinstance(c, Hint) and c.name == 'BitFlipperMutator-N':
				try:
					n = int(c.value)
				except:
					raise PeachException("Expected numerical value for Hint named [%s]" % c.name)
		
		return n
	
	def next(self):
		self._current += 1
		if self._current > self._count:
			raise MutatorCompleted()

	def getCount(self):
		return self._count

	def supportedDataElement(e):
		if isinstance(e, Blob) and e.isMutable:
			return True
		
		return False
	supportedDataElement = staticmethod(supportedDataElement)
	
	def sequencialMutation(self, node):
		for i in range(self._random.randint(0, 10)):
			if self._len - 1 <= 0:
				count = 0
			else:
				count = self._random.randint(0, self._len-1)
				
			node.currentValue = self._performMutation(node, count)
	
	def randomMutation(self, node):
		for i in range(self._random.randint(0, 10)):
			if self._len -1 <= 0:
				count = 0
			else:
				count = self._random.randint(0, self._len-1)
			
			node.currentValue = self._performMutation(node, count)
	
	def _performMutation(self, node, position):
		
		data = node.getValue()
		length = len(data)
		
		if len(data) == 0:
			return data
		
		if position >= length:
			position = length - 1
		if position < 0:
			position = 0
		
		byte = struct.unpack('B', data[position])[0]
		byte ^= self._random.randint(0, 255)
		
		packedup = struct.pack("B", byte)
		data = data[:position] + packedup + data[position+1:]
		
		return data

# end
