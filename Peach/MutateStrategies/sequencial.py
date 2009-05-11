'''
Mutation Strategies

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
from Peach.mutatestrategies import *
from Peach.mutator import *

class _Unknown(object):
	name = "N/A"

class SequencialMutationStrategy(MutationStrategy):
	'''
	Perform a sequencial mutation strategy.
	
	Note: This strategy does not affect the state model
	Note: First test case will not be modified
	'''
	
	def __init__(self, args):
		MutationStrategy.__init__(self, args)
		
		#: Is this a finite strategy?
		self.isFinite = True
		
		#: Number of fields to change
		self._count = None
		
		#: Data models (by fullname)
		self._dataModels = []
		
		#: Data fields (key is data model fullname, value is array of data names)
		self._dataModelFields = {}
		
		#: Key is field fullname, value is array of mutators, position 0 is current
		self._fieldMutators = {}
		
		#: Is initial test case?
		self._isFirstTestCase = True
		
		#: Data model selected for change
		self._dataModelIndex = 0
		
		#: Current data model field
		self._fieldIndex = 0
		
		#: Current mutator for field
		self._mutatorIndex = 0
	
	def getCount(self):
		'''
		Return the number of test cases
		'''
		
		if self._isFirstTestCase:
			return None
		
		if self._count == None:
			cnt = 0
			for mutators in self._fieldMutators.values():
				for m in mutators:
					c = m.getCount()
					if c == None:
						raise Exception("Count was null from %s" % repr(m))
					
					cnt += c
			
			self._count = cnt
			return self._count
		
		return self._count

	def next(self):
		# Goto next test case
		
		dataModelName = self._dataModels[self._dataModelIndex]
		
		while self._fieldIndex >= len(self._dataModelFields[dataModelName]):
			self._fieldIndex = 0
			self._dataModelIndex += 1
				
			dataModelCount = len(self._dataModels)
			if self._dataModelIndex >= dataModelCount:
				raise MutatorCompleted()
			else:
				dataModelName = self._dataModels[self._dataModelIndex]
		
		fieldName = self._dataModelFields[dataModelName][self._fieldIndex]
		
		# If this is the first test case, don't next the mutator
		
		if self._isFirstTestCase:
			self._isFirstTestCase = False
		
		else:
			try:
				mutator = self._fieldMutators[fieldName][self._mutatorIndex]
				mutator.next()
				return
			
			except MutatorCompleted:
				pass
			
			self._mutatorIndex += 1
		
		# Fall through to here and move to next available field/mutator
		
		while self._mutatorIndex >= len(self._fieldMutators[fieldName]):
			self._mutatorIndex = 0
			self._fieldIndex += 1
			
			fieldCount = len(self._dataModelFields[dataModelName])
			if self._fieldIndex >= fieldCount:
				self._fieldIndex = 0
				self._dataModelIndex += 1
				
				dataModelCount = len(self._dataModels)
				if self._dataModelIndex >= dataModelCount:
					raise MutatorCompleted()
				else:
					dataModelName = self._dataModels[self._dataModelIndex]
			else:
				fieldName = self._dataModelFields[dataModelName][self._fieldIndex]
	
	def currentMutator(self):
		'''
		Return the current Mutator in use
		'''
		if self._isFirstTestCase:
			return _Unknown()
		
		dataModelName = self._dataModels[self._dataModelIndex]
		fieldName = self._dataModelFields[dataModelName][self._fieldIndex]
		return self._fieldMutators[fieldName][self._mutatorIndex]
	
	## Events
	
	def onDataModelGetValue(self, action, dataModel):
		'''
		Called before getting a value from a data model
		
		@type	action: Action
		@param	action: Action we are starting
		@type	dataModel: Template
		@param	dataModel: Data model we are using
		'''
		
		# On first test case lets just figure out which
		# data models and fields we will be mutating
		if self._isFirstTestCase:
			fullName = dataModel.getFullname()
			if fullName not in self._dataModels:
				self._dataModels.append(fullName)
				self._dataModelFields[fullName] = []
				
				nodes = dataModel.getAllChildDataElements()
				nodes.append(dataModel)
				
				for node in nodes:
					if node.isMutable:
						self._dataModelFields[fullName].append(node.getFullname())
						mutators = self._fieldMutators[node.getFullname()] = []
						
						# We should also populate the mutators here
						for m in Engine.context.mutators:
							if m.supportedDataElement(node):
								# Need to create new instance from class
								mutators.append( m(Engine.context,node) )
			
			return
		
		# Is this data model we are changing?
		if dataModel.getFullname() != self._dataModels[self._dataModelIndex]:
			return
		
		dataModelName = self._dataModels[self._dataModelIndex]
		fieldName = self._dataModelFields[dataModelName][self._fieldIndex]
		mutator = self._fieldMutators[fieldName][self._mutatorIndex]
		
		node = dataModel.getRoot().getByName(fieldName)
		mutator.sequencialMutation(node)
		
		# all done!


# Set default strategy!
MutationStrategy.DefaultStrategy = SequencialMutationStrategy

# end
