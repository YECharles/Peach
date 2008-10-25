
'''
Convert WireShark PDML files into Fuzzers

@author: Michael Eddington
@version: $Id$
'''

#
# Copyright (c) 2007 Michael Eddington
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

import sys, struct, re
from Ft.Xml import Parse

def debug(str):
	sys.stderr.write("debug: %s\n" % str)

#pdml/packet/proto
# method

# 1. Check for children, if we have them make block and recurse
# 2. Look for value show attribute and see if it contains a sub portion of the
#    data (treat this different)
# 3. Look for items labled "len" or "length" and try and match them up
# 4. Optionally look at RFC's and try and match things up

class PeachShark:
	
	def __init__(self):
		self._currentPos = 0
		self._regexIp = re.compile("^\d+\.\d+\.\d+\.\d+$")
		self._regexFlagBit1 = re.compile("^(\.*)(\d+)(\.*)")
		self._relations = {}
	
	def inStr(self, str, values):
		str = str.lower()
		for value in values:
			if str.find(value) > -1:
				#debug("found str")
				return True
		
		#debug("No: %s" % str)
		return False
	
	def findSizeRelation(self, sizeNode, node):
		# We know two things:
		#
		# 1. Sizes always come first
		# 2. It will be the size of something :P
		#
		size = self.findSizeGetSize(node)
		
		for child in node.childNodes:
			checkSize = int(child.getAttributeNS(None, 'size'))
			
			if checkSize == size:
				return child
			
			ret = self.findSizeRelation(sizeNode, child)
			if ret != None:
				return ret
		
		sibling = node.nextSibling
		while sibling != None:
			checkSize = int(sibling.getAttributeNS(None, 'size'))
			
			if checkSize == size:
				return sibling
			
			ret = self.findSizeRelation(sizeNode, sibling)
			if ret != None:
				return ret
			
			sibling = sibling.nextSibling
		
		return None
		
	def findSizes(self, nodes):
		
		if nodes == None:
			return []
		
		findValues = ["length", "size"]
		sizeNodes = []
		
		for node in nodes:
			if node == None:
				continue
			
			name = node.getAttributeNS(None, 'name')
			show = node.getAttributeNS(None, 'show')
			showName = node.getAttributeNS(None, 'showname')
			
			if self.inStr(show, findValues) or self.inStr(showName, findValues) or self.inStr(name, findValues):
				debug("findSizes(): Found size: %s" % name)
				sizeNodes.append(node)
			
			for n in self.findSizes(node.childNodes):
				sizeNodes.append(n)
		
		return sizeNodes
	
	def findSizeGetSize(self, node):
		
		try:
			return int(node.getAttributeNS(None, 'show'))
		except:
			pass
		
		return int(re.compile(r"(\d+)").search(node.getAttributeNS(None, 'show')).group(1))
	

	def findSizeRelationCheckSelf(self, node):
		'''
		Check if parent - me + prior siblings == size
		'''
		
		parentSize = int(node.parentNode.getAttributeNS(None, 'size'))
		sizeUptoMe = int(node.getAttributeNS(None, 'size'))
		size = self.findSizeGetSize(node)
		
		sibling = node.previousSibling
		while sibling != None:
			sizeUptoMe += int(sibling.getAttributeNS(None, 'size'))
			sibling = sibling.previousSibling
			
		if (parentSize - sizeUptoMe) == size:
			return True
		else:
			print "Nope: ParentSize: %d - SizeUptoMe: %d -- Size: %d" % (parentSize, sizeUptoMe, size)
	
	def findSizeRelations(self, nodes):
		
		debug("Finding relations")
		
		sizeNodes = self.findSizes(nodes)
		
		for node in sizeNodes:
			debug("findSizeRelations()...")
			if self.findSizeRelationCheckSelf(node):
				debug("findSizeRelations: Found relation: %s and %s" % (node.getAttributeNS(None, 'name'), node.parentNode.getAttributeNS(None, 'name')))
				self._relations[node] = node.parentNode
			
			else:
				ret = self.findSizeRelation(node, nodes[0].parentNode)
				if ret != None:
					debug("findSizeRelations: Found relation: %s and %s" % (node.getAttributeNS(None, 'name'), ret.getAttributeNS(None, 'name')))
					self._relations[node] = ret
		
	
	def removeTextNodes(self, node):
		
		for child in node.childNodes:
			if child.nodeName == '#text':
				node.removeChild(child)
			else:
				self.removeTextNodes(child)

	def peachNode(self, node, tabCount, size, parent):
		
		if node.nodeName == '#text':
			return '', 0, 0
		
		tabs = '\t' * tabCount
		name = node.getAttributeNS(None, 'name')
		show = node.getAttributeNS(None, 'show')
		showName = node.getAttributeNS(None, 'showname')
		size = int(node.getAttributeNS(None, 'size'))
		pos = int(node.getAttributeNS(None, 'pos'))
		ret = ''
		
		# This should be prior sibling, not parent!!
		if parent != None:
			parentPos = int(parent.getAttributeNS(None, 'pos'))
			parentSize = int(parent.getAttributeNS(None, 'size'))
		else:
			parentPos = -1
			parentSize = -1
		
		self._currentPos = pos
		
		if size == 0:
			#print "Size == 0: ", node.getAttributeNS(None, 'size')
			return '', 0, 0
		
		if tabCount == 0:
			# Do this just once
			self.findSizeRelations([node])
			
			if name.find('-'):
				newName = ''
				for n in name.split('-'):
					newName += n[:1].upper() + n[1:]
				name = newName
			
			self._groupName = 'group%s' % (name[:1].upper() + name[1:])
			self._genName = 'gen%s' % (name[:1].upper() + name[1:])
			
			name = node.getAttributeNS(None, 'name')
		
		ret += tabs + '# %s (%s, %s)\n' % (name, show, showName)
		
		if len(node.childNodes) > 0:
			
			curPos = pos
			sizeOfChildren = 0
			
			if tabCount == 0:
				ret += '%s = Block([\n' % self._genName
			else:
				ret += tabs + 'Block([\n'
			
			for child in node.childNodes:
				
				sibling = child.nextSibling
				if sibling != None:
					siblingPos = int(sibling.getAttributeNS(None, 'pos'))
					siblingSize = int(sibling.getAttributeNS(None, 'size'))
					childPos = int(child.getAttributeNS(None, 'pos'))
					childSize = int(child.getAttributeNS(None, 'size'))
					
					if siblingPos == childPos and siblingSize < childSize:
						debug("Found that crazy stuff" + child.getAttributeNS(None, 'name'))
						ret += tabs + "\t# Skipping %s, same as following fields\n" % child.getAttributeNS(None, 'name')
						continue
				
				childShow = child.getAttributeNS(None, 'show')
				
				#print "Child: %s" % childShow
				
				childRet, childSize, childPos = self.peachNode(child, tabCount + 1, size, node)
				
				childPos = int(childPos)
				childSize = int(childSize)
				
				#print "Child: %s, %d, %d" % (childShow, childPos, childSize)
				
				if childSize == 0:
					continue
				
				if int(childPos) == pos + int(sizeOfChildren):
					ret += childRet
					
				else:
					valueHex = node.getAttributeNS(None, 'value')
					value = self.hex2bin(valueHex)
					
					# Locate "extra" bits not covered by children and
					# add them in.  Maybe we should fuzz this too?
					if curPos < childPos:
						if len(valueHex) >= (childPos-pos)*2:
							ret += tabs + "\t# Found some extra bits...\n"
							ret += tabs + "\tStaticBinary('''" + valueHex[(curPos-pos)*2:(childPos-pos)*2] + "'''),\n"
						else:
							ret += tabs + "\t# Found some extra bits, guessing they are z3r0\n"
							ret += tabs + "\tStaticBinary('00'*%d),\n\n" % ((childPos-pos) - (curPos-pos))
					
					ret += childRet
				
				sizeOfChildren += childSize
				curPos = childPos + childSize
			
			#if sizeOfChildren != size:
			#	raise "Size not match %d != %d" % (size, sizeOfChildren)
			
			if tabCount == 0:
				ret += tabs + '\t])\n'
				
				name = self._genName[3:]
			
			else:
				ret += tabs + '\t]),\n'
			
		else:
			
			type = self.figureType(node)
			valueHex = node.getAttributeNS(None, 'value')
			show = node.getAttributeNS(None, 'show')
			value = self.hex2bin(valueHex)
			
			if type != 'bit_flag':
				if node.previousSibling != None:
					previousSiblingPos = int(node.previousSibling.getAttributeNS(None, 'pos'))
					previousSiblingSize = int(node.previousSibling.getAttributeNS(None, 'size'))
					
					if pos == previousSiblingPos and size == previousSiblingSize:
						debug("node same position and size of previousSibling")
						return '', 0, 0
			
			#ret += " [%s] " % type
			
			if type.find('str') > -1:
				# TODO: We should take into account that this string
				#       may be fixed in size as well as different lengths.
				
				value = value.replace('\n', '\\n')
				value = value.replace('\r', '\\r')
				value = value.replace('\t', '\\t')
				value = value.replace('\0', '\\0')
				
				if type == 'str':
					# regular string
					ret += tabs + ("WithDefault(%s.addNewGroup(), '''%s''', StringTokenFuzzer(None, '''%s''')),\n" % (self._groupName, value, value))
				
				elif type == 'p_str':
					# Padded string
					ret += tabs + ("WithDefault(%s.addNewGroup(), '''%s''', FixedLengthString(None, StringTokenFuzzer(None, '''%s'''), %d, '\\0'),\n" % (self._groupName, value, value, size))
				
				elif type == 'w_str':
					# wchar string
					
					# TODO: More advanced wchar tests! (high bit stuff, odd byte length, etc)
					
					ret += tabs + ("WithDefault(%s.addNewGroup(), '''%s''', StringTokenFuzzer(None, '''%s''')).setTransformer(WideChar()),\n" % (self._groupName, value, value))
				
				elif type == 'p_w_str':
					# padded wchar string
					ret += tabs + ("WithDefault(%s.addNewGroup(), '''%s''', FixedLengthString(None, StringTokenFuzzer(None, '''%s'''), %d, '\\0')),\n" % (self._groupName, value, value, size))
			
			elif type == 'byte' or type == 'uint8':
				ret += tabs + ("AsInt8(%s.addNewGroup(), WithDefault(None, 0x%s, List(None, range(255))),0,0),\n" % (self._groupName, valueHex))
			
			elif type == 'int16':
				ret += tabs + ("AsInt16(%s.addNewGroup(), WithDefault(None, 0x%s, BadNumbers16()),1,1),\n" % (self._groupName, valueHex))
			elif type == 'uint16':
				ret += tabs + ("AsInt16(%s.addNewGroup(), WithDefault(None, 0x%s, BadNumbers16()),0,1),\n" % (self._groupName, valueHex))
			elif type == 'n_int16':
				ret += tabs + ("AsInt16(%s.addNewGroup(), WithDefault(None, 0x%s, BadNumbers16()),1,0),\n" % (self._groupName, valueHex))
			elif type == 'n_uint16':
				ret += tabs + ("AsInt16(%s.addNewGroup(), WithDefault(None, 0x%s, BadNumbers16()),0,0),\n" % (self._groupName, valueHex))
			
			elif type == 'int32':
				ret += tabs + ("AsInt32(%s.addNewGroup(), WithDefault(None, 0x%s, BadNumbers()),1,1),\n" % (self._groupName, valueHex))
			elif type == 'uint32':
				ret += tabs + ("AsInt32(%s.addNewGroup(), WithDefault(None, 0x%s, BadNumbers()),0,1),\n" % (self._groupName, valueHex))
			elif type == 'n_int32':
				ret += tabs + ("AsInt32(%s.addNewGroup(), WithDefault(None, 0x%s, BadNumbers()),1,0),\n" % (self._groupName, valueHex))
			elif type == 'n_uint32':
				ret += tabs + ("AsInt32(%s.addNewGroup(), WithDefault(None, 0x%s, BadNumbers()),0,0),\n" % (self._groupName, valueHex))
			
			elif type == 'blob':
				ret += tabs + "StaticBinary('" + valueHex + "'),\n"
			
			elif type == 'ip':
				ret += tabs + "WithDefault(%s.addNewGroup(), '%s', BadIpAddress()).setTransformer(Ipv4StringToOctet()),\n" % ( self._groupName, show )
			
			elif type == 'n_ip':
				ret += tabs + "WithDefault(%s.addNewGroup(), '%s', BadIpAddress()).setTransformer(Ipv4StringToNetworkOctet()),\n" % ( self._groupName, show )
			
			elif type == 'bit_flag':
				# TODO: Handle flags!
				
				if node.previousSibling == None:
					# First flag, lets do it!
					
					offsets = []
					bits = []
					shownames = []
					
					offset, bit = self.getFlagBits(node)
					
					offsets.append(offset)
					bits.append(bit)
					shownames.append(showName)
					
					sibling = node.nextSibling
					while sibling != None:
						offset, bit = self.getFlagBits(sibling)
						
						offsets.append(offset)
						bits.append(bit)
						shownames.append(sibling.getAttributeNS(None, 'showname'))
						
						sibling = sibling.nextSibling
					
					# Now output Flags generator
					
					ret += tabs + "Flags(%s.addNewGroup(), [\n" % self._groupName
					
					for offset in offsets:
						ret += tabs + "\t%d,\n" % offset
					
					ret += tabs + "\t],[\n"
					
					for bit in bits:
						if bit == 1:
							ret += tabs + "\tBit(),\n"
						else:
							ret += tabs + "\tNumberLimiter(None, BadNumbers(), 0, %d),\n" %  ((2**bit)-1)
					
					ret += tabs + "\t]),\n"
					
				#if node.nextSibling == None:
				#	valueHex = parent.getAttributeNS(None, 'value')
				#	ret += "\n"
				#	ret += tabs + "# TODO: Handle flags!\n"
				#	ret += tabs + "StaticBinary('" + valueHex + "'),\n"
				
			else:
				raise "Unknown type: %s" % type
		
		return ret + '\n', size, pos
	
	def hex2bin(self, h):
		'''
		Convert hex string to binary string
		'''
		ret = ''
		for cnt in range(0, len(h), 2):
			ret += chr(int(h[cnt:cnt+2],16))
		
		return ret
	
	def isWideString(self, str):
		'''
		Is this a wchar string?
		'''
		
		# Wide chars should always have even string
		# length
		if len(str) < 4 or len(str) % 2 != 0:
			return False
		
		for i in range(0, len(str), 2):
			c = str[i]
			c2 = str[i+1]
			
			# Assume we don't actually have characters that
			# require two bytes to display.  So second byte
			# should always be NULL
			if c2 != '\0':
				return False
			
			o = ord(c)
			if o < 32 or o > 126:
				if c == '\n' or c == '\r' or c == '\t':
					continue
				
				return False
		
		return True
	
	def isPaddedWideString(self, str):
		'''
		Is this a wchar string with nulls at the end?
		'''
		
		# Wide chars should always have even string
		# length
		if len(str) < 4 or len(str) % 2 != 0:
			return False
		
		if str[-1] != '\0' or str[-2] != '\0':
			return False
		
		for i in range(0, len(str), 2):
			c = str[i]
			c2 = str[i+1]
			
			# Assume we don't actually have characters that
			# require two bytes to display.  So second byte
			# should always be NULL
			if c2 != '\0':
				return False
			
			o = ord(c)
			if o < 32 or o > 126:
				if c == '\n' or c == '\r' or c == '\t' or c == '\0':
					continue
				
				return False
		
		return True
	
	def isString(self, str):
		'''
		Is this a char string?
		'''
		
		if len(str) < 3:
			return False
		
		for c in str:
			o = ord(c)
			if o < 32 or o > 126:
				if c == '\n' or c == '\r' or c == '\t':
					continue
				
				return False
		
		#debug("isString('%s'): True" % str)
		
		return True

	def isPaddedString(self, str):
		'''
		Is this a char string with nulls at the end?
		'''
		
		if len(str) < 3:
			#debug("to small")
			return False
		
		if str[-1] != '\0':
			#debug("no null term")
			return False
		
		for c in str:
			o = ord(c)
			if o < 32 or o > 126:
				if c == '\n' or c == '\r' or c == '\t' or c == '\0':
					continue
				
				debug("odd char [%d]" % o)
				return False
		
		return True
	
	def getFlagBits(self, node):
		'''
		Checks out the showname field to see if we can determin
		the number of bits this flag is and it's offset in the packet.
		'''
		# .... ...1 .... .... = Recursion desired: Do query recursively
		
		show = node.getAttributeNS(None, 'showname')
		
		#debug("flag str (initial): [%s]" % show)
		
		# remove spaces
		show = show.replace(' ', '')
		
		# Get dots and numbers
		result = self._regexFlagBit1.match(show)
		firstDots = result.group(1)
		number = result.group(2)
		lastDots = result.group(3)
		
		offset = len(firstDots)
		bits = len(number)
		
		#debug("flag str: [%s]" % show)
		#debug("offset: %d - bits: %s - remander: %d" % (offset, bits, len(lastDots)))
		
		if (len(firstDots) + len(number) + len(lastDots)) % 2 != 0:
			debug("getFlagBits(): Something fishy about this!!! %d" % (len(firstDots) + len(number) + len(lastDots)))
		
		return offset, bits
	
	def figureType(self, node):
	
		# Try and figure out our type, number, string, etc.
	
		show = node.getAttributeNS(None, 'show')
		showName = node.getAttributeNS(None, 'showname')
		value = self.hex2bin(node.getAttributeNS(None, 'value'))
		valueHex = node.getAttributeNS(None, 'value')
		size = int(node.getAttributeNS(None, 'size'))
		pos = int(node.getAttributeNS(None, 'pos'))
		parentPos = int(node.parentNode.getAttributeNS(None, 'pos'))
		parentSize = int(node.parentNode.getAttributeNS(None, 'size'))
		
		#print "Show: [%s], valueHex: [%s], size: %d" % (show, valueHex, size)
	
		# If just compar pos == parentPos we will get the first
		# child.  Should also check next child and size
		if pos == parentPos and parentSize == size:
			# A flag will have the same position as it's parent
			# parent will have size of 1
			#print "bit_flag: pos: %d parentPos: %d" % (pos, parentPos)
			#debug("show: %s - showName: %s" % (show, showName))
			return 'bit_flag'
		#else:
		#	print "pos: %d parentPos: %d" % (pos, parentPos)
	
		if len(value) > 2 and value.isalnum() and not show.isdigit():
			return 'str'
		
		elif self._regexIp.match(show) != None and size == 4:
			# ip address
			ip1, ip2, ip3, ip4 = show.split('.')
			
			#debug("ip: %s - %s - %s - %s" % (show, ip1, valueHex[len(valueHex)-2:], valueHex))
			if int(ip1) == int(valueHex[6:], 16) and int(ip2) == int(valueHex[4:6], 16) and int(ip3) == int(valueHex[2:4], 16) and int(ip4) == int(valueHex[:2], 16):
				return 'n_ip'
			
			if int(ip1) == int(valueHex[:2], 16):
				return 'ip'
		
		elif show[:2] == "0x":
			
			# Figure if we are little or big endian
			
			showHex = show[2:]
			
			if showHex == valueHex or int(showHex, 16) == int(valueHex, 16):
				# little
				if size == 1:
					return 'uint8'
				
				if size == 2:
					return 'uint16'
					
				elif size == 4:
					return 'uint32'
				
				elif size == 8:
					return 'uint64'
			
			#debug("bigBalue: [%s][%s]" % (valueHex, show))
			bigValue = struct.unpack("!H", value)[0]
			if int(bigValue) == int(showHex, 16):
				if size == 1:
					return 'n_uint8'
				
				if size == 2:
					return 'n_uint16'
					
				elif size == 4:
					return 'n_uint32'
				
				elif size == 8:
					return 'n_uint64'
	
		
		elif not show.isdigit() and self.isWideString(value):
			return 'w_str'
		
		elif not show.isdigit() and self.isPaddedWideString(value):
			return 'p_w_str'
		
		elif not show.isdigit() and self.isString(value):
			return 'str'
		
		elif not show.isdigit() and self.isPaddedString(value):
			return 'p_str'
		
		elif show.isdigit() or (len(showName) == 0 and size <= 4):
			
			cnt = len(valueHex)
			
			if size == 1:
				# Byte I bet
				return 'byte'
				
			elif size == 2:
				# Maybe 16 bit int?
				
				try:
					show = int(show)
				except:
					show = 0
				
				try:
					val = struct.unpack('H', value)[0]
					if int(val) == show:
						return 'uint16'
					
					val = struct.unpack('h', value)[0]
					if val == show:
						return 'int16'
					
					val = struct.unpack('!H', value)[0]
					if val == show:
						return 'n_int16'
					
					val = struct.unpack('!h', value)[0]
					if val == show:
						return 'n_uint16'
				
				except struct.error:
					pass
				
				return 'n_uint16'
			
			elif size == 4:
				# Maybe 32 bit int?
				if struct.unpack('I', value)[0] == show:
					return 'uint32'
				
				elif struct.unpack('i', value)[0] == show:
					return 'int32'
				
				elif struct.unpack('!I', value)[0] == show:
					return 'n_int32'
				
				return 'n_uint32'
	
		return 'blob'

# ########################################################################

sys.stderr.write("\n]] PeachShark\n\n")
sys.stderr.write("Loading pdml: %s\n\n" % sys.argv[1])

name = sys.argv[1]
doc = Parse(sys.argv[1])

node = doc.xpath('descendant::proto[@name="%s"]' % sys.argv[2])[0]
#nodes = doc.xpath('descendant::proto')

shark = PeachShark()

top = """
# --// Auto generated by PeachShark //--

import sys

# Change to point to Peach if needed
sys.path.append("c:/projects/peach")

from Peach.group import *
from Peach.Generators.block import *
from Peach.Generators.data import *
from Peach.Generators.dictionary import *
from Peach.Transformers.encode import *
from Peach.Protocols	import *
from Peach.Publishers	import *
from Peach.script 		import *

"""

groups = []
blocks = {}
gens = []

shark.removeTextNodes(node.parentNode)

ret, s, p = shark.peachNode(node, 0, node.getAttributeNS(None, 'size'), None)
top += '%s = GroupSequence([], "%s")\n' % (shark._groupName, shark._groupName)
blocks[shark._genName] = ret
groups.append(shark._groupName)
gens.append(shark._genName)

sibling = node.nextSibling
while sibling != None:

	shark.removeTextNodes(sibling.parentNode)
	ret, s, p = shark.peachNode(sibling, 0, sibling.getAttributeNS(None, 'size'), None)	
	top += '%s = GroupSequence([], "%s")\n' % (shark._groupName, shark._groupName)
	blocks[shark._genName] = ret
	gens.append(shark._genName)
	groups.append(shark._groupName)
	
	sibling = sibling.nextSibling

print top

for gen in gens:
	print blocks[gen]

print "group = GroupSequence(["
for group in groups:
	print "\t%s," % group
print "\t], 'group')\n"

print "gen = Block(["
for gen in gens:
	print "\t%s," % gen
print "\t])\n"

print """

if __name__ == "__main__":
	print "\\n]] %s Fuzzer by PeachShark\\n"
	
	if len(sys.argv) == 2 and sys.argv[1] == 'count':
		count = 0
		try:
			while True:
				group.next()
				count += 1
		except:
			pass
		
		print "\\nTotal of %%d test cases" %% count
		sys.exit(0)
	
	if len(sys.argv) < 4:
		print "Syntax: fuzzer.py count"
		print "Syntax: fuzzer.py <udp|tcp> <ip> <port> [test #]\\n"
		sys.exit(0)
	
	prot = sys.argv[1]
	ip = sys.argv[2]
	port = sys.argv[3]
	
	sys.argv.remove(prot)
	sys.argv.remove(ip)
	sys.argv.remove(port)
	
	protocol = None
	if prot == 'tcp':
		protocol = null.NullStdout(tcp.Tcp(ip, int(port)), gen)
	elif prot == 'udp':
		protocol = null.NullStdout(udp.Udp(ip, int(port)), gen)
	else:
		print "Unknown protocol, udp or tcp please"
		sys.exit(-1)
		
	print "Running fuzzer on %%s:%%s via %%s\\n" %% (ip, port, prot)
	
	Script(protocol, group, 0.25).go()

# end

""" % (name)

# end
