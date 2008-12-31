
'''
Mutators that operate on arrays and count relations.

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

from Peach.Generators.data import BadPositiveNumbersSmaller
from Peach.mutator import *
from Peach.Engine.common import *

class ArrayVarianceMutator(Mutator):
	'''
	Change the length of arrays to count - N to count + N.
	'''
	
	def __init__(self, peach, node, name = "ArrayVarianceMutator"):
		Mutator.__init__(self)
		
		if not ArrayVarianceMutator.supportedDataElement(node):
			raise Exception("Error: ArrayVarianceMutator created with bad node")
		
		#: Is mutator finite?
		self.isFinite = True
		
		self.name = name
		self._peach = peach
		self._n = self._getN(node, 50)
		self._arrayCount = node.getArrayCount()
		self._minCount = self._arrayCount - self._n
		self._maxCount = self._arrayCount + self._n
		
		if self._minCount < 0:
			self._minCount = 0
			
		self._currentCount = self._minCount
	
	def _getN(self, node, n):
		'''
		Gets N by checking node for hint, or returnign default
		'''
		
		for c in node._children:
			if isinstance(c, Hint) and c.name == ('%s-N' % self.name):
				try:
					n = int(c.value)
				except:
					raise PeachException("Expected numerical value for Hint named [%s]" % c.name)
		
		return n
	
	def next(self):
		'''
		Goto next mutation.  When this is called
		the state machine is updated as needed.
		'''
		
		self._currentCount += 1
		if self._currentCount > self._maxCount:
			raise MutatorCompleted()
	
	def getCount(self):
		
		return self._maxCount - self._minCount
	
	def supportedDataElement(e):
		'''
		Returns true if element is supported by
		this mutator
		
		 * Is a DataElement
		 * Is an Array
		 * Is head of array
		'''
		
		if isinstance(e, DataElement) and e.isArray() and e.arrayPosition == 0 and e.isMutable:
			return True
		
		return False
	supportedDataElement = staticmethod(supportedDataElement)
	
	def sequencialMutation(self, node):
		'''
		Perform a sequencial mutation
		'''
		
		self._performMutation(node, self._currentCount)
	
	def randomMutation(self, node):
		'''
		Perform a random mutation
		'''
		
		count = self._random.randint(self._minCount, self._maxCount)
		self._performMutation(node, count)
	
	def _performMutation(self, node, count):
		'''
		Perform array mutation using count
		'''
		
		n = count
		arrayHead = node
		
		# TODO: Support zero array elements!
		if n == 0:
			## Remove all
			#for i in xrange(self._arrayCount - 1, -1, -1):
			#	obj = arrayHead.getArrayElementAt(i)
			#	if obj == None:
			#		raise Exception("Couldn't locate item at pos %d (max of %d)" % (i, self._arrayCount))
			#	
			#	obj.parent.__delitem__(obj.name)
			pass
		
		elif n < self._arrayCount:
			# Remove some items
			for i in xrange(self._arrayCount - 1, n-1, -1):
				obj = arrayHead.getArrayElementAt(i)
				if obj == None:
					raise Exception("Couldn't locate item at pos %d (max of %d)" % (i, self._arrayCount))
				obj.parent.__delitem__(obj.name)
			
			assert(arrayHead.getArrayCount() == n)
		
		elif n > self._arrayCount:
			# Add some items
			headIndex = arrayHead.parent.index(arrayHead)
			
			# Faster, but getValue() might not be correct.
			obj = arrayHead.getArrayElementAt(arrayHead.getArrayCount()-1)
			try:
				obj.value = obj.getValue() * (n - self._arrayCount)
				obj.arrayPosition = n-1
			except MemoryError:
				# Catch out of memory errors
				pass
			
			### Slower but reliable (we hope)
			#for i in xrange(self._arrayCount, n):
			#	obj = arrayHead.copy(arrayHead)
			#	obj.arrayPosition = i
			#	arrayHead.parent.insert(headIndex+i, obj)
			
			#print arrayHead.getArrayCount(), n
			assert(arrayHead.getArrayCount() == n)

class ArrayNumericalEdgeCasesMutator(ArrayVarianceMutator):
	_counts = None
	
	def __init__(self, peach, node):
		ArrayVarianceMutator.__init__(self, peach, node, "ArrayNumericalEdgeCasesMutator")
		
		if self._counts == None:
			ArrayNumericalEdgeCasesMutator._counts = []
			gen = BadPositiveNumbersSmaller()
			try:
				while True:
					self._counts.append(int(gen.getValue()))
					gen.next()
			except:
				pass
		
		self._minCount = None
		self._maxCount = None
		
		self._countsIndex = 0
		self._currentCount = self._counts[self._countsIndex]
	
	def next(self):
		'''
		Goto next mutation.  When this is called
		the state machine is updated as needed.
		'''
		
		self._countsIndex += 1
		if self._countsIndex >= len(self._counts):
			raise MutatorCompleted()
		
		self._currentCount = self._counts[self._countsIndex]
	
	def getCount(self):
		return len(self._counts)
	
	def randomMutation(self, node):
		'''
		Perform a random mutation
		'''
		
		count = self._random.choice(self._counts)
		self._performMutation(node, count)


class ArrayReverseOrderMutator(ArrayVarianceMutator):
	def __init__(self, peach, node):
		ArrayVarianceMutator.__init__(self, peach, node, "ArrayReverseOrderMutator")
	
	def next(self):
		raise MutatorCompleted()
	
	def getCount(self):
		return 1
	
	def sequencialMutation(self, node):
		self._performMutation(node)

	def randomMutation(self, node):
		self._performMutation(node)

	def _performMutation(self, node):
		arrayHead = node
		headIndex = arrayHead.parent.index(arrayHead)
		items = []
		
		for i in xrange(self._arrayCount):
			obj = arrayHead.getArrayElementAt(i)
			items.append(obj)
			del obj.parent[obj.name]
		
		x = 0
		for i in xrange(self._arrayCount-1, -1, -1):
			obj = items[i]
			obj.parent.insert(headIndex + x, obj)
			obj.arrayPosition = x
			x+=1
		
		assert(self._arrayCount == arrayHead.getArrayCount())


class ArrayRandomizeOrderMutator(ArrayVarianceMutator):
	def __init__(self, peach, node):
		ArrayVarianceMutator.__init__(self, peach, node, "ArrayRandomizeOrderMutator")
		self._count = 0
		
	def next(self):
		self._count += 1
		if self._count > self._n:
			raise MutatorCompleted()
	
	def getCount(self):
		return self._n
	
	def sequencialMutation(self, node):
		self._performMutation(node)

	def randomMutation(self, node):
		self._performMutation(node)

	def _performMutation(self, node):
		arrayHead = node
		headIndex = arrayHead.parent.index(arrayHead)
		items = []
		
		for i in xrange(self._arrayCount):
			obj = arrayHead.getArrayElementAt(i)
			items.append(obj)
			del obj.parent[obj.name]
		
		random.shuffle(items)
		
		for i in xrange(self._arrayCount):
			obj = items[i]
			obj.parent.insert(headIndex + i, obj)
			obj.arrayPosition = i
		
		assert(self._arrayCount == arrayHead.getArrayCount())

# end
