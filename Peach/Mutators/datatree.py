
'''
Mutators that modify the data tree structure.

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
from Peach.Generators.static import Static, _StaticFromTemplate, _StaticCurrentValueFromDom
from Peach.Transformers.encode import WideChar
from Peach import Transformers
from Peach.mutator import *
from Peach.group import *
from Peach.Engine.common import *

class DataTreeRemoveMutator(Mutator):
	'''
	Remove nodes from data tree.
	'''
	
	def __init__(self, peach):
		Mutator.__init__(self)
		
		self.name = "DataTreeRemoveMutator"
		self._peach = peach
		self._countThread = None
		
		self._actionPos = 0
		self._actions = []
		# Key is template object, value is current node position
		self._templatePosition = {}
		
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
		self._templatePosition = {}
	
	def _moveNext(self, currentNode):
		
		# Check if we are top dog
		if currentNode.parent == None or not isinstance(currentNode.parent, DataElement):
			return None
		
		# Get sibling
		foundCurrent = False
		for node in currentNode.parent:
			if node == currentNode:
				foundCurrent = True
				continue
			
			if foundCurrent and isinstance(node, DataElement):
				return node
		
		# Get sibling of parent
		return self._moveNext(currentNode.parent)

	def _nextNode(self, action):
		nextNode = None
		
		# Get current node
		node = action.template.findDataElementByName(self._templatePosition[action])
		
		# Walk down node tree
		for child in node._children:
			if isinstance(child, DataElement):
				nextNode = child
				break
		
		# Walk over or up if we can
		if nextNode == None:
			nextNode = self._moveNext(node)
		
		if nextNode != None:
			return nextNode.getFullnameInDataModel()
		
		return None
	
	def next(self):
		'''
		Goto next mutation.  When this is called
		the state machine is updated as needed.
		'''
		
		action = self._actions[self._actionPos]
		
		if self._templatePosition[action] != None:
			self._templatePosition[action] = self._nextNode(action)
		
		if self._templatePosition[action] == None:
			self._actionPos += 1
			
			if self._actionPos >= len(self._actions):
				self._actionPos -= 1
				raise MutatorCompleted()
		
		self._masterCount += 1
	
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
		
		self._stateMasterCount = int(state)
		
		try:
			for i in xrange(self._masterCount, self._stateMasterCount):
				self.next()
			
			self._stateMasterCount = -1
		except:
			pass
	
	def _countDataNodes(self, node):
		
		cnt = 0
		
		for n in node._children:
			if n.elementType not in self.dataTypes:
				continue;
			cnt += 1
			cnt += self._countDataNodes(n)
		
		return cnt
	
	def getCount(self):
		if self._countThread != None and self._countThread.hasCountEvent.isSet():
			self._count = self._countThread.count
			self._countThread = None
			self._countGroup = None
			self._countGeneratorMap = None
		
		return self._count

	def calculateCount(self):
		# We just need to figure out how may data
		# nodes are in the tree.
		cnt = 0
		for a in self._templatePosition.keys():
			cnt += 1 # for the template
			cnt += self._countDataNodes(a.template)
		
		return cnt

	#####################################################
	# Callbacks when Action needs a value
	
	def getActionValue(self, action):
		
		# Check if we know this template yet
		if action not in self._templatePosition.keys():
			self._actions.append(action)
			self._templatePosition[action] = action.template.getFullnameInDataModel()
		
		# remove node
		if self._actions[self._actionPos] == action:
			if self._templatePosition[action] != None:
				n = action.template.findDataElementByName(self._templatePosition[action])
				n.setValue("")
		
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

class DataTreeDuplicateMutator(Mutator):
	'''
	Duplicate nodes in data model.  Currently we do a static
	x2 duplication.
	
	TODO: Change this todo x2 -> x10
	'''
	
	def __init__(self, peach):
		Mutator.__init__(self)
		
		self.name = "DataTreeDuplicateMutator"
		self._peach = peach
		self._countThread = None
		
		self._actionPos = 0
		self._actions = []
		# Key is action object, value is current node name
		self._templatePosition = {}
		self._cnt = 2
		self._maxCount = 50
		
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
		self._templatePosition = {}
	
	def _moveNext(self, currentNode):
		
		# Check if we are top dog
		if currentNode.parent == None or not isinstance(currentNode.parent, DataElement):
			return None
		
		# Get sibling
		foundCurrent = False
		for node in currentNode.parent:
			if node == currentNode:
				foundCurrent = True
				continue
			
			if foundCurrent and isinstance(node, DataElement):
				return node
		
		# Get sibling of parent
		return self._moveNext(currentNode.parent)

	def _nextNode(self, action):
		nextNode = None
		
		# Get current node
		node = action.template.findDataElementByName(self._templatePosition[action])
		
		# Walk down node tree
		for child in node._children:
			if isinstance(child, DataElement):
				nextNode = child
				break
		
		# Walk over or up if we can
		if nextNode == None:
			nextNode = self._moveNext(node)
		
		if nextNode != None:
			return nextNode.getFullnameInDataModel()
		
		return None
	
	def next(self):
		'''
		Goto next mutation.  When this is called
		the state machine is updated as needed.
		'''
		
		self._masterCount += 1
		
		self._cnt+=1
		if self._cnt < self._maxCount:
			return
		
		self._cnt = 0
		action = self._actions[self._actionPos]
		self._templatePosition[action] = self._nextNode(action)
		
		if self._templatePosition[action] == None:
			self._actionPos += 1
			
			if self._actionPos >= len(self._actions):
				self._actionPos -= 1
				self._masterCount -= 1
				raise MutatorCompleted()
	
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
		
		self._stateMasterCount = int(state)
		try:
			for i in xrange(self._masterCount, self._stateMasterCont):
				self.next()
			
			self._stateMasterCount = -1
		except:
			pass
		
	def _countDataNodes(self, node):
		
		cnt = 2
		
		for n in node._children:
			if n.elementType not in self.dataTypes:
				continue;
			cnt += 1
			cnt += self._countDataNodes(n)
		
		return cnt
	
	def getCount(self):
		if self._countThread != None and self._countThread.hasCountEvent.isSet():
			self._count = self._countThread.count
			self._countThread = None
			self._countGroup = None
			self._countGeneratorMap = None
		
		return self._count

	def calculateCount(self):
		# We just need to figure out how may data
		# nodes are in the tree.
		cnt = 0
		for a in self._templatePosition.keys():
			cnt += 1 # for the template
			cnt += self._countDataNodes(a.template)
		
		return cnt * self._maxCount

	#####################################################
	# Callbacks when Action needs a value
	
	def getActionValue(self, action):
		
		# Check if we know this template yet
		if action not in self._templatePosition.keys():
			self._actions.append(action)
			n = action.template
			self._templatePosition[action] = n.getFullnameInDataModel()
		
		# duplicate node
		if self._actions[self._actionPos] == action:
			if self._templatePosition[action] != None:
				n = self._getElementByName(action.template, self._templatePosition[action] )
				n.setValue(n.getValue() * self._cnt)
		
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


class DataTreeSwapNearNodesMutator(Mutator):
	'''
	Swap two nodes in the data model that
	are near each other.
	
	TODO: Actually move the nodes instead of
	      just the data.
	'''
	
	def __init__(self, peach):
		Mutator.__init__(self)
		
		self.name = "DataTreeSwapNearNodesMutator"
		self._peach = peach
		self._countThread = None
		
		self._actionPos = 0
		self._actions = []
		# Key is template object, value is current node position
		self._templatePosition = {}
		
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
		self._templatePosition = {}
	
	def _moveNext(self, currentNode):
		
		# Check if we are top dog
		if currentNode.parent == None or not isinstance(currentNode.parent, DataElement):
			return None
		
		# Get sibling
		foundCurrent = False
		for node in currentNode.parent:
			if node == currentNode:
				foundCurrent = True
				continue
			
			if foundCurrent and isinstance(node, DataElement):
				return node
		
		# Get sibling of parent
		return self._moveNext(currentNode.parent)

	def _nextNode(self, action):
		nextNode = None
		
		# Get current node
		node = action.template.findDataElementByName(self._templatePosition[action])
		
		# Walk down node tree
		for child in node._children:
			if isinstance(child, DataElement):
				nextNode = child
				break
		
		# Walk over or up if we can
		if nextNode == None:
			nextNode = self._moveNext(node)
		
		if nextNode != None:
			return nextNode.getFullnameInDataModel()
		
		return None
	
	def next(self):
		'''
		Goto next mutation.  When this is called
		the state machine is updated as needed.
		'''
		
		action = self._actions[self._actionPos]
		
		if self._templatePosition[action] != None:
			self._templatePosition[action] = self._nextNode(action)
		
		if self._templatePosition[action] == None:
			self._actionPos += 1
			
			if self._actionPos >= len(self._actions):
				self._actionPos -= 1
				raise MutatorCompleted()
		
		self._masterCount += 1
	
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
		self._stateMasterCount = int(state)
		try:
			for i in xrange(self._masterCount, self._stateMasterCont):
				self.next()
			
			self._stateMasterCount = -1
		except:
			pass
	
	def _countDataNodes(self, node):
		
		cnt = 0
		
		for n in node._children:
			if n.elementType not in self.dataTypes:
				continue;
			cnt += 1
			cnt += self._countDataNodes(n)
		
		return cnt
	
	def getCount(self):
		if self._countThread != None and self._countThread.hasCountEvent.isSet():
			self._count = self._countThread.count
			self._countThread = None
			self._countGroup = None
			self._countGeneratorMap = None
		
		return self._count

	def calculateCount(self):
		# We just need to figure out how may data
		# nodes are in the tree.
		cnt = 0
		for a in self._templatePosition.keys():
			cnt += 1 # for the template
			cnt += self._countDataNodes(a.template)
		
		return cnt
	
	#####################################################
	# Callbacks when Action needs a value
	
	def getActionValue(self, action):
		
		# Check if we know this template yet
		if action not in self._templatePosition.keys():
			self._actions.append(action)
			n = action.template
			self._templatePosition[action] = n.getFullnameInDataModel()
		
		# swap node
		if self._actions[self._actionPos] == action:
			if self._templatePosition[action] != None:
				nextNode = self._nextNode(action)
				if nextNode != None:
					node = self._getElementByName(action.template, self._templatePosition[action] )
					nextNode = self._getElementByName(action.template, nextNode )
					
					v1 = node.getValue()
					v2 = nextNode.getValue()
					node.setValue(v2)
					nextNode.setValue(v1)
		
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

# end
