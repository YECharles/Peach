
'''
Mutators that operate on string types.

@author: Michael Eddington
@version: $Id$
'''

#
# Copyright (c) 2008-2009 Michael Eddington
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

import sys, os, time, random, array

from Peach.generator import *
from Peach.Generators.data import *
from Peach.Generators.xmlstuff import *

from Peach.mutator import *
from Peach.Engine.common import *

class StringCaseMutator(Mutator):
	'''
	This mutator changes the case of a string.
	'''
	
	def __init__(self, peach, node):
		Mutator.__init__(self)
		self.isFinite = True
		self.name = "StringCaseMutator"
		self._peach = peach
		self._mutations = [
			self._mutationLowerCase,
			self._mutationUpperCase,
			self._mutationRandomCase,
			]
		self._count = len(self._mutations)
		self._index = 0
	
	def next(self):
		self._index += 1
		if self._index >= self._count:
			raise MutatorCompleted()
	
	def getCount(self):
		return self._count

	def supportedDataElement(node):
		if isinstance(node, String) and node.isMutable:
			return True
		
		return False
	supportedDataElement = staticmethod(supportedDataElement)

	def sequencialMutation(self, node):
		node.currentValue = self._mutations[self._index](node.getInternalValue())
	
	def randomMutation(self, node):
		node.currentValue = self._random.choice(self._mutations)(node.getInternalValue())
		
	def _mutationLowerCase(self, data):
		return data.lower()
	
	def _mutationUpperCase(self, data):
		return data.upper()
	
	def _mutationRandomCase(self, data):
		if len(data) > 20:
			for i in self._random.sample(xrange(len(data)), 20):
				c = data[i]
				c = self._random.choice([c.lower(), c.upper()])
				data = data[:i] + c + data[i+1:]
			
			return data
		
		for i in range(len(data)):
			c = data[i]
			c = self._random.choice([c.lower(), c.upper()])
			data = data[:i] + c + data[i+1:]
			
		return data


class UnicodeStringsMutator(Mutator):
	'''
	Generate unicode strings
	'''
	
	values = None
	
	def __init__(self, peach, node):
		Mutator.__init__(self)
		#: Weight to be chosen randomly
		self.weight = 2
		
		self.name = "UnicodeStringsMutator"
		
		if UnicodeStringsMutator.values == None:
			self._genValues()
			
		self.isFinite = True
		self._peach = peach
		self._count = 0
		self._maxCount = len(self.values)
		
	def _genValues(self):
		if UnicodeStringsMutator.values == None:
			
			values = []
			
			# Add some long strings
			sample = random.sample(range(2, 6024), 200)
			sample.append(0)
			sample.append(1024 * 65)
			
			uchars = xrange(0, 0xffff)
			for length in sample:
				
				value = u""
				for i in range(length):
					value += unichr(random.choice(uchars))
				
				values.append(value)
			
			UnicodeStringsMutator.values = values
	
	def next(self):
		'''
		Goto next mutation.  When this is called
		the state machine is updated as needed.
		'''
		
		self._count += 1
		if self._count >= self._maxCount:
			self._count -= 1
			raise MutatorCompleted()
	
	def getCount(self):
		return self._maxCount

	def supportedDataElement(node):
		if isinstance(node, String) \
			and node.type != 'ascii' \
			and node.type != 'char' \
			and node.isMutable:
			
			return True
		
		return False
	supportedDataElement = staticmethod(supportedDataElement)

	def sequencialMutation(self, node):
		node.currentValue = self.values[self._count]
	
	def randomMutation(self, node):
		node.currentValue = random.choice(self.values)


class ValidValuesMutator(Mutator):
	'''
	Allows different valid values to be
	specified.
	'''
	
	# 'ValidValues'
	
	def __init__(self, peach, node):
		Mutator.__init__(self)
		
		#: Weight to be chosen randomly
		self.weight = 2
		
		self.name = "ValidValuesMutator"
		
		self.values = []
		
		self._genValues(node)
		
		self.isFinite = True
		self._peach = peach
		self._count = 0
		self._maxCount = len(self.values)
		
	def _genValues(self, node):
		self.values = []
		
		for child in node:
			if isinstance(child, Hint) and child.name == 'ValidValues':
				self.values = child.value.split(';')
		
	def next(self):
		'''
		Goto next mutation.  When this is called
		the state machine is updated as needed.
		'''
		
		self._count += 1
		if self._count >= self._maxCount:
			self._count -= 1
			raise MutatorCompleted()
	
	def getCount(self):
		return self._maxCount

	def supportedDataElement(node):
		if isinstance(node, String) and node.isMutable:
			return True
		
		return False
	supportedDataElement = staticmethod(supportedDataElement)

	def sequencialMutation(self, node):
		node.finalValue = self.values[self._count]
	
	def randomMutation(self, node):
		node.finalValue = random.choice(self.values)

class UnicodeBomMutator(Mutator):
	'''
	Injects BOM markers into default value and longer strings.
	'''
	
	values = None
	boms = ['\xFE\xFF', '\xFF\xEF', '\xEF\xBB\xBF']
	
	def __init__(self, peach, node):
		Mutator.__init__(self)
		#: Weight to be chosen randomly
		self.weight = 2
		
		self.name = "UnicodeBomMutator"
		
		if UnicodeBomMutator.values == None:
			self._genValues()
			
		self.isFinite = True
		self._peach = peach
		self._count = 0
		self._maxCount = len(self.values)
		
	def _genValues(self):
		if UnicodeBomMutator.values == None:
			
			valuesWithBOM = []
			
			values = []
			
			# Add some long strings
			sample = random.sample(range(2, 2024, 2), 200)
			sample.append(0)
			sample.append(1024 * 2)
			
			for r in sample:
				values.append('A' * r)
			
			# 1. Prefix with both BOMs
			for v in values:
				for b in self.boms:
					valuesWithBOM.append(b + v)
			
			# 2. Every other wchar
			for v in values:
				for b in self.boms:
					newval = b
					for i in range(0, len(v), 2):
						newval += v[i:i+2]
						newval += b
					
					valuesWithBOM.append(newval)
			
			# 3. Just BOM's
			for r in sample:
				newval = ""
				for i in range(r):
					newval += random.choice(self.boms)
				
				valuesWithBOM.append(newval)
			
			UnicodeBomMutator.values = valuesWithBOM
			values = None
		
	def next(self):
		'''
		Goto next mutation.  When this is called
		the state machine is updated as needed.
		'''
		
		self._count += 1
		if self._count >= self._maxCount:
			self._count -= 1
			raise MutatorCompleted()
	
	def getCount(self):
		return self._maxCount

	def supportedDataElement(node):
		if isinstance(node, String) and node.isMutable:
			return True
		
		return False
	supportedDataElement = staticmethod(supportedDataElement)

	def sequencialMutation(self, node):
		node.finalValue = self.values[self._count]
	
	def randomMutation(self, node):
		node.finalValue = random.choice(self.values)


class UnicodeBadUtf8Mutator(Mutator):
	'''
	Generate bad UTF-8 strings.
	'''
	
	values = None
	
	def __init__(self, peach, node):
		Mutator.__init__(self)
		#: Weight to be chosen randomly
		self.weight = 2
		
		self.name = "UnicodeBadUtf8Mutator"
		
		if UnicodeBadUtf8Mutator.values == None:
			self._genValues()
			
		self.isFinite = True
		self._peach = peach
		self._count = 0
		self._maxCount = len(self.values)
	
	def _utf8OneByte(self, c):
		return struct.pack("!B", c)
	
	def binaryFormatter(self, num, bits = None, strip = False):
		
		if bits == None:
			bits = 64
			strip = True
		
		if type(num) == str:
			raise Exception("Strings not permitted")
		
		ret = ""
		for i in range(bits-1, -1, -1):
			ret += str((num >> i) & 1)
		
		if strip:
			return ret.lstrip('0')
		
		return ret
	
	def _utf8TwoByte(self, c, mask = '1100000010000000'):
		
		bfC = self.binaryFormatter(c)
		if len(bfC) > 11:
			raise Exception("Larger than two byte UTF-8")
		
		bfC = self.binaryFormatter(c, 11)
		bf = array.array('c', mask)
		
		bf[3:8] = array.array('c', bfC[0:5])
		bf[10:16] = array.array('c', bfC[5:])
		
		bfs = bf.tostring()
		return struct.pack("!BB", int(bfs[0:8], 2), int(bfs[8:16], 2))
		
	def _utf8ThreeByte(self, c, mask = '111000001000000010000000'):
		
		bfC = self.binaryFormatter(c)
		if len(bfC) > 16:
			raise Exception("Larger than three byte UTF-8")
		
		bfC = self.binaryFormatter(c, 16)
		bf = array.array('c', mask)
		bf[4:8] = array.array('c', bfC[:4])
		bf[10:16] = array.array('c', bfC[4:10])
		bf[18:24] = array.array('c', bfC[10:])
		
		bfs = bf.tostring()
		return struct.pack("!BBB", int(bfs[0:8], 2), int(bfs[8:16], 2),
						   int(bfs[16:24], 2))
		
	def _utf8FourByte(self, c, mask = '11110000100000001000000010000000'):
		
		bfC = self.binaryFormatter(c)
		if len(bfC) > 21:
			raise Exception("Larger than four byte UTF-8")
		
		bfC = self.binaryFormatter(c, 21)
		bf = array.array('c', mask)
		bf[5:8] = array.array('c', bfC[:3])
		bf[10:16] = array.array('c', bfC[3:9])
		bf[18:24] = array.array('c', bfC[9:15])
		bf[26:32] = array.array('c', bfC[15:])
		
		bfs = bf.tostring()
		return struct.pack("!BBBB", int(bfs[0:8], 2), int(bfs[8:16], 2),
						   int(bfs[16:24], 2), int(bfs[24:32], 2))
		
	def _utf8FiveByte(self, c, mask = '1111100010000000100000001000000010000000'):
		
		bfC = self.binaryFormatter(c)
		if len(bfC) > 26:
			raise Exception("Larger than five byte UTF-8")
		
		bfC = self.binaryFormatter(c, 26)
		bf = array.array('c', mask)
		bf[6:8] = array.array('c', bfC[:2])
		bf[10:16] = array.array('c', bfC[2:8])
		bf[18:24] = array.array('c', bfC[8:14])
		bf[26:32] = array.array('c', bfC[14:20])
		bf[34:40] = array.array('c', bfC[20:])
		
		bfs = bf.tostring()
		return struct.pack("!BBBBB", int(bfs[0:8], 2), int(bfs[8:16], 2),
						   int(bfs[16:24], 2), int(bfs[24:32], 2), int(bfs[32:40], 2))
	
	def _utf8SixByte(self, c, mask = '111111001000000010000000100000001000000010000000'):
		
		bfC = self.binaryFormatter(c)
		if len(bfC) > 31:
			raise Exception("Larger than six byte UTF-8")
		
		bfC = self.binaryFormatter(c, 31)
		bf = array.array('c', mask)
		bf[7] = bfC[0]
		bf[10:16] = array.array('c', bfC[1:7])
		bf[18:24] = array.array('c', bfC[7:13])
		bf[26:32] = array.array('c', bfC[13:19])
		bf[34:40] = array.array('c', bfC[19:25])
		bf[42:48] = array.array('c', bfC[25:31])
		
		bfs = bf.tostring()
		return struct.pack("!BBBBBB", int(bfs[0:8], 2), int(bfs[8:16], 2),
						   int(bfs[16:24], 2), int(bfs[24:32], 2), int(bfs[32:40], 2),
						   int(bfs[40:48], 2))
	
	def _utf8SevenByte(self, c, mask = '11111110100000001000000010000000100000001000000010000000'):
		
		bfC = self.binaryFormatter(c, 36)
		bf = array.array('c', mask)
		bf[10:16] = array.array('c', bfC[:6])
		bf[18:24] = array.array('c', bfC[6:12])
		bf[26:32] = array.array('c', bfC[12:18])
		bf[34:40] = array.array('c', bfC[18:24])
		bf[42:48] = array.array('c', bfC[24:30])
		bf[50:56] = array.array('c', bfC[30:])
		
		bfs = bf.tostring()
		return struct.pack("!BBBBBBB", int(bfs[0:8], 2), int(bfs[8:16], 2),
						   int(bfs[16:24], 2), int(bfs[24:32], 2), int(bfs[32:40], 2),
						   int(bfs[40:48], 2), int(bfs[48:], 2))
		
	def _genValues(self):
		if UnicodeBadUtf8Mutator.values == None:
			
			encoding = [
				self._utf8OneByte,
				self._utf8TwoByte,
				self._utf8ThreeByte,
				self._utf8FourByte,
				self._utf8FiveByte,
				self._utf8SixByte,
				self._utf8SevenByte
				]
			
			endValues = []
			
			# Add some long strings
			sample = random.sample(range(2, (2 * 1024), 2), 100)
			sample.append(1024 * 2)
			for s in random.sample(range(2, 500), 50):
				sample.append(s)
			
			ascii = range(32, 126)
			for r in sample:
				value = ""
				for i in range(r):
					value += random.choice(encoding)(random.choice(ascii))
			
				endValues.append(value)
			
			UnicodeBadUtf8Mutator.values = endValues
		
	def next(self):
		'''
		Goto next mutation.  When this is called
		the state machine is updated as needed.
		'''
		
		self._count += 1
		if self._count >= self._maxCount:
			self._count -= 1
			raise MutatorCompleted()
	
	def getCount(self):
		return self._maxCount+1

	def supportedDataElement(node):
		if isinstance(node, String) and node.isMutable and node.type != 'wchar':
			return True
		
		return False
	supportedDataElement = staticmethod(supportedDataElement)

	def sequencialMutation(self, node):
		node.finalValue = self.values[self._count]
	
	def randomMutation(self, node):
		node.finalValue = random.choice(self.values)


class UnicodeUtf8ThreeCharMutator(UnicodeBadUtf8Mutator):
	'''
	Generate long UTF-8 three byte strings
	'''
	
	def __init__(self, peach, node):
		UnicodeBadUtf8Mutator.__init__(self, peach, node)
		
		#: Weight to be chosen randomly
		self.weight = 2
		self.name = "UnicodeUtf8ThreeCharMutator"
		
	def _genValues(self):
		if UnicodeUtf8ThreeCharMutator.values == None:
			
			endValues = []
			
			# Add some long strings
			sample = random.sample(range(2, (2 * 1024), 2), 300)
			sample.append(1024 * 2)
			
			# 1. Three char encoded values (can cause odd overflows)
			for r in sample:
				print type(r), r
				s = self._utf8ThreeByte(0xf0f0)
				endValues.append(s * r)
			
			UnicodeUtf8ThreeCharMutator.values = endValues


class _SimpleGeneratorMutator(Mutator):
	'''
	Base class for other mutators that use a
	generator.
	'''
	
	def __init__(self, peach, node):
		Mutator.__init__(self)
		self.isFinite = True
		self._peach = peach
		self._count = None
		self._generator = None
	
	def next(self):
		'''
		Goto next mutation.  When this is called
		the state machine is updated as needed.
		'''
		
		try:
			self._generator.next()
		
		except GeneratorCompleted:
			raise MutatorCompleted()
	
	def getCount(self):
		return self._count

	def supportedDataElement(node):
		if isinstance(node, String) and node.isMutable:
			return True
		
		return False
	supportedDataElement = staticmethod(supportedDataElement)

	def sequencialMutation(self, node):
		'''
		Perform a sequencial mutation
		'''
		node.currentValue = self._generator.getValue()
	
	def randomMutation(self, node):
		'''
		Perform a random mutation
		
		TODO: This is slow, we should speed it up
		'''
		count = self._random.randint(0, self._count - 1)
		gen = BadStrings()
		
		try:
			for i in range(count):
				gen.next()
		
		except GeneratorCompleted:
			pass
		
		node.currentValue = gen.getValue()


class StringMutator(_SimpleGeneratorMutator):
	'''
	Apply StringFuzzer to each string node in DDT
	one Node at a time.
	'''
	
	def __init__(self, peach, node):
		_SimpleGeneratorMutator.__init__(self, peach, node)
		#: Weight to be chosen randomly
		self.weight = 3
		
		self.name = "StringMutator"
		self._generator = BadStrings()
		
		# Get count
		gen = BadStrings()
		try:
			self._count = 0
			while True:
				self._count += 1
				gen.next()
		except GeneratorCompleted:
			pass
		self._count -= 1
	

class XmlW3CMutator(_SimpleGeneratorMutator):
	'''
	Performs the W3C parser tests.  Only works on
	<String> elements with a <Hint name="type" value="xml">
	'''
	
	def __init__(self, peach, node):
		_SimpleGeneratorMutator.__init__(self, peach, node)
		#: Weight to be chosen randomly
		self.weight = 2
		
		self.name = "XmlW3CMutator"
		self._generator = XmlParserTests(None)
		
		# Get count
		gen = XmlParserTests(None)
		try:
			self._count = 0
			while True:
				self._count += 1
				gen.next()
		except GeneratorCompleted:
			pass
	
	def supportedDataElement(node):
		if isinstance(node, String) and node.isMutable:
			for child in node:
				if isinstance(child, Hint) and child.name == 'type' and child.value == 'xml':
					return True
		
		return False
	supportedDataElement = staticmethod(supportedDataElement)


class PathMutator(_SimpleGeneratorMutator):
	'''
	Perform path mutatons.  Only works on
	<String> elements with a <Hint name="type" value="path">
	'''
	
	def __init__(self, peach, node):
		_SimpleGeneratorMutator.__init__(self, peach, node)
		#: Weight to be chosen randomly
		self.weight = 2
		
		self.name = "PathMutator"
		self._generator = BadPath(None)
		
		# Get count
		gen = BadPath(None)
		try:
			self._count = 0
			while True:
				self._count += 1
				gen.next()
		except GeneratorCompleted:
			pass
	
	def supportedDataElement(node):
		if isinstance(node, String) and node.isMutable:
			for child in node:
				if isinstance(child, Hint) and child.name == 'type' and child.value == 'path':
					return True
		
		return False
	supportedDataElement = staticmethod(supportedDataElement)


class HostnameMutator(_SimpleGeneratorMutator):
	'''
	Perform hostname mutators.  Only works on
	<String> elements with a <Hint name="type" value="hostname">
	'''
	
	def __init__(self, peach, node):
		_SimpleGeneratorMutator.__init__(self, peach, node)
		#: Weight to be chosen randomly
		self.weight = 2
		
		self.name = "HostnameMutator"
		self._generator = BadHostname(None)
		
		# Get count
		gen = BadHostname(None)
		try:
			self._count = 0
			while True:
				self._count += 1
				gen.next()
		except GeneratorCompleted:
			pass
	
	def supportedDataElement(node):
		if isinstance(node, String) and node.isMutable:
			for child in node:
				if isinstance(child, Hint) and child.name == 'type' and child.value == 'hostname':
					return True
		
		return False
	supportedDataElement = staticmethod(supportedDataElement)


class FilenameMutator(_SimpleGeneratorMutator):
	'''
	Perform hostname mutators.  Only works on
	<String> elements with a <Hint name="type" value="filename">
	'''
	
	def __init__(self, peach):
		_SimpleGeneratorMutator.__init__(self, peach, node)
		#: Weight to be chosen randomly
		self.weight = 2
		
		self.name = "FilenameMutator"
		self._generator = BadFilename(None)
		
		# Get count
		gen = BadFilename(None)
		try:
			self._count = 0
			while True:
				self._count += 1
				gen.next()
		except GeneratorCompleted:
			pass
	
	def supportedDataElement(node):
		if isinstance(node, String) and node.isMutable:
			for child in node:
				if isinstance(child, Hint) and child.name == 'type' and child.value == 'filename':
					return True
		
		return False
	supportedDataElement = staticmethod(supportedDataElement)


# end
