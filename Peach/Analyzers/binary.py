'''
Analyzers that produce data models from Binary blobs

@author: Michael Eddington
@version: $Id$
'''

#
# Copyright (c) 2009 Michael Eddington
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

import sys, os, re, struct

from Peach.Engine.dom import *
from Peach.Engine.common import *
from Peach.analyzer import *

class _Node(object):
	def __init__(self, type, startPos, endPos, value):
		self.type = type
		self.value = value
		self.startPos = startPos
		self.endPos = endPos


class Binary(Analyzer):
	'''
	Analyzes binary blobs to build data models
	
	 1. Locate strings, char & wchar
	   a. Analyze string for XML
	   b. UTF8/UTF16 and byte order marks
	 2. Find string lengths (relations!) --> Would also give us endian
	 3. Compressed segments (zip, gzip)
	 
	 ?. Look for ASN.1 style data?
	 ?. Look for CRCs
	'''
	
	#: Does analyzer support asParser()
	supportParser = False
	#: Does analyzer support asDataElement()
	supportDataElement = True
	#: Does analyzer support asCommandLine()
	supportCommandLine = False
	#: Does analyzer support asTopLevel()
	supportTopLevel = True
	
	def __init__(self):
		pass
	
	def locateStrings(self, data):
		strs = []
		for match in re.finditer(r"[\n\r\ta-zA-Z0-9,./<>\?;':\"\[\]\\\{\}|=\-+_\)\(*&^%$#@!~`]{3,}\0*", data):
			strs.append(_Node('str', match.start(), match.end(), match.group(0)))
		
		return strs
	
	def locateStringLengths(self, strs, data):
		lengths = []
		
		for s in strs:
			length = len(s.value)
			lengthL16 = struct.pack("H", length)
			lengthL32 = struct.pack("I", length)
			lengthB16 = struct.pack("!H", length)
			lengthB32 = struct.pack("!I", length)
			
			first2 = data[s.startPos - 2:s.startPos]
			first4 = data[s.startPos - 4:s.startPos]
			
			if first2 == lengthL16:
				obj = _Node('len', s.startPos - 2, s.startPos, length)
				obj.endian = 'little'
				obj.lengthOf = s
				lengths.append(obj)
			elif first2 == lengthB16:
				obj = _Node('len', s.startPos - 2, s.startPos, length)
				obj.endian = 'big'
				obj.lengthOf = s
				lengths.append(obj)
			elif first4 == lengthL32:
				obj = _Node('len', s.startPos - 4, s.startPos, length)
				obj.endian = 'little'
				obj.lengthOf = s
				lengths.append(obj)
			elif first4 == lengthB32:
				obj = _Node('len', s.startPos - 4, s.startPos, length)
				obj.endian = 'big'
				obj.lengthOf = s
				lengths.append(obj)
		
		return lengths
	
	def locateCompressedSegments(self, data):
		pass

	def analyzeBlob(self, data):
		pass

	def asDataElement(self, parent, args, dataBuffer):
		'''
		Called when Analyzer is used in a data model.
		
		Should return a DataElement such as Block, Number or String.
		'''
		raise Exception("asDataElement not supported")
	
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
		raise Exception("asTopLevel not supported")
	