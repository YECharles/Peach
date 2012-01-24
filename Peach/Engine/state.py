
'''
State Machine Engine

Will try and run a state machine.

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

import sys, re, types, time, struct, ctypes
import traceback, random
##import cProfile as profile

import Ft.Xml.Domlette
from Ft.Xml.Domlette import Print, PrettyPrint

from Peach.Engine.dom import *
from Peach.Engine.parser import *
from Peach.Engine.path import *
from Peach.Engine.common import *
from Peach.Engine.incoming import *
from Peach.publisher import PublisherBuffer

import Peach

def Debug(level, msg):
	if Peach.Engine.engine.Engine.debug:
		print msg

def peachPrint(msg):
	print "peachPrint: ", msg

class StateEngine:
	'''
	Runs a StateMachine instance.
	'''
	
	def __init__(self, engine, stateMachine, publishers):
		'''
		engine - Engine
		stateMachien - StateMachine to use
		publishers - Available Publishers
		'''
		
		#: Engine reference
		self.engine = engine
		
		#: State model we are using
		self.stateMachine = stateMachine
		
		# publishers - Available Publishers
		self.publishers = publishers
		
		self.f = peachPrint
		
		#: pathFinder -- to describe the path
		self.pathFinder = PathFinder(stateMachine)
		
		#: Cache of generated XML
		self.cachedXml = None
		
		#: Background dom copier
		#self.domCopier = DomBackgroundCopier()
	
	def getXml(self):
		'''
		Get the XML document representation of this
		DOM for use by slurp, etc.  For speed we will
		cache the generated XML until an operation
		occurs to dirty the cache.
		'''
		
		if self.cachedXml == None:
			dict = {}
			doc  = Ft.Xml.Domlette.NonvalidatingReader.parseString("<Peach/>", "http://phed.org")
			self.stateMachine.toXmlDom(doc.rootNode.firstChild, dict)
			self.cachedXml = doc
			
		return self.cachedXml
	
	def dirtyXmlCache(self):
		'''
		Mark XML cache as dirty.
		'''
		self.cachedXml = None
	
	def run(self, mutator):
		'''
		Perform a single run of a StateMachine using the provided
		mutator.
		'''
		
		Debug(1, "StateEngine.run: %s" % self.stateMachine.name)

		for pub in self.publishers:
			pub.hasBeenConnected = False
			pub.hasBeenStarted = False
		
		self.actionValues = []
		
		mutator.onStateMachineStarting(self)
		
		try:
			obj = self._getStateByName(self.stateMachine.initialState)
			if obj == None:
				raise PeachException("Unable to locate initial state \"%s\"." % self.stateMachine.initialState)
			
			self._runState(obj, mutator)
		
		except StateChangeStateException, e:
			
			# Hack to stop stack recurtion
			
			newState = e.state
			
			while True:
				try:
					self._runState(newState, mutator)
					break
				
				except StateChangeStateException, ee:
					newState = ee.state
		
		except SoftException:
			
			# Soft exceptions are okay except for 
			# first iteration
			
			if Peach.Engine.engine.Engine.context.testCount == 1:
			  raise PeachException("Error: First test case failed: ", str(sys.exc_info()[1]))
			  
			pass
		
		finally:
		
			for pub in self.publishers:
				# At end of state machine make sure publisher is closed
				if pub.hasBeenConnected:
						pub.close()
						pub.hasBeenConnected = False

				# At end of state machine make sure publisher is stopped
				if pub.hasBeenStarted:
					pub.stop()
					pub.hasBeenStarted = False
			
		mutator.onStateMachineFinished(self)
		
		return self.actionValues
		
	def _getPublisherByName(self, publisherName):
		'''
		Locate a Publisher object by name
		'''
		
		for child in self.publishers:
			if child.domPublisher.elementType == 'publisher' and child.domPublisher.name == publisherName:
				return child
		
		return None

	def _getStateByName(self, stateName):
		'''
		Locate a State object by name in the StateMachine.
		'''
		
		for child in self.stateMachine:
			if child.elementType == 'state' and child.name == stateName:
				return child
			
			#else:
			#	Debug(1, "_getStateByName: No match on %s" % child.name)
		
		return None
	
	def _runState(self, state, mutator):
		'''
		Runs a specific State from a StateMachine.
		'''
		
		Debug(1, "StateEngine._runState: %s" % state.name)
		Engine.context.watcher.OnStateEnter(state)
		
		# First up we need to copy all the action's templates
		# otherwise values can leak all over the place!
		
		cracker = DataCracker(self.engine.peach)
		for action in state:
			if not isinstance(action, Action):
				continue
			
			if action.template == None:
				for c in action:
					if c.elementType == 'actionparam' or c.elementType == 'actionresult':
						# Copy template from origional first
						if not hasattr(c, 'origionalTemplate'):
							if c.elementType == 'actionresult':
								cracker.optmizeModelForCracking(c.template, True)
							c.origionalTemplate = c.template
							c.origionalTemplate.BuildRelationCache()
							c.origionalTemplate.resetDataModel()
							c.origionalTemplate.getValue()
							#self.domCopier.addDom(c.origionalTemplate)
						
						# Make a fresh copy of the template
						del c[c.template.name]
						c.template = None
						##while c.template == None:
						##	c.template = self.domCopier.getCopy(c.origionalTemplate)
						if c.template == None:
							c.template = c.origionalTemplate.copy(c)
						#c.template = c.origionalTemplate.clone()
						c.append(c.template)
				
				continue
			
			# Copy template from origional first
			if not hasattr(action, 'origionalTemplate'):
				if action.type == 'input':
					cracker.optmizeModelForCracking(action.template, True)
				
				action.origionalTemplate = action.template
				action.origionalTemplate.BuildRelationCache()
				action.origionalTemplate.resetDataModel()
				action.origionalTemplate.getValue()
				#self.domCopier.addDom(action.origionalTemplate)
			
			# Make a fresh copy of the template
			del action[action.template.name]
			action.template = None
			##while action.template == None:
			##	print "0"
			##	action.template = self.domCopier.getCopy(action.origionalTemplate)
			action.template = action.origionalTemplate.copy(action)
			action.append(action.template)
		
		# Next setup a few things
		self.actionValues.append( [ state.name, 'state' ] )
		mutator.onStateStarting(self, state)
		
		# EVENT: onEnter
		if state.onEnter != None:
			environment = {
				'Peach' : self.engine.peach,
				'State' : state,
				'StateModel' : state.parent,
				'peachPrint' : self.f,
				'Mutator' : mutator,
				'sleep' : time.sleep
				}
			
			evalEvent(state.onEnter, environment, self.engine.peach)
		
		stopFuzzing = False
		try:
			# Check if this state is marked with a Stop. If so, end fuzzing
			currentPath = self.pathFinder.current()
			if not currentPath:
				if self.pathFinder.canMove():
					currentPath = self.pathFinder.next()
					
			if currentPath:
				stopFuzzing = currentPath.stop
				
			# Advance to the next path on pathFinder
			nextPath = None
			if self.pathFinder.canMove():
				nextPath = self.pathFinder.next()
		
			try:
				# Start with first action and continue along
				for action in state:
					if action.elementType != 'action':
						continue
					
					self._runAction(action, mutator)
			
			except SoftException:
				# SoftExceptions are fine
				
				if Peach.Engine.engine.Engine.context.testCount == 1:
				  raise PeachException("Error: First test case failed: ", str(sys.exc_info()[1]))
				
				pass
			
			# Pass through the nextState?
			if nextPath:
				raise StateChangeStateException(self._getStateByName(nextPath.stateName))
			
			# EVENT: onExit
			if state.onExit != None:
				environment = {
					'Peach' : self.engine.peach,
					'State' : state,
					'StateModel' : state.parent,
					'peachPrint' : self.f,
					'Mutator' : mutator,
					'sleep' : time.sleep
					}
				
				evalEvent(state.onExit, environment, self.engine.peach)
				
			mutator.onStateFinished(self, state)
			Engine.context.watcher.OnStateExit(state)
			
		except StateChangeStateException, e:
			
			# EVENT: onExit
			if state.onExit != None:
				environment = {
					'Peach' : self.engine.peach,
					'State' : state,
					'StateModel' : state.parent,
					'peachPrint' : self.f,
					'Mutator' : mutator,
					'sleep' : time.sleep
					}
				
				evalEvent(state.onExit, environment, self.engine.peach)
			
			mutator.onStateFinished(self, state)
			Engine.context.watcher.OnStateExit(state)
			newState = mutator.onStateChange(state, e.state)
			if newState == None:
				newState = e.state
			
			# stop fuzzing next state?
			if not stopFuzzing:
				#self._runState(newState, mutator)
				raise StateChangeStateException(newState)
		
	def _runAction(self, action, mutator):
		
		Debug(1, "\nStateEngine._runAction: %s" % action.name)
				
		mutator.onActionStarting(action.parent, action)
		
		# If publisher property has been given, use referenced Publisher; otherwise the first one
		if action.publisher != None:
			pub = self._getPublisherByName(action.publisher)
			
			if pub == None:
				raise PeachException("Publisher '%s' not found!" % action.publisher)
		else:
			pub = self.publishers[0]
		
		# EVENT: when
		if action.when != None:
			environment = {
				'Peach' : self.engine.peach,
				'Action' : action,
				'State' : action.parent,
				'StateModel' : action.parent.parent,
				'Mutator' : mutator,
				'peachPrint' : self.f,
				'sleep' : time.sleep,
				'getXml' : self.getXml,
				'random' : random
				}
			
			if not evalEvent(action.when, environment, self.engine.peach):
				Debug(1, "Action when failed: " + action.when)
				return
			else:
				Debug(1, "Action when passed: " + action.when)
		
		Engine.context.watcher.OnActionStart(action)
		
		# EVENT: onStart
		if action.onStart != None:
			environment = {
				'Peach' : self.engine.peach,
				'Action' : action,
				'State' : action.parent,
				'StateModel' : action.parent.parent,
				'Mutator' : mutator,
				'peachPrint' : self.f,
				'sleep' : time.sleep
				}
			
			evalEvent(action.onStart, environment, self.engine.peach)
		
		if action.type == 'input':
			action.value = None
			
			if pub.hasBeenStarted == False:
				pub.start()
				pub.hasBeenStarted = True
			if not pub.hasBeenConnected:
				pub.connect()
				pub.hasBeenConnected = True
			
			# Make a fresh copy of the template
			action.__delitem__(action.template.name)
			action.template = action.origionalTemplate.copy(action)
			action.append(action.template)
			
			# Create buffer
			buff = PublisherBuffer(pub)
			self.dirtyXmlCache()
			
			# Crack data
			cracker = DataCracker(self.engine.peach)
			(rating, pos) = cracker.crackData(action.template, buff, "setDefaultValue")
			
			if rating > 2:
				raise SoftException("Was unble to crack incoming data into %s data model." % action.template.name)
			
			action.value = action.template.getValue()
			
		elif action.type == 'output':
			
			if not pub.hasBeenStarted:
				pub.start()
				pub.hasBeenStarted = True
			if not pub.hasBeenConnected:
				pub.connect()
				pub.hasBeenConnected = True
			
			# Run mutator
			mutator.onDataModelGetValue(action, action.template)
			
			# Get value
			if action.template.modelHasOffsetRelation:
				stringBuffer = StreamBuffer()
				action.template.getValue(stringBuffer)
				
				stringBuffer.setValue("")
				stringBuffer.seekFromStart(0)
				action.template.getValue(stringBuffer)
				
				action.value = stringBuffer.getValue()
				
			else:
				action.value = action.template.getValue()
			
			Debug(1, "Actiong output sending %d bytes" % len(action.value))
			
			if not pub.withNode:
				pub.send(action.value)
			else:
				pub.sendWithNode(action.value, action.template)
			
			# Save the data filename used for later matching
			if action.data != None and action.data.fileName != None:
				self.actionValues.append( [ action.name, 'output', action.value, action.data.fileName ] )
			
			else:
				self.actionValues.append( [ action.name, 'output', action.value ] )
			
			obj = Element(action.name, None)
			obj.elementType = 'dom'
			obj.defaultValue = action.value
			action.value = obj
		
		elif action.type == 'call':
			action.value = None
			
			actionParams = []
			
			if not pub.hasBeenStarted:
				pub.start()
				pub.hasBeenStarted = True
			
			# build up our call
			method = action.method
			if method == None:
				raise PeachException("StateEngine: Action of type \"call\" does not have method name!")
			
			params = []
			for c in action:
				if c.elementType == 'actionparam':
					params.append(c)
			
			argNodes = []
			argValues = []
			for p in params:
				if p.type == 'out' or p.type == 'inout':
					raise PeachException("StateEngine: Action of type \"call\" does not yet support out or inout parameters (bug in comtypes)!")
				
				# Run mutator
				mutator.onDataModelGetValue(action, p.template)
				
				# Get value
				if p.template.modelHasOffsetRelation:
					stringBuffer = StreamBuffer()
					p.template.getValue(stringBuffer)
					stringBuffer.setValue("")
					stringBuffer.seekFromStart(0)
					p.template.getValue(stringBuffer)
					
					p.value = stringBuffer.getValue()
					
				else:
					p.value = p.template.getValue()

				argValues.append(p.value)
				argNodes.append(p.template)
				
				actionParams.append([p.name, 'param', p.value])
			
			if not pub.withNode:
				ret = pub.call(method, argValues)
			else:
				ret = pub.callWithNode(method, argValues, argNodes)
			
			# look for and set return
			for c in action:
				if c.elementType == 'actionresult':
					self.dirtyXmlCache()
					
					print "RET:",ret,type(ret)
					
					data = None
					if type(ret) == int:
						data = struct.pack("i", ret)
					elif type(ret) == long:
						data = struct.pack("q", ret)
					elif type(ret) == str:
						data = ret
					
					if c.template.isPointer:
						print "Found ctypes pointer...trying to cast..."
						retCtype = c.template.asCTypeType()
						retCast = ctypes.cast(ret, retCtype)
						
						for i in range(len(retCast.contents._fields_)):
							(key, value) = retCast.contents._fields_[i]
							value = eval("retCast.contents.%s" % key)
							c.template[key].defaultValue = value
							print "Set [%s=%s]" % (key, value)
					
					else:
						cracker = DataCracker(self.engine.peach)
						cracker.haveAllData = True
						(rating, pos) = cracker.crackData(c.template, PublisherBuffer(None, data, True))
						if rating > 2:
							raise SoftException("Was unble to crack result data into %s data model." % c.template.name)
			
			self.actionValues.append( [ action.name, 'call', method, actionParams ] )
		
		elif action.type == 'getprop':
			action.value = None
			
			if not pub.hasBeenStarted:
				pub.start()
				pub.hasBeenStarted = True
			
			# build up our call
			property = action.property
			if property == None:
				raise Exception("StateEngine._runAction(): getprop type does not have property name!")
			
			data = pub.property(property)
			
			self.actionValues.append( [ action.name, 'getprop', property, data ] )
			
			self.dirtyXmlCache()
			
			cracker = DataCracker(self.engine.peach)
			(rating, pos) = cracker.crackData(action.template, PublisherBuffer(None,data))
			if rating > 2:
				raise SoftException("Was unble to crack getprop data into %s data model." % action.template.name)
			
			# If no exception, it worked
			
			action.value = action.template.getValue()
			
			if Peach.Engine.engine.Engine.debug:
				print "*******POST GETPROP***********"
				doc = self.getXml()
				PrettyPrint(doc, asHtml=1)
				print "******************"
			
		elif action.type == 'setprop':
			action.value = None
			
			if not pub.hasBeenStarted:
				pub.start()
				pub.hasBeenStarted = True
				
			# build up our call
			property = action.property
			if property == None:
				raise Exception("StateEngine: setprop type does not have property name!")
			
			value = None
			valueNode = None
			for c in action:
				if c.elementType == 'actionparam' and c.type == "in":
					# Run mutator
					mutator.onDataModelGetValue(action, c.template)
					
					# Get value
					if c.template.modelHasOffsetRelation:
						stringBuffer = StreamBuffer()
						c.template.getValue(stringBuffer)
						stringBuffer.setValue("")
						stringBuffer.seekFromStart(0)
						c.template.getValue(stringBuffer)
						
						value = c.value = stringBuffer.getValue()
						
					else:
						value = c.value = c.template.getValue()
					
					valueNode = c.template
					break
			
			if not pub.withNode:
				pub.property(property, value)
			else:
				pub.propertyWithNode(property, value, valueNode)
			
			self.actionValues.append( [ action.name, 'setprop', property, value ] )
		
		elif action.type == 'changeState':
			action.value = None
			self.actionValues.append( [ action.name, 'changeState', action.ref ] )
			mutator.onActionFinished(action.parent, action)
			raise StateChangeStateException(self._getStateByName(action.ref))
			
		elif action.type == 'slurp':
			action.value = None
			
			startTime = time.time()
			
			doc = self.getXml()
			setNodes = doc.xpath(action.setXpath)
			if len(setNodes) == 0:
				PrettyPrint(doc, asHtml=1)
				raise PeachException("Slurp [%s] setXpath [%s] did not return a node" % (action.name,action.setXpath))
			
			# Only do this once :)
			valueElement = None
			if action.valueXpath != None:
				valueNodes = doc.xpath(action.valueXpath)
				if len(valueNodes) == 0:
					print "Warning: valueXpath did not return a node"
					raise SoftException("StateEngine._runAction(xpath): valueXpath did not return a node")
				
				valueNode = valueNodes[0]
				try:
					valueElement = action.getRoot().getByName(str(valueNode.getAttributeNS(None, "fullName")))
					
				except:
					print "valueNode:", valueNode
					print "valueNode.nodeName:", valueNode.nodeName
					print "valueXpath:", action.valueXpath
					print "results:", len(valueNodes)
					raise PeachException("Slurp AttributeError: [%s]" % str(valueNode.getAttributeNS(None, "fullName")))
				
			for node in setNodes:
				
				setElement = action.getRoot().getByName(str(node.getAttributeNS(None, "fullName")))
				
				if valueElement != None:
					
					Debug(1, "Action-Slurp: 1 Setting %s from %s" % (
						str(node.getAttributeNS(None, "fullName")),
						str(valueNode.getAttributeNS(None, "fullName"))
						))
					
					valueElement = action.getRoot().getByName(str(valueNode.getAttributeNS(None, "fullName")))
					
					# Some elements like Block do not have a current or default value
					if valueElement.currentValue == None and valueElement.defaultValue == None:
						setElement.currentValue = None
						setElement.defaultValue = valueElement.getValue()
					
					else:
						setElement.currentValue = valueElement.getValue()
						setElement.defaultValue = valueElement.defaultValue
					
					setElement.value = None
					
				else:
					
					Debug(1, "Action-Slurp: 2 Setting %s to %s" % (
						str(node.getAttributeNS(None, "fullName")),
						repr(action.valueLiteral)
						))
					
					setElement.defaultValue = action.valueLiteral
					setElement.currentValue = None
					setElement.value = None
			
			#print " - Total time to slurp data: %.2f" % (time.time() - startTime)
		
		elif action.type == 'connect':
			if not pub.hasBeenStarted:
				pub.start()
				pub.hasBeenStarted = True
				
			pub.connect()
			pub.hasBeenConnected = True
		
		elif action.type == 'accept':
			if not pub.hasBeenStarted:
				pub.start()
				pub.hasBeenStarted = True
			
			pub.accept()
			pub.hasBeenConnected = True
		
		elif action.type == 'close':
			if not pub.hasBeenConnected:
				# If we haven't been opened lets ignore
				# this close.
				return
				
			pub.close()
			pub.hasBeenConnected = False
		
		elif action.type == 'start':
			pub.start()
			pub.hasBeenStarted = True
		
		elif action.type == 'stop':
			if pub.hasBeenStarted:
				pub.stop()
				pub.hasBeenStarted = False
		
		elif action.type == 'wait':
			time.sleep(float(action.valueLiteral))
		
		else:
			raise Exception("StateEngine._runAction(): Unknown action.type of [%s]" % str(action.type))
		
		# EVENT: onComplete
		if action.onComplete != None:
			environment = {
				'Peach' : self.engine.peach,
				'Action' : action,
				'State' : action.parent,
				'Mutator' : mutator,
				'StateModel' : action.parent.parent,
				'sleep' : time.sleep
				}
			
			evalEvent(action.onComplete, environment, self.engine.peach)
		
		mutator.onActionFinished(action.parent, action)
		Engine.context.watcher.OnActionComplete(action)
	
	def _resetXmlNodes(self, node):
		'''
		Reset XML node tree starting at 'node'.  We will remove
		any attribute calleed:
		
		  value
		  currentValue
		  defaultValue
		  value-Encoded
		  currentValue-Encoded
		  defaultValue-Encoded
		
		'''
		
		att = ['value', 'currentValue', 'defaultValue',
			   'value-Encoded', 'currentValue-Encoded', 'defaultValue-Encoded']
		
		for a in att:
			if node.hasAttributeNS(None, a):
				node.removeAttributeNS(None, a)
		
		for child in node.childNodes:
			self._resetXmlNodes(child)

class StateChangeStateException:
	def __init__(self, state):
		self.state = state
	
	def __str__(self):
		return "Exception: StateChangeStateException"

class StateError:
	def __init__(self, msg):
		self.msg = msg
	
	def __str__(self):
		return self.msg

# End
