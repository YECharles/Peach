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
from Peach.Engine.engine import Engine
from Peach.mutatestrategies import *

class _RandomMutator(object):
	name = "chosen randomly"
	
class RandomMutationStrategy(MutationStrategy):
	'''
	This mutation strategy will randomly select N fields
	from a data model to fuzz on each test case.
	
	Note: This strategy does not affect the state model
	Note: First test case will not be modified
	'''
	
	def __init__(self, args):
		MutationStrategy.__init__(self, args)
		
		#: Will this mutation strategy ever end?
		self.isFinite = False
		
		#: Number of fields to change
		self._n = 5
		
		#: Data models (fullname as key, value is node count)
		self._dataModels = {}
		
		#: Mutators for each field
		self._fieldMutators = {}
		
		#: Is initial test case?
		self._isFirstTestCase = True
		
		#: Data model selected for change
		self._dataModelToChange = None
		
		#: Random number generator for our instance
		self._random = random.Random()
	
		self._mutator = _RandomMutator()
		
	def next(self):
		pass
	
	def getCount(self):
		'''
		Return the number of test cases
		'''
		return None
	
	def _getNodeCount(self, node):
		'''
		Return the number of DataElements that are children of node
		'''
		return len(node.getAllChildDataElements())
	
	def currentMutator(self):
		'''
		Return the current Mutator in use
		'''
		return self._mutator
	
	## Events
	
	def onTestCaseStarting(self, test, count, stateEngine):
		'''
		Called as we start a test case
		
		@type	test: Test instance
		@param	test: Current test being run
		@type	count: int
		@param	count: Current test #
		@type	stateEngine: StateEngine instance
		@param	stateEngine: StateEngine instance in use
		'''
		
		if not self._isFirstTestCase:
			## Select the data model to change
			self._dataModelToChange = self._random.choice(self._dataModels.keys())
	
	
	def onTestCaseFinished(self, test, count, stateEngine):
		'''
		Called as we exit a test case
		
		@type	test: Test instance
		@param	test: Current test being run
		@type	count: int
		@param	count: Current test #
		@type	stateEngine: StateEngine instance
		@param	stateEngine: StateEngine instance in use
		'''
		
		self._isFirstTestCase = False
		self._dataModelToChange = None
		
	
	
	def onDataModelGetValue(self, action, dataModel):
		'''
		Called before getting a value from a data model
		
		@type	action: Action
		@param	action: Action we are starting
		@type	dataModel: Template
		@param	dataModel: Data model we are using
		'''
		
		if self._isFirstTestCase:
			fullName = dataModel.getFullname()
			
			if fullName not in self._dataModels:
				self._dataModels[fullName] = self._getNodeCount(dataModel)
				
				nodes = dataModel.getAllChildDataElements()
				nodes.append(dataModel)
				
				for node in nodes:
					mutators = []
					self._fieldMutators[node.getFullname()] = mutators
					
					for m in Engine.context.mutators:
						if m.supportedDataElement(node):
							# Need to create new instance from class
							for i in range(m.weight):
								mutators.append( m(Engine.context,node) )
			
			return
		
		else:
			## Is this data model we are changing?
			if dataModel.getFullname() != self._dataModelToChange:
				return
			
			## Select fields to modify
			nodes = dataModel.getAllChildDataElements()
			nodes.append(dataModel)
			
			# Remove non-mutable fields
			for node in nodes:
				if not node.isMutable:
					nodes.remove(node)
			
			# Select nodes we will modify
			if len(nodes) <= self._n:
				fields = nodes
			else:
				fields = self._random.sample(nodes, self._n)
			
			# Now perform mutations on fields
			for node in fields:
				try:
					mutator = self._random.choice(self._fieldMutators[node.getFullname()])
					
					# Note: Since we are applying multiple mutations
					#       sometimes a mutation will fail.  We should
					#       ignore those failures.
					try:
						mutator.randomMutation(node)
					except:
						pass
				
				except:
					pass
			
		# all done!

#MutationStrategy.DefaultStrategy = RandomMutationStrategy
# end
