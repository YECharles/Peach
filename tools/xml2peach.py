'''
Convert an XML document to a Peach PIT using the XmlElement, and XmlAttribute
DataElements to perform fuzzing of XML content.
'''

try:
	import Ft.Xml.Domlette
	from Ft.Xml.Catalog import GetDefaultCatalog
	from Ft.Xml.InputSource import InputSourceFactory
	from Ft.Lib.Resolvers import SchemeRegistryResolver
	from Ft.Lib import Uri
	from Ft.Xml import Parse
	from Ft.Xml.Sax import DomBuilder
	from Ft.Xml import Sax, CreateInputSource
	from Ft.Xml import EMPTY_NAMESPACE
	from Ft.Xml.Domlette import Print, PrettyPrint

except:
	raise PeachException("Error loading 4Suite XML library.  This library\ncan be installed from the dependencies folder or\ndownloaded from http://4suite.org/.\n\n")


class PeachResolver(SchemeRegistryResolver):
	def __init__(self):
		SchemeRegistryResolver.__init__(self)
	
	def resolve(self, uri, base=None):
		scheme = Uri.GetScheme(uri)
		if scheme == None:
			if base != None:
				scheme = Uri.GetScheme(base)
			if scheme == None:
				#Another option is to fall back to Base class behavior
				raise Uri.UriException(Uri.UriException.SCHEME_REQUIRED,
									   base=base, ref=uri)
		
		# Add the files path to our sys.path
		
		if scheme == 'file':
			filename = uri[5:]
			try:
				index = filename.rindex('\\')
				sys.path.append(filename[: 0 - (index+1)])
				#print "Adding [%s]" % filename[: 0 - (index+1)]
				
			except:
				try:
					index = filename.rindex('/')
					sys.path.append(filename[: 0 - (index+1)])
					#print "Adding [%s]" % filename[: 0 - (index+1)]
					
				except:
					#print "Adding [.][%s]" % uri
					sys.path.append('.')
		
		try:
			func = self.handlers.get(scheme)
			if func == None:
				func = self.handlers.get(None)
				if func == None:
					return Uri.UriResolverBase.resolve(self, uri, base)
			
			return func(uri, base)
		
		except:
			
			if scheme != 'file':
				raise PeachException("Peach was unable to locate [%s]" % uri)
			
			# Lets try looking in our sys.path
			
			paths = []
			for path in sys.path:
				paths.append(path)
				paths.append("%s/Peach/Engine" % path)
			
			for path in paths:
				newuri = uri[:5] + path + '/' + uri[5:]
				#print "Trying: [%s]" % newuri
				
				try:
					func = self.handlers.get(scheme)
					if func == None:
						func = self.handlers.get(None)
						if func == None:
							return Uri.UriResolverBase.resolve(self, newuri, base)
					
					return func(uri, base)
				except:
					pass
			
			raise PeachException("Peach was unable to locate [%s]" % uri)

class Xml2Peach(object):
	
	XmlContainer = """<?xml version="1.0" encoding="utf-8"?>
<Peach xmlns="http://phed.org/2008/Peach" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
	xsi:schemaLocation="http://phed.org/2008/Peach /peach/peach.xsd">
	
	<!-- Import defaults for Peach instance -->
	<Include ns="default" src="file:defaults.xml" />
	<Include ns="pt" src="file:PeachTypes.xml" />
	
	<DataModel name="TheDataModel">
%s
	</DataModel>
	
	<!-- TODO: Create state model -->
	<StateModel name="TheState" initialState="Initial">
		
		<State name="Initial">
			<Action type="output">
				<DataModel ref="TheDataModel" />
			</Action>
		</State>
		
	</StateModel>
	
	<!-- TODO: Configure agent/monitors
	<Agent name="LocalAgent" location="http://127.0.0.1:9000">
		<Monitor class="test.TestStopOnFirst" />
	</Agent>
	-->
	
	<Test name="TheTest">
		<!-- <Agent ref="LocalAgent"/> -->
		<StateModel ref="TheState"/>
		
		<!-- TODO: Complete publisher -->
		<Publisher class="stdout.Stdout" />
	</Test>
	
	<!-- Configure a single run -->
	<Run name="DefaultRun">
		
		<Test ref="TheTest" />
		
	</Run>
	
</Peach>
<!-- end -->
"""
	
	def xml2Peach(self, url):
		factory = InputSourceFactory(resolver=PeachResolver(), catalog=GetDefaultCatalog())
		isrc = factory.fromUri(url)
		doc = Ft.Xml.Domlette.NonvalidatingReader.parse(isrc)
		
		peachDoc = Ft.Xml.Domlette.implementation.createDocument(EMPTY_NAMESPACE, None, None)
		self.handleElement(doc.firstChild, peachDoc)
		
		# Get the string representation
		import cStringIO
		buff = cStringIO.StringIO()
		PrettyPrint(peachDoc.firstChild, stream=buff, encoding="utf8")
		value = buff.getvalue()
		buff.close()
		
		print self.XmlContainer % value
		
	def handleElement(self, node, parent):
		'''
		Handle an XML element, children and attributes.
		Returns an XmlElement object.
		'''
		
		doc = parent.ownerDocument
		if doc == None:
			doc = parent

		#print "--- Attributes ---"
		#if node.attributes != None:
		#	for attrib in node.attributes:
		#		print attrib, node.attributes[attrib]
		#print "------------------"
		
		## Element
		
		element = doc.createElementNS(None, "XmlElement")
		element.setAttributeNS(None, "elementName", node.nodeName)
		parent.appendChild(element)
		
		if node.namespaceURI != None:
			element.setAttributeNS(None, "ns", node.namespaceURI)
		
		## Element attributes
		
		if node.attributes != None:
			for attrib in node.attributes:
				attribElement = self.handleAttribute(attrib, node.attributes[attrib], element)
				element.appendChild(attribElement)
		
		## Element children
		
		for child in node.childNodes:
			if child.nodeName == "#text":
				if len(child.nodeValue.strip('\n\r\t\x10 ')) > 0:
					# This is node's value!
					string = doc.createElementNS(None, "String")
					string.setAttributeNS(None, "value", child.nodeValue)
					element.appendChild(string)
				
			elif child.nodeName == "#comment":
				# xml comment
				pass
			else:
				childElement = self.handleElement(child, element)
		
		return element
	
	def handleAttribute(self, attrib, attribObj, parent):
		'''
		Handle an XML attribute.   Returns an XmlAttribute object.
		'''
		
		doc = parent.ownerDocument
		if doc == None:
			doc = parent
		
		## Attribute
		
		element = doc.createElementNS(None, "XmlAttribute")
		element.setAttributeNS(None, "attributeName", attribObj.name)
		
		if attrib[0] != None:
			element.setAttributeNS(None, "ns", attrib[0])
		
		## Attribute value
		
		string = doc.createElementNS(None, "String")
		string.setAttributeNS(None, "value", attribObj.value)
		element.appendChild(string)
		
		return element
	

import sys

if len(sys.argv) < 2:
	print """
] Create Fuzzer from XML Document v0.1
] Copyright (c) Michael Eddington

Syntax: xml2peach.py file.xml > fuzzer.xml

"""
	sys.exit(0)

Xml2Peach().xml2Peach("file:"+sys.argv[1])

# end















































































