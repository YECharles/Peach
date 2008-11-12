
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
		if action.template.modelHasOffsetRelation:
			stringBuffer = StreamBuffer()
			action.template.getValue(stringBuffer)
			stringBuffer.setValue("")
			stringBuffer.seekFromStart(0)
			action.template.getValue(stringBuffer)
			return stringBuffer.getValue()
		
		return action.template.getValue()
	
	def getActionParamValue(self, action):
		if action.template.modelHasOffsetRelation:
			stringBuffer = StreamBuffer()
			action.template.getValue(stringBuffer)
			stringBuffer.setValue("")
			stringBuffer.seekFromStart(0)
			action.template.getValue(stringBuffer)
			return stringBuffer.getValue()
		
		return action.template.getValue()
	
	def getActionChangeStateValue(self, action, value):
		return value
	

# end
