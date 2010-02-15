'''
Mutation Strategies

@author: Michael Eddington
@version: $Id$
'''

#
# Copyright (c) Michael Eddington
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
	name = "Random"
	changedName = "N/A"
	
class RandomMutationStrategy(MutationStrategy):
	'''
	This mutation strategy will randomly select N fields
	from a data model to fuzz on each test case.
	
	Note: This strategy does not affect the state model
	Note: First test case will not be modified
	'''
	
	def __init__(self, args):
		MutationStrategy.__init__(self, args)
		
		#: Number of iterations befor we switch files
		self.switchCount = 100
		
		#: Number of iterations
		self.iterationCount = 0
		
		#: Are we using multiple data sets?
		self.multipleFiles = False
		
		#: Will this mutation strategy ever end?
		self.isFinite = False
		
		#: Number of fields to change
		self._n = 7
		
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
		
		self.iterationCount += 1
		
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
		
	
	def GetRef(self, str, parent = None, childAttr = 'templates'):
		'''
		Get the object indicated by ref.  Currently the object must have
		been defined prior to this point in the XML
		'''
		
		#print "GetRef(%s) -- Starting" % str
		
		origStr = str
		baseObj = self.context
		hasNamespace = False
		isTopName = True
		found = False
		
		# Parse out a namespace
		
		if str.find(":") > -1:
			ns, tmp = str.split(':')
			str = tmp
			
			#print "GetRef(%s): Found namepsace: %s" % (str, ns)
			
			# Check for namespace
			if hasattr(self.context.namespaces, ns):
				baseObj = getattr(self.context.namespaces, ns)
			else:
				#print self
				raise PeachException("Unable to locate namespace: " + origStr)
			
			hasNamespace = True
		
		for name in str.split('.'):
			
			#print "GetRef(%s): Looking for part %s" % (str, name)
			
			found = False
			
			if not hasNamespace and isTopName and parent != None:
				# check parent, walk up from current parent to top
				# level parent checking at each level.
				
				while parent != None and not found:
					
					#print "GetRef(%s): Parent.name: %s" % (name, parent.name)
					
					if hasattr(parent, 'name') and parent.name == name:
						baseObj = parent
						found = True
						
					elif hasattr(parent, name):
						baseObj = getattr(parent, name)
						found = True
					
					elif hasattr(parent.children, name):
						baseObj = getattr(parent.children, name)
						found = True
					
					elif hasattr(parent, childAttr) and hasattr( getattr(parent, childAttr), name):
						baseObj = getattr( getattr(parent, childAttr), name)
						found = True
						
					else:
						parent = parent.parent
			
			# check base obj
			elif hasattr(baseObj, name):
				baseObj = getattr(baseObj, name)
				found = True
				
			# check childAttr
			elif hasattr(baseObj, childAttr):
				obj = getattr(baseObj, childAttr)
				if hasattr(obj, name):
					baseObj = getattr(obj, name)
					found = True
			
			else:
				raise PeachException("Could not resolve ref %s" % origStr)
			
			# check childAttr
			if found == False and hasattr(baseObj, childAttr):
				obj = getattr(baseObj, childAttr)
				if hasattr(obj, name):
					baseObj = getattr(obj, name)
					found = True
			
			# check across namespaces if we can't find it in ours
			if isTopName and found == False:
				for child in baseObj:
					if child.elementType != 'namespace':
						continue
					
					#print "GetRef(%s): CHecking namepsace: %s" % (str, child.name)
					ret = self._SearchNamespaces(child, name, childAttr)
					if ret:
						#print "GetRef(%s) Found part %s in namespace" % (str, name)
						baseObj = ret
						found = True
			
			isTopName = False
		
		if found == False:
			raise PeachException("Unable to resolve reference: %s" % origStr)
		
		return baseObj
	
	def _SearchNamespaces(self, obj, name, attr):
		'''
		Used by GetRef to search across namespaces
		'''
		
		#print "_SearchNamespaces(%s, %s)" % (obj.name, name)
		#print "dir(obj): ", dir(obj)
		
		# Namespaces are stuffed under this variable
		# if we have it we should be it :)
		if hasattr(obj, 'ns'):
			obj = obj.ns

		if hasattr(obj, name):
			return getattr(obj, name)
		
		elif hasattr(obj, attr) and hasattr(getattr(obj, attr), name):
			return getattr(getattr(obj, attr), name)
		
		for child in obj:
			if child.elementType != 'namespace':
				continue
			
			ret = self._SearchNamespaces(child, name, attr)
			if ret != None:
				return ret
		
		return None
	
	def onDataModelGetValue(self, action, dataModel):
		'''
		Called before getting a value from a data model
		
		@type	action: Action
		@param	action: Action we are starting
		@type	dataModel: Template
		@param	dataModel: Data model we are using
		'''
		
		if action.data != None and action.data.multipleFiles:
			self.switchCount = action.data.switchCount
		
		if action.data != None and action.data.multipleFiles and \
					self.iterationCount % self.switchCount == 0:
			
			self.context = action.getRoot()
			
			# Time to switch to another file!
			action.data.gotoRandomFile()
			
			# Locate fresh copy of template with no data
			obj = self.GetRef(action.template.ref)
			template = obj.copy(action)
			template.ref = action.template.ref
			template.parent = action
			template.name = action.template.name
			
			# Switch any references to old name
			oldName = template.ref
			for relation in template._genRelationsInDataModelFromHere():
				if relation.of == oldName:
					relation.of = template.name
				
				elif relation.From == oldName:
					relation.From = template.name
			
			# Crack file
			template.setDefaults(action.data)
			
			# Cache default values
			action.template = template
			template.getValue()
			template.getValue()
			
			# Remove state engine copy
			if hasattr(action, "origionalTemplate"):
				delattr(action, "origionalTemplate")
			
			# Regenerate mutator state
			self._isFirstTestCase = True
			self._dataModels = {}
			self._fieldMutators = {}
		
		
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
							for i in range(m.weight**4):
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
				
				for i in range(self._n):
					# Now perform mutations on fields
					for node in fields:
						try:
							mutator = self._random.choice(self._fieldMutators[node.getFullname()])
							
							print "> %s: %s" % (node.getFullnameInDataModel(), mutator.name)
							
							# Note: Since we are applying multiple mutations
							#       sometimes a mutation will fail.  We should
							#       ignore those failures.
							try:
								mutator.randomMutation(node)
							except:
								pass
						
						except:
							pass
			else:
				fields = self._random.sample(nodes, self._n)
				
				# Now perform mutations on fields
				for node in fields:
					try:
						mutator = self._random.choice(self._fieldMutators[node.getFullname()])
						
						print "> %s: %s" % (node.getFullnameInDataModel(), mutator.name)
						
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

class SingleRandomMutationStrategy(RandomMutationStrategy):
	'''
	This mutation strategy will randomly select N fields
	from a data model to fuzz on each test case.
	
	Note: This strategy does not affect the state model
	Note: First test case will not be modified
	'''
	
	def __init__(self, args):
		RandomMutationStrategy.__init__(self, args)
		
		#: Number of fields to change
		self._n = 1


class DoubleRandomMutationStrategy(RandomMutationStrategy):
	'''
	This mutation strategy will randomly select N fields
	from a data model to fuzz on each test case.
	
	Note: This strategy does not affect the state model
	Note: First test case will not be modified
	'''
	
	def __init__(self, args):
		RandomMutationStrategy.__init__(self, args)
		
		#: Number of fields to change
		self._n = 2
		


# end
