
'''
Mutators that operate on numerical types.

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

import sys, os, time, random
from Peach.Generators.data import *
from Peach.mutator import *
from Peach.Engine.common import *

class NumericalVarianceMutator(Mutator):
	'''
	Produce numbers that are defaultValue - N to defaultValue + N.
	'''
	
	def __init__(self, peach, node):
		Mutator.__init__(self)
		#: Weight to be chosen randomly
		self.weight = 2
		
		self.name = "NumericalVarianceMutator"
		
		#: Is mutator finite?
		self.isFinite = True
		
		self._dataElementName = node.getFullname()
		self._random = random.Random()
		
		self._n = self._getN(node, 50)
		self._values = range(0 - self._n, self._n)
		self._currentCount = 0
		
		self._minValue = node.getMinValue()
		self._maxValue = node.getMaxValue()
	
	def _getN(self, node, n):
		for c in node._children:
			if isinstance(c, Hint) and c.name == 'NumericalVarianceMutator-N':
				try:
					n = int(c.value)
				except:
					raise PeachException("Expected numerical value for Hint named [%s]" % c.name)
		
		return n
	
	def next(self):
		
		self._currentCount += 1
		if self._currentCount >= len(self._values):
			raise MutatorCompleted()
	
	def getCount(self):
		return len(self._values)
	
	def supportedDataElement(e):
		
		if isinstance(e, Number) and e.isMutable:
			return True
		
		return False
	supportedDataElement = staticmethod(supportedDataElement)
	
	def sequencialMutation(self, node):
		
		# Sometimes self._n == 0, catch that here
		if self._currentCount >= len(self._values):
			return
		
		node.currentValue = long(node.getInternalValue()) - self._values[self._currentCount]
	
	def randomMutation(self, node):
		try:
			count = self._random.choice(self._values)
			node.currentValue = str(long(node.getInternalValue()) + count)
		except ValueError:
			# Okay to skip, another mutator probably
			# changes this value already (like a datatree one)
			pass


class NumericalEdgeCaseMutator(Mutator):
	'''
	This is a straight up generation class.  Produces values
	that have nothing todo with defaultValue :)
	'''
	
	_values = None
	
	def __init__(self, peach, node):
		Mutator.__init__(self)
		#: Weight to be chosen randomly
		self.weight = 3
		
		#: Is mutator finite?
		self.isFinite = True
		self.name = "NumericalEdgeCaseMutator"
		self._peach = peach
		
		self._n = self._getN(node, 50)
		
		if self._values == None:
			self._populateValues()
		
		self._size = node.size
		self._dataElementName = node.getFullname()
		self._random = random.Random()
		self._currentCount = 0
		
		self._minValue = node.getMinValue()
		self._maxValue = node.getMaxValue()

	def _populateValues(self):
		NumericalEdgeCaseMutator._values = {}
		
		nums = []
		try:
			gen = BadNumbers8()
			while True:
				nums.append(int(gen.getValue()))
				gen.next()
		except:
			pass
		
		self._values[8] = nums
		
		nums = []
		try:
			
			gen = BadNumbers16(None, self._n)
			while True:
				nums.append(int(gen.getValue()))
				gen.next()
		except:
			pass
		
		self._values[16] = nums
		
		nums = []
		try:
			gen = BadNumbers24(None, self._n)
			while True:
				nums.append(int(gen.getValue()))
				gen.next()
		except:
			pass
		
		self._values[24] = nums
		
		nums = []
		try:
			gen = BadNumbers32(None, self._n)
			while True:
				nums.append(int(gen.getValue()))
				gen.next()
		except:
			pass
		
		self._values[32] = nums
		
		nums = []
		try:
			gen = BadNumbers(None, self._n)
			while True:
				nums.append(int(gen.getValue()))
				gen.next()
		except:
			pass
	
		self._values[64] = nums
	
	def next(self):
		self._currentCount += 1
		if self._currentCount >= len(self._values[self._size]):
			raise MutatorCompleted()
	
	def getCount(self):
		return len(self._values[self._size])

	def supportedDataElement(e):
		
		if isinstance(e, Number) and e.isMutable:
			return True
		
		return False
	supportedDataElement = staticmethod(supportedDataElement)

	def _getN(self, node, n):
		for c in node._children:
			if isinstance(c, Hint) and c.name == 'NumericalEdgeCaseMutator-N':
				try:
					n = int(c.value)
				except:
					raise PeachException("Expected numerical value for Hint named [%s]" % c.name)
		
		return n

	def sequencialMutation(self, node):
		node.currentValue = self._values[self._size][self._currentCount]
	
	def randomMutation(self, node):
		node.currentValue = self._random.choice(self._values[self._size])



class FiniteRandomNumbersMutator(Mutator):
	'''
	Produce a finite number of random numbers for
	each <Number> element.
	'''
	
	def __init__(self, peach, node):
		Mutator.__init__(self)
		#: Weight to be chosen randomly
		self.weight = 2
		
		self.name = "FiniteRandomNumbersMutator"
		self._peach = peach
		self._countThread = None
		
		self._random = random.Random()
		
		self._n = self._getN(node, 500)
		self._currentCount = 0
		
		self._minValue = node.getMinValue()
		self._maxValue = node.getMaxValue()

	def next(self):
		self._currentCount += 1
		if self._currentCount > self._n:
			raise MutatorCompleted()
	
	def getCount(self):
		return self._n
	
	def supportedDataElement(e):
		
		if isinstance(e, Number) and e.isMutable:
			return True
		
		return False
	supportedDataElement = staticmethod(supportedDataElement)
	
	def _getN(self, node, n):
		for c in node._children:
			if isinstance(c, Hint) and c.name == 'FiniteRandomNumbersMutator-N':
				try:
					n = int(c.value)
				except:
					raise PeachException("Expected numerical value for Hint named [%s]" % c.name)
		
		return n
	
	def sequencialMutation(self, node): 
		node.currentValue = self._random.randint(self._minValue, self._maxValue)
	
	def randomMutation(self, node):
		node.currentValue = self._random.randint(self._minValue, self._maxValue)



# end
