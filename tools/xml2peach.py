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
	
	XmlContainer = """
<?xml version="1.0" encoding="utf-8"?>
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
		<Publisher />
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
		isrc = factory.fromUri(uri)
		doc = Ft.Xml.Domlette.NonvalidatingReader.parse(isrc)
		
		innerPit = ""
		
	def handleElement(self, node, parent):
		'''
		Handle an XML element, children and attributes.
		Returns an XmlElement object.
		'''
		
		# 1. Element
		
		element = parent.createElementNS(None, "XmlElement")
		element.setAttributeNS(None, "value", node.nodeName)
		
		# 2. Element value
		
		string = element.createElementNS(None, "String")
		string.setAttributeNS(None, "value", node.nodeValue)
		
		# 3. Element attributes
		
		for attrib in node.attributes.keys():
			attribElement = self.handleAttribute(attrib, node.attributes[attrib], element)
			element.appendChild(attribElement)
		
		# 4. Element children
		
		for child in node.childNodes:
			childElement = self.handleElement(child, element)
			element.appendChild(childElement)
		
		return element
	
	def handleAttribute(self, attrib, attribObj, parent):
		'''
		Handle an XML attribute.   Returns an XmlAttribute object.
		'''
		
		# 1. Element
		
		element = parent.createElementNS(None, "XmlAttribute")
		if attrib[0] != None:
			element.setAttributeNS(None, "ns", attrib[0])
		
		element.setAttributeNS(None, "value", attrib[1])
		
		string = element.createElementNS(None, "String")
		string.setAttributeNS(None, "value", attribObj.value)
		
		element.appendChild(string)
		
		return element
	

# end















































































