
'''
A few standard fixups.
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

import zlib, hashlib, struct, binascii, array
from Peach.fixup import Fixup
from Peach.Engine.common import *

class ExpressionFixup(Fixup):
	'''
	Sometimes you need to perform some math as the fixup.  This
	relation will take a ref, then an expression (python).
	'''
	
	def __init__(self, ref, expression):
		Fixup.__init__(self)
		self.ref = ref
		self.expression = expression
	
	def fixup(self):
		ref = self._findDataElementByName(self.ref)
		stuff = ref.getValue()
		if stuff == None:
			raise Exception("Error: ExpressionFixup was unable to locate [%s]" % self.ref)
		
		return evalEvent(self.expression, { "self" : self, "ref" : ref, "data" : stuff  }, self)

class SHA224Fixup(Fixup):
	def __init__(self, ref):
		Fixup.__init__(self)
		self.ref = ref
			def fixup(self):
		self.context.defaultValue = "0"
		stuff = self._findDataElementByName(self.ref).getValue()
		if stuff == None:
			raise Exception("Error: SHA1Fixup was unable to locate [%s]" % self.ref)
		h = hashlib.sha224()
		h.update(stuff)
		return h.digest()
	
class SHA256Fixup(Fixup):
	def __init__(self, ref):
		Fixup.__init__(self)
		self.ref = ref
			def fixup(self):
		self.context.defaultValue = "0"
		stuff = self._findDataElementByName(self.ref).getValue()
		if stuff == None:
			raise Exception("Error: SHA256Fixup was unable to locate [%s]" % self.ref)
		h = hashlib.sha256()
		h.update(stuff)
		return h.digest()
	
class SHA384Fixup(Fixup):
	def __init__(self, ref):
		Fixup.__init__(self)
		self.ref = ref
			def fixup(self):
		self.context.defaultValue = "0"
		stuff = self._findDataElementByName(self.ref).getValue()
		if stuff == None:
			raise Exception("Error: SHA384Fixup was unable to locate [%s]" % self.ref)
		h = hashlib.sha384()
		h.update(stuff)
		return h.digest() 

class SHA512Fixup(Fixup):
	def __init__(self, ref):
		Fixup.__init__(self)
		self.ref = ref
		
	def fixup(self):
		self.context.defaultValue = "0"
		stuff = self._findDataElementByName(self.ref).getValue()
		if stuff == None:
			raise Exception("Error: SHA512Fixup was unable to locate [%s]" % self.ref)
		h = hashlib.sha512()
		h.update(stuff)
		return h.digest()
	class SHA1Fixup(Fixup):
	def __init__(self, ref):
		Fixup.__init__(self)
		self.ref = ref
		
	def fixup(self):
		self.context.defaultValue = "0"
		stuff = self._findDataElementByName(self.ref).getValue()
		if stuff == None:
			raise Exception("Error: SHA1Fixup was unable to locate [%s]" % self.ref)
		h = hashlib.sha1()
		h.update(stuff)
		return h.digest() 
	class MD5Fixup(Fixup):
	def __init__(self, ref):
		
		Fixup.__init__(self)
		self.ref = ref
			def fixup(self):
		self.context.defaultValue = "0"
		stuff = self._findDataElementByName(self.ref).getValue()
		if stuff == None:
			raise Exception("Error: MD5Fixup was unable to locate [%s]" % self.ref)
		h = hashlib.md5()
		h.update(stuff)
		return h.digest() 
	
class Crc32Fixup(Fixup):
	'''
	Standard CRC32 as defined by ISO 3309.  Used by PNG, zip, etc.
	'''
	
	def __init__(self, ref):
		Fixup.__init__(self)
		self.ref = ref
	
	def fixup(self):
		self.context.defaultValue = "0"
		stuff = self._findDataElementByName(self.ref).getValue()
		if stuff == None:
			raise Exception("Error: Crc32Fixup was unable to locate [%s]" % self.ref)
		
		return zlib.crc32(stuff)


class Crc32DualFixup(Fixup):
	'''
	Standard CRC32 as defined by ISO 3309.  Used by PNG, zip, etc.
	'''
	
	def __init__(self, ref1, ref2):
		Fixup.__init__(self)
		self.ref1 = ref1
		self.ref2 = ref2
	
	def fixup(self):
		self.context.defaultValue = "0"
		stuff1 = self._findDataElementByName(self.ref1).getValue()
		stuff2 = self._findDataElementByName(self.ref2).getValue()
		if stuff1 == None or stuff2 == None:
			raise Exception("Error: Crc32DualFixup was unable to locate [%s] or [%s]" % (self.ref1, self.ref2))
		
		crc1 = zlib.crc32(stuff1)
		return zlib.crc32(stuff2, crc1)


class EthernetChecksumFixup(Fixup):
	'''
	Ethernet Chucksum Fixup.
	'''
	
	def __init__(self, ref):
		Fixup.__init__(self)
		self.ref = ref
	
	def _checksum(self, checksum_packet):
		"""Calculate checksum"""
		ethernetKey = 0x04C11DB7
		return binascii.crc32(checksum_packet, ethernetKey)
	
	def fixup(self):
		self.context.defaultValue = "0"
		stuff = self._findDataElementByName(self.ref).getValue()
		if stuff == None:
			raise Exception("Error: EthernetChecksumFixup was unable to locate [%s]" % self.ref)
		
		return self._checksum(stuff)


class IcmpChecksumFixup(Fixup):
	'''
	Ethernet Chucksum Fixup.
	'''
	
	def __init__(self, ref):
		Fixup.__init__(self)
		self.ref = ref
	
	def _checksum(self, checksum_packet):
		"""Calculate checksum"""
		# add byte if not dividable by 2
		if len(checksum_packet) & 1:              
			checksum_packet = checksum_packet + '\0'
		# split into 16-bit word and insert into a binary array
		words = array.array('h', checksum_packet) 
		sum = 0
		
		# perform ones complement arithmetic on 16-bit words
		for word in words:
			sum += (word & 0xffff) 
		
		hi = sum >> 16 
		lo = sum & 0xffff 
		sum = hi + lo
		sum = sum + (sum >> 16)
		
		return (~sum) & 0xffff # return ones complement
	
	def fixup(self):
		self.context.defaultValue = "0"
		stuff = self._findDataElementByName(self.ref).getValue()
		if stuff == None:
			raise Exception("Error: IcmpChecksumFixup was unable to locate [%s]" % self.ref)
		
		return self._checksum(stuff)

# end
