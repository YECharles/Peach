
'''
State Machine Engine

Will try and run a state machine.

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

import sys, re, types, time
import traceback

import Ft.Xml.Domlette
from Ft.Xml.Domlette import Print, PrettyPrint

from Peach.Engine.dom import *
from Peach.Engine.parser import *
from Peach.Engine.path import *
from Peach.Engine.common import *
from Peach.Engine.incoming import *

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
	
	def __init__(self, engine, stateMachine, publisher):
		'''
		engine - Engine
		stateMachien - StateMachine to use
		publisher - Publisher to use
		'''
		
		self.engine = engine
		self.stateMachine = stateMachine
		self.publisher = publisher
		self.f = peachPrint
		
		'''
		pathFinder -- to describe the path
		'''
		self.pathFinder = PathFinder(stateMachine)
	
	def run(self, mutator):
		'''
		Perform a single run of a StateMachine using the provided
		mutator.
		'''
		
		Debug(1, "StateEngine.run: %s" % self.stateMachine.name)

		self.publisher.hasBeenConnected = False
		self.publisher.hasBeenStarted = False
		
		self.actionValues = []
		
		mutator.onStateMachineStart(self)
		
		try:
			self._runState(self._getStateByName(self.stateMachine.initialState), mutator)
		
		except SoftException:
			
			# Soft exceptions are okay
			pass
		
		finally:
		
			# At end of state machine make sure publisher is closed
			if self.publisher.hasBeenConnected:
				self.publisher.close()
				self.publisher.hasBeenConnected = False
				
			# At end of state machine make sure publisher is stopped
			if self.publisher.hasBeenStarted:
				self.publisher.stop()
				self.publisher.hasBeenStarted = False
			
		mutator.onStateMachineComplete(self)
		
		return self.actionValues

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
		
		# First up we need to copy all the action's templates
		# otherwise values can leak all over the place!
		
		for action in state:
			if not isinstance(action, Action):
				continue
			
			if action.template == None:
				for c in action:
					if c.elementType == 'actionparam' or c.elementType == 'actionresult':
						# Copy template from origional first
						if not hasattr(c, 'origionalTemplate'):
							c.origionalTemplate = c.template
							c.origionalTemplate.BuildRelationCache()
						
						# Make a fresh copy of the template
						c.__delitem__(c.template.name)
						c.template = c.origionalTemplate.copy(c)
						c.append(c.template)
				
				continue
			
			# Copy template from origional first
			if not hasattr(action, 'origionalTemplate'):
				action.origionalTemplate = action.template
				action.origionalTemplate.BuildRelationCache()
			
			# Make a fresh copy of the template
			action.__delitem__(action.template.name)
			action.template = action.origionalTemplate.copy(action)
			action.append(action.template)
		
		# Next setup a few things
		
		self.actionValues.append( [ state.name, 'state' ] )
		mutator.onStateStart(state)
		
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
				
			mutator.onStateComplete(state)
			
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
			
			mutator.onStateComplete(state)
			
			# stop fuzzing next state?
			if not stopFuzzing:
				self._runState(e.state, mutator)
		
	
	#def _execEvent(self, code, environment):
	#	'''
	#	exec python code, no result.
	#	
	#	code - String
	#	environment - Dictionary, keys are variables to place in local scope
	#	'''
	#	
	#	#print globals()
	#	scope = { '__builtins__' : globals()['__builtins__'] }
	#	for k in environment.keys():
	#		scope[k] = environment[k]
	#	
	#	ret = exec(code, scope, scope)
	#	
	#	return ret
	
	def _runAction(self, action, mutator):
		
		Debug(1, "StateEngine._runAction: %s" % action.name)
				
		mutator.onActionStart(action)
		
		# EVENT: when
		if action.when != None:
			environment = {
				'Peach' : self.engine.peach,
				'Action' : action,
				'State' : action.parent,
				'StateModel' : action.parent.parent,
				'Mutator' : mutator,
				'peachPrint' : self.f,
				'sleep' : time.sleep
				}
			
			#print action.parent.parent
			#for k in action.parent.parent._childrenHash.keys():
			#	print "Key: ", k
			
			if not evalEvent(action.when, environment, self.engine.peach):
				return
		
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
			
			if self.publisher.hasBeenStarted == False:
				self.publisher.start()
				self.publisher.hasBeenStarted = True
			if not self.publisher.hasBeenConnected:
				self.publisher.connect()
				self.publisher.hasBeenConnected = True
			
			# Determine initial read size
			cracker = DataCracker(self.engine.peach)
			size = cracker.getInitialReadSize(action.template)
			Debug(1, "StateEngine._runAction(input): Found initial read size of %s" % size)
			
			data = ""			# Data Buffer
			timeout = False		# Have we hit a timeout exception?
			haveAllData = False	# Do we have all the data?
			
			while True:
				try:
					Debug(2, ">> STATE IS CALLING RECEIVE FOR %d BYTES" % size)
					
					# Did we get asked for all the data?
					if size == -1:
						try:
							# Read everything in
							haveAllData = True
							data += self.publisher.receive()
						
						except Peach.publisher.Timeout, e:
							# Timeout is okay here
							pass
						except Peach.Publishers.tcp.Timeout:
							pass
					
					# Else try and read wanted size
					else:
						try:
							data += self.publisher.receive(size)
							timeout = False
						
						except Peach.publisher.Timeout, e:
							
							# Retry after a timeout
							if timeout:
								raise
							
							timeout = True
							haveAllData = True
						
						except Peach.Publishers.tcp.Timeout:
							# Retry after a timeout
							if timeout:
								raise
							
							timeout = True
							haveAllData = True
					
					# Make a fresh copy of the template
					action.__delitem__(action.template.name)
					action.template = action.origionalTemplate.copy(action)
					action.append(action.template)
					
					# Try and crack the data
					Debug(1, "\n\n\n\n### cracker.crackData(%d) ##############################################" % len(data))
					if haveAllData:
						Debug(1, "### HAVE ALL DATA!!!!!! ##############################################")
						
					cracker = DataCracker(self.engine.peach)
					cracker.haveAllData = haveAllData
					(rating, pos) = cracker.crackData(action.template, data)
					if rating > 2:
						raise SoftException("Was unble to crack incoming data into %s data model." % action.template.name)
					
					# If no exception, it worked
					break
				
				except NeedMoreData, e:
					size = e.amount
					Debug(2, ">> Going back for: %d" % size)
					Debug(2, ">> Tab Level: %d" % DataCracker._tabLevel)
					if DataCracker._tabLevel > 0:
						size = 0
					
					#Debug(2, ">> Currently Have:")
					#Debug(2, "><><><><><><><><><><><><><><><><><><")
					#Debug(2, data)
					#Debug(2, "><><><><><><><><><><><><><><><><><><")
			
			action.value = action.template.getValue()
			
			#print "VALUE: %s" % repr(action.value)
			
			#print ">>> action.template.gatValue(): " + action.template.getValue()
			#print ">>> action.template", action.template
			if Peach.Engine.engine.Engine.debug:
				dict = {}
				doc  = Ft.Xml.Domlette.NonvalidatingReader.parseString("<Peach/>", "http://phed.org")
				
				stateMachine = action.parent.parent
				stateMachineNode = stateMachine.toXmlDom(doc.rootNode.firstChild, dict)
				
				print "*****POST INPUT*************"
				PrettyPrint(doc, asHtml=1)
				print "******************"
		
		elif action.type == 'output':
			
			if not self.publisher.hasBeenStarted:
				self.publisher.start()
				self.publisher.hasBeenStarted = True
			if not self.publisher.hasBeenConnected:
				self.publisher.connect()
				self.publisher.hasBeenConnected = True
			
			action.value = mutator.getActionValue(action)
			
			Debug(1, "Actiong output sending %d bytes" % len(action.value))
			
			if not self.publisher.withNode:
				self.publisher.send(action.value)
			else:
				self.publisher.sendWithNode(action.template)
			
			self.actionValues.append( [ action.name, 'output', action.value ] )
			
			obj = Element(action.name, None)
			obj.elementType = 'dom'
			obj.defaultValue = action.value
			action.value = obj
		
		elif action.type == 'call':
			action.value = None
			
			actionParams = []
			
			if not self.publisher.hasBeenStarted:
				self.publisher.start()
				self.publisher.hasBeenStarted = True
			
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
				
				p.value = mutator.getActionParamValue(p)
				argValues.append(p.value)
				argNodes.append(p.template)
				
				actionParams.append([p.name, 'param', p.value])
			
			if not self.publisher.withNode:
				ret = self.publisher.call(method, argValues)
			else:
				ret = self.publisher.callWithNode(method, argValues, argValues)
			
			# look for and set return
			for c in action:
				if c.elementType == 'actionresult':
					cracker = DataCracker(self.engine.peach)
					cracker.haveAllData = True
					(rating, pos) = cracker.crackData(action.template, ret)
					if rating > 2:
						raise SoftException("Was unble to crack result data into %s data model." % action.template.name)
			
			self.actionValues.append( [ action.name, 'call', method, actionParams ] )
		
		elif action.type == 'getprop':
			action.value = None
			
			if not self.publisher.hasBeenStarted:
				self.publisher.start()
				self.publisher.hasBeenStarted = True
			
			# build up our call
			property = action.property
			if property == None:
				raise Exception("StateEngine._runAction(): getprop type does not have property name!")
			
			data = self.publisher.property(property)
			
			self.actionValues.append( [ action.name, 'getprop', property, data ] )
			
			cracker = DataCracker(self.engine.peach)
			cracker.haveAllData = True
			(rating, pos) = cracker.crackData(action.template, data)
			if rating > 2:
				raise SoftException("Was unble to crack getprop data into %s data model." % action.template.name)
			
			# If no exception, it worked
			
			action.value = action.template.getValue()
			
			if Peach.Engine.engine.Engine.debug:
				### Test CODE
				dict = {}
				doc  = Ft.Xml.Domlette.NonvalidatingReader.parseString("<Peach/>", "http://phed.org")
				
				stateMachine = action.parent.parent
				stateMachineNode = stateMachine.toXmlDom(doc.rootNode.firstChild, dict)
				
				print "*******POST GETPROP***********"
				PrettyPrint(doc, asHtml=1)
				print "******************"
			
		elif action.type == 'setprop':
			action.value = None
			
			if not self.publisher.hasBeenStarted:
				self.publisher.start()
				self.publisher.hasBeenStarted = True
				
			# build up our call
			property = action.property
			if property == None:
				raise Exception("StateEngine: setprop type does not have property name!")
			
			value = None
			valueNode = None
			for c in action:
				if c.elementType == 'actionparam' and c.type == "in":
					value = c.value = mutator.getActionParamValue(c)
					valueNode = c.template
					break
			
			if not self.publisher.withNode:
				self.publisher.property(property, value)
			else:
				self.publisher.propertyWithNode(property, value, valueNode)
			
			self.actionValues.append( [ action.name, 'setprop', property, value ] )
		
		elif action.type == 'changeState':
			action.value = None
			self.actionValues.append( [ action.name, 'changeState', action.ref ] )
			mutator.onActionComplete(action)
			raise StateChangeStateException(self._getStateByName(action.ref))
			
		elif action.type == 'slurp':
			action.value = None
			
			dict = {}
			doc  = Ft.Xml.Domlette.NonvalidatingReader.parseString("<Peach/>", "http://phed.org")
			
			stateMachine = action.parent.parent
			stateMachineNode = stateMachine.toXmlDom(doc.rootNode.firstChild, dict)
			
			if Peach.Engine.engine.Engine.debug:
				print "****** PRE SLURP ************"
				PrettyPrint(doc, asHtml=1)
				print "******************"
			
			setNodes = doc.xpath(action.setXpath)
			if len(setNodes) == 0:
				raise Exception("StateEngine._runAction(xpath): setXpath did not return a node")
			
			for node in setNodes:
				
				if action.valueXpath != None:
					valueNodes = doc.xpath(action.valueXpath)
					if len(valueNodes) == 0:
						raise Exception("StateEngine._runAction(xpath): valueXpath did not return a node")
					
					valueNode = valueNodes[0]
					
					if valueNode.hasAttributeNS(None, "currentValue"):
						Debug(1, "Setting currentValue: [%s]" % str(valueNode.getAttributeNS(None, 'currentValue')))
						node.setAttributeNS(None, 'currentValue', valueNode.getAttributeNS(None, 'currentValue'))
						
						if valueNode.hasAttributeNS(None, 'currentValue-Encoded'):
							node.setAttributeNS(None, 'currentValue-Encoded',
												valueNode.getAttributeNS(None, 'currentValue-Encoded'))
					
					elif valueNode.hasAttributeNS(None, 'value'):
						Debug(1, "Setting value: [%s]" % str(valueNode.getAttributeNS(None, 'value')))
						node.setAttributeNS(None, 'currentValue', valueNode.getAttributeNS(None, 'value'))
						
						if valueNode.hasAttributeNS(None, 'value-Encoded'):
							node.setAttributeNS(None, 'currentValue-Encoded',
												valueNode.getAttributeNS(None, 'value-Encoded'))
				
				else:
					Debug(1, "Setting currentValue: [%s]" % str(action.valueLiteral))
					try:
						node.setAttributeNS(None, 'currentValue', action.valueLiteral)
					
					except UnicodeDecodeError:
						node.setAttributeNS(None, "currentValue-Encoded", "base64")
						node.setAttributeNS(None, 'currentValue', base64.b64encode(action.valueLiteral))
			
			
			if Peach.Engine.engine.Engine.debug:
				print "****** POST SLURP ************"
				PrettyPrint(doc, asHtml=1)
				print "******************"
			
			stateMachine.updateFromXmlDom(stateMachineNode, dict)
			dict = None
		
		elif action.type == 'connect':
			if not self.publisher.hasBeenStarted:
				self.publisher.start()
				self.publisher.hasBeenStarted = True
				
			self.publisher.connect()
			self.publisher.hasBeenConnected = True
		
		elif action.type == 'accept':
			if not self.publisher.hasBeenStarted:
				self.publisher.start()
				self.publisher.hasBeenStarted = True
			
			self.publisher.accept()
			self.publisher.hasBeenConnected = True
		
		elif action.type == 'close':
			if not self.publisher.hasBeenConnected:
				# If we haven't been opened lets ignore
				# this close.
				return
				
			self.publisher.close()
			self.publisher.hasBeenConnected = False
		
		elif action.type == 'start':
			self.publisher.start()
			self.publisher.hasBeenStarted = True
		
		elif action.type == 'stop':
			if self.publisher.hasBeenStarted:
				self.publisher.stop()
				self.publisher.hasBeenStarted = False
		
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
		
		mutator.onActionComplete(action)
	
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
