
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

class NumericalVarianceMutator(Mutator):
	'''
	Produce numbers that are defaultValue - N to defaultValue + N.
	'''
	
	def __init__(self, peach):
		Mutator.__init__(self)
		
		self.name = "NumericalVarianceMutator"
		self._peach = peach
		
		self._stateMasterCount = -1
		self._masterGroup = GroupSequence()
		self._masterCount = 0
		self._countThread = None
		self._countGroup = GroupSequence()
		self._actions = []
		self._N = 50
		self._origN = 50
		
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

	def _getNumberElements(self, node):
		
		elements = []
		
		for e in node._children:
			if e.elementType == 'number' and e.isMutable:
				elements.append(e)
			
			if e.hasChildren:
				for ee in self._getNumberElements(e):
					elements.append(ee)
		
		return elements

	def _getN(self, node):
		'''
		Gets N by checking node for hint, or returnign default
		'''
		
		n = self._origN
		
		for c in node._children:
			if isinstance(c, Hint) and c.name == 'NumericalVarianceMutator-N':
				try:
					n = int(c.value)
				except:
					raise PeachException("Expected numerical value for Hint named [%s]" % c.name)
		
		return n

	#####################################################
	# Callbacks when Action needs a value
	
	def getActionValue(self, action):
		
		if action not in self._actions:
			
			self._generatorMap[action] = {}
			self._countGeneratorMap[action] = {}
			
			# Walk data tree and locate each string type.
			numberElements = self._getNumberElements(action.template)
			
			for e in numberElements:
				group = Group()
				
				value = e.getInternalValue()
				
				if value == None:
					value = 0
				
				n = self._getN(e)
				
				gen = NumberVariance(None, long(value), n)
				gen = WithDefault(group, _StaticFromTemplate(action, e), gen)
				self._masterGroup.append(group)
				self._generatorMap[action][e.getFullnameInDataModel()] = gen
				
				group = Group()
				gen = NumberVariance(None, long(value), n)
				gen = WithDefault(group, _StaticFromTemplate(action, e), gen)
				self._countGroup.append(group)
				self._countGeneratorMap[action][e.getFullnameInDataModel()] = gen
			
			self._actions.append(action)
		
		# Set values
		for name in self._generatorMap[action].keys():
			self._getElementByName(action.template, name).setValue(self._generatorMap[action][name].getValue())
		
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


class NumericalEdgeCaseMutator(Mutator):
	'''
	This is a straight up generation class.  Produces values
	that have nothing todo with defaultValue :)
	'''
	
	def __init__(self, peach):
		Mutator.__init__(self)
		
		self.name = "NumericalEdgeCaseMutator"
		self._peach = peach
		
		self._stateMasterCount = -1
		self._masterGroup = GroupSequence()
		self._masterCount = 0
		self._countThread = None
		self._countGroup = GroupSequence()
		self._actions = []
		self._origN = 50
		
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

	def _getNumberElements(self, node):
		
		elements = []
		
		for e in node._children:
			if e.elementType == 'number' and e.isMutable:
				elements.append(e)
			
			if e.hasChildren:
				for ee in self._getNumberElements(e):
					elements.append(ee)
		
		return elements

	def _getN(self, node):
		'''
		Gets N by checking node for hint, or returnign default
		'''
		
		n = self._origN
		
		for c in node._children:
			if isinstance(c, Hint) and c.name == 'NumericalEdgeCaseMutator-N':
				try:
					n = int(c.value)
				except:
					raise PeachException("Expected numerical value for Hint named [%s]" % c.name)
		
		return n

	#####################################################
	# Callbacks when Action needs a value
	
	def getActionValue(self, action):
		
		if action not in self._actions:
			
			self._generatorMap[action] = {}
			self._countGeneratorMap[action] = {}
			
			# Walk data tree and locate each string type.
			numberElements = self._getNumberElements(action.template)
			
			for e in numberElements:
				group = Group()
				
				n = self._getN(e)
				
				if e.size == 8:
					gen = BadNumbers8()
				elif e.size == 16:
					gen = BadNumbers16(None, n)
				elif e.size == 24:
					gen = BadNumbers24(None, n)
				elif e.size == 32:
					gen = BadNumbers32(None, n)
				else:
					gen = BadNumbers(None, n)
				
				gen = WithDefault(group, _StaticFromTemplate(action, e), gen)
				
				self._masterGroup.append(group)
				self._generatorMap[action][e.getFullnameInDataModel()] = gen
				
				group = Group()
				
				if e.size == 8:
					gen = BadNumbers8()
				elif e.size == 16:
					gen = BadNumbers16(None, n)
				elif e.size == 24:
					gen = BadNumbers24(None, n)
				elif e.size == 32:
					gen = BadNumbers32(None, n)
				else:
					gen = BadNumbers(None, n)
				
				gen = WithDefault(group, _StaticFromTemplate(action, e), gen)
				
				self._countGroup.append(group)
				self._countGeneratorMap[action][e.getFullnameInDataModel()] = gen
			
			self._actions.append(action)
		
		# Set values
		for key in self._generatorMap[action].keys():
			try:
				self._getElementByName(action.template, key).setValue(self._generatorMap[action][key].getValue())
			except:
				print "Caught exception on _getElementByName looking for [%s]" % key
				raise
		
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
	
	def onStateStart(self, state):
		pass
	
	def onStateComplete(self, state):
		pass
	
	def onActionStart(self, action):
		pass
	
	def onActionComplete(self, action):
		pass
	
	def onStateMachineStart(self, stateMachine):
		pass
	
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


class FiniteRandomNumbersMutator(Mutator):
	'''
	Produce a finite number of random numbers for
	each <Number> element.
	'''
	
	def __init__(self, peach):
		Mutator.__init__(self)
		
		self.name = "FiniteRandomNumbersMutator"
		self._peach = peach
		self._countThread = None
		
		self._random = random.Random()
		self._random.seed(12345)
		
		self._stateActionPos = -1
		self._statePos = -1
		self._masterCount = 0
		
		self._origN = 500
		self._maxCount = 500
		self._pos = 0
		self._actionPos = 0
		
		self._actions = []
		# key = action, value = array(numbername, cnt,min,max)
		self._map = {}
		self._value = 0
		
		self._masterCount = 0
		self._stateMasterCount = -1
	
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
		
		self._random = random.Random()
		self._random.seed(12345)
		self._countThread = None
		
		self._stateActionPos = -1
		self._statePos = -1
		self._masterCount = 0
		
		self._origN = 5000
		self._maxCount = 5000
		self._pos = 0
		self._actionPos = 0
		
		self._actions = []
		# key = action, value = array(numbername, cnt,min,max)
		self._map = {}
		self._value = 0
	
	def next(self):
		'''
		Goto next mutation.  When this is called
		the state machine is updated as needed.
		'''
		
		# Check if we set our state and need
		# to skip ahead.  We need todo this in
		# next() to assure we have all our action
		# templates added into our masterGroup
		if self._stateActionPos > -1:
			while self._actionPos < self._stateActionPos:
				self.realNext()
			
			while self._pos < self._statePos:
				self.realNext()
			
			self._stateActionPos = -1
			self._statePos = -1
		
		else:
			self.realNext()
		
		self._masterCount += 1
	
	def realNext(self):
		
		if len(self._map[self._actions[self._actionPos]]) > 0:
			(name, cnt, min, max, self._maxCount) = self._map[self._actions[self._actionPos]][self._pos]
			cnt += 1
			self._map[self._actions[self._actionPos]][self._pos][1] = cnt
		
		else:
			# Trigger next
			cnt = self._maxCount + 1
		
		if cnt > self._maxCount:
			try:
				self._map[self._actions[self._actionPos]][self._pos][1] = 0
			except:
				pass
			
			self._pos += 1
			
			if self._pos >= len(self._map[self._actions[self._actionPos]]):
				self._pos = 0
				self._actionPos += 1
				
				if self._actionPos >= len(self._actions):
					self._actionPos -= 1
					raise MutatorCompleted()
		
		# Only generate the value once.  So even if our .getValue() was called 20
		# times per round we always do the correct thing.
		if len(self._map[self._actions[self._actionPos]]) > 0:
			(name, cnt, min, max, self._maxCount) = self._map[self._actions[self._actionPos]][self._pos]
			self._value = self._random.randint(min, max)
		else:
			self._value = 0
	
	def getState(self):
		'''
		Return a binary string that contains
		any information about current state of
		Mutator.  This state information should be
		enough to let the same mutator "restart"
		and continue when setState() is called.
		'''
		
		return str(self._masterCount)
	
	def setState(self, state):
		'''
		Set the state of this object.  Should put us
		back in the same place as when we said
		"getState()".
		'''
		
		self._stateMasterCount = int(self._masterCount)
		try:
			for i in xrange(self._masterCount, self._stateMasterCont):
				self.next()
			
			self._stateMasterCount = -1
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
		for action in self._actions:
			for obj in self._map[action]:
				count += obj[4]
		
		return count

	def _getNumberElements(self, node):
		
		elements = []
		
		for e in node._children:
			if e.elementType == 'number' and e.size > 8 and e.isMutable:
				elements.append(e)
			
			if e.hasChildren:
				for ee in self._getNumberElements(e):
					elements.append(ee)
		
		return elements
	
	def _getN(self, node):
		'''
		Gets N by checking node for hint, or returnign default
		'''
		
		n = self._origN
		
		for c in node._children:
			if isinstance(c, Hint) and c.name == 'FiniteRandomNumbersMutator-N':
				try:
					n = int(c.value)
				except:
					raise PeachException("Expected numerical value for Hint named [%s]" % c.name)
		
		return n
	
	#####################################################
	# Callbacks when Action needs a value
	
	def getActionValue(self, action):
		
		if action not in self._actions:
			
			# Walk data tree and locate each string type.
			numberElements = self._getNumberElements(action.template)
			
			self._map[action] = []
			for e in numberElements:
				self._map[action].append([
					e.getFullnameInDataModel(),
					0,
					e.getMinValue(),
					e.getMaxValue(),
					self._getN(e)
					])
			
			self._actions.append(action)
		
		# Set values
		if self._actions[self._actionPos] == action and len(self._map[action]) > 0:
			(name, cnt, min, max, maxCount) = self._map[action][self._pos]
			action.template.findDataElementByName(name).setValue(self._value)
		
		# return value
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


# end
