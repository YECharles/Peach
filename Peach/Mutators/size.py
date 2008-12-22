
'''
Mutators that operate on size-of relations.

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

class SizedVaranceMutator(Mutator):
	'''
	Change the length of sizes to count - N to count + N.
	'''
	
	def __init__(self, peach, node):
		Mutator.__init__(self)
		
		#: Is mutator finite?
		self.isFinite = True
		
		self.name = name
		self._peach = peach
		
		self._dataElementName = node.getFullname()
		self._random = random.Random()
		
		self._n = self._getN(node, n)
		self._range = range(0 - self._n, self._n)
		self._currentCount = 0
	
	def _getN(self, node, n):
		for c in node._children:
			if isinstance(c, Hint) and c.name == ('%s-N' % self.name):
				try:
					n = int(c.value)
				except:
					raise PeachException("Expected numerical value for Hint named [%s]" % c.name)
		
		return n
	
	def next(self):
		self._currentCount += 1
		if self._currentCount >= len(self._range):
			raise MutatorCompleted()
	
	def getCount(self):
		return len(self._range)
	
	def supportedDataElement(e):
		if isinstance(e, DataElement) and e._HasSizeofRelation(e) and e.isMutable:
			return True
		
		return False
	supportedDataElement = staticmethod(supportedDataElement)
	
	def sequencialMutation(self, node):
		self._performMutation(node, self._range[self._currentCount])
	
	def randomMutation(self, node):
		count = self._random.choice(self._range)
		self._performMutation(node, count)
	
	def _performMutation(self, node, count):
		'''
		Perform array mutation using count
		'''
		
		relation = node._GetSizeofRelation()
		nodeOf = relation.getOfElement()
		size = long(node.getInternalValue())
		n = size + count
		
		if n == 0:
			node.currentValue = ""
		
		elif n < size:
			node.currentValue = nodeOf.getValue()[:n]
			
		elif size == 0:
			node.currentValue = "A" * n
		
		else:
			node.currentValue = (node.getValue() * ((n/size)+1))[:n]
		
		# Verify things worked out okay
		assert(n == long(node.getInternalValue()))


class SizedNumericalEdgeCasesMutator(Mutator):
	'''
	Change the length of sizes to numerical edge cases
	'''
	
	def __init__(self, peach, node):
		Mutator.__init__(self)
		
		#: Is mutator finite?
		self.isFinite = True
		
		self.name = name
		self._peach = peach
		
		self._dataElementName = node.getFullname()
		self._random = random.Random()
		
		self._n = self._getN(node, n)
		self._range = self._populateValues(node)
		self._currentCount = 0
	
	def _populateValues(self, node):
		if isinstance(node, Number):
			size = node.size
		elif isinstance(node, Flag):
			size = node.length
			
			if size < 16:
				size = 8
			elif size < 32:
				size = 16
			elif size < 64:
				size = 32
			else:
				size = 64
			
		else:
			size = 64 # In the case of strings or blobs
		
		nums = []
		try:
			
			if size < 16:
				gen = BadNumbers8()
			else:
				gen = BadNumbers16(None, self._n)
			
			## Only if we are testing large memory
			#gen = BadNumbers24(None, self._n)
			#gen = BadNumbers32(None, self._n)
			#gen = BadNumbers(None, self._n)
			
			while True:
				nums.append(int(gen.getValue()))
				gen.next()
		except:
			pass
		
		return nums
		
	def _getN(self, node, n):
		for c in node._children:
			if isinstance(c, Hint) and c.name == ('%s-N' % self.name):
				try:
					n = int(c.value)
				except:
					raise PeachException("Expected numerical value for Hint named [%s]" % c.name)
		
		return n
	
	def next(self):
		self._currentCount += 1
		if self._currentCount >= len(self._range):
			raise MutatorCompleted()
	
	def getCount(self):
		return len(self._range)
	
	def supportedDataElement(e):
		# This will pick up both numbers or strings, etc that have a size-of relation
		if isinstance(e, DataElement) and e._HasSizeofRelation(e) and e.isMutable:
			return True
		
		return False
	supportedDataElement = staticmethod(supportedDataElement)
	
	def sequencialMutation(self, node):
		self._performMutation(node, self._range[self._currentCount])
	
	def randomMutation(self, node):
		count = self._random.choice(self._range)
		self._performMutation(node, count)
	
	def _performMutation(self, node, count):
		'''
		Perform array mutation using count
		'''
		
		relation = node._GetSizeofRelation()
		nodeOf = relation.getOfElement()
		size = long(node.getInternalValue())
		n = count
		
		if n == 0:
			node.currentValue = ""
		
		elif n < size:
			node.currentValue = nodeOf.getValue()[:n]
			
		elif size == 0:
			node.currentValue = "A" * n
		
		else:
			node.currentValue = (node.getValue() * ((n/size)+1))[:n]
		
		# Verify things worked out okay
		assert(n == long(node.getInternalValue()))


class SizedDataVaranceMutator(Mutator):
	'''
	Change the length of sized data to count - N to count + N.
	Size indicator will stay the same
	'''
	
	def __init__(self, peach, node):
		Mutator.__init__(self)
		
		#: Is mutator finite?
		self.isFinite = True
		
		self.name = name
		self._peach = peach
		
		self._dataElementName = node.getFullname()
		self._random = random.Random()
		
		self._n = self._getN(node, n)
		self._range = range(0 - self._n, self._n)
		self._currentCount = 0
	
	def _getN(self, node, n):
		for c in node._children:
			if isinstance(c, Hint) and c.name == ('%s-N' % self.name):
				try:
					n = int(c.value)
				except:
					raise PeachException("Expected numerical value for Hint named [%s]" % c.name)
		
		return n
	
	def next(self):
		self._currentCount += 1
		if self._currentCount >= len(self._range):
			raise MutatorCompleted()
	
	def getCount(self):
		return len(self._range)
	
	def supportedDataElement(e):
		if isinstance(e, DataElement) and e._HasSizeofRelation(node) and e.isMutable:
			return True
		
		return False
	supportedDataElement = staticmethod(supportedDataElement)
	
	def sequencialMutation(self, node):
		self._performMutation(node, self._range[self._currentCount])
	
	def randomMutation(self, node):
		count = self._random.choice(self._range)
		self._performMutation(node, count)
	
	def _performMutation(self, node, count):
		'''
		Perform array mutation using count
		'''
		
		relation = node._GetSizeofRelation()
		nodeOf = relation.getOfElement()
		size = long(node.getInternalValue())
		
		# Keep size indicator the same
		node.currentValue = node.getInternalValue()
		
		# Modify data
		n = size + count
		
		if n == 0:
			node.currentValue = ""
		
		elif n < size:
			node.currentValue = nodeOf.getValue()[:n]
			
		elif size == 0:
			node.currentValue = "A" * n
		
		else:
			node.currentValue = (node.getValue() * ((n/size)+1))[:n]
		
		# Verify things worked out okay
		assert(size == long(node.getInternalValue()))


class SizedDataNumericalEdgeCasesMutator(Mutator):
	'''
	Change the length of sizes to numerical edge cases
	'''
	
	def __init__(self, peach, node):
		Mutator.__init__(self)
		
		#: Is mutator finite?
		self.isFinite = True
		
		self.name = name
		self._peach = peach
		
		self._dataElementName = node.getFullname()
		self._random = random.Random()
		
		self._n = self._getN(node, n)
		self._range = self._populateValues(node)
		self._currentCount = 0
	
	def _populateValues(self, node):
		if isinstance(node, Number):
			size = node.size
		elif isinstance(node, Flag):
			size = node.length
			
			if size < 16:
				size = 8
			elif size < 32:
				size = 16
			elif size < 64:
				size = 32
			else:
				size = 64
			
		else:
			size = 64 # In the case of strings or blobs
		
		nums = []
		try:
			
			if size < 16:
				gen = BadNumbers8()
			else:
				gen = BadNumbers16(None, self._n)
			
			## Only if we are testing large memory
			#gen = BadNumbers24(None, self._n)
			#gen = BadNumbers32(None, self._n)
			#gen = BadNumbers(None, self._n)
			
			while True:
				nums.append(int(gen.getValue()))
				gen.next()
		except:
			pass
		
		return nums
		
	def _getN(self, node, n):
		for c in node._children:
			if isinstance(c, Hint) and c.name == ('%s-N' % self.name):
				try:
					n = int(c.value)
				except:
					raise PeachException("Expected numerical value for Hint named [%s]" % c.name)
		
		return n
	
	def next(self):
		self._currentCount += 1
		if self._currentCount >= len(self._range):
			raise MutatorCompleted()
	
	def getCount(self):
		return len(self._range)
	
	def supportedDataElement(e):
		# This will pick up both numbers or strings, etc that have a size-of relation
		if isinstance(e, DataElement) and e._HasSizeofRelation(node) and e.isMutable:
			return True
		
		return False
	supportedDataElement = staticmethod(supportedDataElement)
	
	def sequencialMutation(self, node):
		self._performMutation(node, self._range[self._currentCount])
	
	def randomMutation(self, node):
		count = self._random.choice(self._range)
		self._performMutation(node, count)
	
	def _performMutation(self, node, count):
		'''
		Perform array mutation using count
		'''
		
		relation = node._GetSizeofRelation()
		nodeOf = relation.getOfElement()
		size = long(node.getInternalValue())
		
		# Keep size indicator the same
		node.currentValue = node.getInternalValue()

		n = count
		
		if n == 0:
			node.currentValue = ""
		
		elif n < size:
			node.currentValue = nodeOf.getValue()[:n]
			
		elif size == 0:
			node.currentValue = "A" * n
		
		else:
			node.currentValue = (node.getValue() * ((n/size)+1))[:n]
		
		# Verify things worked out okay
		assert(size == long(node.getInternalValue()))

# end
