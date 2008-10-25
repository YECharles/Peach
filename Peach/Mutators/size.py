
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
from Peach.Generators.block import *
from Peach.Generators.data import *
from Peach.Generators.dictionary import *
from Peach.Generators.flipper import *
from Peach.Generators.static import Static, _StaticFromTemplate, _StaticCurrentValueFromDom
from Peach.Transformers.encode import WideChar
from Peach import Transformers
from Peach.Generators.block import *
from Peach.Generators.data import *
from Peach.Generators.dictionary import *
from Peach.Generators.flipper import *
from Peach.Generators.static import Static, _StaticFromTemplate
from Peach.Transformers.encode import WideChar
from Peach.mutator import *
from Peach.group import *
from Peach.Engine.common import *

class _SizedMutator(Mutator):
	'''
	Common baseclass for SizeOf mutators
	'''
	
	def __init__(self, peach, name, n = 50):
		Mutator.__init__(self)
		
		self.name = name
		self._peach = peach
		
		self._stateMasterCount = -1
		self._masterGroup = GroupSequence()
		self._masterCount = 0
		self._countThread = None
		self._countGroup = GroupSequence()
		self._actions = []
		self._N = n
		self._origN = n
		
		# All active groups
		self._activeGroups = []
		
		# Hashtable, key is element, value is [group, generator]
		self._generatorMap = {}
		self._countGeneratorMap = {}
	
	def isFinite(self):
		'''
		Some mutators could contine forever, this
		should indicate.
		'''
		return True
	
	def reset(self):
		'''
		Reset mutator
		'''
		
		self._masterGroup = GroupSequence()
		self._activeGroups = []
		self._generatorMap = {}
		self._masterCount = 0
		self._actions = []
	
	def next(self):
		'''
		Goto next mutation.  When this is called
		the state machine is updated as needed.
		'''
		
		try:
			# Check if we set our state and need
			# to skip ahead.  We need todo this in
			# next() to assure we have all our action
			# templates added into our masterGroup
			if self._stateMasterCount > -1:
				for cnt in xrange(self._masterCount, self._stateMasterCount):
					self._masterGroup.next()
					self._masterCount += 1
				self._stateMasterCount = -1
			else:
				self._masterGroup.next()
				self._masterCount += 1
		
		except GroupCompleted:
			raise MutatorCompleted()
	
	def getState(self):
		'''
		Return a binary string that contains
		any information about current state of
		Mutator.  This state information should be
		enough to let the same mutator "restart"
		and continue when setState() is called.
		'''
		
		# Ensure a minor overlap of testing
		return str(self._masterCount - 2)
	
	def setState(self, state):
		'''
		Set the state of this object.  Should put us
		back in the same place as when we said
		"getState()".
		'''
		self._stateMasterCount = int(state)
		try:
			self.next()
		except:
			pass
		
	def getCount(self):
		if self._countThread != None and self._countThread.hasCountEvent.isSet():
			self._count = self._countThread.count
			self._countThread = None
			self._countGroup = None
			self._countGeneratorMap = None
		
		return self._count

	def calculateCount(self):
		
		count = 0
		try:
			while True:
				count += 1
				self._countGroup.next()
			
		except GroupCompleted:
			pass
		
		return count

	def _getSizedElements(self, node):
		'''
		Locate elements that are sized by a size-of relations.  We should
		beable to use the relation cache for this.
		'''
		
		if node.relationCache == None:
			raise Exception("relationCache does not exist!")
		
		elements = []
		root = node.getRootOfDataMap()
		
		for r in root.relationCache:
			r = node.find(r)
			if r != None and r.type == "size":
				elements.append(r.getOfElement())
		
		return elements

	def _getN(self, node):
		'''
		Gets N by checking node for hint, or returnign default
		'''
		
		n = self._origN
		
		for c in node._children:
			if isinstance(c, Hint) and c.name == ('%s-N' % self.name):
				try:
					n = int(c.value)
				except:
					raise PeachException("Expected numerical value for Hint named [%s]" % c.name)
		
		return n

	#####################################################
	# Callbacks when Action needs a value
	
	def getGenerator(self, e, n):
		pass
	
	def getActionValue(self, action):
		
		if action not in self._actions:
			
			self._generatorMap[action] = {}
			self._countGeneratorMap[action] = {}
			
			# Walk data tree and locate each string type.
			numberElements = self._getSizedElements(action.template)
			
			for e in numberElements:
				group = Group()
				
				n = self._getN(e)
				
				gen = self.getGenerator(e, n)
				gen = WithDefault(group, _StaticFromTemplate(action, e), gen)
				self._masterGroup.append(group)
				self._generatorMap[action][e.getFullnameInDataModel()] = gen
				
				group = Group()
				gen = self.getGenerator(e, n)
				gen = WithDefault(group, _StaticFromTemplate(action, e), gen)
				self._countGroup.append(group)
				self._countGeneratorMap[action][e.getFullnameInDataModel()] = gen
			
			self._actions.append(action)
		
		# Run Generator, no need to set the value, nothing is produced
		for name in self._generatorMap[action].keys():
			self._generatorMap[action][name].getValue()
		
		if action.template.modelHasOffsetRelation:
			stringBuffer = StreamBuffer()
			action.template.getValue(stringBuffer)
			stringBuffer.setValue("")
			stringBuffer.seekFromStart(0)
			action.template.getValue(stringBuffer)
		
			return stringBuffer.getValue()
		
		return action.template.getValue()
	
	def getActionParamValue(self, action):
		return self.getActionValue(action)
	
	def getActionChangeStateValue(self, action, value):
		return value
	
	
	#####################################################
	# Event callbacks for state machine
	
	def onStateMachineComplete(self, stateMachine):
		
		# Lets calc our count if we haven't already
		if self._count == -1 and self._countThread == None:
			self._countThread = MutatorCountCalculator(self)
			self._countThread.start()
		
		elif self._countThread != None:
			if self._countThread.hasCountEvent.isSet():
				self._count = self._countThread.count
				self._countThread = None
				self._countGroup = None
				self._countGeneratorMap = None

class SizedVaranceMutator(_SizedMutator):
	def __init__(self, peach):
		_SizedMutator.__init__(self, peach, "SizedVaranceMutator", 50)
	
	def getGenerator(self, e, n):
		return SizeVariance(None, e, n)

class SizedNumericalEdgeCasesMutator(_SizedMutator):
	def __init__(self, peach):
		_SizedMutator.__init__(self, peach, "SizedNumericalEdgeCasesMutator")
	
	def getGenerator(self, e, n):
		return SizeBadNumbers(None, e, n)

# end
