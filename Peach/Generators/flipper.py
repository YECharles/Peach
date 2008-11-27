
'''
Default flippers.  Flippers are used to flip bits in a data.  This
is used for "random" or "bute force" fuzzing.  Usefull on codecs and
fully unknown protocols.  Runtime is long for flippers.

Flippers can be "stacked" so to speak to make for interesting random
flipping.  To stack, just use one Flipper as the data generator for
another flipper.

@author: Michael Eddington
@version: $Id$
'''

#
# Copyright (c) 2005-2007 Michael Eddington
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


import re, struct
from Peach.generator import *

#__all__ = ["SequentialFlipper"]

class SequentialFlipper(SimpleGenerator):
	'''
	Sequencially flipps bits in a data blob.  This is for
	"random" fuzzing.  Usefull brute forcing, codecs, etc.
	'''
	
	_data = None
	_position = 0
	
	def __init__(self, group, data):
		'''
		@type	data: string
		@param	data: Binary static blob to flip
		'''
		SimpleGenerator.__init__(self, group)
		
		self._data = str(data)	# Could be a unicode string.
		self._len = len(data)
		self._position = 0
		self._bit = 0
	
	def next(self):
		if self._bit == 7:
			self._position += 1
			self._bit = 0
			
			if self._position >= self._len:
				self._position -= 1
				self._bit = 7
				
				raise GeneratorCompleted("all done here")
			
		else:
			self._bit += 1
	
	def reset(self):
		self._bit = 0
		self._position = 0
	
	def getRawValue(self):
		
		if self._position >= self._len:
			return ""
		
		data = self._data
		
		byte = struct.unpack('B', data[self._position])[0]
		mask = 1 << self._bit
		
		if ( (byte & mask) >> self._bit ) == 1:
			
			mask = 0
			for i in range(8-self._bit):
				mask |= 1 << i
			mask = mask << 1
			
			if self._bit > 1:
				mask = mask << (self._bit)
				
				for i in range(self._bit):
					mask |= 1 << i
			
			byte = byte & mask
			
		else:
			byte = byte | mask
		
		packedup = struct.pack("B", byte)
		data = data[:self._position] + packedup + data[self._position+1:]
		
		return data

class SequentialDWORDSlider(SimpleGenerator):
	'''
	Sequencially slides a DWORD through a data blob.  This is for
	"random" fuzzing.  Usefull brute forcing, codecs, etc.
	'''
	
	_data = None
	_position = 0
	
	def __init__(self, group, data, dword=0xFFFFFFFF):
		'''
		@type	data: string
		@param	data: Binary static blob to slide through
		@type	dword: ulong
		@param	dword: The dword to slide through (e.g. 0xBAADFOOD), slides 0XFFFFFFFF by default
		'''
		SimpleGenerator.__init__(self, group)
		
		self._data = str(data)	# Could be a unicode string.
		self._len = len(data)
		self._position = 0		
		self._dword = dword		
		self._counts = 0
	
	def next(self):
	
		if self._counts < 4 and self._counts < self._len:
			self._counts += 1		
		elif self._position < self._len:
			self._position += 1
		else:
			raise GeneratorCompleted("DWORD Slider Complete")
		
	def reset(self):
		self._position = 0
	
	def getRawValue(self):
		
		if self._position >= self._len:
		    return ""
		
		data = self._data
		
		inject = ''
		remaining = self._len - self._position
		
		#Need to determine the size of what to inject based on
		#the end of the data and the beginning
		if self._counts == 0 or remaining == 1:
			inject = struct.pack('B', self._dword & 0x000000FF)
		elif (self._counts == 1 and remaining >= 2) or remaining <= 2:
			inject = struct.pack('H', self._dword & 0x0000FFFF) #ushort
		elif (self._counts == 2 and remaining >= 3) or remaining <= 3: 
			inject = struct.pack('B', (self._dword & 0x00FF0000) >> 16) + \
			struct.pack('>H', self._dword & 0xFFFF)		    
		else:
			inject = struct.pack('L', self._dword)
		
		data = data[:self._position] + inject + data[self._position + len(inject):]
		
		return data


import random
class PartialFlipper(SimpleGenerator):
	'''
	Performs flips of 20% of bits in data.
	'''
	
	_data = None
	_position = 0
	
	def __init__(self, group, data, maxRounds = None):
		'''
		@type	data: string
		@param	data: Binary static blob to flip
		@type	maxRounds: int
		@param	maxRounds: optional, override 0.2% with a fixed number
		'''
		SimpleGenerator.__init__(self, group)
		
		self._data = str(data)	# Could be a unicode string.
		self._len = len(data)
		self._position = 0
		self._bit = 0
		self._maxRounds = int((len(data)*8) * 0.20)
		self._round = 0
	
		if maxRounds != None:
			self._maxRounds = maxRounds
	
	def next(self):
		self._round += 1
		
		# Exit if we are completed with rounds, or have no data
		# to flip
		if self._round > self._maxRounds or (len(self._data)-1) < 1:
			raise GeneratorCompleted("all don here")
		
		self._position = random.randint(0, len(self._data)-1)
		self._bit = random.randint(0, 7)
	
	def reset(self):
		self._bit = 0
		self._position = 0
		self._round = 0
	
	def getRawValue(self):
		
		if self._position >= self._len:
			return ""
		
		data = self._data
		
		byte = struct.unpack('B', data[self._position])[0]
		mask = 1 << self._bit
		
		if ( (byte & mask) >> self._bit ) == 1:
			
			mask = 0
			for i in range(8-self._bit):
				mask |= 1 << i
			mask = mask << 1
			
			if self._bit > 1:
				mask = mask << (self._bit)
				
				for i in range(self._bit):
					mask |= 1 << i
			
			byte = byte & mask
			
		else:
			byte = byte | mask
		
		packedup = struct.pack("B", byte)
		data = data[:self._position] + packedup + data[self._position+1:]
		
		return data

# end


