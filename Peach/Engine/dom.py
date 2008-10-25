
'''
Peach 2 DOM.  Peach XML files are parsed into an object model using
these classes.  The document object is Peach and all objects extend
from Element.

@author: Michael Eddington
@version: $Id$
'''

#
# Copyright (c) 2007-2008 Michael Eddington
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

PROFILE = False

if PROFILE:
	print " --- INCOMING PROFILING ENABLED ---- "
	import profile


import sys, re, types, new, base64, time
from Peach.Transformers.encode import WideChar
from Peach import Transformers
from Peach.Engine.common import *
from Peach.Engine.engine import Engine
import Peach
PeachModule = Peach
import Ft.Xml.Domlette
from Ft.Xml.Domlette import Print, PrettyPrint

if Engine.nativeDeepCopy:
	from cDeepCopy import deepcopy

else:
	from copy import deepcopy

try:
	import Ft.Xml.Domlette
	from Ft.Xml.Catalog import GetDefaultCatalog
	from Ft.Xml.InputSource import InputSourceFactory
	from Ft.Lib.Resolvers import SchemeRegistryResolver
	from Ft.Lib import Uri
	from Ft.Xml import Parse
except:
	print "\nError loading 4Suite XML library.  This library"
	print "can be installed from the dependencies folder or"
	print "downloaded from http://4suite.org/.\n\n"
	raise

class Empty:
	pass

def PeachDeepCopy(self, memo):
	'''
	Copying objects in our DOM is a crazy business.  Here we
	try and help out as much as we can.
	'''
	
	# Copy procedures
	#
	#  - Only copy children array (_children)
	#  - Remove array and re-add children via append
	#  - Set our __deepcopy__ attributes
	#  - Fixup our toXml functions
	
	node = self.node
	parent = self.parent
	me = getattr(self, '__deepcopy__')
	
	# Only copy _children
	if isinstance(self, ElementWithChildren):
		# Save children
		_childrenHash = self._childrenHash
		_children = self._children
		children = self.children
		
		# Null out children except for array
		self._childrenHash = None
		self.children = None
	
	# Null out 4Suite XML node (why do we keep this?)
	self.node = None
	self.parent = None
	delattr(self, '__deepcopy__')
	
	if self.elementType == 'block' or self.elementType == 'namespace':
		toXml = getattr(self, 'toXml')
		setattr(self, 'toXml', None)
	
	e = deepcopy(self, memo)
	e.__deepcopy__ = new.instancemethod(PeachDeepCopy, e, e.__class__)
	
	try:
		if e.elementType == 'block':
			e.toXml = new.instancemethod(BlockToXml, e, e.__class__)
			setattr(self, 'toXml', toXml)
		
		elif e.elementType == 'namespace':
			e.toXml = new.instancemethod(NamespaceToXml, e, e.__class__)
			setattr(self, 'toXml', toXml)
	except:
		print dir(e)
		raise
	
	if isinstance(self, ElementWithChildren):
		# Don't copy kids yet
		self._childrenHash = _childrenHash
		self._children = _children
		self.children = children
	
		# Fixup ElementWithChildren types
		# We need to try and keep things in order
		# and not have to many duplicated elements
		# GAR, this isn't working...
		children = e._children
		e._children = []
		e._childrenHash = {}
		e.children = Empty()
		
		for c in children:
			if isinstance(c, Element) and not hasattr(c, 'name'):
				c.name = "The Lost Element"
			e.append(c)
	
	self.node = node
	self.parent = parent
	setattr(self, '__deepcopy__', me)
	
	return e

class Element:
	'''
	Element in our template tree.
	'''
	
	__CurNameNum = 0	#: For generating unknown element names
	
	def __init__(self, name = None, parent = None):
		#: Name of Element, cannot include "."s
		self.name = name
		#: Parent of Element
		self.parent = parent
		#: If element has children
		self.hasChildren = False
		#: Type of this element
		self.elementType = None
		#: Fullname cache
		self.fullName = None
		
		self.node = None	#: Our XML node
		self.ref = None		#: The reference that made us, or None
		
		self.__deepcopy__ = new.instancemethod(PeachDeepCopy, self, self.__class__)
		
		if self.name == None or len(self.name) == 0:
			self.name = self.getUniqueName()
		
	def getElementsByType(self, type, ret = None):
		'''
		Will return an array all elements of a specific type
		in the tree starting with us.
		'''
		
		if ret == None:
			ret = []
		
		if isinstance(self, type):
			ret.append(self)
		
		return ret
	
	def getUniqueName():
		
		name = "Unknown Element %d" % Element.__CurNameNum
		Element.__CurNameNum += 1
		
		return name
	getUniqueName = staticmethod(getUniqueName)
	
	def getFullDataName(self):
		'''
		Return fully qualified name inside of data map
		'''
		
		return self.getFullnameInDataModel()
	
	def getRoot(self):
		'''
		Get the root of this DOM tree
		'''
		
		stack = []
		
		root = self
		stack.append(root)
		while root.parent != None and root.parent not in stack:
			root = root.parent
			stack.append(root)
		
		if root.parent != None and root.parent in stack:
			raise Exception("Error: getRoot found a recursive relationship! EEk!")
		
		return root
	
	def printDomMap(self, level = 0):
		'''
		Print out a map of the dom.
		'''
		print ("   "*level) + "- %s [%s](%s)" % (self.name, self.elementType, str(self)[-9:])
	
	def toXmlDom(self, parent, dict):
		'''
		Convert to an XML DOM object tree for use in xpath queries.
		'''
		
		owner = parent.ownerDocument
		if owner == None:
			owner = parent
		
		if hasattr(self, 'ref') and self.ref != None:
			node = owner.createElementNS(None, self.ref)
		else:
			node = owner.createElementNS(None, self.name)
		
		node.setAttributeNS(None, "elementType", self.elementType)
		node.setAttributeNS(None, "name", self.name)
		
		if hasattr(self, 'ref') and self.ref != None:
			self._setXmlAttribute(node, "ref", self.ref)
		if hasattr(self, 'defaultValue') and self.defaultValue != None:
			self._setXmlAttribute(node, "defaultValue", self.defaultValue)
		if hasattr(self, 'currentValue') and self.currentValue != None:
			self._setXmlAttribute(node, "currentValue", self.currentValue)
		if hasattr(self, 'value') and self.value != None:
			self._setXmlAttribute(node, "value", self.value)
		
		dict[node] = self
		dict[self] = node
		
		parent.appendChild(node)
		
		return node
	
	def toXmlDomLight(self, parent, dict):
		'''
		Convert to an XML DOM object tree for use in xpath queries.
		Does not include values (Default or otherwise)
		'''
		
		owner = parent.ownerDocument
		if owner == None:
			owner = parent
		
		if hasattr(self, 'ref') and self.ref != None:
			node = owner.createElementNS(None, self.ref)
		else:
			node = owner.createElementNS(None, self.name)
		
		node.setAttributeNS(None, "elementType", self.elementType)
		node.setAttributeNS(None, "name", self.name)
		
		if hasattr(self, 'ref') and self.ref != None:
			self._setXmlAttribute(node, "ref", self.ref)
		
		dict[node] = self
		dict[self] = node
		
		parent.appendChild(node)
		
		return node
	
	def _setXmlAttribute(self, node, key, value):
		'''
		Set an XML attribute with handling for UnicodeDecodeError.
		'''
		
		try:
			value = str(value)
			node.setAttributeNS(None, key, value)
		
		except UnicodeDecodeError:
			node.setAttributeNS(None, "%s-Encoded" % key, "base64")
			node.setAttributeNS(None, key, base64.b64encode(value))
	
	def _getXmlAttribute(self, node, key):
		'''
		Get an XML attribute with handling for UnicdeDecodeError.
		'''
		
		if not node.hasAttributeNS(None, key):
			return None
		
		value = str(node.getAttributeNS(None, key))
		if node.hasAttributeNS(None, "%s-Encoded" % key):
			value = base64.b64decode(value)
		
		return value
	
	def updateFromXmlDom(self, node, dict):
		'''
		Update our object based on an XML DOM object.
		All we are taking for now is defaultValue.
		'''
		
		if node.hasAttributeNS(None, 'defaultValue'):
			self.defaultValue = self._getXmlAttribute(node, "defaultValue")
			#print "updateFromXmlDom: Set defaultValue %s to %d bytes" % (self.name, len(self.defaultValue))
		
		if node.hasAttributeNS(None, 'currentValue'):
			self.currentValue = self._getXmlAttribute(node, "currentValue")
			#print "updateFromXmlDom: Set currentValue %s to %d bytes" % (self.name, len(self.currentValue))
		
		if node.hasAttributeNS(None, 'value'):
			self.value = self._getXmlAttribute(node, "value")
			#print "updateFromXmlDom: Set value %s to %d bytes" % (self.name, len(self.value))
	
	def compareTree(self, node1, node2):
		'''
		This method will compare two ElementWithChildren
		object tree's.
		'''
		
		if node1.name != node2.name:
			raise Exception("node1.name(%s) != node2.name(%s)" %(node1.name, node2.name))
		
		if node1.elementType != node2.elementType:
			raise Exception("Element types don't match [%s != %s]" % (node1.elementType, node2.elementType))

		if not isinstance(node1, DataElement):
			return True
		
		if len(node1) != len(node2):
			raise Exception("Lengths do not match %d != %d" % (len(node1), len(node2)))
		
		if len(node1._childrenHash) > len(node1._children):
			raise Exception("Node 1 length of hash > list")
		
		if len(node2._childrenHash) > len(node2._children):
			print "node1.name", node1.name
			print "node2.name", node2.name
			print "len(node1)", len(node1)
			print "len(node2)", len(node2)
			print "len(node1._childrenHash)", len(node1._childrenHash)
			print "len(node2._childrenHash)", len(node2._childrenHash)
			for c in node1._childrenHash.keys():
				print "node1 hash key:", c
			for c in node2._childrenHash.keys():
				print "node2 hash key:", c
			raise Exception("Node 2 length of hash > list")
		
		for (key,value) in node1._childrenHash.iteritems():
			if value not in node1._children:
				raise Exception("Error: %s not found in node1 list" % key)
		
		for key,value in node2._childrenHash.iteritems():
			if value not in node2._children:
				raise Exception("Error: %s not found in node2 list" % key)
		
		for i in range(len(node1)):
			if not self.compareTree(node1[i], node2[i]):
				return False
		
		return True
	
	def copy(self, parent):
		## For testing purposes only
		#newSelf2 = copy.deepcopy(self)
		#self._FixParents(newSelf2, parent)
		#newSelf = newSelf2
		
		newSelf = deepcopy(self)
		self._FixParents(newSelf, parent)
		
		## For testing purposes only
		#gc.collect()
		#if not self.compareTree(self, newSelf):
		#	raise Exception("Copy didn't match")
		
		return newSelf
	
	def _FixParents(self, start = None, parent = None):
		'''
		Walk down from start and fix parent settings on children
		'''
		#if hasattr(start, 'name'):
		#	print "--> _FixParents(%s)" % start.name
		#else:
		#	print "--> _FixParents(%s)" % repr(start)
		
		#print "_FixParents(%s): %s" % (start.name, parent.name)
		
		if start == None:
			start = self
		
		if parent != None:
			start.parent = parent
		
		if isinstance(start, ElementWithChildren):
			#for child in start._children:
			#	print "Child: ", repr(child)
			for child in start._children:
				self._FixParents(child, start)
		
		#print "<--"
	
	def getFullname(self):
		
		if self.fullName != None:
			return self.fullName
		
		name = self.name
		node = self
		
		while node.parent != None:
			
			# We need to handle namespaces here!!!
			# TODO
			node = node.parent
			name = "%s.%s" % (node.name, name)
		
		return name
		
	def nextSibling(self):
		'''
		Get the next sibling or return None
		'''
		
		if self.parent == None:
			return None
		
		# First determin our position in parents children
		ourIndex = self.parent._children.index(self)
		
		# Check for next child
		if len(self.parent._children) <= (ourIndex+1):
			return None
		
		#sys.stderr.write("nextSibling: %d:%d\n" % (len(self.parent), (ourIndex+1)))
		return self.parent._children[ourIndex+1]
	
	def previousSibling(self):
		'''
		Get the prior sibling or return None
		'''
		
		if self.parent == None:
			return None
		
		# First determin our position in parents children
		ourIndex = self.parent._children.index(self)
		
		# Check for next child
		if ourIndex == 0:
			return None
		
		return self.parent._children[ourIndex-1]
	
	#def getDefaultValue(self):
	#	return self.transformer.realTransform(self.getDefaultRawValue())
	#
	#def getDefaultRawValue(self):
	#	return self.defaultValue

	def _setAttribute(self, node, name, value, default = None):
		'''
		Set an attribute on an XML Element.  We only set the
		attribute in the following cases:
		
			1. We have no attached xml node or self.ref == None
			2. We have a node, and the node has that attribute
			3. The value is not None
		
		'''
		
		# Simplify the XML by not adding defaults
		if value == default or value == None:
			return
		
		node.setAttributeNS(None, name, str(value))
	
	GuidRegex = re.compile('^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
	def _xmlHadChild(self, child):
		'''
		Verify that we should serialize child node.  Checks
		to see if we have an attached xml node and that xml
		node has the child.  If we don't have an attached
		xml node then say we should add child.
		'''
		
		return True


class ElementWithChildren(Element):
	'''
	Contains functions that cause Element to act as a
	hash table and array for children.  Also children can
	be accessed by name via self.children.name.
	'''
	
	def __init__(self, name = None, parent = None):
		Element.__init__(self, name, parent)
		self._children = []			#: List of children (in order)
		self._childrenHash = {}		#: Dicitonary of children (by name)
		self.children = Empty()		#: Children object, has children as attributes by name
		self.hasChildren = True
	
		
	def getElementsByType(self, type, ret = None):
		'''
		Will return array of a specific type
		in the tree starting with us.
		'''
		
		#print "getElementsByType: %s: %s" % (self.name, self.elementType)
		
		if ret == None:
			ret = []
		
		if isinstance(self, type):
			ret.append(self)
			
		for child in self:
			child.getElementsByType(type, ret)
		
		return ret
	
	def printDomMap(self, level = 0):
		'''
		Print out a map of the dom.
		'''
		print ""
		print ("   "*level) + "+ %s [%s](%s)" % (self.name, self.elementType, str(self)[-9:])
		
		for child in self:
			if isinstance(child, Element):
				child.printDomMap(level+1)
				
				if child.parent != self:
					raise Exception("Error: printDomMap: %s.parent != self : %s:%s " % (child.name, child.name, repr(child.parent)))
	
	def verifyDomMap(self):
		'''
		Verify parent child relationship across DOM Tree
		'''
		for child in self:
			if isinstance(child, Element):
				if child.parent != self:
					raise Exception("Error: verifyDomMap: %s.parent != self : %s:%s " % (child.name, child.name, repr(child.parent)))
			
			if isinstance(child, ElementWithChildren):
				child.verifyDomMap()
	
	def toXmlDom(self, parent, dict):
		'''
		Convert to an XML DOM boject tree for use in xpath queries.
		'''
		
		# Make sure there is a value to get
		if isinstance(self, DataElement):
			self.getValue()
		
		node = Element.toXmlDom(self, parent, dict)
		
		for child in self._children:
			#print ">> toXmlDom child: ", child
			child.toXmlDom(node, dict)
		
		return node
	
	def toXmlDomLight(self, parent, dict):
		'''
		Convert to an XML DOM boject tree for use in xpath queries.
		'''
		
		# Make sure there is a value to get
		if isinstance(self, DataElement):
			self.getValue()
		
		node = Element.toXmlDomLight(self, parent, dict)
		
		for child in self._children:
			#print ">> toXmlDom child: ", child
			child.toXmlDomLight(node, dict)
		
		return node
	
	def updateFromXmlDom(self, node, dict):
		'''
		Update our object based on an XML DOM object.
		All we are taking for now is defaultValue.
		'''
		
		Element.updateFromXmlDom(self, node, dict)
		
		if node.hasChildNodes():
			for child in node.childNodes:
				dict[child].updateFromXmlDom(child, dict)
	
	def setDefaults(self, data, dontCrack = False):
		'''
		Set data elements defaultValue based on a Data object.
		'''
		
		if data.fileName != None:
			
			if dontCrack:
				return
			
			print "[*] Cracking data from %s into %s" % (data.fileName, self.name)
			
			fd = open(data.fileName, "rb")
			stuff = fd.read()
			fd.close()
			
			parent = self.parent
			while parent.parent != None: parent = parent.parent
			
			cracker = PeachModule.Engine.incoming.DataCracker(parent)
			cracker.haveAllData = True
			
			if PROFILE:
				profile.runctx("cracker.crackData(self, stuff, \"setDefaultValue\")",
							   globals(), {"cracker":cracker, "self":self, "stuff":stuff})
			else:
				startTime = time.time()
				cracker.crackData(self, stuff, "setDefaultValue")
				print "[*] Total time to crack data: %.2f" % (time.time() - startTime)
				
				### Some debugging code
				### Use deepcopy and findby name
				#cnt = 0
				#while(1):
					#cnt += 1
					#cpy = self.copy(self.parent)
					#for c in cpy:
						#c.getRelationOfThisElement('count')
						##cPeach.getRootOfDataMap(c)
					
					#cpy.findDataElementByName("FileSize")

					#if cnt % 500 == 0:
						#print "."
				
				
				print "[*] Building relation cache"
				self.BuildRelationCache()
			
			return
		
		if data.expression != None:
			
			stuff = peachEval(data.expression)
			
			parent = self.parent
			while parent.parent != None: parent = parent.parent
			
			cracker = PeachModule.Engine.incoming.DataCracker(parent)
			cracker.haveAllData = True
			cracker.crackData(self, stuff, "setDefaultValue")
			
			return
		
		for field in data:
			obj = self
			
			for name in field.name.split('.'):
				
				if hasattr(obj.children, name):
					obj = getattr(obj.children, name)
				
				else:
					raise str("setDefaults(): Unable to locate field %s" % field.name)
			
			obj.currentValue = field.value
	
	#def getDefaultRawValue(self):
	#	
	#	if self.defaultValue != None:
	#		return self.defaultValue
	#	
	#	ret = ''
	#	for child in self._children:
	#		ret += child.getDefaultValue()
	#	
	#	return ret
	
	def append(self, obj):
		if obj in self._children:
			raise Exception("object already child of element")
		
		# If we have the key we need to replace it
		if self._childrenHash.has_key(obj.name):
			self[obj.name] = obj
			return
		
		# Otherwise add it at the end
		self._children.append(obj)
		if obj.name != None:
			self._childrenHash[obj.name] = obj
			setattr(self.children, obj.name, obj)
	
	def index(self, obj):
		return self._children.index(obj)
	
	def insert(self, index, obj):
		if obj in self._children:
			raise Exception("object already child of element")
		
		self._children.insert(index, obj)
		if obj.name != None:
			self._childrenHash[obj.name] = obj
			setattr(self.children, obj.name, obj)
	
	def firstChild(self):
		if(len(self._children) >= 1):
			return self._children[0]
		
		return None
	
	def lastChild(self):
		if(len(self._children) >= 1):
			return self._children[-1]
		
		return None
	
	def has_key(self, name):
		return self._childrenHash.has_key(name)
	
	
	# Container emulation methods ############################
	
	def __len__(self):
		return self._children.__len__()
	
	def __getitem__(self, key):
		if type(key) == int:
			return self._children.__getitem__(key)
		
		return self._childrenHash.__getitem__(key)
	
	def __setitem__(self, key, value):
		if type(key) == int:
			oldObj = self._children[key]
			if oldObj.name != None:
				del self._childrenHash[oldObj.name]
				#delattr(self.children, oldObj.name)
			
			if value.name != None:
				self._childrenHash[value.name] = value
				setattr(self.children, value.name, value)
			
			return self._children.__setitem__(key, value)
		
		else:
			if key in self._childrenHash:
				# Existing item
				#try:
				inx = self._children.index( self._childrenHash[key] )
				#except:
					#print "Key:",key
					#print "Number of items in _children:", len(self._children)
					#print "Number of items in _childrenHash:", len(self._childrenHash)
					
					#for c in self._children:
						#print "Child:", c.name
					
					#for c in self._childrenHash.keys():
						#print "Hash Child:", c
					
					#raise
					
				self._children[inx] = value
				self._childrenHash[key] = value
				setattr(self.children, value.name, value)
			else:
				self._children.append(value)
				self._childrenHash[key] = value
				setattr(self.children, value.name, value)
	
	def __delitem__(self, key):
		if type(key) == int:
			obj = self._children[key]
			if obj.name != None:
				del self._childrenHash[obj.name]
				delattr(self.children, obj.name)
			
			return self._children.__delitem__(key)
		
		obj = self._childrenHash[key]
		self._children.remove(obj)
		del self._childrenHash[key]
		delattr(self.children, key)
	
	def __iter__(self):
		return self._children.__iter__()
	
	def __contains__(self, item):
		return self._children.__contains__(item)

class Mutatable(ElementWithChildren):
	'''
	To mark a DOM object as mutatable(fuzzable) or not  
	'''
	def __init__(self, name = None, parent = None, isMutable = True):
		ElementWithChildren.__init__(self, name, parent)
		
		#: Can this object be changed by the mutators?
		self.isMutable = isMutable
	
	def setMutable(self, value):
		'''
		Update this element and all childrens isMutable.
		'''
		for child in self:
			if isinstance(child, Mutatable):
				child.setMutable(value)
				
		self.isMutable = value
		
class DataElement(Mutatable):
	'''
	Data elements compose the Data Modle.  This is the base
	class for String, Number, Block, Template, etc.
	
	When iterating over the Peach DOM if an element
	isinstance(obj, DataElement) it is part of a data model.
	'''
	
	def __init__(self, name = None, parent = None):
		ElementWithChildren.__init__(self, name, parent)
		
		if name != None and (name.find(".") > -1 or name.find(":") > -1):
			raise PeachException("Name '%s' contains characters not allowed in names such as period (.) or collen (:)" % name)
		
		#: Should element be mutated?
		self.isMutable = True
		
		#: Does data model have an offset relation?
		self.modelHasOffsetRelation = None
		
		#: Cache of relation, list of full data names (String) of each relation from here down.  cache is build post incoming.
		self.relationCache = None
		
		#: Key is full data name of "of" element (string), value is list of relation full data names (String). cache is bulid post incoming.
		self.relationOfCache = None
		
		#: Event that occurs prior to parsing the next array element.
		self.onArrayNext = None
		
		#: Transformers to apply
		self.transformer = None
		
		#: Fixup if any
		self.fixup = None
		
		#: Placement if any
		self.placement = None
		
		#: Relations this element has
		self.relations = []
		
		#: Fixed occurs
		self.occurs = None
		#: Minimum occurences
		self._minOccurs = 1
		#: Maximum occurences
		self._maxOccurs = 1
		
		#: Default value to use
		self.defaultValue = None
		#: Override default value
		self.currentValue = None
		#: Current value
		self.value = None
		
		#: Expression used by data cracker to determin
		#: if element should be included in cracking.
		self.when = None
		
		self._inInternalValue = False	#: Used to prevent recursion
		
		# Attributes for elements part of an array
		self.array = None			#: Name of array.  The origional name of the data element.
		self.arrayPosition = None	#: Our position in the array.
		self.arrayMinOccurs = None	#: The min occurences in the array
		self.arrayMaxOccurs = None	#: The max occurences in the array
		
		#: Position in data stream item was parsed at
		self.pos = None
		#: Parse rating for element
		self.rating = None
	
		#: Is this element a static token?
		self.isStatic = False

		#: A StringBuffer used to determin offset relations
		self.relationStringBuffer = None
	
		#: Fullname in data model
		self.fullNameDataModel = None
	
	#def __getinitargs__(self):
	#	return (self.name, None)
	
	def BuildFullNameCache(self):
		'''
		Figure out our fullname and fullname in data model
		'''
		
		for node in self._getAllRelationsInDataModel():
			node.fullName = node.getFullname()
			node.fullNameDataModel = node.getFullnameInDataModel()
	
	def BuildRelationCache(self):
		'''
		Build the relation cache for this data element and it's children.
		'''
		
		# 0. Build the fullname cache first
		if self.fullName == None or self.fullNameDataModel == None:
			self.BuildFullNameCache()

		# Update modelHasOffsetRelation when not using cache
		if self.modelHasOffsetRelation == None and PeachModule.Engine.engine.Engine.relationsNew:
			relations = self._getAllRelationsInDataModel(self, False)
			for r in relations:
				if r.type == 'count':
					self.modelHasOffsetRelation = True
					break
			
		# Exit if we already have a cache, or don't need one
		if self.relationCache != None or PeachModule.Engine.engine.Engine.relationsNew:
			return
		
		# 1. Build list of all relations from here down
		relations = self._getAllRelationsInDataModel(self, False)
		
		# 2. Fill in both cache lists
		self.relationCache = []
		self.relationOfCache = {}
		
		for r in relations:
			rStr = r.getFullnameInDataModel()
			
			# Update modelHasOffsetRelation
			if r.type == 'count':
				self.modelHasOffsetRelation = True
			
			if r.type != 'when':
				ofStr = r.getOfElement().getFullnameInDataModel()
				if not self.relationOfCache.has_key(ofStr):
					self.relationOfCache[ofStr] = []
				
				if rStr not in self.relationOfCache[ofStr]:
					self.relationOfCache[ofStr].append(rStr)
			
			if rStr not in self.relationCache:
				self.relationCache.append(rStr)
		
		for child in self._children:
			
			if isinstance(child, DataElement):
				child.BuildRelationCache()
	
	def get_minOccurs(self):
		minOccurs = self._minOccurs
		
		if minOccurs != None:
			minOccurs = eval(str(minOccurs))
		
		if minOccurs == None:
			minOccurs = 1
		
		elif minOccurs != None:
			minOccurs = int(minOccurs)
		
		return minOccurs
	
	def set_minOccurs(self, value):
		if value == None:
			self._maxOccurs = None
		
		else:
			self._minOccurs = str(value)
		
	#: Minimum occurences (property)
	minOccurs = property(get_minOccurs, set_minOccurs)
	
	def get_maxOccurs(self):
		if self._maxOccurs == None:
			return None
		
		return eval(str(self._maxOccurs))
	
	def set_maxOccurs(self, value):
		if value == None:
			self._maxOccurs = None
		else:	
			self._maxOccurs = str(value)
	
	#: Maximum occurences (property)
	maxOccurs = property(get_maxOccurs, set_maxOccurs)
	
	def getAllChildDataElements(self, ret = None):
		'''
		Get all children data elements.  Recursive
		'''
		
		if ret == None:
			ret = []
		
		for child in self:
			if isinstance(child, DataElement):
				ret.append(child)
				child.getAllChildDataElements(ret)
		
		return ret
	
	def _HasSizeofRelation(self, node = None):
		
		if node == None:
			node = self
			
		for relation in node.relations:
			if relation.type == 'size' and relation.of != None:
				return True
		
		return False
	
	def _HasOffsetRelation(self, node = None):
		
		if node == None:
			node = self
			
		for relation in node.relations:
			if relation.type == 'offset' and relation.of != None:
				return True
		
		return False
	
	def _GetOffsetRelation(self, node = None):
		
		if node == None:
			node = self
			
		for relation in node.relations:
			if relation.type == 'offset' and relation.of != None:
				return relation
		
		return False
	
	def _GetSizeofRelation(self, node = None):
		
		if node == None:
			node = self
			
		for relation in node.relations:
			if relation.type == 'size' and relation.of != None:
				return relation
		
		return None
	
	def GetWhenRelation(self, node = None):
		
		if node == None:
			node = self
			
		for relation in node.relations:
			if relation.type == 'when':
				return relation
		
		return None
	
	def HasWhenRelation(self, node = None):
		
		if node == None:
			node = self
		
		for relation in node.relations:
			if relation.type == 'when':
				return True
		
		return False

	def _HasCountofRelation(self, node = None):
		
		if node == None:
			node = self
			
		for relation in node.relations:
			if relation.type == 'count' and relation.of != None:
				return True
		
		return False

	def _GetCountofRelation(self, node = None):
		
		if node == None:
			node = self
			
		for relation in node.relations:
			if relation.type == 'count' and relation.of != None:
				return relation
		
		return None

	def getFullnameInDataModel(self):
		'''
		This will get fully qualified name of this element starting with the
		root node of the data model.
		'''
		
		if self.fullNameDataModel != None:
			return self.fullNameDataModel
		
		name = self.name
		node = self
		
		while node.parent != None and isinstance(node.parent, DataElement):
			node = node.parent
			name = "%s.%s" % (node.name, name)
		
		return name
		
	def getRootOfDataMap(self):
		'''
		Return the root of this data map.  This should always return
		a Template object.
		'''
		
		# Slower then PSYCO
		#return cPeach.getRootOfDataMap(self)

		root = self
		while root.parent != None and isinstance(root.parent, DataElement):
			root = root.parent

		return root
	
	def findArrayByName(self, name):
		'''
		Will find first element in array named "name".
		
		This method should allow for more natural reuse of Blocks/Templates
		w/o the user needing to think about it.
		
		@type	name: string
		@param	name: Array to find.  Does not support dotted name.
		@rtype: DataElement
		@return: DataElement or None
		'''
		
		for block in self._findAllBlocksGoingUp():
			obj = self._findArrayByName(block, name)
			if obj != None:
				return obj
		
		return None
	
	def _findArrayByName(self, node, name):
		'''
		A generator that returns each instance of name in a data model.
		'''
		
		# look at us!
		if node.array == name and node.arrayPosition == 0:
			return node
		
		# look at each child
		for child in node._children:
			if isinstance(child, DataElement) and child.array == name and child.arrayPosition == 0:
				return child
		
		# search down each child path
		for child in node._children:
			if isinstance(child, DataElement):
				obj = self._findArrayByName(child, name)
				if obj != None:
					return obj
		
		# done!
		return None
	
	def findDataElementByName(self, name):
		'''
		Will find a data element in this data map by name.  The search
		pattern we use is to locate each block we are a member of
		starting with the nearest.  At each block we look down to see
		if we can resolve the name.  If not we move closer towards the
		root of the data model.
		
		This method should allow for more natural reuse of Blocks/Templates
		w/o the user needing to think about it.
		
		@type	name: string
		@param	name: Name of element to find.  Can be full or relative.
		@rtype: DataElement
		@return: DataElement or None
		'''
		
		names = name.split('.')
		
		if self.name == names[0]:
			obj = self._checkDottedName(self, names)
			if obj != None:
				return obj
		
		# Assume if we have more then 2 parts we may be from the root
		if len(names) > 2:
			obj = self._checkDottedName(self.getRootOfDataMap(), names)
			if obj != None:
				return obj
		
		return cPeach.findDataElementByName(self, names)
		
		#for block in self._findAllBlocksGoingUp():
		#	print "findDataElementByName: Looking for %s in %s" % (name, block.name)
		#	for node in self._findDataElementByName(block, names[0]):
		#		obj = self._checkDottedName(node, names)
		#		if obj != None:
		#			#print "Could not locate", name
		#			#print "But we did with old code", obj.getFullnameInDataModel()
		#			#print node
		#			#print obj.parent
		#			#raise Exception("Boggers")
		#			return obj
		#
		#return None

	def find(self, name):
		'''
		Alias for findDataElementByName.
		
		Will find a data element in this data map by name.  The search
		pattern we use is to locate each block we are a member of
		starting with the nearest.  At each block we look down to see
		if we can resolve the name.  If not we move closer towards the
		root of the data model.
		
		This method should allow for more natural reuse of Blocks/Templates
		w/o the user needing to think about it.
		
		@type	name: string
		@param	name: Name of element to find.  Can be full or relative.
		@rtype: DataElement
		@return: DataElement or None
		'''
		return self.findDataElementByName(name)
	
	def _findAllBlocksGoingUp(self):
		'''
		Generator that locates all blocks by walking up
		our tree.
		'''
		
		ret = []
		
		obj = self
		if isinstance(obj, Block) or isinstance(obj, Template):
			ret.append(obj)
		
		while obj.parent != None and isinstance(obj.parent, DataElement):
			obj = obj.parent
			ret.append(obj)
			
		return ret
	
	def _findDataElementByName(self, node, name):
		'''
		A generator that returns each instance of name in a data model.
		'''
		
		# look at us!
		if node.name == name:
			yield node
		
		# look at each child
		if node._childrenHash.has_key(name):
			yield node[name]
		else:
			for c in node:
				print "%s: %s" % (node.name, c.name)
		
		# search down each child path
		for child in node._children:
			if isinstance(child, DataElement):
				for n in self._findDataElementByName(child, name):
					yield n
		
		# done!
	
	def _checkDottedName(self, node, names):
		'''
		Internal helper method, not for use!
		'''
		
		if node.name != names[0]:
			#print "_checkDottedName: %s != %s" % (node.name, names[0])
			return None
		
		obj = node
		for i in range(1, len(names)):
			if not obj.has_key(names[i]):
				#print "_checkDottedName: no %s" % (names[i])
				#for c in obj:
				#	print "_checkDottedName: c.name: %s" % c.name
				#	
				return None
			
			obj = obj[names[i]]
		
		return obj
	
	def getDataElementByName(self, name):
		'''
		Get an element relative to here with a qualified name
		'''
		
		names = name.split(".")
		
		if self.name != names[0]:
			return None
		
		obj = self
		for i in range(1, len(names)):
			if not obj.has_key(names[i]):
				return None
			
			obj = obj[names[i]]
		
		return obj
	
	
	def getRelationOfThisElement(self, type):
		'''
		Locate and return a relation of this element.
		'''
		
		if PeachModule.Engine.engine.Engine.relationsNew:
			# Assume both of and from relations in model
			
			for r in self.relations:
				# Lets not return "when" :)
				if r.type == 'when' or r.From == None:
					continue
				
				if type == None or r.type == type:
					#print "Found of relation for", self.getFullDataName()
					obj = self.findDataElementByName(r.From)
					
					if obj == None:
						raise Exception("Mismatched relations1???")
					
					if type != None:
						for rel in obj.relations:
							if rel.type == type:
								return rel
						
						raise Exception("Mismatched relations???")
					
					for rel in obj.relations:
						if rel.type == 'when':
							continue
						
						return rel
					
					raise Exception("MIssmatched relations2???")
			
			#print "Not for", self.getFullDataName()
			return None
		
		if self.relationCache != None:
			root = self.getRootOfDataMap()
			name = self.getFullnameInDataModel()
			
			if root.relationOfCache.has_key(name):
				for r in root.relationOfCache[name]:
					r = self.find(r)
					if r != None and (type == None or r.type == type):
						return r
			
			return None

		# Faster by some
		return cPeach.getRelationOfThisElement(self, type)

		## To Test
		##print "getRelationOfThisElement: ", self.getFullDataName()
		##obj = cPeach.getRelationOfThisElement(self, type)
		##
		#for r in self._genRelationsInDataModelFromHere():
			#if r.getOfElement() == self:
				#if type == None or r.type == type:
					##if r != obj:
					##	print "r != obj"
					##	print obj
					##	print r
					##	raise Exception("EERRK")
					#return r
		
		##if obj != None:
		##	raise Exception("SHOULD BE NULL")
		#return None
	
	def getRelationsOfThisElement(self):
		'''
		Locate and return a relation of this element.
		'''
		
		relations = []
		
		if PeachModule.Engine.engine.Engine.relationsNew:
			# Assume both of and from relations in model
			
			for r in self.relations:
				# Lets not return "when" :)
				if r.type == 'when' or r.From == None:
					continue
				
				#print "Found of relation for", self.getFullDataName()
				obj = self.findDataElementByName(r.From)
				
				if obj == None:
					raise Exception("Mismatched relations1???")
				
				for rel in obj.relations:
					relations.append(rel)
				
				for rel in obj.relations:
					if rel.type == 'when':
						continue
					
					relations.append(rel)
			
			#print "Not for", self.getFullDataName()
			return relations
		
		if self.relationCache != None:
			print "Using relation cache!"
			root = self.getRootOfDataMap()
			name = self.getFullnameInDataModel()
			
			if root.relationOfCache.has_key(name):
				for r in root.relationOfCache[name]:
					r = self.find(r)
					if r != None:
						return relations.append(r)
			
			return relations
		
		for r in self._genRelationsInDataModelFromHere():
			if r.getOfElement() == self:
				relations.append(r)
		
		return relations
	
	def _genRelationsInDataModelFromHere(self, node = None):
		'''
		Instead of returning all relations starting with
		root we will walk up looking for relations.
		'''
		
		if node == None:
			node = self
		
		# Check if we are the top of the data model
		if not isinstance(node.parent, DataElement):
			for r in self._getAllRelationsInDataModel(node):
				yield r
			
		else:
			# If not start searching
			cur = node.parent
			while cur != None and isinstance(cur, DataElement):
				for r in self._getAllRelationsInDataModel(cur):
					yield r
				
				cur = cur.parent
	
	def _getAllRelationsInDataModel(self, node = None, useCache = True):
		'''
		Generator that gets all relations in data model.
		'''
		
		if node == None:
			node = self.getRootOfDataMap()
		
		# Use cache if we have it
		if useCache and isinstance(node, DataElement) and node.relationCache != None:
			root = self.getRootOfDataMap()
			for s in node.relationCache:
				yield root.getDataElementByName(s)
			
			return
		
		if isinstance(node, Relation) and node.From == None:
			#print "_getAllRelationsInDataModel: Yielding self"
			yield node
		
		if isinstance(node, DataElement):
			for child in node._children:
				for r in self._getAllRelationsInDataModel(child, useCache):
					#print "_getAllRelationsInDataModel: Yielding"
					yield r
	#_getAllRelationsInDataModel = profile(_getAllRelationsInDataModel)
	
	def isArray(self):
		'''
		Check if this data element is part of an array.
		'''
		
		if self.array != None:
			return True
	
	def getArrayCount(self):
		'''
		Return number of elements in array.
		'''
		
		if not self.isArray():
			return -1
		
		maxPos = int(self.arrayPosition)
		for c in self.parent:
			if isinstance(c, DataElement) and c.array == self.array:
				if int(c.arrayPosition) > maxPos:
					maxPos = int(c.arrayPosition)
		
		return maxPos+1
	
	def getArrayElementAt(self, num):
		'''
		Return array element at position num.
		'''
		
		if not self.isArray():
			return None
		
		for c in self.parent:
			if isinstance(c, DataElement) and c.array == self.array and int(c.arrayPosition) == num:
				return c
		
		return None

	def getCount(self):
		'''
		Return how many times this element occurs.  If it is part
		of an array the array size is returned, otherwise we will
		look at the min/max and any count relations.
		'''
		
		# If we are an array, we have a size already
		if self.isArray():
			return self.getArrayCount()
		
		# Sanity check
		if self.minOccurs == 1 and self.maxOccurs == 1:
			return 1
		
		# Otherwise see if we have a relation and min/max occurs
		rel = self.getRelationOfThisElement('count')
		if rel != None:
			try:
				cnt = int(rel.parent.getInternalValue())
				
				if cnt < self.minOccurs:
					cnt = self.minOccurs
				elif cnt > self.maxOccurs:
					cnt = self.maxOccurs
				
				return cnt
			
			except:
				# If relation wasn't set with number then ignore
				pass
		
		# If our minOccurs is larger than one and no relation
		# go with the min.
		if self.minOccurs > 1:
			return self.minOccurs
		
		return 1

	def getInternalValue(self):
		'''
		Return the internal value of this date element.  This
		value comes before any modifications such as packing,
		padding, truncating, etc.
		
		For Numbers this is the python int or long value.
		'''
		print self
		raise Exception("TODO: Implement me!")

	def getRelationValue(self, value):
		'''
		This is common logic that was being duplicated across several data
		elements.  The logic is used in getInternalValue() to check if a
		relation of size-of or count-of should modify the value.
		
		@rtype: string or number
		@return: the value passed in or an integer if the value needed to be changed.
		'''
		
		if self._HasSizeofRelation(self) and not self._inInternalValue:
			try:
				self._inInternalValue = True
				relation = self._GetSizeofRelation(self)
				value = len(relation.getOfElement().getValue())
				value = relation.setValue(value)
				#print "SIZE REALTION %s of %s: " % (relation.parent.name, relation.of), value
			
			finally:
				self._inInternalValue = False
		
		elif self._HasCountofRelation(self) and not self._inInternalValue:
			# This could cause recursion, use this variable to prevent
			self._inInternalValue = True
			try:
				
				relation = self._GetCountofRelation(self)
				ofElement = relation.getOfElement()
				
				# Ask for value before we get the count
				ofElement.getValue()
				
				value = ofElement.getCount()
				value = relation.setValue(value)
				#print "COUNT REALTION %s of %s: " % (relation.parent.name, relation.of), value
					
			finally:
				self._inInternalValue = False
		
		elif self._HasOffsetRelation() and not self._inInternalValue and self.getRootOfDataMap().relationStringBuffer != None:
			try:
				self._inInternalValue = True
				relation = self._GetOffsetRelation(self)
				ofElement = relation.getOfElement()
				newValue = self.getRootOfDataMap().relationStringBuffer.getPosition(ofElement.getFullDataName())
				#print "OFFSET REALTION %s of %s: " % (relation.parent.name, relation.of), newValue
				
				if newValue != None:
					value = relation.setValue(newValue)
			
			finally:
				self._inInternalValue = False
		
		return value
	#getRelationValue = profile(getRelationValue)
	
	def getRawValue(self, sout = None):
		'''
		Get the value of this data element pre-transformers.
		'''
		
		raise Exception("TODO: Implement me!")
	
	def getValue(self, sout = None):
		'''
		Get the value of this data element.
		'''
		
		# This method can be called while we are in it.
		# so lets not use self.value to hold anything.
		value = None
		
		if sout != None:
			sout.storePosition(self.getFullDataName())
		
		if self.transformer != None:
			value = self.getRawValue()
			value = self.transformer.transformer.encode(value)
		
			if sout != None:
				sout.write(value)
		
		else:
			value = self.getRawValue(sout)
		
		# See if we need to repeat ourselvs.
		if not self.isArray():
			count = self.getCount()
			if count > 1:
				origValue = value
				value = value * count
				
				if sout != None:
					sout.write(origValue * (count-1))
		
		if value == None:
			raise Exception("value is None for %s type %s" % (self.name, self.elementType))
		
		self.value = value
		return self.value
	
	def setDefaultValue(self, value):
		'''
		Set the default value for this data element.
		'''
		self.defaultValue = value
	
	def setValue(self, value):
		'''
		Set the current value for this data element
		'''
		self.currentValue = value
		self.getValue()
	
	def reset(self):
		'''
		Reset the value of this data element back to
		the default.
		'''
		self.currentValue = None
		self.value = None
		
	def resetDataModel(self, node = None):
		'''
		Reset the entire data model.
		'''
		
		if node == None:
			node = self.getRootOfDataMap()
		
		node.reset()
		
		for c in node._children:
			if isinstance(c, DataElement()):
				self.resetDataModel(c)
	
	def _fixRealParent(self, node):
		
		# 1. Find root
		
		root = node
		while root.parent != None:
			root = root.parent
		
		# 2. Check if has a realParent
		
		if hasattr(root, 'realParent'):
			#print "_fixRealParent(): Found fake root: ", root.name
			root.parent = root.realParent
		
		# done!
	
	def _unFixRealParent(self, node):
		
		# 1. Look for fake root
		
		root = node
		while not hasattr(root, 'realParent') and root.parent != None:
			root = root.parent
		
		# 2. Remove parent link
		#print "_unFixRealParent(): Found fake root: ", root.name
		root.parent = None

	def	calcLength(self):
		'''
		Calculate length
		'''
		
		environment = {
			'self' : self
			}
		
		try:
			self._fixRealParent(self)
			return evalEvent(self.lengthCalc, environment, self)
		finally:
			self._unFixRealParent(self)
		
class Transformer(ElementWithChildren):
	'''
	The Trasnfomer DOM object.  Should only be a child of
	a data element.
	'''
	def __init__(self, parent, transformer = None):
		ElementWithChildren.__init__(self, None, parent)
		self.elementType = 'transformer'
		
		# Instance of actual transformer
		self.transformer = transformer
		
		# Class string used to create transformer instance
		self.classStr = None
	
class Fixup(ElementWithChildren):
	'''
	Fixup DOM element.  Child of data elements only.
	'''
	def __init__(self, parent, fixup = None):
		ElementWithChildren.__init__(self, None, parent)
		self.elementType = 'fixup'
		self.classStr = None
		self.fixup = fixup
	
class Placement(ElementWithChildren):
	'''
	Indicates were a block goes after cracking.
	'''
	def __init__(self, parent, fixup = None):
		ElementWithChildren.__init__(self, None, parent)
		self.elementType = 'placement'
		self.after = None
		self.before = None

class Param(ElementWithChildren):
	def __init__(self, parent):
		ElementWithChildren.__init__(self, None, parent)
		self.elementType = 'param'
		self.valueType = 'string'


class Peach(ElementWithChildren):
	'''
	This is our root node container.
	'''
	def __init__(self):
		ElementWithChildren.__init__(self, 'peach', None)
		
		self.elementType = 'peach'
		self.version = None
		self.description = None
		self.author = None


class Test(ElementWithChildren):
	def __init__(self, name, parent = None):
		ElementWithChildren.__init__(self, name, parent)
		
		self.elementType = 'test'
		self.description = None
		self.template = None
		self.data = None
		self.publisher = None
		self.stateMachine = None
		self.ref = None
		self.mutators = None

		# To mark Mutatable elements
		self.mutatables = []
		
	def getMutators(self):
		'''
		returns a lsit of mutators
		'''
		
		ret = []
		for m in self.mutators:
			if m.elementType == 'mutator':
				ret.append(m)
		
		return ret
	
	def markMutatableElements(self, node):
		if len(self.mutatables) == 0:
			return
		
		domDict = {}
		xmlDom = self.stateMachine.toXmlDomLight(node, domDict)
		
		for opt in self.mutatables:
			isMutable = opt[0]
			xpath = str(opt[1])
			
			try:
				xnodes = xmlDom.xpath(xpath)
				#print "XPATH: %s # of nodes: %s" % (xpath, str(len(xnodes)))
				if len(xnodes) == 0:
					raise PeachException("XPath:[%s] must return at least an XNode. Please check your references or xpath declarations." % xpath)
				
				for node in xnodes:
					try:
						elem = domDict[node]
		
						if isinstance(elem, Mutatable):
							elem.setMutable(isMutable)
							
					except KeyError:
						pass
							
			except SyntaxError:
				raise PeachException("Invalid xpath string: %s" % xpath)

class Run(ElementWithChildren):
	def __init__(self, name, parent = None):
		ElementWithChildren.__init__(self, name, parent)
		self.elementType = 'run'
		self.description = None
		self.tests = []
		self.parent = None
		self.waitTime = 0
	
	def getLogger(self):
		
		for child in self:
			if child.elementType == 'logger':
				return child
		
		return None


class Agent(ElementWithChildren):
	def __init__(self, name, parent = None):
		ElementWithChildren.__init__(self, name, parent)
		self.elementType = 'agent'
		self.description = None
		self.location = None
		self.password = None
	
	def getPythonPaths(self):
		p = []
		
		for child in self:
			if child.elementType == 'pythonpath':
				p.append({'name': child.name})
		
		if len(p) == 0:
			return None
		
		return p
	
	def getImports(self):
		p = []
		
		for child in self:
			if child.elementType == 'import':
				p.append({'import': child.importStr, 'from' : child.fromStr})
		
		if len(p) == 0:
			return None
		
		return p

class Monitor(ElementWithChildren):
	def __init__(self, name, parent = None):
		ElementWithChildren.__init__(self, name, parent)
		self.elementType = 'monitor'
		self.classStr = None
		self.params = {}


#############################################################################
## Data Generating Elements

class Template(DataElement):
	'''
	Essentially a Block, but is the top level element in a data model.
	
	TODO: Refactor this to DataModel
	'''
	
	def __init__(self, name):
		DataElement.__init__(self, name, None)
		self.elementType = 'template'
		self.ref = None
		self.length = None
		self.lengthType = None
	
	def hasLength(self):
		if self.length != None:
			return True
		
		return False
	
	def getLength(self):
		'''
		Get the length of this element.
		'''
		
		if self.lengthType == 'calc':
			self.length = self.calcLength()
		
		elif self.isStatic:
			return len(self.getValue())
		
		return self.length
	
	def getValue(self, sout = None):
		'''
		Template needs a custom getValue method!
		'''
		try:
			self.relationStringBuffer = sout
			return DataElement.getValue(self, sout)
			
		finally:
			self.relationStringBuffer = None
	
	def getInternalValue(self, sout = None):
		'''
		Return the internal value of this date element.  This
		value comes before any modifications such as packing,
		padding, truncating, etc.
		
		For Numbers this is the python int value.
		
		@type	sout: StreamBuffer
		@param	sout: Output stream
		'''
		
		value = ""
		
		# 0. If using a stream store our location
		if sout != None:
			pos = sout.storePosition(self.getFullDataName())
		
		# 1. Override with currentValue
		
		if self.currentValue != None:
			value = self.currentValue
			if sout != None:
				sout.write(value, self.getFullDataName())
		
			return value
		
		# 2. Get value from children
		
		for c in self:
			if isinstance(c, DataElement):
				try:
					if self.fixup != None or self.transformer != None:
						value += c.getValue()
					
					else:
						value += c.getValue(sout)
				
				except:
					print "value: [%s]" % repr(value)
					print "c.name: %s" % c.name
					print "c.type: %s" % c.elementType
					#print "c.getValue(): ", c.getValue()
					raise
		
		# 3. Fixup
		
		if self.fixup != None:
			self.fixup.fixup.context = self
			ret = self.fixup.fixup.dofixup()
			if ret != None:
				value = ret
				if sout != None:
					sout.write(value, self.getFullDataName())
		
		return value

	def getRawValue(self, sout = None):
		'''
		Get value for this data element.
			
		Performs any needed transforms to produce
		value.
		'''
			
		return self.getInternalValue(sout)
		
	#def getValue(self, sout = None):
	#	'''
	#	Get value for this data element.
	#	
	#	Performs any needed transforms to produce
	#	value.
	#	'''
	#	
	#	try:
	#		self.relationStringBuffer = sout
	#	
	#		self.value = ""
	#	
	#		if self.currentValue != None:
	#			# override children
	#			self.value = self.currentValue
	#	
	#		else:
	#			if self.transformer != None:
	#				childSout = None
	#			else:
	#				childSout = sout
	#
	#			for c in self:
	#				if isinstance(c, DataElement):
	#					if self.transformer == None:
	#						self.value += c.getValue(childSout)
	#					else:
	#						self.value += c.getValue(childSout)
	#		
	#		if self.transformer != None:
	#			self.value = self.transformer.transformer.encode(self.value)
	#			sout.write(self.value)
	#		
	#		return self.value
	#	
	#	finally:
	#		self.relationStringBuffer = None
	
	def setValue(self, value):
		'''
		Override value created via children.
		'''
		
		self.currentValue = value
	
	def reset(self):
		'''
		Reset current state.
		'''
		self.currentValue = None
		self.value = None


class Choice(DataElement):
	'''
	Choice, chooses one or emore sub-elements
	'''
	def __init__(self, name, parent):
		'''
		Don't put too much logic here.  See HandleBlock in the parser.
		'''
		DataElement.__init__(self, name, parent)
		self.elementType = 'choice'
		self.currentElement = None
		self.length = None
		self.lengthType = None
	
	def hasLength(self):
		if self.length != None:
			return True
		
		return False
	
	def getLength(self):
		'''
		Get the length of this element.
		'''
		
		if self.lengthType == 'calc':
			self.length = self.calcLength()
		
		elif self.isStatic:
			return len(self.getValue())
		
		return self.length
	
	
	def SelectedElement(self, value = None):
		
		if value != None:
			self.currentElement = self[value]
		
		return self.currentElement
	
	def getInternalValue(self, sout = None):
		'''
		Return the internal value of this date element.  This
		value comes before any modifications such as packing,
		padding, truncating, etc.
		
		For Numbers this is the python int value.
		'''
		return self.getRawValue(sout)
		
	def getRawValue(self, sout = None):
		
		value = ""
		if self.currentValue != None:
			value = self.currentValue
			if sout != None:
				sout.write(value, self.getFullDataName())
		
		else:
			if self.currentElement == None:
				for n in self:
					if isinstance(n, DataElement):
						self.currentElement = n
						break
			
			value = self.currentElement.getValue(sout)
			if value == None:
				print "Choice.getRawValue: value is null!"
				print "Choice.getRawValue: ", self.currentElement.getFullname()
				print "Choice.getRawValue: ", self.currentElement.elementType
				print "Choice.getRawValue: ", self.currentElement
				raise Exception("Value should not be null!")
		
		return value

def BlockToXml(self, parent):
	node = parent.rootNode.createElementNS(None, 'Block')
	parent.appendChild(node)
	
	self._setAttribute(node, 'name', self.name)
	self._setAttribute(node, 'ref', self.ref)
		
	for child in self:
		if self._xmlHadChild(child):
			child.toXml(node)
	
	return node

class Block(DataElement):
	'''
	Block or sequence of other data types.
	'''
	def __init__(self, name, parent):
		'''
		Don't put too much logic here.  See HandleBlock in the parser.
		'''
		DataElement.__init__(self, name, parent)
		self.elementType = 'block'
		self.toXml = new.instancemethod(BlockToXml, self, self.__class__)
		self.length = None
		self.lengthType = None
	
	def hasLength(self):
		if self.length != None:
			return True
		
		return False
	
	def getLength(self):
		'''
		Get the length of this element.
		'''
		
		if self.lengthType == 'calc':
			self.length = self.calcLength()
		
		elif self.isStatic:
			return len(self.getValue())
		
		return self.length
	
	def getInternalValue(self, sout = None):
		'''
		Return the internal value of this date element.  This
		value comes before any modifications such as packing,
		padding, truncating, etc.
		
		For Numbers this is the python int value.
		
		@type	sout: StreamBuffer
		@param	sout: Output stream
		'''
		
		value = ""
		
		# 0. If using a stream store our location
		if sout != None:
			pos = sout.storePosition(self.getFullDataName())
		
		# 1. Override with currentValue
		
		if self.currentValue != None:
			value = self.currentValue
			if sout != None:
				sout.write(value, self.getFullDataName())
		
			return value
		
		# 2. Get value from children
		
		for c in self:
			if isinstance(c, DataElement):
				try:
					if self.fixup != None or self.transformer != None:
						value += c.getValue()
					
					else:
						value += c.getValue(sout)
				
				except:
					print "value: [%s]" % repr(value)
					print "c.name: %s" % c.name
					print "c.getValue(): ", c.getValue()
					raise
		
		# 3. Fixup
		
		if self.fixup != None:
			self.fixup.fixup.context = self
			ret = self.fixup.fixup.dofixup()
			if ret != None:
				value = ret
				if sout != None:
					sout.write(value, self.getFullDataName())
		
		if value == None:
			raise Exception("value should not be None here")
		
		return value
	
	def getRawValue(self, sout = None):
		'''
		Get value for this data element.
		
		Performs any needed transforms to produce
		value.
		'''
		
		return self.getInternalValue(sout)


class Number(DataElement):
	'''
	A numerical field
	'''
	
	_allowedSizes = [8, 16, 24, 32, 64]
	
	def __init__(self, name, parent):
		DataElement.__init__(self, name, parent)
		self.elementType = 'number'
		self.size = 8
		self.ref = None
		self.endian = 'little'
		self.signed = False
		self.valueType = 'string'
		self.currentValue = None
		self.generatedValue = None
		self.insideRelation = False
	
	def getMinValue(self):
		'''
		Get the minimum value this number can have.
		'''
		
		if not self.signed:
			return 0
		
		max = long('FF'*(self.size/8), 16)
		return 0 - max
	
	def getMaxValue(self):
		'''
		Get the maximum value for this number.
		'''
		max = long('FF'*(self.size/8), 16)
		if self.signed:
			return max/2
		
		return max
	
	def getInternalValue(self, sout = None):
		'''
		Return the internal value of this date element.  This
		value comes before any modifications such as packing,
		padding, truncating, etc.
		
		For Numbers this is the python int value.
		'''
		
		# 0. Override default?
		if self.currentValue != None:
			return self.currentValue
			
		# 1. Our value to return
		value = 0
		
		# 2. Have default value?
		
		if self.defaultValue != None:
			value = self.defaultValue
		
		# 3. Relation?
		
		value = self.getRelationValue(value)
		
		# 4. fixup?
		if self.fixup != None:
			self.fixup.fixup.context = self
			ret = self.fixup.fixup.dofixup()
			if ret != None:
				value = ret
		
		if sout != None:
			sout.write(value, self.getFullDataName())
		
		return value
	
	def pack(self, num):
		'''
		Pack a number into proper format for this Number
		'''
		
		# 1. Get the transformer we need
		isSigned = 0
		if self.signed:
			isSigned = 1
		
		isLittleEndian = 0
		if self.endian == 'little':
			isLittleEndian = 1
		
		if self.size == 8:
			trans = Transformers.type.AsInt8(isSigned, isLittleEndian)
		elif self.size == 16:
			trans = Transformers.type.AsInt16(isSigned, isLittleEndian)
		elif self.size == 24:
			trans = Transformers.type.AsInt24(isSigned, isLittleEndian)
		elif self.size == 32:
			trans = Transformers.type.AsInt32(isSigned, isLittleEndian)
		elif self.size == 64:
			trans = Transformers.type.AsInt64(isSigned, isLittleEndian)

		# 2. Encode number
		
		try:
			# This could fail if our override was not
			# a number or empty ('')
			num = long(num)
		except:
			num = 0
			
		return trans.encode(long(num))
	
	def unpack(self, buff):
		'''
		Unpack a number from proper format fo this Number
		'''
		# 1. Get the transformer we need
		isSigned = 0
		if self.signed:
			isSigned = 1
		
		isLittleEndian = 0
		if self.endian == 'little':
			isLittleEndian = 1
		
		if self.size == 8:
			trans = Transformers.type.AsInt8(isSigned, isLittleEndian)
		elif self.size == 16:
			trans = Transformers.type.AsInt16(isSigned, isLittleEndian)
		elif self.size == 24:
			trans = Transformers.type.AsInt24(isSigned, isLittleEndian)
		elif self.size == 32:
			trans = Transformers.type.AsInt32(isSigned, isLittleEndian)
		elif self.size == 64:
			trans = Transformers.type.AsInt64(isSigned, isLittleEndian)

		# 2. Encode number
		
		try:
			# This could fail if our override was not
			# a number or empty ('')
			return trans.decode(buff)
		
		except:
			pass
		
		return 0
	
	def getRawValue(self, sout):
		value = self.getInternalValue()
		if value == '':
			return ''
		
		#if long(value) < -182229420:
		#	print "Value: ", value
		#	print "Name: ", self.name
		#	print "Parent Name: ", self.parent.name
		#	raise Exception("Fucked")
		
		ret = self.pack(value)
		
		if sout != None:
			sout.write(ret, self.getFullDataName())
		
		return ret


class String(DataElement):
	'''
	A string field
	'''
	def __init__(self, name = None, parent = None):
		DataElement.__init__(self, name, parent)
		self.elementType = 'string'
		self.valueType = 'string'
		self.defaultValue = None
		self.isStatic = False
		self.lengthType = 'string'
		self.lengthCalc = None
		self.length = None
		self.minOccurs = 1
		self.maxOccurs = 1
		self.generatedOccurs = 1
		self.currentValue = None
		self.insideRelation = False
		
		self.padCharacter = '\0'	#: Value to pad string with, defaults to NULL '\0'
		self.type = 'char'			#: Type of string, currently only char and wchar are supported.
		self.nullTerminated = False	#: Is string null terminated, defaults to false
		self.tokens = None			#: DEPRICATED, Use hint instead
	
	def getLength(self, inRaw = True):
		'''
		Get the length of this element.
		'''
		
		if not inRaw and (self.currentValue != None or self.isStatic):
			return len(self.getValue())
		
		if self.lengthType == 'calc':
			self.length = self.calcLength()
		
		return self.length
		
	def getInternalValue(self, sout = None):
		'''
		Return the internal value of this date element.  This
		value comes before any modifications such as packing,
		padding, truncating, etc.
		
		For Numbers this is the python int value.
		'''
		
		# 0. Override value?
		if self.currentValue != None:
			if sout != None:
				sout.write(self.currentValue, self.getFullDataName())
			
			return self.currentValue
			
		# 1. Init value
		value = ""
		
		# 3. default value?
		if self.defaultValue != None:
			value = self.defaultValue
		
		# 4. Relations
		
		value = self.getRelationValue(value)
		if type(value) != str:
			#print "Type was:", type(value)
			value = str(value)
		
		# 5. fixup
		
		if self.fixup != None:
			self.fixup.fixup.context = self
			ret = self.fixup.fixup.dofixup()
			if ret != None:
				value = ret
		
		if sout != None:
			sout.write(value, self.getFullDataName())
		
		return value
		
	def getRawValue(self, sout = None):
		
		
		# -1. Character encoding
		
		trans = None
		if self.type == 'wchar':
			trans  = WideChar()
		
		# 0. Override value?
		if self.currentValue != None:
			value = self.currentValue
		
		else:
			# 1. Init value
			value = self.getInternalValue()
			
			# 6. Fixed length string
			if self.length != None:
				self.length = self.getLength(True)
				
				if len(value) < self.length:
					value += self.padCharacter * (self.length - len(value))
				else:
					value = value[:self.length]
			
		# 7. Null terminated strings
		# Lets try null terminating even the mutated value.  Might as well!
		if self.nullTerminated and (len(value) == 0 or value[-1] != '\0'):
			value += '\0'
			
		# 9. All done
		if trans != None:
			value = trans.encode(value)
		
		if sout != None:
			sout.write(value, self.getFullDataName())
		
		return value


def ToXmlCommonDataElements(element, node):
	element._setAttribute(node, 'minOccurs', str(element.minOccurs))
	element._setAttribute(node, 'maxOccurs', str(element.maxOccurs))
	element._setAttribute(node, 'generatedOccurs', str(element.generatedOccurs))
	
	# Generators
	for child in element.extraGenerators:
		if element._xmlHadChild(child):
			child.toXml(node)
	
	# Relations
	for child in element.relations:
		if element._xmlHadChild(child):
			child.toXml(node)
	
	# Transformer
	if element.transformer != None:
		if element._xmlHadChild(child):
			child.toXml(node)
	

class Flags(DataElement):
	'''
	Set of flags
	'''
	def __init__(self, name, parent):
		DataElement.__init__(self, name, parent)
		self.elementType = 'flags'
		self.length = None	# called size
		self.endian = 'little'

	def getInternalValue(self, sout = None):
		'''
		Return the internal value of this date element.  This
		value comes before any modifications such as packing,
		padding, truncating, etc.
		
		For Numbers this is the python int value.
		'''
		# 1. Init our value
		
		ret = 0
		
		# 3. Build our flags up
		
		flags = []
		for n in self:
			if n.elementType == 'flag':
				flags.append(n)
		
		for flag in flags:
			mask = 0x00 << self.length - (flag.position + flag.length)
			
			cnt = flag.position + flag.length - 1
			for i in range(flag.length):
				#print "<< %d" % cnt
				mask |= 1 << cnt
				cnt -= 1
			
			#print "Mask:",repr(mask)
			flagValue = flag.getValue()
			try:
				flagValue = long(flagValue)
			except:
				flagValue = 0
			
			ret |= mask & (int(flagValue) << flag.position)
		
		# 4. do we fixup?
		
		if self.fixup != None:
			self.fixup.fixup.context = self
			ret = self.fixup.fixup.dofixup()
			if ret != None:
				value = ret
		
		# 5. Do we have an override?
		
		if self.currentValue != None:
			ret = self.currentValue
		
		# 7. Return value
		
		if sout != None:
			sout.write(ret, self.getFullDataName())
		
		return ret
		
	def getRawValue(self, sout = None):
		
		# 2. Get our transformer
		isSigned = 0
		isLittleEndian = 0
		if self.endian == 'little':
			isLittleEndian = 1
		
		if self.length == 8:
			trans = Transformers.type.AsInt8(isSigned, isLittleEndian)
		elif self.length == 16:
			trans = Transformers.type.AsInt16(isSigned, isLittleEndian)
		elif self.length == 24:
			trans = Transformers.type.AsInt24(isSigned, isLittleEndian)
		elif self.length == 32:
			trans = Transformers.type.AsInt32(isSigned, isLittleEndian)
		elif self.length == 64:
			trans = Transformers.type.AsInt64(isSigned, isLittleEndian)
		
		# 6. Apply numerical transformer
		
		ret = self.getInternalValue()
		
		if ret != '':
			ret = trans.encode(ret)
		
		# 7. Return value
		
		if sout != None:
			sout.write(ret, self.getFullDataName())
		
		return ret


class Flag(DataElement):
	'''
	A flag in a flag set
	'''
	def __init__(self, name, parent):
		DataElement.__init__(self, name, parent)
		self.elementType = 'flag'
		self.defaultValue = None
		self.position = None
		self.length = None	# called size
	
	def getInternalValue(self):
		'''
		Return the internal value of this date element.  This
		value comes before any modifications such as packing,
		padding, truncating, etc.
		
		For Numbers this is the python int value.
		'''
		return self.getRawValue()
		
	def getRawValue(self, sout = None):
		# 1. Init our value
		
		value = 0
		
		# 2. Default value?
		
		if self.defaultValue != None:
			value = self.defaultValue
		
		# 3. Relations
		
		value = self.getRelationValue(value)
		
		# 4. Fixup
		
		if self.fixup != None:
			self.fixup.fixup.context = self
			ret = self.fixup.fixup.dofixup()
			if ret != None:
				value = ret
		
		# 5. Do we have an override?
		
		if self.currentValue != None:
			value = self.currentValue
		
		# 6. Return value
		
		return value


class Seek(ElementWithChildren):
	'''
	Change the current position in the data stream.
	'''
	
	def __init__(self, name, parent):
		ElementWithChildren.__init__(self, name, parent)
		
		self.elementType = "seek"
		
		#: Python expression to calculate new position
		self.expression = None
		#: Integer position
		self.position = None
		#: Position change is relative to current position
		self.relative = None
		
		# EMulate some of the DataElement stuff
		self.array = None
		self.minOccurs = 1
		self.maxOccurs = 1
		self.currentValue = None
		self.defaultValue = None
	
	def HasWhenRelation(self):
		return False
	
	def _getExpressionPosition(self, currentPosition, dataLength, data):
		environment = {
			'self' : self,
			'pos' : currentPosition,
			'dataLength' : dataLength
			}
		
		#DataElement._fixRealParent(self, self)
		try:
			pos = -1
			pos = evalEvent(self.expression, environment, self)
			
		finally:
			#DataElement._unFixRealParent(self)
			pass
		
		return pos
	
	def _getPosition(self):
		return self.position
	
	def getPosition(self, currentPosition, dataLength, data):
		if self.expression != None:
			return self._getExpressionPosition(currentPosition, dataLength, data)
		
		if self.relative != None:
			return currentPosition + self.relative
		
		return self._getPosition();
	
	def _fixRealParent(self, node):
		'''
		Sometimes when we recurse to crack a
		block we remove the parent from the block
		and save it to .realParent.
		
		Since many scripts want to look up we will
		unsave the parent for a bit.
		'''
		
		# 1. Find root
		
		root = node
		while root.parent != None:
			root = root.parent
		
		# 2. Check if has a realParent
		
		if hasattr(root, 'realParent'):
			#print "_fixRealParent(): Found fake root: ", root.name
			root.parent = root.realParent
		
		# done!
	
	def _unFixRealParent(self, node):
		'''
		Clear the parent if we have it saved.
		'''
		
		# 1. Look for fake root
		
		root = node
		while not hasattr(root, 'realParent') and root.parent != None:
			root = root.parent
		
		# 2. Remove parent link
		#print "_unFixRealParent(): Found fake root: ", root.name
		root.parent = None


class Blob(DataElement):
	'''
	A flag in a flag set
	'''
	def __init__(self, name, parent):
		DataElement.__init__(self, name, parent)
		self.elementType = 'blob'
		self.valueType = 'string'
		self.lengthType = 'string'
		self.length = None
		self.lengthCalc = None

	def getInternalValue(self, sout = None):
		'''
		Return the internal value of this date element.  This
		value comes before any modifications such as packing,
		padding, truncating, etc.
		
		For Numbers this is the python int value.
		'''
		return self.getRawValue(sout)
	
	def getLength(self):
		'''
		Get the length of this element.
		'''
		
		if self.lengthType == 'calc':
			self.length = self.calcLength()
			#print "Calucalted length:", self.length
		
		elif self.isStatic:
			return len(self.getValue())
		
		return self.length
		
	def getRawValue(self, sout = None):
		
		# 1. init
		value = ""
		
		# 2. default value?
		if self.defaultValue != None:
			value = self.defaultValue
		
		# 3. Fixup
		if self.fixup != None:
			self.fixup.fixup.context = self
			ret = self.fixup.fixup.dofixup()
			if ret != None:
				value = ret
		
		# 4. Override?
		if self.currentValue != None:
			value = self.currentValue
		
		# 5. If we have sout
		if sout != None:
			sout.write(value, self.getFullDataName())
		
		return value
	

###################################################################################
###################################################################################

class Relation(Element):
	'''
	Specifies relations between data
	
	- size-of
	- (when a flag indicates something exists)
	- Zero or more
	- 1 or more
	'''
	def __init__(self, name, parent):
		Element.__init__(self, name, parent)
		self.elementType = 'relation'
		
		#: Type of relation (size, count, when)
		self.type = None
		
		#: Reference to target
		self.of = None
		
		#: Reference to matching of relation
		self.From = None
		
		#: Parent of this object
		self.parent = parent
		#: Expression to apply to relation when getting value
		self.expressionGet = None
		#: Expression to apply to relation when setting value
		self.expressionSet = None
	
	def getFullnameInDataModel(self):
		'''
		This will get fully qualified name of this element starting with the
		root node of the data model.
		'''
		
		name = self.name
		node = self
		
		while node.parent != None and isinstance(node.parent, DataElement):
			node = node.parent
			name = "%s.%s" % (node.name, name)
		
		return name
		
	def getValue(self, default = False):
		'''
		For a size-of relation get the size
		of the referenced value.  Apply expression
		to the value if needed.
		
		@type	default: Boolean
		@param	default: Should we try for .defaultValue first? (defaults False)
		'''
		
		if self.From != None:
			raise Exception("Only 'of' relations should have getValue method called.")
		
		environment = None
		value = 0
		
		if self.type == 'size':
			
			if default:
				try:
					value = int(self.parent.defaultValue)
				except:
					value = int(self.parent.getInternalValue())
			
			else:
				value = int(self.parent.getInternalValue())
			
			environment = {
				'self' : self.parent,
				'length' : value,
				'size' : value,
				}
		
		elif self.type == 'count':
			if default:
				try:
					value = int(self.parent.defaultValue)
				except:
					value = int(self.parent.getInternalValue())
			else:
				value = int(self.parent.getInternalValue())
			
			environment = {
				'self' : self.parent,
				'count' : value,
				}
		
		elif self.type == 'offset':
			if default:
				try:
					value = int(self.parent.defaultValue)
				except:
					value = int(self.parent.getInternalValue())
			else:
				value = int(self.parent.getInternalValue())
			
			environment = {
				'self' : self.parent,
				'offset' : value,
				}
		else:
			raise Exception("Should not be here!")
		
		if self.expressionGet != None:
			try:
				self.parent._fixRealParent(self.parent)
				return evalEvent(self.expressionGet, environment, self)
			
			finally:
				self.parent._unFixRealParent(self.parent)
		
		return value

	def setValue(self, value):
		'''
		For a size-of relation get the size
		of the referenced value.  Apply expression
		to the value if needed.
		'''
		
		if self.From != None:
			raise Exception("Only 'of' relations should have setValue method called.")
		
		environment = None
		value = int(value)
		
		if self.type == 'size':
			environment = {
				'of' : self.getOfElement(),
				'self' : self.parent,
				'length' : value,
				'size' : int(value),
				}
		
		elif self.type == 'count':
			environment = {
				'of' : self.getOfElement(),
				'self' : self.parent,
				'count' : int(value),
				}
			
		elif self.type == 'offset':
			environment = {
				'of' : self.getOfElement(),
				'self' : self.parent,
				'offset' : int(value),
				}
		
		else:
			raise Exception("Should not be here!")
		
		if self.expressionSet != None:
			try:
				self.parent._fixRealParent(self.parent)
				ret = evalEvent(self.expressionSet, environment, self)
				return ret
			
			finally:
				self.parent._unFixRealParent(self.parent)
		
		return int(value)

	
	def getOfElement(self):
		'''
		Resolve of reference.  We want todo this at
		runtime in case we are copied around.
		'''
		
		if self.of == None:
			return None
		
		obj = self.parent.findDataElementByName(self.of)
		if obj == None:
			# Could element have become an array?
			obj = self.parent.findArrayByName(self.of)
		
		if obj == None:
			print "Fullname:", self.getFullDataName()
			print "Couldn't locate [%s]" % self.of
			raise Exception("Couldn't locate [%s]" % self.of)
		
		return obj
	
	def getFromElement(self):
		'''
		Resolve of reference.  We want todo this at
		runtime in case we are copied around.
		'''
		
		if self.From == None:
			return None
		
		return self.parent.findDataElementByName(self.From)


class Data(ElementWithChildren):
	'''
	Default data container.  Children are Field objects.
	'''
	def __init__(self, name):
		ElementWithChildren.__init__(self, name, None)
		self.elementType = 'data'
		
		#: Name of file containing data to load
		self.fileName = None
		#: Expression that returns data to load
		self.expression = None


class Field(ElementWithChildren):
	'''
	Default bit of data.
	'''
	def __init__(self, name, value, parent):
		ElementWithChildren.__init__(self, name, parent)
		self.elementType = 'field'
		
		#: Value to set on data element
		self.value = value
		#: Indicates type of value. ['string', 'literal', 'hex'] supported.
		self.valueType = None


class Logger(ElementWithChildren):
	'''
	A logger used to log peach events.
	'''
	def __init__(self, parent):
		ElementWithChildren.__init__(self, None, parent)
		self.elementType = 'logger'


def NamespaceToXml(self, parent):
	node = parent.rootNode.createElementNS(None, 'Include')
	parent.appendChild(node)
	
	self._setAttribute(node, 'ns', self.nsName)
	self._setAttribute(node, 'src', self.nsSrc)
	
	return node


class Namespace(Element):
	def __init__(self):
		Element.__init__(self, None, None)
		self.elementType = 'namespace'
		self.nsName = None
		self.nsSrc = None
		self.toXml = new.instancemethod(NamespaceToXml, self, self.__class__)


class PythonPath(Element):
	def __init__(self):
		Element.__init__(self, None, None)
		self.elementType = 'pythonpath'


class Publisher(ElementWithChildren):
	def __init__(self):
		ElementWithChildren.__init__(self, None, None)
		self.elementType = 'publisher'
		self.classStr = None
		self.publisher = None


# ###################################################################
# ## StateMachine Objects

class StateMachine(Mutatable):
	def __init__(self, name, parent):
		Mutatable.__init__(self, name, parent)
		self.elementType = 'statemachine'
		self.initialState = None
		self.onEnter = None
		self.onExit = None

	def findStateByName(self, stateName):
		for child in self:
			if child.elementType == 'state' and child.name == stateName:
				return child
			
		return None
	
	def getRoute(self):
		paths = [child for child in self if child.elementType == 'path']
		return paths


class State(Mutatable):
	def __init__(self, name, parent):
		Mutatable.__init__(self, name, parent)
		self.elementType = 'state'
		self.onEnter = None
		self.onExit = None

	def getChoice(self):
		for child in self:
			if child.elementType == 'stateChoice':
				return child
		
		return None

class StateChoice(ElementWithChildren):
	def __init__(self, parent):
		ElementWithChildren.__init__(self, None, parent)
		self.elementType = 'stateChoice'
		
	def findActionByRef(self, ref):
		for child in self:
			if child.elementType == 'stateChoiceAction' and child.ref == ref:
				return child
			
		return None
		
class StateChoiceAction(Element):
	def __init__(self, ref, type, parent):
		Element.__init__(self, None, parent)
		self.elementType = 'stateChoiceAction'
		self.ref = ref
		self.type = type
		
class Path(Element):
	def __init__(self, ref, parent):
		Element.__init__(self, None, parent)
		self.elementType = 'path'
		self.ref = ref
		self.stop = False

class Strategy(ElementWithChildren):
	def __init__(self, classStr, parent):
		ElementWithChildren.__init__(self, None, parent)
		self.elementType = 'strategy'
		self.params = {}
		self.classStr = classStr

class Action(Mutatable):
	def __init__(self, name, parent):
		Mutatable.__init__(self, name, parent)
		self.elementType = 'action'
		self.type = None
		self.ref = None
		self.when = None
		self.onStart = None
		self.onComplete = None
		self.data = None
		self.template = None
		self.setXpath = None
		self.valueXpath = None
		self.valueLiteral = None
		self.value = None
		self.method = None
		self.property = None

class ActionParam(ElementWithChildren):
	def __init__(self, name, parent):
		ElementWithChildren.__init__(self, name, parent)
		self.elementType = 'actionparam'
		self.type = 'in'
		self.template = None
		self.data = None
		self.value = None

class ActionResult(ElementWithChildren):
	def __init__(self):
		ElementWithChildren.__init__(self, None, None)
		self.elementType = 'actionresult'
		self.template = None
		self.value = None
		
class Mutators(ElementWithChildren):
	def __init__(self, name, parent):
		ElementWithChildren.__init__(self, name, parent)
		self.elementType = 'mutators'

class Mutator(ElementWithChildren):
	def __init__(self, name, parent):
		ElementWithChildren.__init__(self, name, parent)
		self.elementType = 'mutator'
		self.mutator = None
		
class Hint(ElementWithChildren):
	'''
	Hints can be a child of DataElements.  They provide hints
	to mutators about the data element.  Hints can be things
	like finer grained type information like "type=xml" or
	possibly hints about related data values "related=Foo".
	
	Hints are optional bits of meta data.
	'''
	def __init__(self, name, parent):
		ElementWithChildren.__init__(self, name, parent)
		self.elementType = 'hint'
		self.value = None
	
class Custom(DataElement):
	
	def __init__(self, name, parent):
		DataElement.__init__(self, name, parent)
		self.elementType = 'custom'
	
	def handleParsing(self, node):
		'''
		Handle any custom parsing of the XML such as
		attributes.
		'''
		
		raise Exception("handleParsing not implemented")
	
	def handleIncomingSize(self, node, data, pos, parent):
		'''
		Return initial read size for this type.
		'''
		
		# Always at least a single byte
		#return (2,1)
		raise Exception("handleIncomingSize not implemented")
	
	def handleIncoming(self, cntx, data, pos, parent, doingMinMax = False):
		'''
		Handle data cracking.
		'''
		
		#value = str(i)
		#eval("self.%s(value)" % cntx.method)
		
		#return (2, pos)
		
		raise Exception("handleIncoming not implemented")
	
	def getInternalValue(self, sout = None):
		'''
		Return the internal value of this date element.  This
		value comes before any modifications such as packing,
		padding, truncating, etc.
		
		For Numbers this is the python int value.
		'''
		
		#value = None
		#
		## Override value?
		#if self.currentValue != None:
		#	value = self.currentValue
		#
		#else:
		#	# Default value
		#	value = self.defaultValue
		#	
		#	# Relation
		#	value = str(self.getRelationValue(value))
		#	
		#	# Fixup
		#	if self.fixup != None:
		#		self.fixup.fixup.context = self
		#		ret = self.fixup.fixup.dofixup()
		#		if ret != None:
		#			value = ret
		#
		## Apply mbint pack
		#
		#### CUSTOM CODE HERE
		#
		## Write to buffer
		#if sout != None:
		#	sout.write(value, self.getFullDataName())
		#
		## Return value
		#return ret;
		raise Exception("getInternalValue not implemented")
	
	def getLength(self):
		'''
		Get the length of this element.
		'''
		
		return len(self.getValue())
	
	def getRawValue(self, sout = None):
		return self.getInternalValue(sout)
		

# ###################################################################

import cPeach

def DomPrint(indent, node):
	
	tabs = '  ' * indent
	
	if hasattr(node, 'parent') and node.parent != None:
		p = "parent"
	else:
		p = "!! no parent !!"
	
	print tabs + node.elementType + ": " + node.name + ": " + p
	
	if node.hasChildren:
		for child in node._children:
			DomPrint(indent+1, child)

# ###########################################################################

# end
