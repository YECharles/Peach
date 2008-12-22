
'''
Mutators that operate on string types.

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

import sys, os, time

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


class StringTokenMutator(_SimpleGeneratorMutator):
	'''
	Apply StringTokenFuzzer to each string node in DDT
	one Node at a time.
	'''
	
	def __init__(self, peach, node):
		_SimpleGeneratorMutator.__init__(self, peach, node)
		
		self.name = "StringTokenMutator"
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
	

class XmlW3CMutator(_SimpleGeneratorMutator):
	'''
	Performs the W3C parser tests.  Only works on
	<String> elements with a <Hint name="type" value="xml">
	'''
	
	def __init__(self, peach, node):
		_SimpleGeneratorMutator.__init__(self, peach, node)
		
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
