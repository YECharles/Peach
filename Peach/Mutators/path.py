import sys, os, time
#from parser import *

from Peach.Mutators.default import *

class PathValidationMutator(NullMutator):
	'''
	This mutator is just used to trace path
    of each test for path validation purposes
    so this is not an actual Mutator
    that is used on fuzzing
	'''
	
	def __init__(self):
		Mutator.__init__(self)
		self.states = []
		self.name = "PathValidationMutator"
		
	def onStateStart(self, state):
		self.states.append(state.name)
        
	def onStateMachineStart(self, engine):
		pass
		
	def onStateMachineComplete(self, engine):
		engine.pathFinder.reset()