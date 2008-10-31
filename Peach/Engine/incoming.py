'''
Convert data blob into a Peach DOM based on a template specification.

The data cracker is still early in it's development lifecycle.  Currently
it is capable of using well defined templates to crack data.
 
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

import sys, os, time, struct, types, operator
from Peach.Engine.common import *
from Peach.Engine.dom import *
import Peach

def Debug(level, msg):
	'''
	Debug output.  Uncommenting the following
	print line will cause *lots* of output
	to be displayed.  It significantly slows the
	data cracking process.
	'''
	# Don't show look aheads
	if Peach.Engine.engine.Engine.debug:
		if DataCracker._tabLevel == 0:
			print msg

class DataCracker:
	'''
	This class will try and parse data into a data model.  This
	process will try and best-fit data based on performing look
	aheads with fit-ratings.
	'''
	
	#: Have we recursed into DataCracker?
	_tabLevel = 0
	
	def __init__(self, peachXml, inner = False):
		self.peach = peachXml
		self.deepString = -1
		
		#: To what depth are we looking ahead?
		self.lookAheadDepth = 0
		
		#: Are we looking ahead?
		self.lookAhead = False
		
		#: Do we have all the data?
		self.haveAllData = False
		
		#: Stop when we real the goal node (inclusive)
		self.nodeGoal = None
		
		#: Parent position (if any)
		self.parentPos = 0
		
		if not inner:
			DataCracker._tabLevel = 0
	
	def internalCrackData(self, template, data, method = 'setValue'):
		'''
		This is the internal method called when we recurse into
		crackData.  It will not perform certain operations that should
		be performed on the entire data model instead of sub-portions.
		'''
		
		self.method = method
		(rating, pos) = self._handleNode(template, data, 0, None) #, self.dom)
		Debug(1, "RATING: %d - POS: %d - LEN(DATA): %d" % (rating, self.parentPos+pos, len(data)))
		if pos < len(data)-1:
			Debug(1, "WARNING: Did not consume all data!!!")
		
		Debug(1, "Done cracking stuff")
		return (rating, pos)
	
	def crackData(self, template, data, method = 'setValue'):
		'''
		Crack data based on template.  Set values into data tree.
		
		Will throw an exception (NeedMoreData) if additional data is required.
		The exception contains the minimum amount of additional data needed before
		trying to re-crack the data.
		'''
		
		# Reset all values in tree
		# NOTE: Do not change setValue to method.  We NEEVER want
		#       to run this with setDefaultValue or else DEATH AND DOOM TO U!
		self._resetDataElementValues(template, 'setValue')
		
		#self.method = 'setValue'
		self.method = method
		(rating, pos) = self._handleNode(template, data, 0, None) #, self.dom)
		Debug(1, "RATING: %d - POS: %d - LEN(DATA): %d" % (rating, self.parentPos+pos, len(data)))
		if pos < len(data)-1:
			Debug(1, "WARNING: Did not consume all data!!!")
		
		# Find all our placements and shift elements around.
		placements = []
		for placement in template.getElementsByType(Placement):
			placements.append(placement)
			
		for placement in placements:
			# ----
			
			# We need to update all relations to fully qualified names since we have fully moved
			# nodes around.  There are two categories.  First, of-relations and second relations.
			# We will track these in to arrays of a tuple.
			
			relations = []
			relationsHold = []
			
			Debug(1, "Get all relations")
			for relation in placement.parent.getRelationsOfThisElement():
				relations.append([relation, placement.parent])
				relationsHold.append(relation)
			
			for child in placement.parent.getAllChildDataElements():
				for relation in child.getRelationsOfThisElement():
					if relation not in relationsHold:
						relations.append([relation, child])
						relationsHold.append(relation)
			
			for relation in placement.parent._getAllRelationsInDataModel(placement.parent):
				if relation not in relationsHold:
					relations.append([relation, relation.getOfElement()])
					relationsHold.append(relation)
			
			# ----
			
			if placement.after != None:
				after = template.findDataElementByName(placement.after)
				if after == None:
					raise Exception("Error: Unable to locate element [%s] for placement" % placement.after)
				
				Debug(1, "Moving element [%s] to after [%s]." % (placement.parent.name, after.name))
				Debug(1, "  Pre-name: %s" % placement.parent.getFullDataName())
				Debug(1, "  Found %d relations" % len(relationsHold))
				
				# Do we need to rename our Element?
				placement.parent.origName = placement.parent.name
				if after.parent.has_key(placement.parent.name):
					# Yes... :)
					cnt = 0
					while after.parent.has_key(placement.parent.name):
						placement.parent.name = placement.parent.origName + ("_%d" % cnt)
						cnt += 1
					
					Debug(1, "  Renamed before move from [%s] to [%s]" % (placement.parent.origName,placement.parent.name))
				
				# Insert after after
				after.parent.insert(after.parent.index(after)+1, placement.parent)
				
				# Remove from old place
				placement.parent.parent.__delitem__(placement.parent.origName)
				
				# Update parent
				placement.parent.parent = after.parent
				
				# Remove placement
				placement.parent.__delitem__(placement.name)
				
			elif placement.before != None:
				before = template.findDataElementByName(placement.before)
				if before == None:
					raise Exception("Error: Unable to locate element [%s] for placement" % placement.before)
				
				Debug(1, "Moving element [%s] to before [%s]." % (placement.parent.name, before.name))
				Debug(1, "  Pre-name: %s" % placement.parent.getFullDataName())
				Debug(1, "  Found %d relations" % len(relationsHold))
				
				# Do we need to rename our Element?
				placement.parent.origName = placement.parent.name
				if before.parent.has_key(placement.parent.name):
					# Yes... :)
					cnt = 0
					while before.parent.has_key(placement.parent.name):
						placement.parent.name = placement.parent.origName + ("_%d" % cnt)
						cnt += 1
					
					Debug(1, "  Renamed before move from [%s] to [%s]" % (placement.parent.origName,placement.parent.name))
				
				# Insert after after
				before.parent.insert(before.parent.index(before), placement.parent)
				
				# Remove from old place
				placement.parent.parent.__delitem__(placement.parent.origName)
				
				# Update parent
				placement.parent.parent = before.parent
				
				# Remove placement
				placement.parent.__delitem__(placement.name)
				
				Debug(1, "  Final name: %s" % placement.parent.getFullDataName())
				
			else:
				raise Exception("Error: placement is all null in bad ways!")
		
			# Update relations
			Debug(1, "Update relations")
			for relation, of in relations:
				relation.of = of.getFullnameInDataModel()
				#print "Updating %s to %s" % (relation.getFullname(), relation.of)
			
		Debug(1, "Done cracking stuff")
		#sys.exit(0)
		
		#template.printDomMap()
		
		return (rating, pos)
	
	def _resetDataElementValues(self, node, method):
		'''
		Reset values in data tree to None.
		'''
		
		eval("node.%s(None)" % method)
		
		if hasattr(node, 'rating'):
			delattr(node, 'rating')
		
		if hasattr(node, 'pos'):
			delattr(node, 'pos')
		
		for child in node._children:
			if isinstance(child, Peach.Engine.dom.DataElement):
				self._resetDataElementValues(child, method)
		
		
	def getInitialReadSize(self, template):
		'''
		Determin the initial read size for this template.
		'''
		
		(rating, size) = self._handleBlockSize(template, None, None, None)
		if rating < 4:
			return size
		
		return -1
	
	def _handleNodeSize(self, node, data, pos, parent):
		'''
		Try and determine size of a node.
		
		Rating of:
		
		  1 - Exact
		  2 - Exact, but not everything
		  3 - Not complete to block yet
		  4 - Nadda
		
		'''
		
		if node == None:
			raise Exception("Node is None, bailing!")
		
		if node.elementType == 'string':
			(rating, size) = self._handleStringSize(node, data, pos, parent)
			
		elif node.elementType == 'number':
			(rating, size) = self._handleNumberSize(node, data, pos, parent)
			
		elif node.elementType == 'block' or node.elementType == 'template':
			(rating, size) = self._handleBlockSize(node, data, pos, parent)
			
		elif node.elementType == 'blob':
			(rating, size) = self._handleBlobSize(node, data, pos, parent)
		
		elif node.elementType == 'custom':
			(rating, size) = self._handleCustomSize(node, data, pos, parent)
		
		elif node.elementType == 'flags':
			(rating, size) = self._handleFlagsSize(node, data, pos, parent)
		
		elif node.elementType == 'choice':
			rating = 1
			size = 1
		
		else:
			raise Exception("Unknown elementType: %s" % node.elementType)
	
		return (rating, size)
	
	def _handleStringSize(self, node, data, pos, parent):
		
		Debug(1, "_handleStringSize(%s)" % node.name)
		
		## TODO: Handle size relation!
		
		if node.defaultValue != None and node.isStatic:
			node.length = len(node.defaultValue)
		
		if node.length != None:
			return (1, int(node.length))
		
		if node.defaultValue != None:
			return (2, len(node.defaultValue))
		
		return (2, 1)
	
	def _handleBlobSize(self, node, data, pos, parent):
		
		Debug(1, "_handleBlobSize(%s)" % node.name)
		
		## TODO: Handle size relation!
		
		if node.defaultValue != None and node.isStatic:
			node.length = len(node.defaultValue)
		
		if node.length != None:
			return (1, int(node.length))
		
		# This probably isn't a good idea, so lets not do it :)
		#if node.defaultValue != None:
		#	return (2, len(node.defaultValue))
		
		return (2, 1)
	
	def _handleNumberSize(self, node, data, pos, parent):
		return (1, node.size / 8)
	
	def _handleFlagsSize(self, node, data, pos, parent):
		return (1, node.length / 8)
	
	def _handleBlockSize(self, node, data, pos, parent):
		
		## TODO: Handle maxOccurs!
		
		Debug(1, "_handleBlockSize(%s)" % node.name)
		
		curSize = 0
		curRating = 0
		
		for child in node._children:
			
			if not isinstance(child, DataElement):
				continue
			
			(rating, size) = self._handleNodeSize(child, data, pos, node)
			if rating < 3:
				curSize += size
				curRating = rating
			
			elif rating == 3:
				curSize += size
				curRating = rating
				break
			
			else:
				curRating = 3
				break
		
		return (curRating, curSize)
	
	def _GetTemplateByName(self, str):
		'''
		Get the object indicated by ref.  Currently the object must have
		been defined prior to this point in the XML
		'''
		
		origStr = str
		baseObj = self.peach
		
		# Parse out a namespace
		
		if str.find(":") > -1:
			ns, tmp = str.split(':')
			str = tmp
			
			# Check for namespace
			if hasattr(self.context.namespaces, ns):
				baseObj = getattr(self.context.namespaces, ns)
			else:
				raise Exception("Unable to locate namespace")
		
		for name in str.split('.'):
			
			# check base obj
			if hasattr(baseObj, name):
				baseObj = getattr(baseObj, name)
				
			# check templates
			elif hasattr(baseObj, 'templates') and hasattr(baseObj.templates, name):
				baseObj = getattr(baseObj.templates, name)
			
			else:
				raise Exception("Could not resolve ref", origStr)
		
		return baseObj
	
	def _getRootParent(self, node):
		
		root = node
		while hasattr(root, 'parent') and root.parent != None:
			root = root.parent
		
		return root
	
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
	
	def _handleNode(self, node, data, pos, parent = None, doingMinMax = False):
		
		Debug(1, "_handleNode(%s): %s >>Enter" % (node.name, node.elementType))
		
		# 0. Are we okay?
		
		if pos > len(data):
			raise Exception("Running past data!")
		
		# 1. do we have a node?
		
		if node == None:
			raise Exception("Node is None, bailing!")
		
		origPos = pos
		
		# Cache of relations
		#print "Caching relation"
		#node.relationOf = node.getRelationOfThisElement()
		
		# 2. check for when relation
		
		if node.HasWhenRelation():
			rel = node.GetWhenRelation()
			
			environment = {
				#'Peach' : self.engine.peach,
				'self' : node,
				'pos' : pos,
				'data' : data
				}
			
			Debug(1, "_handleNode: When: Running expression")
			self._fixRealParent(node)
			
			if not evalEvent(rel.when, environment, node):
				# Remove this node from data tree
				self._unFixRealParent(node)
				node.parent.__delitem__(node.name)
				
				Debug(1, "_handleNode: When: Returned False. Returning 1.")
				node.relationOf = None
				return (1, pos)
		
			self._unFixRealParent(node)
			Debug(1, "_handleNode: When: Returned True.")
		
		# 3.1. Skipp around if we have an offset relations
		popPosition = None
		if isinstance(node, DataElement):
			relation = node.getRelationOfThisElement('offset')
			if relation != None and relation.type == 'offset':
				# We need to move this show!
				try:
					Debug(1, "Found offset relation")
					Debug(1, "Origional position saved as %d" % (self.parentPos+pos))
					popPosition = pos
					pos = int(relation.getValue(True))
					Debug(1, "Changed position to %d" % (self.parentPos+pos))
			
				except:
					raise
		
		# Would be nice to have our current pos in scripting :)
		node.possiblePos = pos
		
		## Check for count relation, verify > 0
		if node.minOccurs == 0:
			relation = node.getRelationOfThisElement('count')
			if relation != None and node.parent != None:
				occurs = int(relation.getValue(True))
				if occurs == 0:
					# Remove element
					node.parent.__delitem__(node.name)
					
					# Remove relation (else we get errors)
					relation.parent.relations.remove(relation)
					relation.parent.__delitem__(relation.name)
					
					# We passed muster...I think :)
					rating = 2
					pos = origPos
					
					Debug(1, "_handleNode(%s): Zero count on array, removed <<EXIT")
					return (rating, pos)
		
		# 3.5. Save origional copy
		
		origionalNode = node.copy(node.parent)
		
		# 4. do the crazy!
		
		if node.elementType == 'string':
			(rating, pos) = self._handleString(node, data, pos, parent, doingMinMax)
		
		elif node.elementType == 'number':
			(rating, pos) = self._handleNumber(node, data, pos, parent, doingMinMax)
		
		elif node.elementType in ['block', 'template', 'choice']:
			
			# First -- Determin if we know the size of this block via a
			#          size-of relation
			
			length = None
			relation = node.getRelationOfThisElement('size')
			if relation != None and node.getRelationOfThisElement('offset') == None and node.parent != None:
				try:
					
					length = relation.getValue(True)
					Debug(1, "-----> FOUND BLOCK OF RELATION [%s] <-----" % repr(length))
					fullName = relation.parent.getFullname()
					Debug(1, "Size-of Fullname: " + fullName)
					Debug(1, "node Fullname: " + node.getFullname())
					
					#length = relation.getValue()
					Debug(1, "Size-of Length: %s" % length)

					# Verify we are not inside the "of" portion
					if fullName.find(node.getFullname()+".") == 0:
						length = None
						Debug(1, "!!! Not using relation, inside of OF element")

				except:
					length = None
			
			elif node.hasLength():
				length = node.getLength()
				Debug(1, "-----> Block has known legnth: %d" % length)
			
			# Only if we have a length, and we are not already the top
			# level element.  This will prevent infinit recursion into
			# the data cracker if we have a <Block length="10" /> type
			# situation.
			if length != None and node.parent != None:
				# Make sure we have the data
				if len(data) < (pos+length):
					if not self.haveAllData:
						node.relationOf = None
						raise NeedMoreData(length, "")
					
					else:
						rating = 4
						pos = pos + length
				
				else:
					Debug(1, "---- About to Crack internal Block ----")
					
					# Parse this node on it's own
					cracker = DataCracker(self.peach, True)
					cracker.haveAllData = True
					cracker.parentPos = pos+self.parentPos
					data = data[pos:pos+length]
					
					# Do we have a transformer, if so decode the data
					if node.transformer != None:
						try:
							Debug(1, "Found transformer, decoding...")
							data = node.transformer.transformer.decode(data)
						
						except:
							Debug(1, "Transformer threw exception!")
							pass
					
					# We need to remove the parent temporarily to
					# avoid a recursion issue.
					parent = node.parent
					node.parent = None
					node.realParent = parent
					
					try:
						(rating, crackpos) = cracker.internalCrackData(node, data, self.method)
						if rating == 0:
							rating = 1
						
					finally:
						# We need to update the positions of each child
						# to be + node.pos.
						#
						# Note: We are doing this in a finally to make
						#   sure the values in peach validation are
						#   correct.
						for c in node.getAllChildDataElements():
							if hasattr(c, 'pos') and c.pos != None:
								c.pos += pos
						
					node.parent = parent
					node.realParent = None
					node.pos = pos
					node.rating = rating
					
					pos += length
					
					# Verify we used all the data
					if crackpos != len(data):
						Debug(1, "---- Crackpos != len(data): %d != %d ----" % (self.parentPos+crackpos, len(data)))
						rating = 4
					
					Debug(1, "---- Finished with internal block (%d:%d) ----" % (rating, self.parentPos+pos))
			
			else:
				if node.elementType == 'choice':
					(rating, pos) = self._handleChoice(node, data, pos, parent, doingMinMax)
				else:
					(rating, pos) = self._handleBlock(node, data, pos, parent, doingMinMax)
		
		elif node.elementType == 'blob':
			(rating, pos) = self._handleBlob(node, data, pos, parent, doingMinMax)
			Debug(1, "---] pos = %d" % (self.parentPos+pos))
		elif node.elementType == 'custom':
			(rating, pos) = self._handleCustom(node, data, pos, parent, doingMinMax)
			Debug(1, "---] pos = %d" % (self.parentPos+pos))
		elif node.elementType == 'flags':
			(rating, pos) = self._handleFlags(node, data, pos, parent, doingMinMax)
		elif node.elementType == 'seek':
			(rating, pos) = self._handleSeek(node, data, pos, parent, doingMinMax)
		
		else:
			raise str("Unknown elementType: %s" % node.elementType)
		
		## Check our goal, want todo this before we parse an array (if any)
		
		if self.nodeGoal != None and self.nodeGoal == node.getFullDataName():
			# Throw the required exception :)
			raise ReachedGoalNode(raiting, pos, node)
		
		## Handle minOccurs == 0
		elif rating >= 3 and node.minOccurs == 0 and not doingMinMax:
			
			# Remove node and increase rating.
			Debug(1, "Rating was poor and minOccurs == 0, remoing element and upping rating.")
			
			# Remove relation (else we get errors)
			for relation in node.getRelationsOfThisElement():
				relation.parent.relations.remove(relation)
				relation.parent.__delitem__(relation.name)
			
			node.parent.__delitem__(node.name)
			rating = 2
			pos = origPos
		
		## 5. Handle maxOccurs > 1
		
		elif rating < 3 and node.maxOccurs > 1 and not doingMinMax:
			Debug(1, "*** NOde Occures more then once!")
			occurs = 1
			newRating = rating
			newCurPos = pos
			dom = None
			curpos = None
			maxOccurs = node.maxOccurs
			name = node.name
			goodLookAhead = None
			hasCountRelation = False
			isDeterministic = self._doesNodeHaveStatic(node)
			
			try:
				
				# Locate any count restrictions and update maxCount to match
				
				Debug(1, "-- Looking for Count relation...")
				relation = node.getRelationOfThisElement('count')
				if relation != None and relation.type == 'count' and node.parent != None:
					try:
						maxOccurs = int(relation.getValue(True))
						Debug(1, "@@@ Found count relation [%d]" % maxOccurs)
						hasCountRelation = True
					
					except:
						pass
				
				# Hack for fixed length arrays to remove lookAheads
				if node.occurs != None:
					maxOccurs = node.occurs
					hasCountRelation = True
				
				node.relationOf = None
				Debug(1, "@@@ Entering while loop")
				while occurs < maxOccurs and rating < 3:
					if popPosition != None:
						print "@@@ Note: popPosition is not null!"
					
					Debug(1, "@@@ In While, newCurPos=%d" % (self.parentPos+newCurPos))
					
					# 0. Are we out at end of stream?
					if self.haveAllData and newCurPos >= len(data):
						Debug(1, "@ Exiting while loop, end of data! YAY!")
						break
					else:
						Debug(1, "@ Have enough data to try again: %d < %d" % (newCurPos, len(data)))
					
					# 1. Make a copy so we don't overwrite
					#    existing node
					nodeCopy = origionalNode.copy(node.parent)
					nodeCopy.name = name + "-%d" % occurs
					
					# 1.1 Add to parent
					try:
						node.parent.insert(node.parent.index(node)+occurs, nodeCopy)
					except:
						print "Node:", node.name
						print "Node.parent:", node.parent.name
						
						for c in node.parent:
							print "Child:", c.name
						
						raise

					# 1.2. Run onArrayNext
					
					if DataCracker._tabLevel == 0 and nodeCopy.onArrayNext != None:
						evalEvent( node.onArrayNext, { 'node' : nodeCopy }, node )
					
					# 2. Check out look-ahead (unless we have count relation)
					if (not isDeterministic) and (not hasCountRelation) and self._nextNode(nodeCopy) != None:
						Debug(1, "*** >> node.name: %s" % node.name)
						Debug(1, "*** >> nodeCopy.name: %s" % nodeCopy.name)
						Debug(1, "*** >> LookAhead")
						
						newRating = self._lookAhead(nodeCopy, data, newCurPos, None, False)
						Debug(1, "*** << LookAhead [%d]" % newRating)
						
						# If look ahead was good, save and check later.
						if newRating < 3:
							goodLookAhead = newRating
						
					# 3. Do actual
					Debug(1, "*** >> nodeCopy.name: %s" % nodeCopy.name)
					Debug(1, "*** >> DOING ACTUAL HANDLENODE")
					
					origNewCurPos = newCurPos
					(newRating, newCurPos) = self._handleNode(nodeCopy, data, newCurPos, None, True)
					if newCurPos < origNewCurPos:
						raise Exception("WHoa!  We shouldn't have moved back in position there... [%d:%d]" % origNewCurPos, newCurPos)
					
					# Verify we didn't break a good lookahead
					if not hasCountRelation and newRating < 3 and not self.lookAhead and goodLookAhead != None:
						lookAheadRating = self._lookAhead(nodeCopy, data, newCurPos, None, False)
						if lookAheadRating >= 3:
							del node.parent[nodeCopy.name]
							Debug(1, "*** Exiting min/max: We broke a good lookAhead!")
							break
					
					# 4. Verify high enough rating
					if newRating < 3 and not self.lookAhead:
						Debug(1, "*** That worked out!")
						pos = curpos = newCurPos
						rating = newRating
						
						# First time through convert position 0 node
						if occurs == 1:
							# First fix up our first node
							index = node.parent.index(node)
							del node.parent[node.name]
							
							node.array = node.name
							node.name = node.name + "-0"
							node.arrayPosition = 0
							node.arrayMinOccurs = node.minOccurs
							node.arrayMaxOccurs = node.maxOccurs
							node.minOccurs = 1
							node.maxOccurs = 1
						
							node.parent.insert(index, node)
						
						# Next fix up our copied node
						nodeCopy.array = node.array
						nodeCopy.arrayPosition = occurs
						nodeCopy.arrayMinOccurs = node.arrayMinOccurs
						nodeCopy.arrayMaxOccurs = node.arrayMaxOccurs
						nodeCopy.minOccurs = 1
						nodeCopy.maxOccurs = 1
						
					else:
						Debug(1, "*** Didn't work out!")
						node.parent.__delitem__(nodeCopy.name)
						break
					
					occurs += 1
					
					Debug(1, "@@@ Looping, occurs=%d, rating=%d" % (occurs, rating))
			
				Debug(1, "@@@ Exiting While Loop")
				
			except:
				#pass
				raise
			
			if curpos != None:
				if popPosition != None:
					pos = popPosition
					Debug(1, "Popping position back to %d" % (self.parentPos+pos))
				
				Debug(1, "@@@ Returning a curpos=%d, pos=%d, newCurPos=%d, occuurs=%d" %(self.parentPos+curpos, self.parentPos+pos, self.parentPos+newCurPos, occurs))
				node.relationOf = None
				return (rating, curpos)
		
		if popPosition != None:
			pos = popPosition
			Debug(1, "Popping position back to %d" % (self.parentPos+pos))
		
		Debug(1, "_handleNode(%s): type=%s, realpos=%d, pos=%d, rating=%d <<EXIT" % (node.name, node.elementType, self.parentPos+pos, pos, rating))
		node.relationOf = None
		return (rating, pos)
	
	def _lookAhead(self, node, data, pos, parent, minMax = True):
		'''
		Look ahead one step and get the next rating.  Looking ahead
		from a current node is more complex than it might first seem.
		
		For example, we might be the 2nd to last element in a block
		that is part of a larger block (but not the last element). We
		will need to be tricky inorder to properly look ahead at the
		rest of the document.
		'''
		
		if node == None:
			return 1
		
		if pos > len(data):
			Debug(1, "_lookAhead(): pos > len(data), no lookahead")
			return 4
		
		## Setup a few variables
		
		DataCracker._tabLevel += 1
		
		self.lookAhead = True
		self.lookAheadDepth += 1
		
		origNode = node
		origParent = parent
		
		## Locate our goal (first static node)
		
		# If we can locate a static node we will only look
		# ahead to that node instead of the entire data model
		# this will hopefully keep the flexability of the look
		# ahead based parsing, but remove the major speed
		# issues.
		
		origionalGoal = self.nodeGoal
		#goal = self._nextStaticNode(node)
		#if goal != None:
		#	self.nodeGoal = goal.getFullDataName()
		#	print "lookAhead: Goal of [%s]" % self.nodeGoal
		#else:
		#	print "lookAhead: No goal in sight :("
		
		## First lets copy the data model
		
		root = origNode.getRootOfDataMap().copy(None)
		root._FixParents()
		
		node = root.findDataElementByName(origNode.getFullDataName())
		sibling = self._nextNode(node)
		
		if node == None:
			raise Exception("Node should not be null here! [%s]" % origNode.getFullDataName())
		
		if origParent != None:
			parent = root.findDataElementByName(origParent.getFullDataName())
		
		## If we could have more than one of the curret node
		## we will try that node again UNLESS we minMax == False
		
		# Why are we doing this?  For String Arrays?
		
		if node.maxOccurs > 1 and minMax:
			Debug(1, "_lookAhead(): look ahead for node")
			
			try:
				(rating, pos) = self._handleNode(node, data, pos, parent)
				
				# If we have a good rating return it
				if rating < 3:
					
					self.lookAheadDepth -= 1
					if self.lookAheadDepth == 0:
						self.lookAhead = False
					
					self.lookAhead = False
					DataCracker._tabLevel -= 1
					return rating
				
			except NeedMoreData:
				self.lookAheadDepth -= 1
				if self.lookAheadDepth == 0:
					self.lookAhead = False
				
				DataCracker._tabLevel -= 1
				return 4
		
		## Now lets try that sibling if we can
		
		if sibling == None:
			
			# if no sibling than everything is okay
			
			Debug(1, "_lookAhead(): node.nextSibling() ==  None, returning 1")
			rating = 1
		
		else:
			
			try:
				Debug(1, "_lookAhead(): look ahead for node.Sibling(): %s->%s" % (node.name,sibling.name))
				(rating, pos) = self._handleNode(sibling, data, pos, parent)
			
			except ReachedGoalNode, e:
				self.nodeGoal = None
				rating = r.rating
				pos = r.pos
				print "lookAhead: Found goal [%s]: %d" % (self.nodeGoal, rating)
				
			except NeedMoreData:
				rating = 4
				
		self.nodeGoal = origionalGoal
		
		self.lookAheadDepth -= 1
		if self.lookAheadDepth == 0:
			self.lookAhead = False
		
		DataCracker._tabLevel -= 1
		if pos < len(data):
			return rating + 1
		
		else:
			return rating
		
	def _isTokenNext(self, node):
		'''
		Determine if a token node follows.  Other sized
		nodes can be between them.
		'''
		
		staticNode = None
		length = 0
		n = node
		while self._nextNode(n) != None:
			n = self._nextNode(n)
			
			if n.isStatic:
				staticNode = n
				break
			
			s = self._hasSize(n)
			if s == None:
				return None
			
			length += s
		
		# Shouldn't need this check
		if staticNode == None:
			return None
		
		return (staticNode, length)
		
	def _isLastUnsizedNode(self, node):
		'''
		Determin if the following nodes all have known
		sizes.  If they do we can determin our size.
		'''
		
		length = 0
		n = node
		while self._nextNode(n) != None:
			n = self._nextNode(n)
			s = self._hasSize(n)
			if s == None:
				return None
			
			length += s
		
		return length

	def _hasSize(self, node):
		'''
		Determin if data element has a size
		and return it or None
		'''
		
		# TODO:
		#  - Relations
		#  - Blocks
		#  - Side cases
			
		if isinstance(node, String) or isinstance(node, Blob):
			if node.length != None:
				return node.length
			
			if node.isStatic:
				return len(node.defaultValue)
		
		elif isinstance(node, Number):
			return int(node.size) / 8
		
		elif isinstance(node, Block):
			return None
		
		elif isinstance(node, Flags):
			return int(node.size) / 8
	
	def _doesNodeHaveStatic(self, node):
		'''
		Return true if node or it's children is static
		'''
		
		if node.isStatic:
			return True
		
		for c in node.getAllChildDataElements():
			if c.isStatic:
				return True
		
		return False
		
	def _nextStaticNode(self, node):
		'''
		Locate the next static node or None
		'''
		
		while node != None and not node.isStatic:
			node = self._nextNode(node)
		
		return node
		
	def _nextNode(self, node):
		'''
		Locate the next node.
		
		1. Do we have a .nextSibling?
		2. Does are parent have .nextSibling?
		...
		
		Need to also support escaping Choice blocks!		
		'''
		
		if node == None:
			return None
		
		try:
			Debug(1, "_nextNode(%s)" % node.name)
		
		except:
			Debug(1, "_nextNode: %s" % repr(node))
			raise
		
		if not isinstance(node, Peach.Engine.dom.DataElement) or \
			node.elementType == 'template':
			
			#Debug(1, "_nextNode(%s): not data element or is template")
			
			return None
		
		# Try and escape Choice blocks.
		if node.parent != None and node.parent.elementType == 'choice':
			node = node.parent
		
		nextNode = node.nextSibling()
		while nextNode != None and not isinstance(nextNode, Peach.Engine.dom.DataElement):
			nextNode = nextNode.nextSibling()
		
		if nextNode != None and isinstance(nextNode, Peach.Engine.dom.DataElement):	
			return nextNode
		
		return self._nextNode(node.parent)

	def _adjustRating(self, rating, lookAheadRating):
		if lookAheadRating == 2 and rating == 1:
			rating = 2
		elif rating < 3 and lookAheadRating > 2:
			return rating - 1
		elif rating == 3 and lookAheadRating > 3:
			return rating - 1
		
		return rating
		
	def _handleChoice(self, node, data, pos, parent, doingMinMax = False):
		Debug(1, "---> %s (%d)" % (node.name,self.parentPos+pos))
		
		# Default is failure
		rating = 4
		curpos = pos
		node.currentElement = None
		
		# Our list can shrink/expand as we go
		# so lets copy the list up front.
		children = []
		for child in node._children:
			if isinstance(child, DataElement):
				children.append(child)
		
		# Look for first child that matches, forget the rest.
		for child in children:
			
			# Skip any children created during array expantion
			# they should already have values 'n all that good
			# stuff :)
			if hasattr(child, 'array') and child.array != None:
				continue
			
			# Try this child
			
			Debug(1, "_handleChoice(): Tring child [%s]" % child.name)
			
			(childRating, newpos) = self._handleNode(child, data, curpos)
			if child.currentValue != None and len(child.currentValue) > 30:
				Debug(1, "_handleChoice(): Rating: (%d) [%s]: %s = [%s]" % (childRating, repr(child.defaultValue), child.name, child.currentValue[:30]))
			else:
				Debug(1, "_handleChoice(): Rating: (%d) [%s]: %s = [%s]" % (childRating, repr(child.defaultValue), child.name, child.currentValue))
			
			# Check if we are keeping this child or not
			if childRating > 2:
				Debug(1, "_handleChoice(): Child did not meet requirements, NEXT!")
				continue
			
			# Keep this child
			Debug(1, "_handleChoice(): Keeping child [%s]" % child.name)
			node.currentElement = child
			rating = childRating
			curpos = newpos
			
			# TODO: Lets not remove the kids, but for now to keep things
			#       simple, we will look like a block after this so to
			#       speek.
			for c in children:
				if c != node.currentElement:
					Debug(1, "_handleChoice(): Removing unused child [%s]" % c.name)
					node.__delitem__(c.name)
			
			break
		
		Debug(1, "Choice rating: %d" % rating)
		Debug(1, "<--- %s (%d through %d)" % (node.name,self.parentPos+pos,self.parentPos+newpos))
		
		if rating < 3:
			node.pos = pos
			node.rating = rating
			
		return (rating, curpos)
	
	def _handleBlock(self, node, data, pos, parent, doingMinMax = False):
		
		# Not going to handle alignment right now :)
		
		Debug(1, "---> %s (%d)" % (node.name,self.parentPos+pos))
		
		rating = 0
		ratingCnt = 0
		ratingTotal = 0
		curpos = pos
		
		# Our list can shrink/expand as we go
		# so lets copy the list up front.
		children = []
		for child in node._children:
			children.append(child)
		
		for child in children:
			
			if not isinstance(child, DataElement) and not isinstance(child, Seek):
				continue
			
			# Skip any children created during array expantion
			# they should already have values 'n all that good
			# stuff :)
			if hasattr(child, 'array') and child.array != None:
				continue
			
			# Do the needfull
			
			ratingCnt += 1
			
			(childRating, newpos) = self._handleNode(child, data, curpos)
			if child != None and child.currentValue != None and len(child.currentValue) > 30:
				if child.defaultValue != None and len(repr(child.defaultValue)) > 30:
					Debug(1, "_handleBlock(%s): Rating: (%d) [%s]: %s = [%s]" % (node.name, childRating, repr(child.defaultValue)[:30], child.name, child.currentValue[:30]))
				else:
					Debug(1, "_handleBlock(%s): Rating: (%d) [%s]: %s = [%s]" % (node.name, childRating, repr(child.defaultValue), child.name, child.currentValue[:30]))
			else:
				if child.defaultValue != None and len(repr(child.defaultValue)) > 30:
					Debug(1, "_handleBlock(%s): Rating: (%d) [%s]: %s = [%s]" % (node.name, childRating, repr(child.defaultValue)[:30], child.name, repr(child.currentValue)))
				else:
					Debug(1, "_handleBlock(%s): Rating: (%d) [%s]: %s = [%s]" % (node.name, childRating, repr(child.defaultValue), child.name, repr(child.currentValue)))

			if childRating > 2:
				Debug(1, "_handleBlock(%s): Child rating sucks, exiting" % node.name)
				rating = childRating
				break
			
			ratingTotal += childRating
			if childRating > rating:
				rating = childRating
			
			curpos = newpos
		
		
		Debug(1, "BLOCK RATING: %d" % rating)
		Debug(1, "<--- %s (%d)" % (node.name,self.parentPos+pos))
		
		if rating < 3:
			node.pos = pos
			node.rating = rating
		
		return (rating, curpos)
		
	def _getDataFromFullname(self, dom, name):
		'''
		Take a fullname (blah.blah.blah) and locate
		it in our data dom.
		'''
		dom = self._getRootParent(dom)
		obj = dom
		
		for part in name.split('.'):
			Debug(2, "_getDataFromFullname(%s): [%s]" % (name, obj.name))
			if part == obj.name:
				continue
			
			obj = obj[part]
		
		return obj[obj.name]
	
	def _handleString(self, node, data, pos, parent, doingMinMax = False):
		'''
		Returns the rating and string.  The rating is
		how well we matched.
		
		Rating:
		
		1 - BEST	If our default matched and look ahead is 1
		2 - GOOD	If our default matched and look ahead is 2
		3 - OK		If our look ahead is 1 or 2
		4 - MPH		If look ahead is 3 or 4
		'''
		
		# We just break from this to return values
		while True:
			
			Debug(1, "---> %s (%d)" % (node.name,self.parentPos+pos))
			
			self.deepString += 1
			
			rating = 0
			newpos = 0
			length = None
			
			# If we are static we should know our
			# length.
			if node.length == None and node.isStatic:
				try:
					node.length = len(node.defaultValue)
				except:
					raise PeachException("Error: String %s doens't have a default value, yet is marked isStatic." % node.name)
			
			# Determin if we have a size-of relation
			# and set our length accordingly.
			relation = node.getRelationOfThisElement('size')
			if relation != None and relation.type == 'size':
				# we have a size-of relation
				Debug(1, "** FOUND SIZE OF RELATION ***")
				
				fullName = relation.parent.getFullname()
				Debug(1, "Size-of Fullname: " + fullName)
				
				length = relation.getValue(True)
				Debug(1, "Size-of Length: %s" % length)
				
				# Value may not be available yet
				try:
					length = int(length)
				except:
					pass
			
			# Do we know our length?
			if node.getLength() != None or length != None:
				
				if length == None:
					length = node.getLength()
				
				Debug(1, "_handleString: Found length of: %d" % length)
				
				if node.type == 'wchar':
					length = length * 2
				
				if len(data) < (pos + length):
					if not self.haveAllData:
						raise NeedMoreData((pos + length) - len(data), "")
					
					else:
						rating = 4
						value = ""
						newpos = pos + length
						Debug(1, "_handleString: Want %d, have %d" % ((pos+length), len(data)))
						break
				
				else:
					
					value = data[pos:pos+length]
					newpos = pos + length
					defaultValue = node.defaultValue
					rating = 2
					
					if node.isStatic:
						if node.type == 'wchar':
							# convert to ascii string
							defaultValue = node.defaultValue.decode("utf-16le")
					
						if value != defaultValue and node.isStatic:
							Debug(1, "%s_handleString: %s: Bad match, static, but default didn't match [%s != %s]" % ('\t'*self.deepString, node.name, repr(value), repr(defaultValue)))
							rating = 4
						
						else:
							Debug(1, "%s_handleString: %s: By length [%s]" % ('\t'*self.deepString, node.name, repr(value)))
							rating = 1
					
					break
				
			# Are we null terminated?
			elif node.nullTerminated:
				value = ''
				
				newpos = pos
				rating = 666
				
				if node.type != 'wchar':
					newpos = data.find('\0', pos)
					
					if newpos == -1:
						if self.haveAllData:
							rating = 4
							value = ''
							newpos = pos
						
						else:
							raise NeedMoreData(1, "Looking for string null terminator")
					
					newpos += 1	# find leaves us a position down, need to add one to get the null
					value = data[pos:newpos]
					rating = 2
					break
				
				elif node.type == 'wchar':
					
					newpos = data.find("\0\0", pos)
					if newpos == -1:
						if self.haveAllData:
							rating = 4
							newpos = pos
							value = ''
							Debug(1, "data.find(00) returned -1, pos: %d" % pos)
							break
						
						else:
							raise NeedMoreData(1, "Looking for string null terminator")
					
					if newpos == pos:
						Debug(1, "Found empty terminated wchar string: [%s]" % repr(value))
						value = ""
						newpos += 2
						rating = 2
						break
					
					newpos += 3 # find leaves us a position down, need to add one to get the null
					value = data[pos:newpos-2]
					rating = 2
					
					if len(value) % 2 != 0:
						value += '\0'
					
					if value == '\0' or value == '\0\0':
						value = ""
					
					# HACK for WCHAR
					for i in xrange(1, len(value), 2):
						if value[i] != '\0':
							value = value[:i] + '\0' + value[i+1:]
					
					for i in xrange(0, len(value), 2):
						if ord(value[i]) > 127:
							value = value[:i] + 'a' + value[i+1:]
					
					Debug(1, "Found null terminated wchar string: [%s]" % repr(value))
					Debug(1, "pos: %d; newpos: %d" % (pos, newpos))
					
					break
				
			elif node.isStatic:
				
				# first, look for our defaultValue
				if node.defaultValue == None:
					raise PeachException("Error: %s is marked as static but has no default value." % node.name)
				
				Debug(1, "%s_handleString: %s: Found default value, doing checks" % ('\t'*self.deepString, node.name))
				
				if node.type == 'wchar':
					defaultValue = str(node.defaultValue.decode("utf-16le"))
					
				else:
					defaultValue = node.defaultValue
				
				newpos = pos+len(defaultValue)
				value = data[pos:newpos]
				if value == defaultValue:
						rating = 2
						break
				
				else:
						rating = 4
						Debug(1, "%s_handleString: %s: No match [%s == %s] @ %d" % ('\t'*self.deepString, node.name, repr(data[newpos:newpos+len(defaultValue)]), repr(defaultValue), pos))
						break
				
			else:
				
				# If we don't have a length, we try for a best fit
				# by adjusting the position until our look ahead has a rating
				# of 1 or 2.
					
				# Are we the last data element?
				if self._nextNode(node) == None:
					if not self.haveAllData:
						#self.haveAllData = True
						raise NeedMoreData(-1, "")
					
					else:
						# Keep all the data :)
						Debug(1, "_handleString: Have all data, keeping it for me :)")
						value = data[pos:]
						newpos = len(data)
						rating = 1
						#break
						
				elif self._isLastUnsizedNode(node) != None:
					# Are all other nodes of deterministic size?
					
					Debug(1, "_handleString: self._isLastUnsizedNode(node)")
					
					if not self.haveAllData:
						#self.haveAllData = True
						raise NeedMoreData(-1, "")
					
					length = self._isLastUnsizedNode(node)
					newpos = len(data) - length
					value = data[pos:newpos]
					rating = 1
				
				elif self._isTokenNext(node) != None:
					# Is there an isStatic ahead?
					
					staticNode, length = self._isTokenNext(node)
					
					Debug(1, "_handleString: self._isTokenNext(%s): %s" % (node.name, staticNode.name))
					
					# 1. Locate staticNode position
					val = staticNode.getValue()
					Debug(1, "Looking for [%s][%s]" % (repr(val), repr(data[pos:])))
					valPos = data[pos:].find(val)
					if valPos == -1:
						if self.haveAllData:
							newpos = pos
							value = ""
							rating = 4
							Debug(1, " :( Have all data")
							break
						
						else:
							Debug(1, " --- NEED MORE DATA ---")
							raise NeedMoreData(1, "")
					
					# 2. Subtract length
					newpos = (pos+valPos) - length
					
					# 3. Yuppie!
					value = data[pos:newpos]
					rating = 1
					
					Debug(1, "Found: [%d][%d:%d][%s]" % (length, self.parentPos+pos, self.parentPos+newpos, value))
				
				else:
					
					# Will will suckup bytes one by one check the
					# look ahead each time to see if we should keep
					# sucking.
					#
					# Note: Turns out running the lookAhead each time is slow.
					
					lookRating = 666
					newpos = pos
					dataLen = len(data)
					
					# If we have a following static just scan
					# for it instead of calling lookAhead.
					nextNode = self._nextNode(node)
					if nextNode.isStatic:
						nextValue = nextNode.getValue()
						nextValueLen = len(nextValue)
						
						newpos = data.find(nextValue, pos)
						if newpos == -1:
							if self.haveAllData:
								value = ""
								rating = 4
								break
							else:
								raise NeedMoreData(1, "Couldn't locate nextValue [%s] in [%s]" % (repr(nextValue), repr(data[pos:])))
						
						value = data[pos:newpos]
						rating = 2
						break
					
					# This loop is slow! Reading one char at a time!
					# We should try a reading at least 2-5 chars at once.
					while lookRating > 2 and newpos < dataLen:
						newpos += 1
						lookRating = self._lookAhead(node, data, newpos, parent)
					
					value = data[pos:newpos]
					
					if lookRating > 2:
						rating = 3
					
					else:
						rating = 2
					
					break
			
			break
		
		# Deal with wchar
		if node.type == 'wchar':
			try:
				value = value.decode("utf-16le").encode("latin-1")
			except:
				print "Error decoding: ", repr(value)
				raise
		
		# contraint
		if node.constraint != None and rating < 3:
			env = {
				"self":node,
				"pos":pos,
				"newpos":newpos,
				"value":value,
				}
			
			if not evalEvent(node.constraint, env, node):
				rating = 4
				newpos = pos
				Debug(1, "_handleString: Constraint failed")
			else:
				Debug(1, "_handleString: Constraint passed")
		
		# Set value
		if rating < 3:
			eval("node.%s(value)" % self.method)
		
		# Are we last?
		if self._nextNode(node) == None:
			
			# Note: If doingMinMax then we can't
			# assume we should eat all data even
			# if we are the last node!
			#
			# Note2: maxOccurs can lie if we are doingMinMax!
			#
			if newpos < len(data) and node.maxOccurs == 1 and (node.parent == None or node.parent.maxOccurs == 1) and not doingMinMax:
				# We didn't use it all up, sad for us!
				Debug(1, "--- Didn't use all data, rating == 4")
				rating = 4
		
		# Return values
		
		Debug(1, "<--- %s (%d, %d-%d)" % (node.name, rating, self.parentPos+pos, self.parentPos+newpos))
		
		if rating < 3:
			node.pos = pos
			node.rating = rating
		
		self.deepString -= 1
		return (rating, newpos)
	
	def _handleNumber(self, node, data, pos, parent, doingMinMax = False):
		'''
		Handle Number.  Return (rating, newpos, value) in tuple.
		
		Rating:
		
		1 - BEST	If our default matched and look ahead is 1
		2 - GOOD	If our default matched and look ahead is 2
		3 - OK		If our look ahead is 1 or 2
		4 - MPH		If look ahead is 3 or 4
		
		'''
		
		Debug(1, "---> %s (%d)" % (node.name,self.parentPos+pos))
		
		node.rating = 0
		length = node.size/8
		
		# See if we have enough data
		
		if (pos+length) > len(data):
			# need more 
			if not self.haveAllData:
				raise NeedMoreData((pos+length) - len(data), node.name)
			else:
				node.rating = None
				return (4, pos)
		
		# Get value based on element length
		
		value = data[pos:pos+length]
		newpos = pos + length
		
		# Build format string
		
		fmt = ''
		
		if node.endian == 'little':
			fmt = '<'
		else:
			fmt = '>'
		
		if node.size == 8:
			fmt += 'b'
		elif node.size == 16:
			fmt += 'h'
		elif node.size == 32:
			fmt += 'i'
		elif node.size == 64:
			fmt += 'q'
		
		if not node.signed:
			fmt = fmt.upper()
		
		# Unpack value
		
		value = str(struct.unpack(fmt, value)[0])
		
		# Adjust rating based on defaultValue
		
		if node.isStatic:
			if value != str(node.defaultValue):
				Debug(1, "_handleNumber: Number is static but did not match, failing. [%s] != [%s]" % (value, node.defaultValue))
				node.rating = 4
			else:
				Debug(1, "_handleNumber: Number is static and matched. [%s] == [%s]" % (value, node.defaultValue))
				node.rating = 1
		else:
			node.rating = 2
		
		# contraint
		if node.constraint != None:
			env = {
				"self":node,
				"value":int(value),
				"pos":pos,
				"newpos":newpos,
				}
			
			if not evalEvent(node.constraint, env, node):
				node.rating = 4
				newpos = pos
				Debug(1, "_handleNumber: Constraint failed")
			else:
				Debug(1, "_handleNumber: Constraint passed")
		
		# Set value on data element
		if node.rating < 3:
			eval("node.%s(value)" % self.method)
		
			# Return all of it
			node.pos = pos
		
		Debug(1, "<--- %s (%d, %d-%d)" % (node.name, node.rating, self.parentPos+pos, self.parentPos+newpos))
		return (node.rating, newpos)
	
	def _handleFlags(self, node, data, pos, parent, doingMinMax = False):
		'''
		Returns the rating and string.  The rating is
		how well we matched.
		
		Rating:
		
		1 - BEST	If our default matched and look ahead is 1
		2 - GOOD	If our default matched and look ahead is 2
		3 - OK		If our look ahead is 1 or 2
		4 - MPH		If look ahead is 3 or 4
		'''
		
		Debug(1, "---> %s (%d)" % (node.name,self.parentPos+pos))
		
		rating = 0
		length = node.length/8
		
		if (pos+length) > len(data):
			# need more
			#print "_handleFlags(): We need %d we have total %d and are at pos %d" % (length, len(data), pos)
			raise NeedMoreData((pos+length) - len(data), node.name)
		
		value = data[pos:pos+length]
		newpos = pos + length
		
		#print "prepack value: %s pos: %d" % (repr(value), pos)
		#print "data: %s" % repr(data)
		# Now, unpack the integer
		
		fmt = '>'
		if node.length == 8:
			fmt += 'B'
		elif node.length == 16:
			fmt += 'H'
		elif node.length == 32:
			fmt += 'I'
		elif node.length == 64:
			fmt += 'Q'
		
		value = int(struct.unpack(fmt, value)[0])
		#print "_handleFlags(): Value: %d" % value
		
		# Now, do the Flag portions

		#print "start value:", self.binaryFormatter(value, node.length)
		
		for child in node._children:
			if child.elementType != 'flag':
				continue
			
			if node.endian == 'little':
				childValue = value >> child.position
				
				mask = 0
				for i in range(0, child.length):
					mask += 1 << i
			
				#print "_handleFlags(): %d, %d, %d" % (childValue, mask, childValue & mask)
				childValue = childValue & mask
			
			else:
				# We will +1 here because position is zero based
				childValue = value >> child.position + 1
				
				mask = 0
				for i in range(0, child.length):
					mask += 1 << i
				
				#preValue = childValue
				childValue = childValue & mask
				#print "mask: %s pre-value: %s post-value: %d" % (
				#	self.binaryFormatter(mask, node.length),
				#	self.binaryFormatter(preValue, node.length),
				#	childValue
				#	)
			
			Debug(1, "Found child flag %s value of %s" % (child.name, str(childValue)))
			
			# Set child node value
			eval("child.%s(childValue)" % self.method)
			#print "[%s] child value:" % child.name, child.getInternalValue()
		
		# Determin rating
		
		rating = 2
		
		# contraint
		if node.constraint != None:
			env = {
				"self":node,
				"pos":pos,
				"newpos":newpos,
				}
			
			if not evalEvent(node.constraint, env, node):
				rating = 4
				newpos = pos
				Debug(1, "_handleFlags: Constraint failed")
			else:
				Debug(1, "_handleFlags: Constraint passed")
		
		Debug(1, "<--- %s (%d, %d-%d)" % (node.name, rating, self.parentPos+pos, self.parentPos+newpos))
		
		node.pos = pos
		node.rating = rating
		return (rating, newpos)

	def binaryFormatter(self, num, bits):
		ret = ""
		for i in range(bits-1, -1, -1):
			ret += str((num >> i) & 1)
		
		assert len(ret) == bits
		return ret
	

	def _handleSeek(self, node, data, pos, parent, doingMinMax = False):
		'''
		Handle a Seek element
		'''
		
		Debug(1, "---> SEEK FROM %d" % (self.parentPos+pos))
		
		# 1. Get the position to jump to
		
		newpos = node.getPosition(pos, len(data), data)
		
		# 2. Can we jump there?
		
		if newpos > data:
			
			# a. Do we have all the data?
			if not self.haveAllData:
				# Request more
				raise NeedMoreData((pos+newpos) - len(data), "")
			
			else:
				# Bad rating
				Debug(1, "<--- SEEK TO %d FAILED, ONLY HAVE %d" % (newpos, len(data)))
				return (4, pos)
		
		elif newpos < 0:
			Debug(1, "<--- SEEK TO %d FAILED, NEGATIVE NOT POSSIBLE" % (newpos))
			return (4, pos)
			
		# 3. Jump there!
		
		Debug(1, "<--- SEEK TO %d" % newpos)
		return (1, newpos)
	
	def _handleCustomSize(self, node, data, pos, parent):
		Debug(1, "_handleCustomSize(%s)" % node.name)
		
		return node.handleIncomingSize(node, data, pos, parent)
		
	def _handleCustom(self, node, data, pos, parent, doingMinMax = False):
		'''
		Returns the rating and string.  The rating is
		how well we matched.
		
		Rating:
		
		1 - BEST	If our default matched and look ahead is 1
		2 - GOOD	If our default matched and look ahead is 2
		3 - OK		If our look ahead is 1 or 2
		4 - MPH		If look ahead is 3 or 4
		'''
		
		Debug(1, "---> %s (%d)" % (node.name, self.parentPos+pos))
		
		rating, newpos = node.handleIncoming(self, data, pos, parent, doingMinMax)
		
		# contraint
		if node.constraint != None and rating < 3:
			env = {
				"self":node,
				"data":data,
				"pos":pos,
				"newpos":newpos,
				}
			
			if not evalEvent(node.constraint, env, node):
				rating = 4
				newpos = pos
				Debug(1, "_handleNumber: Constraint failed")
			else:
				Debug(1, "_handleNumber: Constraint passed")
			
		if rating < 3:
			node.pos = newpos
			node.rating = rating
		
		Debug(1, "<--- %s (%d)" % (node.name, self.parentPos+newpos))
		return (rating, newpos)
		
	def _handleBlob(self, node, data, pos, parent, doingMinMax = False):
		'''
		Returns the rating and string.  The rating is
		how well we matched.
		
		Rating:
		
		1 - BEST	If our default matched and look ahead is 1
		2 - GOOD	If our default matched and look ahead is 2
		3 - OK		If our look ahead is 1 or 2
		4 - MPH		If look ahead is 3 or 4
		'''
		
		Debug(1, "---> %s (%d)" % (node.name,self.parentPos+pos))
		
		rating = 0
		newpos = 0
		length = None
		hasSizeofRelation = False
		length = None
		
		# Determin if we have a size-of relation
		# and set our length accordingly.
		relation = node.getRelationOfThisElement('size')
		if relation != None and relation.type == 'size':
			# we have a size-of relation
			Debug(1, "** FOUND SIZE OF RELATION ***")
			
			fullName = relation.parent.getFullname()
			Debug(1, "Size-of Fullname: " + fullName)
			
			length = relation.getValue(True)
			Debug(1, "Size-of Length: %s" % length)
			
			# We might not be ready to get this
			# value yet (look head), but try
			try:
				length = int(length)
			except:
				pass
		else:
			Debug(1, "_handleBlob: No relation found")
		
		# Do we know our length?
		if node.getLength() != None or length != None:
			
			if length == None:
				length = node.getLength()
			
			value = data[pos:pos + length]
			newpos = pos + length
			rating = 2
			
			if value == node.defaultValue:
				rating = 1
			elif node.isStatic:
				rating = 4
			
			if (pos+length) > len(data):
				if not self.haveAllData:
					raise NeedMoreData((pos+length) - len(data), "")
				else:
					Debug(1, "_handleBlob: Not enough data, rating = 4: %d left" % (len(data)-pos))
					rating = 4
		
		else:
			# If we don't have a sizeof relation, we try for a best fit
			# by adjusting the position until our look ahead has a rating
			# of 1 or 2.
			
			# Are we the last data element?
			if self._nextNode(node) == None:
				#print "--- Last element, snafing it all :)"
				
				if not self.haveAllData:
					self.haveAllData = True
					raise NeedMoreData(-1, "")
				
				else:
					# Keep all the data :)
					value = data[pos:]
					newpos = len(data)
					rating = 1
			
			elif self._isLastUnsizedNode(node) != None:
				# Are all other nodes of deterministic size?
				
				Debug(1, "_handleBlob: self._isLastUnsizedNode(node)")
				
				if not self.haveAllData:
					#self.haveAllData = True
					raise NeedMoreData(-1, "")
				
				length = self._isLastUnsizedNode(node)
				newpos = len(data) - length
				value = data[pos:newpos]
				rating = 1
			
			elif self._isTokenNext(node) != None:
				# Is there an isStatic ahead?
				
				staticNode, length = self._isTokenNext(node)
				
				Debug(1, "_handleBlob: self._isTokenNext(%s): %s" % (node.name, staticNode.name))
				
				# 1. Locate staticNode position
				val = staticNode.getValue()
				Debug(1, "Looking for [%s][%s]" % (repr(val), repr(data[pos:])))
				valPos = data[pos:].find(val)
				if valPos == -1:
					if self.haveAllData:
						newpos = pos
						value = ""
						rating = 4
						Debug(1, " :( Have all data")
					
					else:
						Debug(1, " --- NEED MORE DATA ---")
						raise NeedMoreData(1, "")
				
				else:
					# 2. Subtract length
					newpos = (pos+valPos) - length
					
					# 3. Yuppie!
					value = data[pos:newpos]
					rating = 1
					
					Debug(1, "Found: [%d][%d:%d][%s]" % (length, self.parentPos+pos, self.parentPos+newpos, value))
				
			else:
				#if self.haveAllData:
				#	print "--- Was not last node"
				
				lookRating = 666
				newpos = pos
				
				# If we have a following static just scan
				# for it instead of calling lookAhead.
				nextNode = self._nextNode(node)
				if nextNode.isStatic:
					nextValue = nextNode.getValue()
					nextValueLen = len(nextValue)
					
					newpos = data.find(nextValue, pos)
					if newpos == -1:
						raise NeedMoreData(1, "Couldn't locate nextValue(%s) [%s]" % (nextNode.getFullnameInDataModel(), nextValue))
					
					value = data[pos:newpos]
					rating = 2
				
				else:
					
					while lookRating > 2 and newpos < len(data):
						#Debug(1, ".")
						newpos += 1
						lookRating = self._lookAhead(node, data, newpos, parent)
						#Debug(1, "newpos: %d lookRating: %d data: %d" % (newpos, lookRating, len(data)))
					
					while lookRating <= 2 and newpos < len(data):
						#Debug(1, ",")
						newpos += 1
						lookRating = self._lookAhead(node, data, newpos, parent)
						#Debug(1, "newpos: %d lookRating: %d data: %d" % (newpos, lookRating, len(data)))
					
					#if newpos >= len(data):
					#	newpos -= 1
					#	#raise str("Unable to parse out blob %s" % node.name)
					
					value = data[pos:newpos]
					rating = 2
				
				#print "Found blob: [%s]" % value
		
		# contraint
		if node.constraint != None:
			env = {
				"self":node,
				"value":value,
				"pos":pos,
				"newpos":newpos,
				}
			
			if not evalEvent(node.constraint, env, node):
				rating = 4
				newpos = pos
				Debug(1, "_handleNumber: Constraint failed")
			else:
				Debug(1, "_handleNumber: Constraint passed")
		
		if rating < 3:
			eval("node.%s(value)" % self.method)
		
		Debug(1, "<--- %s (%d, %d-%d)" % (node.name, rating, self.parentPos+pos, self.parentPos+newpos))
		
		node.pos = pos
		node.rating = rating
		return (rating, newpos)

class NeedMoreData:
	def __init__(self, amount, msg):
		#Debug(1, "NeedMoreData: amount = %d" % amount)
		#print "NeedMoreData: amount = %d" % amount
		#print "NeedMoreData: tab level = %d" % DataCracker._tabLevel
		self.amount = amount
		self.msg = "[%d] %s]" % (amount, msg)
	
	def __str__(self):
		return self.msg

class ReachedGoalNode:
	'''
	Thrown when we reach our target node goal.
	'''
	
	def __init__(self, rating, pos, node):
		self.rating = rating
		self.pos = pos
		self.node = node

def printDom(node, level = 0):
	
	tabs = '\t' * level
	
	if node.currentValue != None:	
		Debug(1, tabs + "%s: [%s]" % (node.name, node.currentValue))
	else:
		Debug(1, tabs + "%s" % (node.name))
		
	try:
		for child in node._children:
			printDom(child, level+1)
	except:
		pass

if sys.version.find("AMD64") == -1:
	import psyco
	psyco.bind(DataCracker)

# end
