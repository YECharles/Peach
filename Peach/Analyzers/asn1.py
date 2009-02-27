'''
ASN.1 Analyzer

This analyzer can take ASN.1 binary blobs and build a DOM out of
them.  Can we say easy certificate fuzzing? :)

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

import sys, os

from Peach.analyzer import *
from Peach.Engine.dom import *
from Peach.Engine.common import *

try:
	from pyasn1.type import univ

except:
	raise PeachException("Error loading pyasn1 library.  This library\ncan be installed from the dependencies folder.\n\n")


class Asn1Analyzer(Analyzer):
	'''
	Produces data models or peach pits from XML documents.
	'''
	
	#: Does analyzer support asDataElement()
	supportDataElement = True
	#: Does analyzer support asCommandLine()
	supportCommandLine = True
	#: Does analyzer support asTopLevel()
	supportTopLevel = True
	
	def __init__(self):
		pass

	def asDataElement(self, parent, args, dataBuffer):
		'''
		Called when Analyzer is used in a data model.
		
		Should return a DataElement such as Block, Number or String.
		'''
		raise Exception("asDataElement not supported (yet)")
	
	def asCommandLine(self, args):
		'''
		Called when Analyzer is used from command line.  Analyzer
		should produce Peach PIT XML as output.
		'''
		
		try:
			inFile = args["xmlfile"]
			outFile = args["out"]
		except:
			raise PeachException("XmlAnalyzer requires two parameters, xmlfile and out.")
		
		xml = _Xml2Peach().xml2Peach("file:"+inFile)
		
		fd = open(outfile, "wb+")
		fd.write(xml)
		fd.close()
	
	def asTopLevel(self, peach, args):
		'''
		Called when Analyzer is used from top level.
		
		From the top level producing zero or more data models and
		state models is possible.
		'''
		raise Exception("asTopLevel not supported")


##
##class _Xml2Peach(object):
##	
##	XmlContainer = """<?xml version="1.0" encoding="utf-8"?>
##<Peach xmlns="http://phed.org/2008/Peach" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
##	xsi:schemaLocation="http://phed.org/2008/Peach /peach/peach.xsd">
##	
##	<!-- Import defaults for Peach instance -->
##	<Include ns="default" src="file:defaults.xml" />
##	<Include ns="pt" src="file:PeachTypes.xml" />
##	
##	<DataModel name="TheDataModel">
##%s
##	</DataModel>
##	
##	<!-- TODO: Create state model -->
##	<StateModel name="TheState" initialState="Initial">
##		
##		<State name="Initial">
##			<Action type="output">
##				<DataModel ref="TheDataModel" />
##			</Action>
##		</State>
##		
##	</StateModel>
##	
##	<!-- TODO: Configure agent/monitors
##	<Agent name="LocalAgent" location="http://127.0.0.1:9000">
##		<Monitor class="test.TestStopOnFirst" />
##	</Agent>
##	-->
##	
##	<Test name="TheTest">
##		<!-- <Agent ref="LocalAgent"/> -->
##		<StateModel ref="TheState"/>
##		
##		<!-- TODO: Complete publisher -->
##		<Publisher class="stdout.Stdout" />
##	</Test>
##	
##	<!-- Configure a single run -->
##	<Run name="DefaultRun">
##		
##		<Test ref="TheTest" />
##		
##	</Run>
##	
##</Peach>
##<!-- end -->
##"""
##	
##	def xml2Peach(self, url):
##		factory = InputSourceFactory(resolver=_PeachResolver(), catalog=GetDefaultCatalog())
##		isrc = factory.fromUri(url)
##		doc = Ft.Xml.Domlette.NonvalidatingReader.parse(isrc)
##		
##		peachDoc = Ft.Xml.Domlette.implementation.createDocument(EMPTY_NAMESPACE, None, None)
##		self.handleElement(doc.firstChild, peachDoc)
##		
##		# Get the string representation
##		import cStringIO
##		buff = cStringIO.StringIO()
##		PrettyPrint(peachDoc.firstChild, stream=buff, encoding="utf8")
##		value = buff.getvalue()
##		buff.close()
##		
##		return self.XmlContainer % value
##		
##	def handleElement(self, node, parent):
##		'''
##		Handle an XML element, children and attributes.
##		Returns an XmlElement object.
##		'''
##		
##		doc = parent.ownerDocument
##		if doc == None:
##			doc = parent
##
##		#print "--- Attributes ---"
##		#if node.attributes != None:
##		#	for attrib in node.attributes:
##		#		print attrib, node.attributes[attrib]
##		#print "------------------"
##		
##		## Element
##		
##		element = doc.createElementNS(None, "XmlElement")
##		element.setAttributeNS(None, "elementName", node.nodeName)
##		parent.appendChild(element)
##		
##		if node.namespaceURI != None:
##			element.setAttributeNS(None, "ns", node.namespaceURI)
##		
##		## Element attributes
##		
##		if node.attributes != None:
##			for attrib in node.attributes:
##				attribElement = self.handleAttribute(attrib, node.attributes[attrib], element)
##				element.appendChild(attribElement)
##		
##		## Element children
##		
##		for child in node.childNodes:
##			if child.nodeName == "#text":
##				if len(child.nodeValue.strip('\n\r\t\x10 ')) > 0:
##					# This is node's value!
##					string = doc.createElementNS(None, "String")
##					string.setAttributeNS(None, "value", child.nodeValue)
##					element.appendChild(string)
##				
##			elif child.nodeName == "#comment":
##				# xml comment
##				pass
##			else:
##				childElement = self.handleElement(child, element)
##		
##		return element
##	
##	def handleAttribute(self, attrib, attribObj, parent):
##		'''
##		Handle an XML attribute.   Returns an XmlAttribute object.
##		'''
##		
##		doc = parent.ownerDocument
##		if doc == None:
##			doc = parent
##		
##		## Attribute
##		
##		element = doc.createElementNS(None, "XmlAttribute")
##		element.setAttributeNS(None, "attributeName", attribObj.name)
##		
##		if attrib[0] != None:
##			element.setAttributeNS(None, "ns", attrib[0])
##		
##		## Attribute value
##		
##		string = doc.createElementNS(None, "String")
##		string.setAttributeNS(None, "value", attribObj.value)
##		element.appendChild(string)
##		
##		return element
##	

# end