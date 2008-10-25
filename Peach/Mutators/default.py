
'''
Mutator base classes and interfaces.

A Mutator implements a method of mutating data/state for a Peach 2
fuzzer.  For example a mutator might change the state flow defined
by a Peach fuzzer.  Another mutator might mutate data based on
known relationships.  Another mutator might perform numerical type
tests against fields.

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
#from parser import *
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


class NullMutator(Mutator):
	'''
	Does not make any changes to data tree.  This is
	usually the first mutator applied to a fuzzing run
	so the generated data can be verified.
	'''
	
	def __init__(self, peach):
		Mutator.__init__(self)
		self.name = "NullMutator"
		
	def isFinite(self):
		'''
		Some mutators could contine forever, this
		should indicate.
		'''
		return True
	
	def next(self):
		'''
		Goto next mutation.  When this is called
		the state machine is updated as needed.
		'''
		
		raise MutatorCompleted()
	
	def getState(self):
		'''
		Return a binary string that contains
		any information about current state of
		Mutator.  This state information should be
		enough to let the same mutator "restart"
		and continue when setState() is called.
		'''
		
		return ''
	
	def setState(self, state):
		'''
		Set the state of this object.  Should put us
		back in the same place as when we said
		"getState()".
		'''
		pass
		
	def getCount(self):
		return 1

	#####################################################
	# Callbacks when Action needs a value
	
	def getActionValue(self, action):
		stringBuffer = StreamBuffer()
		action.template.getValue(stringBuffer)
		stringBuffer.setValue("")
		stringBuffer.seekFromStart(0)
		action.template.getValue(stringBuffer)
		return stringBuffer.getValue()
	
	def getActionParamValue(self, action):
		stringBuffer = StreamBuffer()
		action.template.getValue(stringBuffer)
		stringBuffer.setValue("")
		stringBuffer.seekFromStart(0)
		action.template.getValue(stringBuffer)
		return stringBuffer.getValue()
	
	def getActionChangeStateValue(self, action, value):
		return value
	
	


###class GeneratorMutator(Mutator):
###	'''
###	This is the default Peach 2 mutator.  This
###	mutator uses the Peach 1 Generators to build
###	a standard complexity fuzzer that performs
###	type based fuzzing and basic relation based
###	fuzzing for size and count relations.
###	
###	This mutator is *not* state aware.
###	'''
###	
###	def __init__(self, peach):
###		Mutator.__init__(self)
###		
###		self.name = "GeneratorMutator"
###		self._peach = peach
###		
###		self._stateMasterCount = -1
###		self._masterGroup = GroupSequence()
###		self._masterCount = 0
###		self._countThread = None
###		self._countGroup = GroupSequence()
###		
###		# All active groups
###		self._activeGroups = []
###		
###		# Hashtable, key is template, value is [group, generator]
###		self._generatorMap = {}
###		self._countGeneratorMap = {}
###	
###	def isFinite(self):
###		'''
###		Some mutators could contine forever, this
###		should indicate.
###		'''
###		return True
###	
###	def reset(self):
###		'''
###		Reset mutator
###		'''
###		
###		self._masterGroup = GroupSequence()
###		self._activeGroups = []
###		self._generatorMap = {}
###		self._masterCount = 0
###	
###	def next(self):
###		'''
###		Goto next mutation.  When this is called
###		the state machine is updated as needed.
###		'''
###		
###		try:
###			# Check if we set our state and need
###			# to skip ahead.  We need todo this in
###			# next() to assure we have all our action
###			# templates added into our masterGroup
###			if self._stateMasterCount > -1:
###				for cnt in xrange(self._stateMasterCount):
###					self._masterGroup.next()
###					self._masterCount += 1
###				self._stateMasterCount = -1
###			else:
###				self._masterGroup.next()
###				self._masterCount += 1
###		
###		except GroupCompleted:
###			raise MutatorCompleted()
###	
###	def getState(self):
###		'''
###		Return a binary string that contains
###		any information about current state of
###		Mutator.  This state information should be
###		enough to let the same mutator "restart"
###		and continue when setState() is called.
###		'''
###		
###		# Ensure a minor overlap of testing
###		return str(self._masterCount - 2)
###	
###	def setState(self, state):
###		'''
###		Set the state of this object.  Should put us
###		back in the same place as when we said
###		"getState()".
###		'''
###		self.reset()
###		self._stateMasterCount = int(state)
###		
###	def calculateCount(self):
###		
###		count = 0
###		try:
###			while True:
###				count += 1
###				self._countGroup.next()
###			
###		except GroupCompleted:
###			pass
###		
###		return count
###	
###	#####################################################
###	# Callbacks when Action needs a value
###	
###	def getActionValue(self, action):
###		
###		if not self._generatorMap.has_key(action.template):
###			build = _BuildPeach(self._peach)
###			(group, gen, template) = build.getDefaultPeach(action.template, action.data)
###			self._generatorMap[action.template] = gen
###			self._activeGroups.append(group)
###			self._masterGroup.append(group)
###			
###			# For counting
###			(groupCnt, genCnt, templateCnt) = build.getDefaultPeach(action.template, action.data)
###			self._countGeneratorMap[action.template] = genCnt
###			self._countGroup.append(groupCnt)
###		
###		return self._generatorMap[action.template].getValue()
###	
###	def getActionParamValue(self, param):
###		
###		if not self._generatorMap.has_key(param.template):
###			build = _BuildPeach(self._peach)
###			(group, gen, template) = build.getDefaultPeach(param.template, param.data)
###			self._generatorMap[param.template] = gen
###			self._activeGroups.append(group)
###			self._masterGroup.append(group)
###			
###			# For counting
###			(groupCnt, genCnt, templateCnt) = build.getDefaultPeach(param.template, param.data)
###			self._countGeneratorMap[oaram.template] = genCnt
###			self._countGroup.append(groupCnt)
###		
###		return self._generatorMap[param.template].getValue()
###	
###	def getActionChangeStateValue(self, action, value):
###		return value
###	
###	#####################################################
###	# Event callbacks for state machine
###	
###	def onStateStart(self, state):
###		pass
###	
###	def onStateComplete(self, state):
###		pass
###	
###	def onActionStart(self, action):
###		pass
###	
###	def onActionComplete(self, action):
###		pass
###	
###	def onStateMachineStart(self, stateMachine):
###		pass
###	
###	def onStateMachineComplete(self, stateMachine):
###		
###		# Lets calc our count if we haven't already
###		if self._count == -1 and self._countThread == None:
###			self._countThread = MutatorCountCalculator(self)
###			self._countThread.start()
###		
###		elif self._countThread != None:
###			if self._countThread.hasCountEvent.isSet():
###				self._count = self._countThread.count
###				self._countThread = None
###				self._countGroup = None
###				self._countGeneratorMap = None
###
###def PeachStr(s):
###	'''
###	Our implementation of str() which does not
###	convert None to 'None'.
###	'''
###	
###	if s == None:
###		return None
###	
###	return str(s)
###
###class _BuildPeach:
###	'''
###	Logic to build a tree of generators around a Template.  This used
###	to be the base fuzzer logic for Peach 2.0 release and was in
###	Engine\build.py.  No longer :)
###	'''
###	
###	def __init__(self, peachXml):
###		self.context = self.peachXml = peachXml
###		self._relationSizeofNeedResolving = []
###		self._relationCountofNeedResolving = []
###		self._performAllImports()
###	
###	def GetClassesInModule(self, module):
###		'''
###		Return array of class names in module
###		'''
###		
###		classes = []
###		for item in dir(module):
###			i = getattr(module, item)
###			if type(i) == types.ClassType and item[0] != '_':
###				classes.append(item)
###		
###		return classes
###	
###	def getDefaultPeachByName(self, templateName, dataName = None):
###		group = GroupSequence()
###		template = self._GetTemplateByName(templateName)
###		template = template.copy(None)
###		
###		return self.getDefaultPeach(template, dataName)
###		
###	def getDefaultPeach(self, template, dataName = None):
###		'''
###		Return a master generator and group
###		'''
###		
###		group = GroupSequence()
###		
###		#DomPrint(0, template)
###		
###		if dataName != None:
###			data = self._GetDataByName(dataName)
###			template.setDefaults(data)
###		
###		self._ResetTemplate(template)
###		gen = self._getDefaultGenerator(template, group)
###		template.generator = gen
###		
###		# Resolve any sizeof relations waiting around
###		for relation in self._relationSizeofNeedResolving:
###			
###			if relation == None:
###				continue
###			
###			if relation.of_ref != None:
###				if relation.of_ref.generator == None:
###					raise Exception("Found a relation I'm unable to resolve")
###				
###				relation.blockSize.setBlock(relation.of_ref.generator)
###				
###			else:
###				if relation.from_ref.generator == None:
###					raise Exception("Found a relation I'm unable to resolve")
###				
###				relation.blockMulti.setSize(relation.from_ref.generator)
###			
###		# Resolve any countof relations waiting around
###		for relation in self._relationCountofNeedResolving:
###			#print "Resolving count of relation..."
###			if relation.of_ref != None:
###				if relation.of_ref.generator == None:
###					raise Exception("Found a relation I'm unable to resolve")
###				
###				relation.blockCount.setBlock(relation.of_ref.generator)
###			else:
###				if relation.from_ref.generator == None:
###					raise Exception("Found a relation I'm unable to resolve")
###				
###				relation.blockMulti.setGenOccurs(relation.from_ref.generator)
###		
###		return (group, gen, template)
###	
###	def _HasSizeofRelation(self, node):
###		for relation in node.relations:
###			if relation.type == 'size':
###				return True
###		
###		return False
###	def _GetSizeofRelation(self, node):
###		for relation in node.relations:
###			if relation.type == 'size':
###				return relation
###		
###		return None
###	
###	def _HasCountofRelation(self, node):
###		for relation in node.relations:
###			if relation.type == 'count':
###				return True
###		
###		return False
###	def _GetCountofRelation(self, node):
###		for relation in node.relations:
###			if relation.type == 'count':
###				return relation
###		
###		return None
###	
###	def _ResetTemplate(self, node):
###		'''
###		Set the .generator values in template tree to None
###		'''
###		
###		if node.elementType != 'generator':
###			node.generator = None
###		
###		try:
###			for child in node:
###				self._ResetTemplate(child)
###		except:
###			# we arn't always a sequence :)
###			pass
###		
###	def _performAllImports(self):
###		'''
###		Find all Import objects and insert them into the current
###		namespace.
###		'''
###		
###		for obj in self.context:
###			if hasattr(obj, 'elementType') and obj.elementType == 'import':
###				self._performImport(obj)
###	
###	def _performImport(self, importObj):
###		'''
###		Import the specified import object into the current namespace.
###		'''
###		
###		importStr = importObj.importStr
###		
###		if importObj.fromStr != None:
###			fromStr = importObj.fromStr
###			
###			if importStr == "*":
###				module = __import__(PeachStr(fromStr), globals(), locals(), [ PeachStr(importStr) ], -1)
###				
###				try:
###					# If we are a module with other modules in us then we have an __all__
###					for item in module.__all__:
###						globals()["PeachXml_"+item] = getattr(module, item)
###					
###				except:
###					# Else we just have some classes in us with no __all__
###					for item in self.GetClassesInModule(module):
###						globals()["PeachXml_"+item] = getattr(module, item)
###				
###			else:
###				module = __import__(PeachStr(fromStr), globals(), locals(), [ PeachStr(importStr) ], -1)
###				for item in importStr.split(','):
###					item = item.strip()
###					globals()["PeachXml_"+item] = getattr(module, item)
###		
###		else:
###			globals()["PeachXml_"+importStr] = __import__(PeachStr(importStr), globals(), locals(), [], -1)
###	
###	def _GetTemplateByName(self, str):
###		'''
###		Get the object indicated by ref.  Currently the object must have
###		been defined prior to this point in the XML
###		'''
###		
###		origStr = str
###		baseObj = self.peachXml
###		
###		# Parse out a namespace
###		
###		if str.find(":") > -1:
###			ns, tmp = str.split(':')
###			str = tmp
###			
###			print "GetRef(): Found namepsace:",ns
###			
###			# Check for namespace
###			if hasattr(self.context.namespaces, ns):
###				baseObj = getattr(self.context.namespaces, ns)
###			else:
###				raise Exception("Unable to locate namespace")
###		
###		for name in str.split('.'):
###			
###			# check base obj
###			if hasattr(baseObj, name):
###				baseObj = getattr(baseObj, name)
###				
###			# check templates
###			elif hasattr(baseObj, 'templates') and hasattr(baseObj.templates, name):
###				baseObj = getattr(baseObj.templates, name)
###			
###			else:
###				print "name: " + str
###				print baseObj
###				raise Exception("Could not resolve ref", origStr)
###		
###		return baseObj
###	
###	
###	def _GetDataByName(self, str):
###		'''
###		Get the data object indicated by ref.  Currently the object must
###		have been defined prior to this point in the XML.
###		'''
###		
###		if hasattr(str, "elementType") and str.elementType == "data":
###			return str
###		
###		origStr = str
###		baseObj = self.peachXml
###		
###		# Parse out a namespace
###		
###		if str.find(":") > -1:
###			ns, tmp = str.split(':')
###			str = tmp
###			
###			print "_GetDataByName(): Found namepsace:",ns
###			
###			# Check for namespace
###			if hasattr(self.context.namespaces, ns):
###				baseObj = getattr(self.context.namespaces, ns)
###			else:
###				raise Exception("_GetDataByName(): Unable to locate namespace")
###		
###		# check base obj
###		if hasattr(baseObj, str):
###			return getattr(baseObj, str)
###		
###		# check templates
###		elif hasattr(baseObj, 'data') and hasattr(baseObj.data, str):
###			return getattr(baseObj.data, str)
###		
###		raise Exception("_GetDataByName(): Could not resolve ref", origStr)
###	
###	def _lookUp(self, name, start):
###		'''
###		Search up an object tree looking for an element name.
###		'''
###		
###		#if start.name == name:
###		#	print "_lookup: [%s] == [%s]" % (name, start.name)
###		#	return start
###		#
###		#else:
###		#	print "_lookup: [%s] != [%s]" % (name, start.name)
###		
###		obj = None
###		obj = self._lookSiblings(name, start)
###		if obj == None and start.parent != None:
###			return self._lookUp(name, start.parent)
###		
###		return obj
###	
###	def _lookDown(self, name, start):
###		
###		if start.name == name:
###			return start
###		
###		for child in start:
###			
###			ret = self._lookDown(name, child)
###			if ret != None:
###				return ret
###		
###		return None
###	
###	def _lookSiblings(self, name, start):
###		
###		for child in start:
###			if child.name == name:
###				return child
###			#else:
###			#	print "_lookSiblings: [%s] != [%s]" % (name, child.name)
###		
###		return None
###		
###	def _getRef(self, name, parent):
###		'''
###		Get a reference to an element in a tempalte
###		'''
###		
###		obj = None
###		isFirst = True
###		for name in name.split('.'):
###			
###			if isFirst:
###				isFirst = False
###				
###				obj = self._lookUp(name, parent)
###			
###			else:
###				obj = self._lookDown(name, obj)
###		
###		if obj == None:
###			raise Exception("_getRef: Unable to resolve reference", name)
###		
###		return obj
###	
###	def _createExtraGenerator(self, generator):
###		'''
###		Will create and return an instance of an extra
###		generated that was specified by the user.
###		'''
###		
###		code = "PeachXml_"+generator.classStr + '('
###		isFirst = True
###		
###		for param in generator:
###			#if param.elementName != 'param':
###			#	continue
###			
###			if param.valueType == 'ref':
###				# need to resolve reference!
###				obj = self._getRef(param.defaultValue, generator.parent)
###				if obj.generator == None:
###					raise Exception("_createExtraGenerator(): Unable to resolve generator reference.  Object has null generator attribute. [%s]" % str(param.defaultValue))
###				
###				PeachXml_Tmp_Generator = obj.generator
###				value = 'PeachXml_Tmp_Generator'
###			
###			else:
###				value = param.defaultValue
###			
###			if not isFirst:
###				code += ', '
###			else:
###				isFirst = False
###			
###			code += PeachStr(value)
###		
###		code += ')'
###		gen = eval(code, globals(), locals())
###		
###		return gen
###		
###	
###	def _getDefaultGenerator(self, node, group):
###		'''
###		Build up a generator construct for a peach dom node.
###		'''
###		
###		if node.elementType == 'transformer':
###			return Block()
###		
###		generator = None
###		innerGen = None
###		genList = GeneratorList(None, [])
###		
###		if len(node.extraGenerators) > 0:
###			for gen in node:
###				if gen.elementType == 'generator':
###					if gen.generator == None:
###						gen.generator = self._createExtraGenerator(gen)
###					
###					genList.getList().append(gen.generator)
###	
###		### STRING
###		if node.elementType == 'string':
###			
###			charSize = 1
###			if node.type == 'wchar':
###				charSize = 2
###
###			if node.isStatic == False:
###				if node.autoGen == False:
###					if node.defaultValue != None:
###						# genList must have contents else an array index exception is thrown
###						if len(genList.getList()) == 0:
###							innerGen = _StaticFromTemplate(node)
###						else:
###							innerGen = WithDefault(group.addNewGroup(), _StaticFromTemplate(node), genList)
###					else:
###						# if no value is provided and no extra generators exist then we have no values to fuzz with
###						if len(genList.getList()) == 0:
###							raise Exception("'autoGen' disabled, no 'value' provided or generators provide for node '" + node.name + "'")
###						else:
###							genList.setGroup(group.addNewGroup())
###							innerGen = genList
###				else:
###					if node.defaultValue != None:
###						genList.getList().append(StringTokenFuzzer(None, node.defaultValue, node.tokens))
###						innerGen = WithDefault(group.addNewGroup(), _StaticFromTemplate(node), genList)					
###					else:
###						genList.getList().append(BadStrings())
###						genList.setGroup(group.addNewGroup())
###						innerGen = genList
###
###
###			# ignore all extraGenerators (genList) for Static node
###			else: 			
###				if node.defaultValue != None:
###					innerGen = _StaticFromTemplate(node)
###				else:
###				# if the user specifies a static string w/o a default value we should raise an error
###				# because we have no idea what the static value should be.
###					raise Exception("No 'value' specified for Static element '" + node.name + "'")
###
###			# Handle sizeof relation
###			if self._HasSizeofRelation(node):
###				
###				relation = self._GetSizeofRelation(node)
###				blockSize = BlockSize(None)
###				
###				if node.isStatic == False:
###					genList.getList().append(NumberVariance(None, blockSize, 50))
###					genList.getList().append(BadStrings())
###					
###					innerGen = WithDefault(group.addNewGroup(),
###										   blockSize,
###										   genList)
###				else:
###					innerGen = blockSize
###				
###				#print "Of: ", relation.of
###				#print dir(relation)
###				#print relation.of_ref
###				
###				if relation.of_ref.generator != None:
###					blockSize.setBlock(relation.of_ref.generator)
###					
###				else:
###					relation.blockSize = blockSize
###					self._relationSizeofNeedResolving.append(relation)
###			
###			# Handle countof relation
###			if self._HasCountofRelation(node):
###				
###				relation = self._GetCountofRelation(node)
###				
###				if relation.of_ref != None:
###					
###					blockCount = MultiBlockCount(None)
###					
###					if node.isStatic == False:
###						genList.getList().append(NumberVariance(None, blockCount, 50))
###						genList.getList().append(BadStrings())
###						
###						innerGen = WithDefault(group.addNewGroup(),
###											   blockCount,
###											   genList)
###					else:
###						innerGen = blockCount
###					
###					if relation.of_ref.generator != None:
###						blockSize.setBlock(relation.of_ref.generator)
###						
###					else:
###						relation.blockCount = blockCount
###						self._relationCountofNeedResolving.append(relation)
###			
###			if innerGen == None:
###				genList.getList().append(BadStrings())
###				genList.setGroup(group.addNewGroup())
###				innerGen = genList
###			
###			# Handle fixed length string
###			if node.length != None:
###				generator = innerGen = FixedLengthString(None, innerGen, node.length, node.padCharacter, charSize)
###			
###			# Handle null terminated strings
###			if node.nullTerminated:
###				generator = innerGen = Block([
###					innerGen,
###					Static('\0')
###					])
###			
###			# Handle wide char strings
###			if charSize == 2:
###				generator = innerGen.setTransformer(WideChar())
###			
###			# Handle min/max Occurences
###			if node.minOccurs != 1 or node.maxOccurs != 1 or (self._HasCountofRelation(node) and relation.from_ref != None):
###				if self._HasCountofRelation(node) and relation.from_ref != None:
###					
###					if relation.from_ref.generator != None:
###						generator = MultiBlock(group.addNewGroup(), [innerGen], node.minOccurs, node.maxOccurs, relation.from_ref.generator)
###					else:
###						generator = MultiBlock(group.addNewGroup(), [innerGen], node.minOccurs, node.maxOccurs)
###						relation.blockMulti = generator
###						self._relationCountofNeedResolving.append(relation)
###				else:
###					generator = MultiBlock(group.addNewGroup(), [innerGen], node.minOccurs, node.maxOccurs)
###			else:
###				generator = innerGen
###		
###		### NUMBER
###		elif node.elementType == 'number':
###			if node.signed:
###				isSigned = 1
###			else:
###				isSigned = 0
###			
###			if node.endian == 'little':
###				isLittleEndian = 1
###			else:
###				isLittleEndian = 0
###
###			# Is number static?
###			if node.isStatic:
###				innerGen = Static(0)
###				if node.defaultValue != None:
###					innerGen = _StaticFromTemplate(node)
###				else:
###					raise Exception("No 'value' specified for Static element '" + node.name + "'")
###			else:
###				# autoGen
###				if node.autoGen == False:
###					if node.defaultValue != None:
###						# genList must have contents else an array index exception is thrown
###						if len(genList.getList()) == 0:
###							innerGen = _StaticFromTemplate(node)
###						else:
###							innerGen = WithDefault(group.addNewGroup(), _StaticFromTemplate(node), genList)
###					else:
###						# if no value is provided and no extra generators exist then we have no values to fuzz with
###						if len(genList.getList()) == 0:
###							raise Exception("'autoGen' disabled, no 'value' provided or generators provide for node '" + node.name + "'")
###						else:						
###							innerGen = genList
###				else:
###					if node.size == 8:
###						genList.getList().append(BadNumbers8())
###					elif node.size == 16:
###						genList.getList().append(BadNumbers16())
###					elif node.size == 24:
###						genList.getList().append(BadNumbers24())
###					elif node.size == 32:
###						genList.getList().append(BadNumbers32())
###					elif node.size == 64:
###						genList.getList().append(BadNumbers64())
###					else:
###						raise Exception("Invalide 'size' specified for element '" + node.name + "'")					
###
###					if node.defaultValue != None:						
###						innerGen = WithDefault(group.addNewGroup(), _StaticFromTemplate(node), genList)					
###					else:
###						genList.setGroup(group.addNewGroup())
###						innerGen = genList
###								
###			# Does number have size relation?
###			if self._HasSizeofRelation(node):
###				relation = self._GetSizeofRelation(node)
###				blockSize = BlockSize(None)
###				genList.getList().append(NumberVariance(None, blockSize, 50))
###				
###				if relation.of_ref.generator != None:
###					blockSize.setBlock(relation.of_ref.generator)
###					innerGen = WithDefault(None,
###										   blockSize,
###										   genList)
###				else:
###					innerGen = WithDefault(None, blockSize, genList)
###					relation.blockSize = blockSize
###					self._relationSizeofNeedResolving.append(relation)
###			
###			relation = None
###			# Does number have count relation?
###			if self._HasCountofRelation(node):
###				relation = self._GetCountofRelation(node)
###				
###				if relation.of_ref != None:
###					blockCount = MultiBlockCount(None)
###					genList.getList().append(NumberVariance(None, blockCount, 50))
###					
###					if relation.of_ref.generator != None:
###						blockCount.setBlock(relation.of_ref.generator)
###						innerGen = WithDefault(None,
###											   blockCount,
###											   genList)
###					else:
###						innerGen = WithDefault(None, blockCount, genList)
###						relation.blockCount = blockCount
###						self._relationCountofNeedResolving.append(relation)
###			
###			if innerGen == None:
###				innerGen = genList
###				
###			#allow for generator reference (checksums) 
###			if node.defaultValue == None:
###				genList.setGroup(group.addNewGroup())
###				innerGen = genList
###				
###			if node.size == 8:
###				generator = AsInt8(group.addNewGroup(), innerGen, isSigned, isLittleEndian)
###			elif node.size == 16:
###				generator = AsInt16(group.addNewGroup(), innerGen, isSigned, isLittleEndian)
###			elif node.size == 24:
###				generator = AsInt24(group.addNewGroup(), innerGen, isSigned, isLittleEndian)
###			elif node.size == 32:
###				generator = AsInt32(group.addNewGroup(), innerGen, isSigned, isLittleEndian)
###			elif node.size == 64:
###				generator = AsInt64(group.addNewGroup(), innerGen, isSigned, isLittleEndian)
###			
###			if generator == None: raise Exception("Unknown number size, sucks!!")
###			
###			if node.minOccurs != 1 or node.maxOccurs != 1 or (relation != None and relation.from_ref != None):
###				if relation != None and relation.from_ref != None:
###					if relation.from_ref.generator != None:
###						generator = MultiBlock(group.addNewGroup(), [generator], node.minOccurs, node.maxOccurs, relation.from_ref.generator)
###					else:
###						generator = MultiBlock(group.addNewGroup(), [generator], node.minOccurs, node.maxOccurs, relation.from_ref.generator)
###					
###				else:
###					generator = MultiBlock(group.addNewGroup(), [generator], node.minOccurs, node.maxOccurs)
###					relation.blockMulti = generator
###					self._relationCountofNeedResolving.append(relation)
###		
###		### BLOCK or TEMPLATE
###		elif node.elementType == 'block' or node.elementType == 'template':
###			
###			if node.minOccurs != 1 or node.maxOccurs != 1 or self._HasCountofRelation(node):
###				block = MultiBlock(group.addNewGroup(), [], node.minOccurs, node.maxOccurs)
###			else:
###				block = Block([])
###			
###			node.generator = block
###			
###			if self._HasCountofRelation(node):
###				relation = self._GetCountofRelation(node)
###				relation.blockMulti = block
###				
###				if relation.from_ref.generator != None:
###					block.setGenOccurs = relation.from_ref.generator
###				else:
###					relation.blockMulti = block
###					self._relationSizeofNeedResolving.append(relation)
###			
###			for child in node:
###				gen = self._getDefaultGenerator(child, group)
###				block.append(gen)
###				child.generator = gen
###			
###			generator = block
###		
###		### SEQUENCE
###		elif node.elementType == 'sequence':
###			
###			groups = []
###			generators = []
###			
###			block = GeneratorList2(group.addNewGroup(), groups, generators)
###			
###			for child in node:
###				g = GroupSequence()
###				
###				gen = self._getDefaultGenerator(child, g)
###				
###				groups.append(g)
###				generators.append(gen)
###				
###				child.generator = gen
###			
###			
###			if node.minOccurs != 1 or node.maxOccurs != 1 or self._HasCountofRelation(node):
###				block = MultiBlock(group.addNewGroup(), block, node.minOccurs, node.maxOccurs)
###				
###				if self._HasCountofRelation(node):
###					relation = self._GetCountofRelation(node)
###					relation.blockMulti = block
###					
###					if relation.from_ref.generator != None:
###						block.setGenOccurs = relation.from_ref.generator
###					else:
###						relation.blockMulti = block
###						self._relationSizeofNeedResolving.append(relation)
###			
###			generator = block
###		
###		### CHOICE
###		elif node.elementType == 'choice':
###			
###			groups = []
###			generators = []
###			
###			for child in node:
###				g = GroupSequence()
###				
###				gen = self._getDefaultGenerator(child, g)
###				
###				groups.append(g)
###				generators.append(gen)
###				
###				child.generator = gen
###			
###			block = GeneratorChoice(group.addNewGroup(), node.minOccurs, node.maxOccurs, groups, generators, node.generatedOccurs)
###			
###			if self._HasCountofRelation(node):
###				print "Warning: choice does not support count relation yet!!!"
###			
###			#if node.minOccurs != 1 or node.maxOccurs != 1 or self._HasCountofRelation(node):
###			#	block = MultiBlock(block, node.minOccurs, node.maxOccurs)
###			#	
###			#	if self._HasCountofRelation(node):
###			#		relation = self._GetCountofRelation(node)
###			#		relation.blockMulti = block
###			#		
###			#		if relation.from_ref.generator != None:
###			#			block.setGenOccurs = relation.from_ref.generator
###			#		else:
###			#			relation.blockMulti = block
###			#			self._relationSizeofNeedResolving.append(relation)
###			
###			generator = block
###		
###		### FLAGS
###		elif node.elementType == 'flags':
###			
###			flagArray = []
###			
###			for child in node:
###				if child.elementType != 'flag':
###					continue
###				
###				if child.defaultValue != None:
###					defaultValue = child.defaultValue
###				else:
###					defaultValue = 0
###				
###				if child.length == 1:
###					defaultGen = Bit()
###				elif child.length < 10:
###					defaultGen = List(None, range(2**int(child.length)))
###				else:
###					defaultGen = BadUnsignedNumbers16()
###				
###				genList.getList().append(defaultGen)
###				flag = [child.position, child.length, GeneratorList(group.addNewGroup(), [
###					Static(defaultValue),
###					genList,
###					Static(defaultValue)
###					])]
###				
###				flagArray.append(flag)
###			
###			flags = Flags2(None, node.length, flagArray)
###			
###			if node.endian == 'little':
###				endian = 1
###			else:
###				endian = 0
###			
###			if node.length == 8:
###				generator = AsInt8(None, flags, 0, endian)
###			elif node.length == 16:
###				generator = AsInt16(None, flags, 0, endian)
###			elif node.length == 24:
###				generator = AsInt24(None, flags, 0, endian)
###			elif node.length == 32:
###				generator = AsInt32(None, flags, 0, endian)
###			elif node.length == 64:
###				generator = AsInt64(None, flags, 0, endian)
###			
###			if generator == None: raise Exception("Whoops, that was lame, looks like you have a non-standard flag field size.  Sucks to be you!")
###			
###			if node.minOccurs != 1 or node.maxOccurs != 1 or self._HasCountofRelation(node):
###				if self._HasCountofRelation(node):
###					relation = self._GetCountofRelation(node)
###					
###					if relation.from_ref != None:
###						if relation.from_ref.generator != None:
###							generator = MultiBlock(group.addNewGroup(), [generator], node.minOccurs, node.maxOccurs, relation.from_ref.generator)
###						else:
###							generator = MultiBlock(group.addNewGroup(), [generator], node.minOccurs, node.maxOccurs)
###							relation.from_ref.generator = generator
###							self._relationCountofNeedResolving.append(relation)
###					else:
###						generator = MultiBlock(group.addNewGroup(), [generator], node.minOccurs, node.maxOccurs)
###				else:
###					generator = MultiBlock(group.addNewGroup(), [generator], node.minOccurs, node.maxOccurs)
###		
###		### BLOB
###		elif node.elementType == 'blob':
###
###			# TODO: decide what to do with this pad stuff.  A user might want to fill the blob via a generator and therefore
###			# provide no default value. In which case, the padding at this level makes no sense.  Also this will cause 
###			# a runtime error when attempting to calculate len(node.defaultValue) as it will be a NoneType.
###
###			value = node.defaultValue
###			if node.length != None and len(node.defaultValue) < node.length:
###				# need to pad things with null
###				value += node.padValue * (node.length - len(node.defaultValue))
###			
###			if node.isStatic == False and len(value) < 2000:
###
###				# autoGen
###				if node.autoGen == False:
###					if value != None:
###						# genList must have contents else an array index exception is thrown
###						if len(genList.getList()) == 0:
###							innerGen = Static(value)
###						else:
###							innerGen = WithDefault(group.addNewGroup(), Static(value), genList)
###					else:
###						# if no value is provided and no extra generators exist then we have no values to fuzz with
###						if len(genList.getList()) == 0:
###							raise Exception("'autoGen' disabled, no 'value' provided or generators provide for node '" + node.name + "'")
###						else:
###							genList.setGroup(group.addNewGroup())
###							innerGen = genList
###				else:
###					if value != None:
###						# TODO: Lets do a random flipper!!
###						genList.getList().append(WithDefault(group.addNewGroup(), value, SequentialFlipper(None, value)))
###						innerGen = WithDefault(group.addNewGroup(), _StaticFromTemplate(node), genList)					
###					else:
###						# TODO: Lets do a random flipper!!
###						genList.getList().append(SequentialFlipper(None, value))
###						genList.setGroup(group.addNewGroup())
###						innerGen = genList
###
###				generator = innerGen
###		
###			else:
###				generator = Static(value)
###			
###			if node.minOccurs != 1 or node.maxOccurs != 1 or self._HasCountofRelation(node):
###				if self._HasCountofRelation(node):
###					relation = self._GetCountofRelation(node)
###				
###					if relation.from_ref != None:
###						if relation.from_ref.generator != None:
###							generator = MultiBlock(group.addNewGroup(), [generator], node.minOccurs, node.maxOccurs, relation.from_ref.generator)
###						else:
###							generator = MultiBlock(group.addNewGroup(), [generator], node.minOccurs, node.maxOccurs)
###							relation.from_ref.generator = generator
###							self._relationCountofNeedResolving.append(relation)
###					else:
###						generator = MultiBlock(group.addNewGroup(), [generator], node.minOccurs, node.maxOccurs)
###				else:
###					generator = MultiBlock(group.addNewGroup(), [generator], node.minOccurs, node.maxOccurs)
###		
###		if generator == None: raise Exception("Unknown type: %s" % node.elementType)
###		
###		if node.transformer != None:
###			if generator.getTransformer() != None:
###				# Make sure we add this transformer
###				# to the last transformer in the chain
###				trans = generator.getTransformer()
###				while trans.getAnotherTransformer() != None:
###					trans = trans.getAnotherTransformer()
###				trans.setAnotherTransformer(node.transformer.transformer)
###			
###			else:
###				generator.setTransformer(node.transformer.transformer)
###		
###		return generator

# end
