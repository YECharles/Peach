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
	import pyasn1.codec.ber.decoder
	import pyasn1.codec.cer.decoder
	import pyasn1.codec.der.decoder
	
	import pyasn1.codec.ber.encoder
	import pyasn1.codec.cer.encoder
	import pyasn1.codec.der.encoder

except:
	#raise PeachException("Error loading pyasn1 library.  This library\ncan be installed from the dependencies folder.\n\n")
	pass

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

	def analyzeAsn1(self, codec, data):
		
		decoder = eval("pyasn1.codec.%s.decoder" % codec)
		
		asn1Obj = decoder.decode(data)[0]
		return self.Asn12Peach(codec, asn1Obj)
	
	def Asn12Peach(self, codec, asn1Obj):
		
		obj = Asn1Type(None, None)
		obj.asn1Type = asn1Obj.__class__.__name__
		obj.encodeType = codec
		
		if hasattr(asn1Obj, "_value"):
			value = asn1Obj._value
			obj.objType = type(value)
			
			if type(value) == long or type(value) == int:
				n = Number(None, None)
				n.defaultValue = str(value)
				n.size = 32
				
				obj.append(n)
			
			elif type(value) == str:
				# Could be blob or string...hmmm
				b = Blob(None, None)
				b.defaultValue = value
				
				obj.append(b)
			
			elif type(value) == tuple:
				# Probably and ObjectIdentifier!
				
				if asn1Obj.__class__.__name__ == 'ObjectIdentifier':
					oid = []
					for i in value:
						oid.append(str(i))
					
					b = String(None, None)
					b.defaultValue = ".".join(oid)
					
					obj.append(b)
				
				elif asn1Obj.__class__.__name__ == 'BitString':
					# Make this a blob
					b = Blob(None, None)
					
					encoder = eval("pyasn1.codec.%s.encoder" % codec)
					b.defaultValue = encoder.encode(asn1Obj)[4:]
					
					obj.append(b)
				
				else:
					print "UNKNOWN TUPLE TYPE"
					print asn1Obj.__class__.__name__
					print value
					raise Exception("foo")
		
		if hasattr(asn1Obj, "_componentValues"):
			for c in asn1Obj._componentValues:
				child = self.Asn12Peach(codec, c)
				obj.append(child)
		
		return obj

	def asDataElement(self, parent, args, dataBuffer):
		'''
		Called when Analyzer is used in a data model.
		
		Should return a DataElement such as Block, Number or String.
		'''
		
		dom = self.analyzeAsn1("der", dataBuffer)
		
		# Replace parent with new dom
		
		dom.name = parent.name
		parentOfParent = parent.parent
		
		indx = parentOfParent.index(parent)
		del parentOfParent[parent.name]
		parentOfParent.insert(indx, dom)
		
		# now just cross our fingers :)
	
	def asCommandLine(self, args):
		'''
		Called when Analyzer is used from command line.  Analyzer
		should produce Peach PIT XML as output.
		'''
		
		raise Exception("asCommandLine not supported (yet)")
		#try:
		#	inFile = args["xmlfile"]
		#	outFile = args["out"]
		#except:
		#	raise PeachException("XmlAnalyzer requires two parameters, xmlfile and out.")
		#
		#xml = _Xml2Peach().xml2Peach("file:"+inFile)
		#
		#fd = open(outfile, "wb+")
		#fd.write(xml)
		#fd.close()
	
	def asTopLevel(self, peach, args):
		'''
		Called when Analyzer is used from top level.
		
		From the top level producing zero or more data models and
		state models is possible.
		'''
		raise Exception("asTopLevel not supported")


# end
