'''
Analyzers that produce data models from Strings

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
#   Adam Cecchetti (adam@cecchetti.com)

# $Id$

from Peach.Engine.dom import *
from Peach.Engine.common import *
from Peach.analyzer import *

class StringTokenAnalyzer(Analyzer):
	'''
	Produces a tree of strings based on token precidence
	'''
	
	#: Does analyzer support asDataElement()
	supportDataElement = True
	#: Does analyzer support asCommandLine()
	supportCommandLine = True
	#: Does analyzer support asTopLevel()
	supportTopLevel = True
	
	def asDataElement(self, parent, args, data):
		'''
		Called when Analyzer is used in a data model.
		
		Should return a DataElement such as Block, Number or String.
		'''
		
		return self._tokenizeString(data, None)
	
	def asCommandLine(self, args):
		'''
		Called when Analyzer is used from command line.  Analyzer
		should produce Peach PIT XML as output.
		'''
		raise Exception("asCommandLine not supported")
	
	def asTopLevel(self, peach, args):
		'''
		Called when Analyzer is used from top level.
		
		From the top level producing zero or more data models and
		state models is possible.
		'''
		dom = DataModel()
		dom.append(self._tokenizeString)
		
		return dom
	
	def _tokenizeString(self, string, tokens = None):
		
		if tokens == None:
			# Tokens in order of precidence
			tokens = ['\0', '\n', '\r', '<', '>', '?', ' ', ';',',', '|', '@', ':', '(', ')',
					  '{', '}', '[', ']', '/', '\\', '&', '=', '-', '+', '.']
		
		topNode = _StringNode(None, string)
		
		for t in tokens:
			self._tokenTree(t, self._topNode)
		
		# Now build Peach DOM
		return self._buildDom(topNode, None)
	
	def _buildDom(self, stringNode, parent):
		
		if len(stringNode.children) == 0:
			node = String()
			node.defaultValue = stringNode.string
			return node
		
		node = Block()
		for c in stringNode.children:
			node.append(self._buildDom(c, node))
		
		return node
	
	def _split(self, string, tok):
		'''
		A version of split that also returns the tokens.
		'''
		lastPos = 0
		parts = []
		
		tokenLen = len(tok)
		
		if tokenLen == 0:
			return parts
		
		pos = string.find(tok)
		
		if pos == -1:
			return parts
		
		while pos > -1:
			parts.append(string[:pos])
			parts.append(string[pos:pos+tokenLen])
			string = string[pos+tokenLen:]
			lastPos = pos
			pos = string.find(tok)
		
		parts.append(string)
		
		return parts
	
	def _tokenTree(self, token, node):
		
		if node.string == None:
			for child in node.children:
				self._tokenTree(token, child)
			
		else:
			stuff = self._split(node.string, token)
			
			if len(stuff) == 0:
				return
			
			node.string = None
			
			if len(stuff) > 0 and len(node.children) > 0:
				raise Exception("we shouldn't have split a node and have children")
			
			for s in stuff:
				node.children.append( _StringNode(node, s, s == token) )
	
	def buildString(self, node = None):
		'''
		Reassemble node tree into a string
		'''
		
		if node == None:
			node = self._topNode
		
		if node.string == None:
			ret = ''
			
			for child in node.children:
				ret += self.buildString(child)
			
			return ret
		
		else:
			return node.string

class _StringNode(object):
	def __init__(self, parent, string, isToken = False):
		self.children = []
		self.parent = parent
		self.string = string
		self.isToken = isToken


# end
