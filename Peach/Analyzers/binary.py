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

sys.path.append("c:/peach")

from Peach.Engine.dom import *
from Peach.Engine.common import *
from Peach.analyzer import Analyzer

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
		for match in re.finditer(r"[\n\r\ta-zA-Z0-9,./<>\?;':\"\[\]\\\{\}|=\-+_\)\(*&^%$#@!~`]{3,}\0?", data):
			strs.append(_Node('str', match.start(), match.end(), match.group(0)))
		
		return strs
	
	def locateStringLengths(self, strs, data):
		lengths = {}
		
		for s in strs:
			length = len(s.value)
			lengthL16 = struct.pack("H", length)
			lengthL32 = struct.pack("I", length)
			lengthB16 = struct.pack("!H", length)
			lengthB32 = struct.pack("!I", length)
			
			first2 = data[s.startPos - 2:s.startPos]
			first4 = data[s.startPos - 4:s.startPos]
			
			# Always check larger # first in case 0x00AA :)
			if first4 == lengthL32:
				obj = _Node('len', s.startPos - 4, s.startPos, length)
				obj.endian = 'little'
				obj.lengthOf = s
				obj.size = 32
				lengths[s] = obj
			elif first4 == lengthB32:
				obj = _Node('len', s.startPos - 4, s.startPos, length)
				obj.endian = 'big'
				obj.lengthOf = s
				obj.size = 32
				lengths[s] = obj
			elif first2 == lengthL16:
				obj = _Node('len', s.startPos - 2, s.startPos, length)
				obj.endian = 'little'
				obj.lengthOf = s
				obj.size = 16
				lengths[s] = obj
			elif first2 == lengthB16:
				obj = _Node('len', s.startPos - 2, s.startPos, length)
				obj.endian = 'big'
				obj.lengthOf = s
				obj.size = 16
				lengths[s] = obj
		
		return lengths
	
	def locateCompressedSegments(self, data):
		pass

	def analyzeBlob(self, data):
		'''
		Will analyze a binary blob and return a Block
		data element containing the split up blob.
		'''
		
		# 1. First we locate strings
		strs = self.locateStrings(data)
		
		# 2. Now we check for lengths
		lengths = self.locateStringLengths(strs, data)
		
		# 3. Now we need to build up our DataElement DOM
		root = Block(None, None)
		pos = 0
		
		for s in strs:
			
			## Check and see if we need a Blob starter
			
			startPos = s.startPos
			if s in lengths:
				startPos = lengths[s].startPos
			
			print "pos:",pos
			print "startPos:", startPos
			
			if startPos > pos:
				# Need a Blob filler
				b = Blob(None, None)
				b.defaultValue = data[pos:startPos]
				
				root.append(b)
			
			## Now handle what about length?
			
			stringNode = String(None, None)
			numberNode = None
			
			if s in lengths:
				l = lengths[s]
				
				numberNode = Number(None, None)
				numberNode.size = l.size
				numberNode.endian = l.endian
				numberNode.defaultValue = str(n.value)
				root.append(numberNode)
				
				relation = Relation()
				relation.type = "size"
				relation.of = stringNode.name
				
				numberNode.append(relation)
				numberNode.relations.append(relation)
				
				relation = Relation()
				relation.type = "size"
				relation.From = numberNode.name
				
				stringNode.append(relation)
				stringNode.relations.append(relation)
			
			if s.value[-1] == "\0":
				stringNode.defaultValue = s.value[:-1]
				stringNode.nullTerminated = True
			
			else:
				stringNode.defaultValue = s.value
			
			root.append(stringNode)
			
			pos = s.endPos
		
		# Finally, we should see if we need a trailing blob...
		if pos < (len(data)-1):
			
			b = Blob(None, None)
			b.defaultValue = data[pos:]
			root.append(b)
		
		return root

	def asDataElement(self, parent, args, dataBuffer):
		'''
		Called when Analyzer is used in a data model.
		
		Should return a DataElement such as Block, Number or String.
		'''
		dom = self.analyzeBlob(dataBuffer)
		
		# Replace parent with new dom
		
		parentOfParent = parent.parent
		dom.name = parent.name
		
		indx = parentOfParent.index(parent)
		del parentOfParent[parent.name]
		parentOfParent.insert(indx, dom)
		
		# now just cross our fingers :)
	
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


if __name__ == "__main__":

	import Ft.Xml.Domlette
	from Ft.Xml.Domlette import Print, PrettyPrint
	
	fd = open("sample.bin", "rb+")
	data = fd.read()
	fd.close()
	
	b = Binary()
	dom = b.analyzeBlob(data)
	data2 = dom.getValue()
	
	if data2 == data:
		print "THEY MATCH"
	else:
		print repr(data2)
		print repr(data)
	
	dict = {}
	doc  = Ft.Xml.Domlette.NonvalidatingReader.parseString("<Peach/>", "http://phed.org")
	xml = dom.toXmlDom(doc.rootNode.firstChild, dict)
	PrettyPrint(doc, asHtml=1)

# end
