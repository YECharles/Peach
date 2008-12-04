
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

import sys, os, time
from Peach.Generators.block import *
from Peach.Generators.data import *
from Peach.Generators.dictionary import *
from Peach.Generators.flipper import *
from Peach.Generators.static import Static, _StaticAlwaysNone, _StaticCurrentValueFromDom
from Peach.Transformers.encode import WideChar
from Peach import Transformers
from Peach.Generators.data import *
from Peach.Generators.flipper import *
from Peach.Generators.static import _StaticAlwaysNone
from Peach.mutator import *
from Peach.group import *
from Peach.Engine.common import *

class DWORDSliderMutator(Mutator):
	'''
	Slides a DWORD through the blob.
	
	@author Chris Clark
	'''
	
	def __init__(self, peach):
		Mutator.__init__(self)
		                
		self.name = "DWORDSliderMutator"
		self._peach = peach
		
		self._stateMasterCount = -1
		self._masterGroup = GroupSequence()
		self._masterCount = 0
		self._countThread = None
		self._countGroup = GroupSequence()
		self._actions = []
		
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
		str(self._masterCount - 2)
		try:
			self.next()
		except:
			pass
	
	def setState(self, state):
		'''
		Set the state of this object.  Should put us
		back in the same place as when we said
		"getState()".
		'''
		if state == None:
			return
		
		self._stateMasterCount = int(state)
		
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

	def _getStringElements(self, node):
		
		elements = []
		
		for e in node._children:
			if e.elementType == 'blob' and e.isMutable:
				elements.append(e)
				for child in e:
					if isinstance(child, Hint) and child.name == 'DWORDSliderMutator' and child.value == 'off':
						elements.remove(e)
						break
			
			if e.hasChildren:
				for ee in self._getStringElements(e):
					elements.append(ee)
		
		return elements

	#####################################################
	# Callbacks when Action needs a value
	
	def getActionValue(self, action):
		
		if action not in self._actions:
			
			# Walk data tree and locate each string type.
			stringElements = self._getStringElements(action.template)
			self._generatorMap[action] = {}
			self._countGeneratorMap[action] = {}
			
			for e in stringElements:
				group = Group()
				gen = SequentialDWORDSlider(None, e.getValue())
				gen = WithDefault(group, _StaticAlwaysNone(), gen)
				self._masterGroup.append(group)
				self._generatorMap[action][e.getFullnameInDataModel()] = gen
				
				group = Group()
				gen = SequentialDWORDSlider(None, e.getValue())
				gen = WithDefault(group, _StaticAlwaysNone(), gen)
				self._countGroup.append(group)
				self._countGeneratorMap[action][e.getFullnameInDataModel()] = gen
			
			self._actions.append(action)
		
		# Set values
		for key in self._generatorMap[action].keys():
			value = self._generatorMap[action][key].getValue()
			if value != None:
				self._getElementByName(action.template, key).setValue(value)
		
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


class BitFlipperMutator(Mutator):
	'''
	Flip a % of total bits in blob.  Default % is 20.
	'''
	
	def __init__(self, peach):
		Mutator.__init__(self)
		
		self.name = "BitFlipperMutator"
		self._peach = peach
		                
		self._stateMasterCount = -1
		self._masterGroup = GroupSequence()
		self._masterCount = 0
		self._countThread = None
		self._countGroup = GroupSequence()
		self._actions = []
		
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
				for cnt in xrange(self._stateMasterCount):
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
		self.reset()
		self._stateMasterCount = int(state)
		
	def getCount(self):
		if self._countThread != None and self._countThread.hasCountEvent.isSet():
			self._count = self._countThread.count
			self._countThread = None
			self._countGroup = GroupSequence()
			self._countGeneratorMap = {}
		
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

	def _getStringElements(self, node):
		
		elements = []
		
		for e in node._children:
			if e.elementType == 'blob' and e.isMutable:
				elements.append(e)
			
			if e.hasChildren:
				for ee in self._getStringElements(e):
					elements.append(ee)
		
		return elements

	def _getN(self, node):
		'''
		Gets N by checking node for hint, or returnign default
		'''
		
		n = None
		
		for c in node._children:
			if isinstance(c, Hint) and c.name == 'BitFlipperMutator-N':
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
			stringElements = self._getStringElements(action.template)
			self._generatorMap[action] = {}
			self._countGeneratorMap[action] = {}
			
			for e in stringElements:
				group = Group()
				
				if self._getN(e) != None:
					gen = PartialFlipper(None, e.getValue(),self._getN(e))
				else:
					gen = PartialFlipper(None, e.getValue())
					
				gen = WithDefault(group, _StaticAlwaysNone(), gen)
				self._masterGroup.append(group)
				self._generatorMap[action][e.getFullnameInDataModel()] = gen
				
				# Counter
				
				group = Group()
				
				if self._getN(e) != None:
					gen = PartialFlipper(None, e.getValue(),self._getN(e))
				else:
					gen = PartialFlipper(None, e.getValue())
					
				gen = WithDefault(group, _StaticAlwaysNone(), gen)
				self._countGroup.append(group)
				self._countGeneratorMap[action][e.getFullnameInDataModel()] = gen
			
			self._actions.append(action)
		
		# Set values
		for key in self._generatorMap[action].keys():
			value = self._generatorMap[action][key].getValue()
			if value != None:
				self._getElementByName(action.template, key).setValue(value)
		
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


# end
