
'''
Common data generators.  Includes common bad strings, numbers, etc.

@author: Michael Eddington
@version: $Id$
'''

#
# Copyright (c) 2006-2008 Michael Eddington
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

import static
import sys
import copy
import struct
import random
import array 
import binascii

from Peach.generator				import *
from Peach.Generators.dictionary	import *
from Peach.Generators.static		import *
from Peach.Generators.data			import *
from Peach.Generators.repeater		import *
from Peach.Generators.block			import *
from Peach.group					import *
import Peach.Transformers.type

class EndlessRandomStrings(Generator):
	'''
	Generates an endless number of random strings
	between the lengths of 0 and 1024.
	'''
	
	def __init__(self, group = None):
		Generator.__init__(self)
		self.setGroup(group)
	
	def next(self):
		pass
	
	def getRawValue(self):
		str = ''
		for x in range(random.choice(range(0, 1024))):
			str += struct.pack('B', random.randint(0, 255))[0]
		
		return str
	
class EndlessRandomWideStrings(Generator):
	'''
	Generates an endless number of random strings
	between the lengths of 0 and 1024.
	'''
	
	def __init__(self, group = None):
		Generator.__init__(self)
		self.setGroup(group)
		
	def next(self):
		pass
	
	def getRawValue(self):
		str = ''
		
		if random.choice([True, False]):
			for x in range(random.choice(range(0, 1024))):
				str += struct.pack('B', random.randint(0, 255))[0]
			
			if len(str) % 2 != 0:
				str += '\0'
		
		else:
			for x in range(random.choice(range(0, 1024))):
				str += struct.pack('BB', random.randint(0, 255), 0)[0]
			
		return str

class Bit(SimpleGenerator):
	'''
	Generates 0 and 1
	'''
	def __init__(self, group = None):
		SimpleGenerator.__init__(self, group)
		self._generator = List(None, [0, 1])


class BadStrings(SimpleGenerator):
	'''
	Generates variouse string tests.
	
	Examples of data generated:
	
		- Variations on format strings using '%n'
		- Long string
		- Empty string
		- Extended ASCII
		- Common bad ASCII (' " < >)
		- All numbers
		- All letters
		- All spaces
		- etc.
		
	'''
		
	_strings = [
		'Peach',
		'abcdefghijklmnopqrstuvwxyz',
		'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
		'0123456789',
		'',
		'10',
		'0.0',		'1.0',
		'0.1',		'1.1.1',
		'-2,147,483,648',
		'-2,147,483,649',
		'2,147,483,647',
		'2,147,483,649',
		'-2147483648',
		'-2147483649',
		'2147483647',
		'2147483649',
		'-129',
		'129',
		'255',
		'256',
		'-32769',
		'-32,769',
		'32767',
		'32769',
		'4,294,967,295',
		'4294967299',
		'-9,223,372,036,854,775,809',
		'-9223372036854775809',
		'9,223,372,036,854,775,809',
		'9223372036854775809',
		'18,446,744,073,709,551,615',
		'18,446,744,073,709,551,619',
		'18446744073709551619',
		'2.305843009213693952',
		'200000000000000000000.5',
		'200000000000000000000000000000000000000000000.5',
		'0xFF',
		'0xFFFF',
		'0xFFFFFF',
		'0xFFFFFFFFFFFFFFFFFFFF',
		'Yes',
		'No',
		'%n',
		'%n%n%n%n%n%n%n%n%n%n%n%n%n%n%n%n%n%n%n%n%n%n%n%n%n%n%n%n%n%n%n%n%n%n%n',
		'%n'*1024,
		'%x',
		'%x%x%x%x%x%x%x%x',
		'%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x',
		'%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x',
		'%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x',
		"""<>"/\'""",
		"""~`!@#$%^&*()_+=-{}|\][:"';<>?/.,""",
		'\\"',
		"\\'",
		"%",
		"a%",
		"%a",
		"COM1",
		"COM2",
		"AUX",
		"COM1:",
		"COM2:",
		"AUX:",
		"\\\\peach\foo\foo.txt",
		"\\\\\\",
		"..\\..\\..\\..\\..\\..\\..\\..\\",
		"../../../../../",
		"../",
		"/../../../../../../",
		"/../../..",
		"\\..\\..\\..\\..\\..\\",
		";,;,;,;,;,;,;,;,;,;,;,;,;,;,;,;,;,;,;,;,;,;,;,;,;,;,;,;,;,;,;,;,;,;,;,;,;,;,;,;,;,;,",
		";,"*256,
		";,"*512,
		";,"*1024,
		"A;A,"*256,
		"A;A,"*512,
		"A;A,"*1024,
		","*256,
		","*512,
		","*1024,
		"|"*256,
		"|"*512,
		"|"*1024,
		"||"*256,
		"||"*512,
		"||"*1024,
		":"*256,
		":"*512,
		":"*1024,
		struct.pack('B', 0)[0],
		struct.pack('B', 1)[0], 		struct.pack('B', 2)[0],
		struct.pack('B', 3)[0], 		struct.pack('B', 4)[0],
		struct.pack('B', 5)[0], 		struct.pack('B', 6)[0],
		struct.pack('B', 7)[0], 		struct.pack('B', 8)[0],
		struct.pack('B', 9)[0], 		struct.pack('B', 10)[0],
		struct.pack('B', 11)[0],        struct.pack('B', 12)[0],
		struct.pack('B', 13)[0],        struct.pack('B', 14)[0],
		struct.pack('B', 15)[0],        struct.pack('B', 16)[0],
		struct.pack('B', 17)[0],        struct.pack('B', 18)[0],
		struct.pack('B', 19)[0],        struct.pack('B', 20)[0],
		struct.pack('B', 21)[0],        struct.pack('B', 22)[0],
		struct.pack('B', 23)[0],        struct.pack('B', 24)[0],
		struct.pack('B', 25)[0],        struct.pack('B', 26)[0],
		struct.pack('B', 27)[0],        struct.pack('B', 28)[0],
		struct.pack('B', 29)[0],        struct.pack('B', 30)[0],
		struct.pack('B', 31)[0],        struct.pack('B', 32)[0],
		struct.pack('B', 33)[0],        struct.pack('B', 34)[0],
		struct.pack('B', 35)[0],        struct.pack('B', 36)[0],
		struct.pack('B', 37)[0],        struct.pack('B', 38)[0],
		struct.pack('B', 39)[0],        struct.pack('B', 40)[0],
		struct.pack('B', 41)[0],        struct.pack('B', 42)[0],
		struct.pack('B', 43)[0],        struct.pack('B', 44)[0],
		struct.pack('B', 45)[0],        struct.pack('B', 46)[0],
		struct.pack('B', 47)[0],        struct.pack('B', 48)[0],
		struct.pack('B', 49)[0],        struct.pack('B', 50)[0],
		struct.pack('B', 51)[0],        struct.pack('B', 52)[0],
		struct.pack('B', 53)[0],        struct.pack('B', 54)[0],
		struct.pack('B', 55)[0],        struct.pack('B', 56)[0],
		struct.pack('B', 57)[0],        struct.pack('B', 58)[0],
		struct.pack('B', 59)[0],        struct.pack('B', 60)[0],
		struct.pack('B', 61)[0],        struct.pack('B', 62)[0],
		struct.pack('B', 63)[0],        struct.pack('B', 64)[0],
		struct.pack('B', 65)[0],        struct.pack('B', 66)[0],
		struct.pack('B', 67)[0],        struct.pack('B', 68)[0],
		struct.pack('B', 69)[0],        struct.pack('B', 70)[0],
		struct.pack('B', 71)[0],        struct.pack('B', 72)[0],
		struct.pack('B', 73)[0],        struct.pack('B', 74)[0],
		struct.pack('B', 75)[0],        struct.pack('B', 76)[0],
		struct.pack('B', 77)[0],        struct.pack('B', 78)[0],
		struct.pack('B', 79)[0],        struct.pack('B', 80)[0],
		struct.pack('B', 81)[0],        struct.pack('B', 82)[0],
		struct.pack('B', 83)[0],        struct.pack('B', 84)[0],
		struct.pack('B', 85)[0],        struct.pack('B', 86)[0],
		struct.pack('B', 87)[0],        struct.pack('B', 88)[0],
		struct.pack('B', 89)[0],        struct.pack('B', 90)[0],
		struct.pack('B', 91)[0],        struct.pack('B', 92)[0],
		struct.pack('B', 93)[0],        struct.pack('B', 94)[0],
		struct.pack('B', 95)[0],        struct.pack('B', 96)[0],
		struct.pack('B', 97)[0],        struct.pack('B', 98)[0],
		struct.pack('B', 99)[0],        struct.pack('B', 100)[0],
		struct.pack('B', 101)[0],       struct.pack('B', 102)[0],
		struct.pack('B', 103)[0],       struct.pack('B', 104)[0],
		struct.pack('B', 105)[0],       struct.pack('B', 106)[0],
		struct.pack('B', 107)[0],       struct.pack('B', 108)[0],
		struct.pack('B', 109)[0],       struct.pack('B', 110)[0],
		struct.pack('B', 111)[0],       struct.pack('B', 112)[0],
		struct.pack('B', 113)[0],       struct.pack('B', 114)[0],
		struct.pack('B', 115)[0],       struct.pack('B', 116)[0],
		struct.pack('B', 117)[0],       struct.pack('B', 118)[0],
		struct.pack('B', 119)[0],       struct.pack('B', 120)[0],
		struct.pack('B', 121)[0],       struct.pack('B', 122)[0],
		struct.pack('B', 123)[0],       struct.pack('B', 124)[0],
		struct.pack('B', 125)[0],       struct.pack('B', 126)[0],
		struct.pack('B', 127)[0],       struct.pack('B', 128)[0],
		struct.pack('B', 129)[0],       struct.pack('B', 130)[0],
		struct.pack('B', 131)[0],       struct.pack('B', 132)[0],
		struct.pack('B', 133)[0],       struct.pack('B', 134)[0],
		struct.pack('B', 135)[0],       struct.pack('B', 136)[0],
		struct.pack('B', 137)[0],       struct.pack('B', 138)[0],
		struct.pack('B', 139)[0],       struct.pack('B', 140)[0],
		struct.pack('B', 141)[0],       struct.pack('B', 142)[0],
		struct.pack('B', 143)[0],       struct.pack('B', 144)[0],
		struct.pack('B', 145)[0],       struct.pack('B', 146)[0],
		struct.pack('B', 147)[0],       struct.pack('B', 148)[0],
		struct.pack('B', 149)[0],       struct.pack('B', 150)[0],
		struct.pack('B', 151)[0],       struct.pack('B', 152)[0],
		struct.pack('B', 153)[0],       struct.pack('B', 154)[0],
		struct.pack('B', 155)[0],       struct.pack('B', 156)[0],
		struct.pack('B', 157)[0],       struct.pack('B', 158)[0],
		struct.pack('B', 159)[0],       struct.pack('B', 160)[0],
		struct.pack('B', 161)[0],       struct.pack('B', 162)[0],
		struct.pack('B', 163)[0],       struct.pack('B', 164)[0],
		struct.pack('B', 165)[0],       struct.pack('B', 166)[0],
		struct.pack('B', 167)[0],       struct.pack('B', 168)[0],
		struct.pack('B', 169)[0],       struct.pack('B', 170)[0],
		struct.pack('B', 171)[0],       struct.pack('B', 172)[0],
		struct.pack('B', 173)[0],       struct.pack('B', 174)[0],
		struct.pack('B', 175)[0],       struct.pack('B', 176)[0],
		struct.pack('B', 177)[0],       struct.pack('B', 178)[0],
		struct.pack('B', 179)[0],       struct.pack('B', 180)[0],
		struct.pack('B', 181)[0],       struct.pack('B', 182)[0],
		struct.pack('B', 183)[0],       struct.pack('B', 184)[0],
		struct.pack('B', 185)[0],       struct.pack('B', 186)[0],
		struct.pack('B', 187)[0],       struct.pack('B', 188)[0],
		struct.pack('B', 189)[0],       struct.pack('B', 190)[0],
		struct.pack('B', 191)[0],       struct.pack('B', 192)[0],
		struct.pack('B', 193)[0],       struct.pack('B', 194)[0],
		struct.pack('B', 195)[0],       struct.pack('B', 196)[0],
		struct.pack('B', 197)[0],       struct.pack('B', 198)[0],
		struct.pack('B', 199)[0],       struct.pack('B', 200)[0],
		struct.pack('B', 201)[0],       struct.pack('B', 202)[0],
		struct.pack('B', 203)[0],       struct.pack('B', 204)[0],
		struct.pack('B', 205)[0],       struct.pack('B', 206)[0],
		struct.pack('B', 207)[0],       struct.pack('B', 208)[0],
		struct.pack('B', 209)[0],       struct.pack('B', 210)[0],
		struct.pack('B', 211)[0],       struct.pack('B', 212)[0],
		struct.pack('B', 213)[0],       struct.pack('B', 214)[0],
		struct.pack('B', 215)[0],       struct.pack('B', 216)[0],
		struct.pack('B', 217)[0],       struct.pack('B', 218)[0],
		struct.pack('B', 219)[0],       struct.pack('B', 220)[0],
		struct.pack('B', 221)[0],       struct.pack('B', 222)[0],
		struct.pack('B', 223)[0],       struct.pack('B', 224)[0],
		struct.pack('B', 225)[0],       struct.pack('B', 226)[0],
		struct.pack('B', 227)[0],       struct.pack('B', 228)[0],
		struct.pack('B', 229)[0],       struct.pack('B', 230)[0],
		struct.pack('B', 231)[0],       struct.pack('B', 232)[0],
		struct.pack('B', 233)[0],       struct.pack('B', 234)[0],
		struct.pack('B', 235)[0],       struct.pack('B', 236)[0],
		struct.pack('B', 237)[0],       struct.pack('B', 238)[0],
		struct.pack('B', 239)[0],       struct.pack('B', 240)[0],
		struct.pack('B', 241)[0],       struct.pack('B', 242)[0],
		struct.pack('B', 243)[0],       struct.pack('B', 244)[0],
		struct.pack('B', 245)[0],       struct.pack('B', 246)[0],
		struct.pack('B', 247)[0],       struct.pack('B', 248)[0],
		struct.pack('B', 249)[0],       struct.pack('B', 250)[0],
		struct.pack('B', 251)[0],       struct.pack('B', 252)[0],
		struct.pack('B', 253)[0],       struct.pack('B', 254)[0],
		struct.pack('B', 255)[0],
		]
	
	def __init__(self, group = None):
		SimpleGenerator.__init__(self, group)
		
		self._randStrings = []
		
		for i in range(100):
			str = ''
			for x in range(random.choice(range(10, 100))):
				str += struct.pack('B', random.randint(1, 255))[0]
			
			self._randStrings.append(str)
		
		self._generator = GeneratorList(None, [
			List(None, self._strings),
			List(None, self._randStrings),
			Repeater(None, Static("A"), 10, 200),
			Repeater(None, Static("A"), 127, 100),
			Repeater(None, Static("A"), 1024, 10),
			Repeater(None, Static("\x41\0"), 10, 200),
			Repeater(None, Static("\x41\0"), 127, 100),
			Repeater(None, Static("\x41\0"), 1024, 10),

			Block2([
				Static('\0\0'),
				Static('A'*7000)
				]),

			Block2([
				Static('%00%00'),
				Static('A'*7000)
				]),
			
			BadNumbers(),
			])
	
	def unittest():
		g = BadString(None)
		
		if g.getValue() != 'abcdefghijklmnopqrstuvwxyz':
			raise Exception("BadString unittest failed #1")
		g.next()
		
		if g.getValue() != 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
			raise Exception("BadString unittest failed #2")
		
		print "BadString okay\n"
	unittest = staticmethod(unittest)

class BadString(BadStrings):
	'''
	Depricated, use BadStrings instead.
	'''
	pass

class BadTime(SimpleGenerator):
	'''
	Test cases for HTTP-Date type
	'''
	def __init__(self, group = None):
		SimpleGenerator.__init__(self, group)
		
		groupSeq = [Group(), Group(), Group()]
		
		self._generator = GeneratorList2(None, [
			groupSeq[0],
			groupSeq[1],
			groupSeq[2],
			],[
			
			Block([
				GeneratorList(groupSeq[0], [
					Static('08'),
					BadString(),
					BadNumbers(),
					Static('08')
					]),
				Static(':01:01')
				]),
			
			Block([
				Static('08:'),
				GeneratorList(groupSeq[1], [
					Static('08'),
					BadString(),
					BadNumbers(),
					Static('08')
					]),
				Static(':01')
				]),
			
			Block([
				Static('08:01'),
				GeneratorList(groupSeq[2], [
					Static('08'),
					BadString(),
					BadNumbers(),
					Static('08')
					])
				])
			])


class BadDate(SimpleGenerator):
	'''
	[BETA] Generates alot of funky date's.  This Generator is still missing
	alot of test cases.
	
		- Invalid month, year, day
		- Mixed up stuff
		- Crazy odd date formats
	'''
	
	_strings = [
		'1/1/1',
		'0/0/0',
		'0-0-0',
		'00-00-00',
		'-1/-1/-1',
		'XX/XX/XX',
		'-1-1-1-1-1-1-1-1-1-1-1-',
		'Jun 39th 1999',
		'June -1th 1999',
		
		# ANSI Date formats
		'2000',
		'1997',
		'0000',
		'0001',
		'9999',
		
		'0000-00',
		'0000-01',
		'0000-99',
		'0000-13',
		'0001-00',
		'0001-01',
		'0001-99',
		'0001-13',
		'9999-00',
		'9999-01',
		'9999-99',
		'9999-13',
		
		'0000-00-00',
		'0000-01-00',
		'0000-99-00',
		'0000-13-00',
		'0001-00-00',
		'0001-01-00',
		'0001-99-00',
		'0001-13-00',
		'9999-00-00',
		'9999-01-00',
		'9999-99-00',
		'9999-13-00',
		'0000-00-01',
		'0000-01-01',
		'0000-99-01',
		'0000-13-01',
		'0001-00-01',
		'0001-01-01',
		'0001-99-01',
		'0001-13-01',
		'9999-00-01',
		'9999-01-01',
		'9999-99-01',
		'9999-13-01',
		'0000-00-99',
		'0000-01-99',
		'0000-99-99',
		'0000-13-99',
		'0001-00-99',
		'0001-01-99',
		'0001-99-99',
		'0001-13-99',
		'9999-00-99',
		'9999-01-99',
		'9999-99-99',
		'9999-13-99',
		]
	
	def __init__(self, group = None):
		SimpleGenerator.__init__(self, group)
		self._generator = List(None, self._strings)
	
	def unittest():
		g = BadDate(None)
		
		if g.getValue() != '1/1/1':
			raise Exception("BadDate unittest failed #1")
		g.next()
		
		if g.getValue() != '0/0/0':
			raise Exception("BadDate unittest failed #2")
		
		print "BadDate okay\n"
	unittest = staticmethod(unittest)


class NumberLimiter(Generator):
	'''
	Wraps another generator that produces numbers and limits the produced
	number to a range.  If the number produced is outside of this range
	we will skip it.
	'''
	
	def __init__(self, group, generator, min, max):
		'''
		Min and max can be used to limit the produced numbers.
		
		@type	group: Group
		@param	group: Group to use
		@type	generator: Generator
		@param	generator: Generatored number to limit
		@param	min: Number
		@type	min: Minimum allowed number
		@param	max: Number
		@type	max: Maximum allowed number
		'''
		
		Generator.__init__(self)
		self.setGroup(group)
		
		self._generator = generator
		self._min = min
		self._max = max
		self._lastGood = str(self._min)
	
	def _checkAndSkip(self):
		val = int(self._generator.getValue())
		
		while val < self._min or val > self._max:
			#print "_checkAndSkip: Skipping: ", val
			self._generator.next()
			val = int(self._generator.getValue())
	
	def next(self):
		self._generator.next()
		self._checkAndSkip()
	
	def reset(self):
		self._generator.reset()
		self._checkAndSkip()
	
	def getRawValue(self):
		val = int(self._generator.getValue())
		
		if val < self._min or val > self._max:
			return self._lastGood
		
		self._lastGood = str(val)
		return self._lastGood


class StringVariance(Generator):
	'''
	Generate a range of string sizes from len(str) - variance to len(str) + variance.
	'''
	
	
	def __init__(self, group, string, variance, min = None, max = None):
		'''
		Min and max can be used to limit the produced numbers.
		
		@type	group: Group
		@param	group: Group to use
		@type	string: String or Generator
		@param	string: String to vary length of
		@type	variance: + and - change to give length range
		@param	min: Number
		@type	min: Minimum allowed length
		@param	max: Number
		@type	max: Maximum allowed length
		'''
		
		Generator.__init__(self)
		self.setGroup(group)
		
		self._number = None
		self._variance = None
		self._min = None
		self._max = None
		self._current = None
		
		# Can't create negative strings :)
		if variance > len(string) and min == None:
			min = 0
		
		if min != None and min < 0:
			raise Exception("Negative string min length???")
		
		self._string = string
		self._stringLength = len(string)
		self._numberVariance = NumberVariance(None, len(string), variance, min, max)
		self._minAllowed = min
		self._maxAllowed = max
		self._current = string[:self._numberVariance.getValue()]
	
	def getRawValue(self):
		return self._current
	
	def next(self):
		self._numberVariance.next()
		
		# make current value
		length = self._numberVariance.getValue()
		if length < self._stringLength:
			self._current = self._string[:length]
		else:
			multiplier = (length/self._stringLength) + 1
			#print "Multiplier: ",multiplier
			#print "Target length: ",length
			val = self._string * multiplier
			self._current = val[:length]
	
	def reset(self):
		self._numberVariance.reset()


class NumberVariance(Generator):
	'''
	Generate a range of numbers from (number - variance) to (number + variance).
	
	Example:
	
		>>> gen = NumberVariance(None, 10, 5)
		>>> print gen.getValue()
		5
		>>> gen.next()
		>>> gen.getValue()
		6
		>>> gen.next()
		>>> gen.getValue()
		7
		>>> gen.next()
		>>> gen.getValue()
		8
		>>> gen.next()
		>>> gen.getValue()
		9
		>>> gen.next()
		>>> gen.getValue()
		10
		>>> gen.next()
		>>> gen.getValue()
		11
		>>> gen.next()
		>>> gen.getValue()
		12
		>>> gen.next()
		>>> gen.getValue()
		13
		>>> gen.next()
		>>> gen.getValue()
		14
		>>> gen.next()
		>>> gen.getValue()
		15
	'''
	
	def __init__(self, group, number, variance, min = None, max = None):
		'''
		Min and max can be used to limit the produced numbers.
		
		When using a generator's value will be gotten on the first call to
		our .getRawValue/getValue methods that occur after a reset().
		
		@type	group: Group
		@param	group: Group to use
		@type	number: Number or Generator
		@param	number: Number to change
		@type	variance: + and - change to give range
		@param	min: Number
		@type	min: Minimum allowed number
		@param	max: Number
		@type	max: Maximum allowed number
		'''
		
		Generator.__init__(self)
		self.setGroup(group)
		
		if str(type(number)) != "<type 'int'>" and str(type(number)) != "<type 'long'>":
			self._generator = number
			self._number = None
			self._isGenerator = True
		else:
			self._generator = None
			self._number = number
			self._isGenerator = False
		
		# Max range of values
		self._variance = long(variance)
		self._totalVariance = (self._variance * 2) + 1
		
		# Min and Max value to be generated
		self._minAllowed = min
		self._maxAllowed = max
		
		# Current index into range of values
		self._current = 0
		self._currentRange = None
		
		# Calculate this upfront as well to make sure
		# our iteration count is correct!
		if self._isGenerator:
			num = long(self._generator.getValue())
		else:
			num = long(self._number)		
		
		if (num - self._variance) < (num + self._variance):
			min = num - self._variance
			max = num + self._variance
		else:
			max = num - self._variance
			min = num + self._variance
		
		if self._minAllowed != None and min < self._minAllowed:
			min = self._minAllowed
		
		if self._maxAllowed != None and max > self._maxAllowed:
			max = self._maxAllowed
		
		self._currentRange = range(min, max)
	
	def next(self):
		self._current += 1
		if self._current > self._totalVariance:
			raise GeneratorCompleted("NumberVariance 1")
		
		if self._currentRange != None and self._current >= len(self._currentRange):
			raise GeneratorCompleted("NumberVariance 2")
	
	def getRawValue(self):
		# Always get the value from the generator.  In the case of
		# a BlockSize generator this can change when we are recursing
		
		if self._isGenerator:
			num = long(self._generator.getValue())
		else:
			num = long(self._number)		
		
		if (num - self._variance) < (num + self._variance):
			min = num - self._variance
			max = num + self._variance
		else:
			max = num - self._variance
			min = num + self._variance
		
		if self._minAllowed != None and min < self._minAllowed:
			min = self._minAllowed
		
		if self._maxAllowed != None and max > self._maxAllowed:
			max = self._maxAllowed
		
		self._currentRange = range(min, max)
		
		try:
			#print "NumberVariance.getRawValue(): [%d-%d:%d:%d] Returning %d" % (min, max, self._current, len(self._currentRange), self._currentRange[self._current])
			return str(self._currentRange[self._current])
		except:
			#print "NumberVariance.getRawValue(): Returning %d" % self._currentRange[-1]
			return str(self._currentRange[-1])
	

	def reset(self):
		self._current = 0
	
	def unittest():
		gen = NumberVariance(None, 10, 5)
		for cnt in range(5, 15):
			if cnt != gen.getValue():
				raise Exception("NumberVariance broken %d != %d" % (cnt, gen.getValue()))
		
		print "NumberVariance OK!"
		
	unittest = staticmethod(unittest)


class NumbersVariance(SimpleGenerator):
	'''
	Performs a L{NumberVariance} on a list of numbers.  This is a specialized
	version of L{NumberVariance} that takes an array of numbers to perform a
	variance on instead of just a single number.
	
	Example:
	
		>>> gen = NumbersVariance(None, [1,10], 1)
		>>> gen.getValue()
		0
		>>> gen.next()
		>>> gen.getValue()
		1
		>>> gen.next()
		>>> gen.getValue()
		2
		>>> gen.next()
		>>> gen.getValue()
		9
		>>> gen.next()
		>>> gen.getValue()
		10
		>>> gen.next()
		>>> gen.getValue()
		11
		
	
	@see: L{NumberVariance}
	
	'''

	def __init__(self, group, numbers, variance):
		'''
		@type	group: Group
		@param	group: Group to use
		@type	numbers: Array of numbers
		@param	numbers: Numbers to change
		@type	variance: + and - change to give range
		'''
		
		Generator.__init__(self)
		self.setGroup(group)
		
		gens = []
		
		for n in numbers:
			gens.append(NumberVariance(None, n, variance))
		
		self._generator = GeneratorList(group, gens)
		
	def unittest():
		raise Exception("NumbersVariance needs a unittest"		)
	unittest = staticmethod(unittest)



class BadNumbersAsString(SimpleGenerator):
	'''
	[DEPRICATED] Use L{BadNumbers} instead.
	
	@see: Use L{BadNumbers} instead.
	@depricated
	@undocumented
	'''
	
	_ints = [
		0,
		-128,										# signed 8
		127,
		255,										# unsigned 8
		-32768,										# signed 16
		32767,
		65535,										# unsigned 16
		-2147483648,								# signed 32
		2147483647,
		4294967295,									# unisnged 32
		-9223372036854775808,						# signed 64
		9223372036854775807,
		18446744073709551615,						# unsigned 64
		#-170141183460469231731687303715884105728,	# signed 128
		#170141183460469231731687303715884105727,	# signed 128
		#340282366920938463463374607431768211455,	# unsigned 128
		]
	
	def __init__(self, group = None, N=50):
		SimpleGenerator.__init__(self, group)
		self._generator = WithDefault(None, 10, NumbersVariance(None, self._ints, N))
	
	def getRawValue(self):
		try:
			val = self._generator.getValue()
		
		except OverflowError:
			# Wow, that sucks!
			print "BadNumbersAsString(): OverflowError spot 1!"
			return str(0)
		
		return str(val)


class BadNumbers8(SimpleGenerator):
	'''
	Generate numbers that may trigger integer overflows for
	both signed and unsigned numbers.  Under the hood this generator
	performs a L{NumbersVariance} on the boundry numbers for:
	
		- int8 (0, -128, 127)
		- unsigned int8 (255)
	
	@see: L{BadNumbers}, L{NumbersVariance}, L{BadUnsignedNumbers}, L{BadPositiveNumbers}
	'''
	
	_ints = [
		0,
		-128,	# signed 8
		127,
		255,	# unsigned 8
		]
	
	def __init__(self, group = None):
		SimpleGenerator.__init__(self, group)
		self._generator = List(None, range(0, 255))
	
	def getRawValue(self):
		try:
			val = self._generator.getValue()
		
		except OverflowError:
			# Wow, that sucks!
			print "BadNumbersAsString8(): OverflowError spot 1!"
			return str(0)
		
		return str(val)

class BadNumbers16(SimpleGenerator):
	'''
	Generate numbers that may trigger integer overflows for
	both signed and unsigned numbers.  Under the hood this generator
	performs a L{NumbersVariance} on the boundry numbers for:
	
		- int8 (0, -128, 127)
		- unsigned int8 (255)
		- int16 (-32768, 32767)
		- unsigned int16 (65535)
	
	@see: L{BadNumbers}, L{NumbersVariance}, L{BadUnsignedNumbers}, L{BadPositiveNumbers}
	'''
	
	_ints = [
		0,
		-128,	# signed 8
		127,
		255,	# unsigned 8
		-32768,	# signed 16
		32767,
		65535	# unsigned 16
		]
	
	def __init__(self, group = None, N = 50):
		SimpleGenerator.__init__(self, group)
		self._generator = WithDefault(None, 10, NumbersVariance(None, self._ints, N))
	
	def getRawValue(self):
		try:
			val = self._generator.getValue()
		
		except OverflowError:
			# Wow, that sucks!
			print "BadNumbersAsString16(): OverflowError spot 1!"
			return str(0)
		
		return str(val)



class BadNumbers24(SimpleGenerator):
	'''
	Generate numbers that may trigger integer overflows for
	both signed and unsigned numbers.  Under the hood this generator
	performs a L{NumbersVariance} on the boundry numbers for:
	
		- int8 (0, -128, 127)
		- unsigned int8 (255)
		- int16 (-32768, 32767)
		- unsigned int16 (65535)
		- int24 (-8388608, 8388607 )
		- unsigned int24 (16777216)
	
	@see: L{BadNumbers}, L{NumbersVariance}, L{BadUnsignedNumbers}, L{BadPositiveNumbers}
	'''
	
	_ints = [
		0,
		-128,	# signed 8
		127,
		255,	# unsigned 8
		-32768,	# signed 16
		32767,
		65535,	# unsigned 16
		-8388608,
		8388607,
		16777216 # unisnged 24
		]
	
	def __init__(self, group = None, N = 50):
		SimpleGenerator.__init__(self, group)
		self._generator = WithDefault(None, 10, NumbersVariance(None, self._ints, N))
	
	def getRawValue(self):
		try:
			val = self._generator.getValue()
		
		except OverflowError:
			# Wow, that sucks!
			print "BadNumbersAsString16(): OverflowError spot 1!"
			return str(0)
		
		return str(val)




class BadNumbers32(SimpleGenerator):
	'''
	Generate numbers that may trigger integer overflows for
	both signed and unsigned numbers.  Under the hood this generator
	performs a L{NumbersVariance} on the boundry numbers for:
	
		- int8 (0, -128, 127)
		- unsigned int8 (255)
		- int16 (-32768, 32767)
		- unsigned int16 (65535)
		- int32 (-2147483648, 2147483647)
		- unsigned int32 (4294967295)
	
	@see: L{BadNumbers}, L{NumbersVariance}, L{BadUnsignedNumbers}, L{BadPositiveNumbers}
	'''
	
	_ints = [
		0,
		-128,	# signed 8
		127,
		255,	# unsigned 8
		-32768,	# signed 16
		32767,
		65535,	# unsigned 16
		2147483647,
		4294967295,				# unisnged 32
		]
	
	def __init__(self, group = None, N=50):
		SimpleGenerator.__init__(self, group)
		self._generator = WithDefault(None, 10, NumbersVariance(None, self._ints, N))
	
	def getRawValue(self):
		try:
			val = self._generator.getValue()
		
		except OverflowError:
			# Wow, that sucks!
			print "BadNumbersAsString16(): OverflowError spot 1!"
			return str(0)
		
		return str(val)


class BadNumbers(BadNumbersAsString):
	'''
	Generate numbers that may trigger integer overflows for
	both signed and unsigned numbers.  Under the hood this generator
	performs a L{NumbersVariance} on the boundry numbers for:
	
		- int8 (0, -128, 127)
		- unsigned int8 (255)
		- int16 (-32768, 32767)
		- unsigned int16 (65535)
		- int32 (-2147483648, 2147483647)
		- unsigned int32 (4294967295)
		- int64 (-9223372036854775808, 9223372036854775807)
		- unsigned int64 (18446744073709551615)
	
	@see: L{BadNumbers16}, L{NumbersVariance}, L{BadUnsignedNumbers}, L{BadPositiveNumbers}
	'''
	pass


class BadPositiveNumbers(SimpleGenerator):
	'''
	Generate positive numbers that may trigger integer overflows for
	both signed and unsigned numbers.  Under the hood this generator
	performs a L{NumbersVariance} on the boundry numbers for:
	
		- int8 (0, 127)
		- unsigned int8 (255)
		- int16 (32767)
		- unsigned int16 (65535)
		- int32 (2147483647)
		- unsigned int32 (4294967295)
		- int64 (9223372036854775807)
		- unsigned int64 (18446744073709551615)
	
	@see: L{BadNumbers16}, L{NumbersVariance}, L{BadUnsignedNumbers}, L{BadPositiveNumbers}
	'''
	
	_ints = [
		50,						# Don't want any negative numbers
		127,
		255,					# unsigned 8
		32767,
		65535,					# unsigned 16
		2147483647,
		4294967295,				# unisnged 32
		9223372036854775807,
		18446744073709551615,	# unsigned 64
		]
	
	def __init__(self, group = None):
		SimpleGenerator.__init__(self, group)
		self._generator = WithDefault(None, 10, NumbersVariance(None, self._ints, 50))
	
	def getRawValue(self):
		try:
			val = self._generator.getValue()
			
			if val < 0:
				val = 0
		
		except OverflowError:
			# Wow, that sucks!
			print "BadPositiveNumbers(): OverflowError spot 1!"
			return str(0)
		
		return str(val)


class BadPositiveNumbersSmaller(SimpleGenerator):
	'''
	Generate positive numbers that may trigger integer overflows for
	both signed and unsigned numbers.  Under the hood this generator
	performs a L{NumbersVariance} on the boundry numbers for:
	
		- int8 (0, 127)
		- unsigned int8 (255)
		- int16 (32767)
		- unsigned int16 (65535)
		- int32 (2147483647)
		- unsigned int32 (4294967295)
		- int64 (9223372036854775807)
		- unsigned int64 (18446744073709551615)
	
	@see: L{BadNumbers16}, L{NumbersVariance}, L{BadUnsignedNumbers}, L{BadPositiveNumbers}
	'''
	
	_ints = [
		50,						# Don't want any negative numbers
		127,
		255,					# unsigned 8
		32767,
		65535,					# unsigned 16
		]
	
	def __init__(self, group = None):
		SimpleGenerator.__init__(self, group)
		self._generator = WithDefault(None, 10, NumbersVariance(None, self._ints, 50))
	
	def getRawValue(self):
		try:
			val = self._generator.getValue()
			
			if val < 0:
				val = 0
		
		except OverflowError:
			# Wow, that sucks!
			print "BadPositiveNumbers(): OverflowError spot 1!"
			return str(0)
		
		return str(val)


class BadUnsignedNumbers(SimpleGenerator):
	'''
	Generate numbers that may trigger integer overflows for
	both signed and unsigned numbers.  Under the hood this generator
	performs a L{NumbersVariance} on the boundry numbers for:
	
		- unsigned int8  (0, 255)
		- unsigned int16 (65535)
		- unsigned int32 (4294967295)
		- unsigned int64 (18446744073709551615)
	
	@see: L{BadNumbers16}, L{NumbersVariance}, L{BadUnsignedNumbers}, L{BadPositiveNumbers}
	'''
	
	_ints = [
		50,
		255,
		65535,
		4294967295,
		18446744073709551615,
		]
	
	def __init__(self, group = None):
		SimpleGenerator.__init__(self, group)
		self._generator = WithDefault(None, 10, NumbersVariance(None, self._ints, 50))
	
	def getRawValue(self):
		try:
			val = self._generator.getValue()
			
			if val < 0:
				val = 0
		
		except OverflowError:
			# Wow, that sucks!
			print "BadUnsignedNumbers(): OverflowError spot 1!"
			return str(0)
		
		return str(val)
	

class BadUnsignedNumbers16(SimpleGenerator):
	'''
	Generate numbers that may trigger integer overflows for
	both signed and unsigned numbers.  Under the hood this generator
	performs a L{NumbersVariance} on the boundry numbers for:
	
		- unsigned int8  (0, 255)
		- unsigned int16 (65535)
	
	@see: L{BadNumbers16}, L{NumbersVariance}, L{BadUnsignedNumbers}, L{BadPositiveNumbers}
	'''
	
	_ints = [
		50,
		255,
		65535,
		]
	
	def __init__(self, group = None):
		SimpleGenerator.__init__(self, group)
		self._generator = WithDefault(None, 10, NumbersVariance(None, self._ints, 50))
	
	def getRawValue(self):
		try:
			val = self._generator.getValue()
			
			if val < 0:
				val = 0
		
		except OverflowError:
			# Wow, that sucks!
			print "BadUnsignedNumbers(): OverflowError spot 1!"
			return str(0)
		
		return str(val)


class Wrap(SimpleGenerator):
	'''
	Wraps another generator.  This is usefull when you
	want to re-use a generator in a GeneratorList with
	different transformers to change the permutations.
	
	Note: Wrap is implemented using a deep copy of the
	generator object passed to it.
	
	Example:
	
	  gen = Static('123456')
	  
	  allThings = GeneratorList([
		gen,
		Wrap(gen).setTransformer(HtmlEncode()),
		Wrap(gen).setTransformer(UrlEncode())
		])
	
	'''
	
	def __init__(self, generator):
		'''
		@type	group: Group
		@param	group: Group to use
		@type	generator: Generator
		@param	group: Generator to wrap
		'''
		
		Generator.__init__(self)
		self._generator = copy.deepcopy(generator)


class BadIpAddress(SimpleGenerator):
	'''
	[BETA] Generate some bad ip addresses.  Needs work
	should also implement one for ipv6.
	'''
	
	def __init__(self, group = None):
		SimpleGenerator.__init__(self, group)
		self._groupA = Group()
		self._groupB = Group()
		self._generator = GeneratorList(None, [
			Static('10.10.10.10'),
			
			GeneratorList2(None, [
				self._groupA,
				self._groupB
				], [
				GeneratorList(self._groupA, [
					List(None, [
						'0', '0.', '1.', '1.1', '1.1.1', '1.1.1.1.',
						'.1', '.1.1.1', '.1.1.1.1',
						'1.1.1.1\0AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA',
						'0.0.0.0',
						'127.0.0.1',
						'255.255.255',
						'0.0.0.0',
						'256.256.256',
						'-1.-1.-1.-1',
						'FF.FF.FF',
						'\0.\0.\0.\0',
						'\01.\01.\01.\01',
						'\00.\00.\00.\00',
						'1\0.1\0.1\0.1\0',
						'1\0.\01\0.\01\0.\01\0',
						'0\0.\00\0.\00\0.\00\0',
						'999.999.999'
						]),
					
					Block2([
						BadNumbersAsString(),
						Static('.'),
						BadNumbersAsString(),
						Static('.'),
						BadNumbersAsString(),
						Static('.'),
						BadNumbersAsString()
						])
					]),
				
				Block([
					Repeater(self._groupB, Static('120.'), 1, 20),
					Static('1')
					]),
				], 'BadIpAddress-Sub'),
			
				Static('10.10.10.10')
			], 'BadIpAddress')


class TopLevelDomains(SimpleGenerator):
	'''
	Top-level domain names in upper case.  List current
	as of 12/06/2006.  Includes country's.
	'''
	
	def __init__(self, group = None):
		SimpleGenerator.__init__(self, group)
		self._generator = List(None, [
			'com',
			'AC',	'AD',	'AE',	'AERO',	'AF',
			'AG',	'AI',	'AL',	'AM',	'AN',
			'AO',	'AQ',	'AR',	'ARPA',	'AS',
			'AT',	'AU',	'AW',	'AX',	'AZ',
			'BA',	'BB',	'BD',	'BE',	'BF',
			'BG',	'BH',	'BI',	'BIZ',	'BJ',
			'BM',	'BN',	'BO',	'BR',	'BS',
			'BT',	'BV',	'BW',	'BY',	'BZ',
			'CA',	'CAT',	'CC',	'CD',	'CF',
			'CG',	'CH',	'CI',	'CK',	'CL',
			'CM',	'CN',	'CO',	'COM',	'COOP',
			'CR',	'CU',	'CV',	'CX',	'CY',
			'CZ',	'DE',	'DJ',	'DK',	'DM',
			'DO',	'DZ',	'EC',	'EDU',	'EE',
			'EG',	'ER',	'ES',	'ET',	'EU',
			'FI',	'FJ',	'FK',	'FM',	'FO',
			'FR',	'GA',	'GB',	'GD',	'GE',
			'GF',	'GG',	'GH',	'GI',	'GL',
			'GM',	'GN',	'GOV',	'GP',	'GQ',
			'GR',	'GS',	'GT',	'GU',	'GW',
			'GY',	'HK',	'HM',	'HN',	'HR',
			'HT',	'HU',	'ID',	'IE',	'IL',
			'IM',	'IN',	'INFO',	'INT',	'IO',
			'IQ',	'IR',	'IS',	'IT',	'JE',
			'JM',	'JO',	'JOBS',	'JP',	'KE',
			'KG',	'KH',	'KI',	'KM',	'KN',
			'KR',	'KW',	'KY',	'KZ',	'LA',
			'LB',	'LC',	'LI',	'LK',	'LR',
			'LS',	'LT',	'LU',	'LV',	'LY',
			'MA',	'MC',	'MD',	'MG',	'MH',
			'MIL',	'MK',	'ML',	'MM',	'MN',
			'MO',	'MOBI',	'MP',	'MQ',	'MR',
			'MS',	'MT',	'MU',	'MUSEUM',	'MV',
			'MW',	'MX',	'MY',	'MZ',	'NA',
			'NAME',	'NC',	'NE',	'NET',	'NF',
			'NG',	'NI',	'NL',	'NO',	'NP',
			'NR',	'NU',	'NZ',	'OM',	'ORG',
			'PA',	'PE',	'PF',	'PG',	'PH',
			'PK',	'PL',	'PM',	'PN',	'PR',
			'PRO',	'PS',	'PT',	'PW',	'PY',
			'QA',	'RE',	'RO',	'RU',	'RW',
			'SA',	'SB',	'SC',	'SD',	'SE',
			'SG',	'SH',	'SI',	'SJ',	'SK',
			'SL',	'SM',	'SN',	'SO',	'SR',
			'ST',	'SU',	'SV',	'SY',	'SZ',
			'TC',	'TD',	'TF',	'TG',	'TH',
			'TJ',	'TK',	'TL',	'TM',	'TN',
			'TO',	'TP',	'TR',	'TRAVEL',	'TT',
			'TV',	'TW',	'TZ',	'UA',	'UG',
			'UK',	'UM',	'US',	'UY',	'UZ',
			'VA',	'VC',	'VE',	'VG',	'VI',
			'VN',	'VU',	'WF',	'WS',	'YE',
			'YT',	'YU',	'ZA',	'ZM',	'ZW',
			'com'
			])


class BadHostname(BadString):
	'''
	[BETA] Crazy hostnames.
	'''
	
	def __init__(self, group = None):
		SimpleGenerator.__init__(self, group)
		self._generator = GeneratorList(None, [
			Static('localhost'),
			BadString(),
			Repeater(None, Static('A'), 1, 1000),
			Repeater(None, Static('A'), 100, 100),
			Repeater(None, Static('A.'), 5, 100),
			Repeater(None, Static('.'), 1, 10),
			Repeater(None, Static('.'), 20, 20),
			Block2([
				Repeater(None, Static('A'), 5, 20),
				Static('.'),
				Repeater(None, Static('A'), 5, 20),
				Static('.'),
				Repeater(None, Static('A'), 5, 20)
				]),
			Block2([
				Static('AAAA.'),
				TopLevelDomains()
				]),
			
			Static('localhost')
			])


class BadPath(BadString):
	'''
	[BETA] Path generation fun!
	'''
	
	def __init__(self, group = None):
		SimpleGenerator.__init__(self, group)
		self._generator = GeneratorList(None, [
			Static('A'),
			Repeater(None, Static('.'), 1, 1000),
			Repeater(None, Static('\\'), 1, 1000),
			Repeater(None, Static('/'), 1, 1000),
			Repeater(None, Static(':'), 1, 1000),
			Repeater(None, Static('../'), 1, 1000),
			Repeater(None, Static('..\\'), 1, 1000),
			Repeater(None, Static('*\\'), 10, 100),
			Repeater(None, Static('*/'), 10, 100),
			Repeater(None, Static('//\\'), 10, 100),
			Repeater(None, Static('//..\\..'), 10, 100),
			Repeater(None, Static('aaa//'), 10, 100),
			Repeater(None, Static('aaa\\'), 10, 100),
			Block2([
				BadString(),
				Static(':\\')
				]),
			Block2([
				BadString(),
				Static(':/')
				]),
			Block2([
				Static('\\\\'),
				BadString(),
				]),
			Block2([
				Static('./'),
				BadString()
				]),
			Block2([
				Static('/'),
				BadString(),
				Static('/')
				]),
			Static('A')
			])


class BadFilename(BadString):
	'''
	Lots of bad filenames.
	'''
	
	def __init__(self, group = None):
		SimpleGenerator.__init__(self, group)
		self._generator = GeneratorList(None, [
			Static('Peach.txt'),
			BadString(),
			Block2([
				BadString(),
				Static('.'),
				BadString()
				]),
			Block2([
				Static("."),
				BadString()
				]),
			Block2([
				BadString(),
				Static('.')
				]),
			Repeater(None, Static('.'), 1, 1000),
			Repeater(None, Static("a.a"), 1, 1000),
			Block2([
				Static("A."),
				Repeater(None, Static('A'), 1, 1000)
				]),
			Block2([
				Repeater(None, Static('A'), 1, 1000),
				Static('.A')
				]),
			Block2([
				Static('AAAA'),
				Repeater(None, Static('.doc'), 1, 1000)
				]),
			Block2([
				Repeater(None, Static('A'), 10, 100),
				Static('.'),
				Repeater(None, Static('A'), 10, 100)
				]),
				Static('Peach.txt'),
			])

class AsInt4x4(SimpleGenerator):
	'''
	Specify the high and low parts of an Int8
	'''
	
	def __init__(self, group, high, low, isLittleEndian = 1):
		'''
		@type	group: Group
		@param	group: [optional] Group for this generator
		@type	high: Generator
		@param	high: High portion of octet
		@type	low: Generator
		@param	low: Low portion of octet
		@type	isLittleEndian: number
		@param	isLittleEndian: 1 for little, 0 for big
		'''
		Generator.__init__(self)
		self.setGroup(group)
		self._high = high
		self._low = low
		self._isLittleEndian = isLittleEndian
	
	def next(self):
		completed = 0
		
		try:
			self._high.next()
		except GeneratorCompleted:
			completed = 1
		
		try:
			self._low.next()
		except GeneratorCompleted:
			if completed == 1:
				raise GeneratorCompleted("AsInt4x4 Completed")
	
	def getRawValue(self):
		
		high = int(self._high.getValue())
		low = int(self._low.getValue())
		
		ret = (high << 4) + low
		
		if self._isLittleEndian == 1:
			return struct.pack("<B", ret)
		else:
			return struct.pack(">B", ret)
	
	def reset(self):
		self._high.reset()
		self._low.reset()
		

class _AsInt(SimpleGenerator):
	'''
	Base class for AsIntXX functions that implements logic
	to skip values that are the same.
	'''
	
	_last = None
	_inMe = 0
	
	def _getValue(self):
		return self._transformer.encode(self._generator.getValue())
	
	def next(self):
		'''
		Our implementation of next will return skip
		values that are the same as the last value generated.
		
		This is done because packing larger numbers down can
		result in the same value lots of times.
		'''
		
		self._generator.next()
		cur = self._getValue()
		
		while cur == self._last:
			# Skip till we have something different
			try:
				self._generator.next()
			except GeneratorCompleted:
				break
			
			cur = self._getValue()
		
		self._last = cur
		
	def reset(self):
		SimpleGenerator.reset(self)
		cur = None
	
	def getRawValue(self):
		return self._generator.getValue()


class AsInt8(_AsInt):
	'''
	Cause generated value to be an 8 bit number.
	'''
	def __init__(self, group, generator, isSigned = 1, isLittleEndian = 1):
		'''
		@type	isSigned: number
		@param	isSigned: 1 for signed, 0 for unsigned
		@type	isLittleEndian: number
		@param	isLittleEndian: 1 for little, 0 for big
		'''
		SimpleGenerator.__init__(self, group)
		self._generator = generator
		self.setTransformer(Peach.Transformers.type.AsInt8(isSigned, isLittleEndian))
		

class AsInt16(_AsInt):
	'''
	Cause generated value to be a 16 bit number
	'''
	def __init__(self, group, generator, isSigned = 1, isLittleEndian = 1):
		'''
		@type	isSigned: number
		@param	isSigned: 1 for signed, 0 for unsigned
		@type	isLittleEndian: number
		@param	isLittleEndian: 1 for little, 0 for big
		'''
		SimpleGenerator.__init__(self, group)
		self._generator = generator
		self.setTransformer(Peach.Transformers.type.AsInt16(isSigned, isLittleEndian))


class AsInt24(_AsInt):
	'''
	Cause generated value to be a 24 bit number (don't ask)
	'''
	def __init__(self, group, generator, isSigned = 1, isLittleEndian = 1):
		'''
		@type	isSigned: number
		@param	isSigned: 1 for signed, 0 for unsigned (we ignore this)
		@type	isLittleEndian: number
		@param	isLittleEndian: 1 for little, 0 for big
		'''
		SimpleGenerator.__init__(self, group)
		self._generator = generator
		self.setTransformer(Peach.Transformers.type.AsInt24(isSigned, isLittleEndian))


class AsInt32(_AsInt):
	'''
	Cause generated value to be a 32 bit number
	'''
	def __init__(self, group, generator, isSigned = 1, isLittleEndian = 1):
		'''
		@type	isSigned: number
		@param	isSigned: 1 for signed, 0 for unsigned
		@type	isLittleEndian: number
		@param	isLittleEndian: 1 for little, 0 for big
		'''
		SimpleGenerator.__init__(self, group)
		self._generator = generator
		self.setTransformer(Peach.Transformers.type.AsInt32(isSigned, isLittleEndian))


class AsInt64(_AsInt):
	'''
	Cause generated value to be a 64 bit number
	'''
	def __init__(self, group, generator, isSigned = 1, isLittleEndian = 1):
		'''
		@type	isSigned: number
		@param	isSigned: 1 for signed, 0 for unsigned
		@type	isLittleEndian: number
		@param	isLittleEndian: 1 for little, 0 for big
		'''
		SimpleGenerator.__init__(self, group)
		self._generator = generator
		self.setTransformer(Peach.Transformers.type.AsInt64(isSigned, isLittleEndian))


class WithDefault(SimpleGenerator):
	'''
	Wrapps a Generator and makes the first and last value be a default value.
	'''
	def __init__(self, group, default, generator):
		'''
		@type	default: Python primitive or Generator
		@param	default: Default value
		@type	generator: Generator
		@param	generator: Generator to wrap
		'''
		SimpleGenerator.__init__(self, group)
		# If the user passed us a generator as our default value, get the
		# first value out of it and use it.
		if (str(type(default)) == "<type 'instance'>" and hasattr(default, "getValue")):
			self._default = default
		else:
			self._default = Static(str(default))
		
		self._generator = GeneratorList(None, [
			self._default,
			generator,
			self._default,
			])
	
	def setDefaultValeu(self, data):
		'''
		Set the default value, assumes we have a static or
		some other generator that exposes a "setValue()" method
		'''
		self._default.setValue(data)


class FixedLengthString(SimpleGenerator):
	'''
	Generates a fixed length string.  If the generated string
	that this wrapps is to long it will be truncated.  If to short
	it will be padded.
	
	@author Collin Greene
	'''
	def __init__(self, group, gen, length, padChar, charSize=1):
		'''
		@type	group: Group
		@param	group: Group
		@type	generator: Generator
		@param	generator: Generator that generates strings
		@type	length: int
		@param	length: Length of string
		@type	padChar: string
		@param	padChar: Character to pad string with
		@type	charSize: int
		@param	charSize: Character size, defaults to 1.  For WCHARs use 2.
		'''
		SimpleGenerator.__init__(self, group)
		self._generator = gen
		self._maxLength = length
		# at minimum charsize must be 1
		self._charSize = max(charSize, 1)
		self._padChar = padChar
		if len(padChar) != charSize:
			raise Exception("FixedLengthString(): padChar is not the same length as charSize.")

	def getRawValue(self):
		val = self._generator.getValue()
		
		if val is not None and len(val) % self._charSize != 0:
			raise Exception("FixedLengthString(): length of value is not a multiple of charSize.")
		
		# If the value is too long, return a subset of it.
		if val is not None and len(val) > self._maxLength * self._charSize:
			return val[:self._maxLength * self._charSize]
		
		# If the value is too short, pad it.
		if val is not None and len(val) < self._maxLength * self._charSize:
		   padding = ((self._maxLength * self._charSize) - len(val)) / self._charSize
		   return val + (self._padChar * padding)
		
		return val



class FlagSet(Generator):
	'''
	Permute the given integer flags into a series of integer values.  Will generate
	all permutations of given flag set.
	
	@author Jon McClintock (jammer@weak.org)
	'''
	
	_flags = []
	_count = 0
	_value = None
	
	def __init__(self, group = None, flags = None):
		'''
		@type	group: Group
		@param	group: Group for this Generator
		@type	flags: Array
		@param 	flags: An array containing the values of flags to permute.
		'''
		generator.Generator.__init__(self)
		self.setGroup(group)
		self._count = 0
		self._value = 0
		if flags == None:
			flags = self._flags = []
		else:
			self._flags = flags
		
		if len(self._flags) > 16:
			raise Exception("More than 16 flags given to FlagSet generator.")
	
	def next(self):
		self._value = None
		self._count += 1
		
		if self._count >= (1 << len(self._flags)):
			raise GeneratorCompleted("End of flags")
		
		self._value = 0
		for i in range(0, len(self._flags)):
			if ( self._count & (1 << i) ) != 0:
				self._value |= self._flags[i]
		
		return True
	
	def reset(self):
		self._count = 0

	def getRawValue(self):
		return self._value

	def unittest():
		print "FlagSet Unittest..."
		
		flags = [0x1, 0x2, 0x3]
		f = FlagSet(None, flags)
		i = 1
		
		try:	
			while f.next():
				#print f.getRawValue()
				i += 1
		
		except GeneratorCompleted:
			if i == (1 << len(flags)):
				print "FlagSet Unittest Completed: %d of %d" % (i, (1<<len(flags)))
				return
			else:
				raise Exception("FlagSet Unittest Failed: %d instead of %d" % (i, (1<<len(flags))))
		raise Exception("FlagSet Unittest Failed")
	unittest = staticmethod(unittest)


class FlagPermutations(FlagSet):
	'''
	Depricated in favor of FlagSet.
	'''
	pass


import random
class PseudoRandomNumber(Generator):
	'''
	Use the pseudo random number generator to return a set of random numbers.
	Each run of numbers will be the same if the seed is the same.  The default
	seed used is 6587243.
	
	NOTE: If numbersOfNumbers is not specified an infinit number of numbers is
	generated.
	'''
	
	_seed = 6587243234234
	
	def __init__(self, group, numberOfNumbers = None, seed = None, min = None, max = None):
		'''
		@type	group: Group
		@param	group: Group
		@type	numberOfNumbers: Number
		@param	numberOfNumbers: [optional] Number of random numbers to generate
		@type	seed: Number
		@param	seed: [optional] Seed to pseudo random number generator
		@type	min: Number
		@param	min: [optional] Minimum number to return
		@type	max: Number
		@param	max: [optional] Maximum number to return
		'''
		
		Generator.__init__(self)
		self.setGroup(group)
		
		if seed != None:
			self._seed = seed
		
		self._min = min
		self._max = max
		self._numberOfNumbers = numberOfNumbers
		self._count = 0
		self._random = random.Random()
		
		if self._min == None and self._max != None:
			raise Exception("Cannot set only one of min or max")
		if self._max == None and self._min != None:
			raise Exception("Cannot set only one of min or max")
		
		self._random.seed(self._seed)
		self._getRandomNumber()
	
	def _getRandomNumber(self):
		if self._min == None:
			#self._current = self._random.randint(0, 18446744073709551615)
			self._current = self._random.random()
		else:
			self._current = self._random.randint(self._min, self._max)
	
	def next(self):
		self._count += 1
		if self._numberOfNumbers != None and self._count >= self._numberOfNumbers:
			raise GeneratorCompleted("PseudoRandomNumber is done")
		self._getRandomNumber()
	
	def reset(self):
		self._random.seed(self._seed)
		self._getRandomNumber()
		self._count = 0
	
	def getRawValue(self):
		return self._current


class BadDerEncodedOctetString(Generator):
	'''
	Performs DER encoding of an octect string with incorrect lengths.
	'''
	
	def __init__(self, group, generator):
		'''
		@type	group: Group
		@param	group: Group
		@type	generator: Generator
		@param	generator: Generator that produces strings that will have bad der encodings done on 'em
		'''
		
		Generator.__init__(self)
		self.setGroup(group)
		self._generator = generator
		self._setupNextValue()
	
	def _setupNextValue(self):
		self._string = self._generator.getValue()
		self._variance = GeneratorList(None, [
			Static(len(self._string)),
			NumberVariance(None, len(self._string), 20, 0),
			Static(len(self._string)),
			])
	
	def next(self):
		try:
			self._variance.next()
		except GeneratorCompleted:
			self._generator.next()
			self._setupNextValue()
	
	def reset(self):
		self._variance.reset()
	
	def getRawValue(self):
		val = '\x04'
		length = self._variance.getValue()
		
		if length < 255:
			val += struct.pack("B", length)
		
		elif length < 65535:
			cal += '\x82'
			val += struct.pack("H", length)
		
		elif length < 4294967295:
			cal += '\x83'
			val += struct.pack("I", length)
		
		elif length < 18446744073709551615:
			cal += '\x84'
			val += struct.pack("L", length)
		
		else:
			raise Exception("Length way to big for us %d" % length)
		
		return val + self._string


class BadBerEncodedOctetString(BadDerEncodedOctetString):
	'''
	Performs BER encoding of an octect string with incorrect lengths.
	'''
	pass


# ############################################################################

class StringTokenFuzzer(SimpleGenerator):
	'''
	Performs fuzzing on each segment of a string.  A string segment is defined
	as a word or portion boundry.  There is an order of precidence for each
	boundry character.  Each portion of the string is fuzzed, then it's children
	are fuzzed, and so on.
	'''
	def __init__(self, group, string, tokens = None, generator = None):
		'''
		@type	group: Group
		@param	group: Group to assign this generator to
		@type	string: String
		@param	string: String to segment and fuzz
		@type	tokens: Array
		@param	tokens: [optional] Array of tokens in order of precidence
		@type	generator: Generator
		@param	generator: [optional] Generator to use for fuzzing each segment
		
		Test strings
		
		Accept-Charset: ISO-8859-1,utf-8;q=0.7,*;q=0.7
		User-Agent: Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.3) Gecko/20070309 Firefox/2.0.0.3
		Accept: text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5
		'''
		SimpleGenerator.__init__(self, group)
		
		if tokens == None:
			# Tokens in order of precidence
			tokens = ['\0', '\n', '\r', '<', '>', '?', ' ', ';',',', '|', '@', ':', '(', ')',
					  '{', '}', '[', ']', '/', '\\', '&', '=', '-', '+', '.']
		
		self._topNode = _StringNode(None, string)
		
		for t in tokens:
			self._tokenTree(t, self._topNode)
		
		if generator == None:
			generator = BadString()
		
		#self._generator = _GeneratorTreeWalker(None, Static("PEACH"), self._topNode)
		self._generator = GeneratorList(None, [
			_GeneratorTreeWalker(None, generator, self._topNode),
			_GeneratorTreeWalkerWrapPhase(None, generator, self._topNode),
			_GeneratorTreeWalkerDuplicatePhase(None, self._topNode),
			_GeneratorTreeWalkerRemovePhase(None, self._topNode)
			])
	
	
	def _split(self, string, tok):
		'''
		A version of split that also returns the tokens.
		'''
		
		pos = string.find(tok)
		lastPos = 0
		parts = []
		
		if pos == -1:
			return parts
		
		while pos > -1:
			parts.append(string[:pos])
			parts.append(string[pos:pos+1])
			string = string[pos+1:]
			lastPos = pos
			pos = string.find(tok)
		
		parts.append(string)
		
		return parts
	
	def _tokenTree(self, token, node):
		
		if node.string == None:
			for child in node.children:
				self._tokenTree(token, child)
			
		else:
			stuff = self._split(node.string, token)
			
			if len(stuff) == 0:
				return
			
			node.string = None
			
			if len(stuff) > 0 and len(node.children) > 0:
				raise Exception("we shouldn't have split a node and have children")
			
			for s in stuff:
				node.children.append( _StringNode(node, s, s == token) )
	
	def buildString(self, node = None):
		'''
		Reassemble node tree into a string
		'''
		
		if node == None:
			node = self._topNode
		
		if node.string == None:
			ret = ''
			
			for child in node.children:
				ret += self.buildString(child)
			
			return ret
		
		else:
			return node.string


class _StringNode(Generator):
	def __init__(self, parent, string, isToken = False):
		Generator.__init__(self)
		
		self.children = []
		self.parent = parent
		self.string = string
		self.isToken = isToken


class _GeneratorTreeWalker(Generator):
	'''
	Internal class that will walk our string tree and apply a generator to
	each node (not just leaf nodes).
	'''
	
	def __init__(self, group, generator, topNode):
		Generator.__init__(self)
		
		self._topNode = topNode
		self._currentNode = topNode
		self._generator = generator
		self._areWeDone = False
		
	def next(self):
		
		if self._areWeDone == True:
			raise GeneratorCompleted("We are still done")
		
		try:
			self._generator.next()
			return
		except GeneratorCompleted:
			pass
		
		self._generator.reset()
		
		# move to next node
		if len(self._currentNode.children) > 0:
			self._currentNode = self._currentNode.children[0]
		
		else:
			self._currentNode = self._moveNext(self._currentNode)
	
	def _moveNext(self, currentNode):
		
		if currentNode.parent == None:
			self._areWeDone = True
			raise GeneratorCompleted("Parent is None so we are done!")
		
		for i in range(len(currentNode.parent.children)):
			if currentNode.parent.children[i] == currentNode:
				if i+1 == len(currentNode.parent.children):
					return self._moveNext(currentNode.parent)
				
				#if currentNode.parent.children[i+1].isToken:
				#	# Skip token nodes
				#	return self._moveNext(currentNode.parent.children[i+1])
				
				return currentNode.parent.children[i+1]
		
		self._areWeDone = True
		raise GeneratorCompleted("Coun't find things")
	
	
	def reset(self):
		self._areWeDone = False
		self._currentNode = self._topNode
		self._generator.reset()
	
	def getRawValue(self):
		return self._buildString()
	
	def _buildString(self, node = None):
		'''
		Reassemble node tree into a string
		'''
		
		if node == self._currentNode or (node == None and self._currentNode == self._topNode):
			return self._generator.getValue()
		
		if node == None:
			node = self._topNode
		
		if node.string == None:
			ret = ''
			
			for child in node.children:
				ret += self._buildString(child)
			
			return ret
		
		else:
			return node.string

class _GeneratorTreeWalkerWrapPhase(Generator):
	'''
	Internal class that will walk our string tree and apply a generator to
	the "sides" of each node (not just leaf nodes).  Each node has a
	generated value placed on each side of it.  This is to further confuse
	parsers.
	'''
	
	def __init__(self, group, generator, topNode):
		Generator.__init__(self)
		
		self._topNode = topNode
		self._currentNode = topNode
		self._generator = generator
		self._areWeDone = False
		
	def next(self):
		
		if self._areWeDone == True:
			raise GeneratorCompleted("We are still done")
		
		try:
			self._generator.next()
			return
		except GeneratorCompleted:
			pass
		
		self._generator.reset()
		
		# move to next node
		if len(self._currentNode.children) > 0:
			self._currentNode = self._currentNode.children[0]
		
		else:
			self._currentNode = self._moveNext(self._currentNode)
	
	def _moveNext(self, currentNode):
		
		if currentNode.parent == None:
			self._areWeDone = True
			raise GeneratorCompleted("Parent is None so we are done!")
		
		for i in range(len(currentNode.parent.children)):
			if currentNode.parent.children[i] == currentNode:
				if i+1 == len(currentNode.parent.children):
					return self._moveNext(currentNode.parent)
				
				if currentNode.parent.children[i+1].isToken:
					# Skip token nodes
					return self._moveNext(currentNode.parent.children[i+1])
				
				return currentNode.parent.children[i+1]
		
		self._areWeDone = True
		raise GeneratorCompleted("Coun't find things")
	
	
	def reset(self):
		self._areWeDone = False
		self._currentNode = self._topNode
		self._generator.reset()
	
	def getRawValue(self):
		return self._buildString()
	
	def _buildString(self, node = None):
		'''
		Reassemble node tree into a string
		'''
		
		if node == self._currentNode or (node == None and self._currentNode == self._topNode):
			val = self._generator.getValue()
			try:
				return val + self._buildString2(node) + val
			except UnicodeDecodeError:
				print "val: ", repr(val)
				print "identify:", self._generator.identity()
				raise
		
		if node == None:
			node = self._topNode
		
		if node.string == None:
			ret = ''
			
			for child in node.children:
				ret += self._buildString(child)
			
			return ret
		
		else:
			return node.string
	
	def _buildString2(self, node = None):
		'''
		Reassemble node tree into a string
		'''
		
		if node == None:
			node = self._topNode
		
		if node.string == None:
			ret = ''
			
			for child in node.children:
				ret += self._buildString(child)
			
			return ret
		
		else:
			return node.string

class _GeneratorTreeWalkerDuplicatePhase(Generator):
	'''
	Internal class that will walk our string tree and duplicate nodes
	not just leaf nodes.  So if you have a string like "http://user:pass@host"
	you will get variationslike:
	
	http://user:pass@host
	http://user::pass@host
	http://user:pass@host@host
	http://user:passuser:pass@host
	
	etc.
	
	'''
	
	def __init__(self, group, topNode):
		Generator.__init__(self)
		
		self._topNode = topNode
		self._currentNode = topNode
		self._areWeDone = False
		self._sample = [2, 3, 10, 15, 20]
		self._samplePos = 0
		
	def next(self):
		
		if self._areWeDone == True:
			raise GeneratorCompleted("We are still done")
		
		self._samplePos += 1
		
		if self._samplePos >= len(self._sample):
			self._samplePos -= 1
			
			# move to next node
			if len(self._currentNode.children) > 0:
				self._currentNode = self._currentNode.children[0]
			
			else:
				self._currentNode = self._moveNext(self._currentNode)
			
			self._samplePos = 0
		
	
	def _moveNext(self, currentNode):
		
		if currentNode.parent == None:
			self._areWeDone = True
			raise GeneratorCompleted("Parent is None so we are done!")
		
		for i in range(len(currentNode.parent.children)):
			if currentNode.parent.children[i] == currentNode:
				if i+1 == len(currentNode.parent.children):
					return self._moveNext(currentNode.parent)
				
				#if currentNode.parent.children[i+1].isToken:
				#	# Skip token nodes
				#	return self._moveNext(currentNode.parent.children[i+1])
				
				return currentNode.parent.children[i+1]
		
		self._areWeDone = True
		raise GeneratorCompleted("Coun't find things")
	
	
	def reset(self):
		self._areWeDone = False
		self._currentNode = self._topNode
		self._samplePos = 0
	
	def getRawValue(self):
		return self._buildString()
	
	def _buildString(self, node = None):
		'''
		Reassemble node tree into a string
		'''
		
		if node == self._currentNode or (node == None and self._currentNode == self._topNode):
			try:
				return self._buildString2(node) * self._sample[self._samplePos]
			except UnicodeDecodeError:
				print "val: ", repr(val)
				print "identify:", self._generator.identity()
				raise
		
		if node == None:
			node = self._topNode
		
		if node.string == None:
			ret = ''
			
			for child in node.children:
				ret += self._buildString(child)
			
			return ret
		
		else:
			return node.string
	
	def _buildString2(self, node = None):
		'''
		Reassemble node tree into a string
		'''
		
		if node == None:
			node = self._topNode
		
		if node.string == None:
			ret = ''
			
			for child in node.children:
				ret += self._buildString(child)
			
			return ret
		
		else:
			return node.string

class _GeneratorTreeWalkerRemovePhase(_GeneratorTreeWalkerDuplicatePhase):
	'''
	Internal class that will walk our string tree and remove one node at
	at time.  Given "http://user:pass@host" you will get things like:
	
	""
	"://user:pass@host"
	"http//user:pass@host"
	"http:/user:pass@host"
	"http://:pass@host"
	"http://userpass@host"
	"http://user:@host"
	"http://user:passhost"
	"http://user:pass@"
	
	'''
	
	def __init__(self, group, topNode):
		Generator.__init__(self)
		self._topNode = topNode
		self._currentNode = topNode
		self._areWeDone = False
		
	def next(self):
		
		if self._areWeDone == True:
			raise GeneratorCompleted("We are still done")
		
		# move to next node
		if len(self._currentNode.children) > 0:
			self._currentNode = self._currentNode.children[0]
		
		else:
			self._currentNode = self._moveNext(self._currentNode)
		
	
	def reset(self):
		self._areWeDone = False
		self._currentNode = self._topNode
		self._samplePos = 0
	
	def _buildString(self, node = None):
		'''
		Reassemble node tree into a string
		'''
		
		if node == self._currentNode or (node == None and self._currentNode == self._topNode):
			return ""
		
		if node == None:
			node = self._topNode
		
		if node.string == None:
			ret = ''
			
			for child in node.children:
				ret += self._buildString(child)
			
			return ret
		
		else:
			return node.string

# ############################################################################

class EthernetChecksum(generator.Generator):
	'''
	Will generate the Ethernet checksum of Block or another Generator.  EthernetChecksum can
	can detect recursive calls and provides a default based on ICMP RFC.
	
	Produced value is 16 bits.
	
	Example:
	
		>>> block = Block([ Static('12345') ])
		>>> icmpChecksum = IcmpChecksum( block )
		>>> print icmpChecksum.getValue()
		5
	
	'''

	_inGetRawValue = 0	
	
	def __init__(self, block):
		'''
		@type	block: Block
		@param	block: Block to get size of
		'''
		generator.Generator.__init__(self)
		self._block = None
		self.setBlock(block)
		self._defaultValue = struct.pack("!H", 0)
		self._insideSelf = False
	
	def _checksum(self, checksum_packet):
		"""Calculate checksum"""
		ethernetKey = 0x04C11DB7
		return binascii.crc32(checksum_packet, ethernetKey)
		
	def getValue(self):
		'''
		Return data, passed through a transformer if set.
		'''
		out = self.getRawValue()
		#print "block.BlockSize::getValue(): out = %s" % out
		if self._transformer != None and self._inGetRawValue == 0:
			out = self._transformer.encode(out)
		
		#print "block.BlockSize::getValue(): out = %s" % out
		return out
	
	def getRawValue(self):
		'''
		Returns size of block as string.
		
		@rtype: string
		@return: size of specified Block
		'''
		
		if self._inGetRawValue == 1:
			# Avoid recursion and return a string
			# that is defaultSize in length
			print "default:" + self._defaultValue
			return self._defaultValue
		
		self._inGetRawValue = 1
		out = self._checksum(str(self._block.getValue()))
		self._inGetRawValue = 0
		return out
	
	def getBlock(self):
		'''
		Get block object we act on.
		
		@rtype: Block
		@return: current Block
		'''
		return self._block
	
	def setBlock(self, block):
		'''
		Set block we act on.
		
		@type	block: Block
		@param	block: Block to set.
		'''
		self._block = block
		return self

# ############################################################################

class IcmpChecksum(generator.Generator):
	'''
	Will generate the ICMP checksum of Block or another Generator.  IcmpChecksum can
	can detect recursive calls and provides a default based on ICMP RFC.
	
	Produced value is 16 bits.
	
	Example:
	
		>>> block = Block([ Static('12345') ])
		>>> icmpChecksum = IcmpChecksum( block )
		>>> print icmpChecksum.getValue()
		5
	
	'''

	_inGetRawValue = 0	
	
	def __init__(self, block):
		'''
		@type	block: Block
		@param	block: Block to get size of
		'''
		generator.Generator.__init__(self)
		self._block = None
		self.setBlock(block)
		self._defaultValue = struct.pack("!H", 0)
		self._insideSelf = False
	
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
	
	def getValue(self):
		'''
		Return data, passed through a transformer if set.
		'''
		out = self.getRawValue()
		#print "block.BlockSize::getValue(): out = %s" % out
		if self._transformer != None and self._inGetRawValue == 0:
			out = self._transformer.encode(out)
		
		#print "block.BlockSize::getValue(): out = %s" % out
		return out
	
	def getRawValue(self):
		'''
		Returns size of block as string.
		
		@rtype: string
		@return: size of specified Block
		'''
		
		if self._inGetRawValue == 1:
			# Avoid recursion and return a string
			# that is defaultSize in length
			print "default:" + self._defaultValue
			return self._defaultValue
		
		self._inGetRawValue = 1
		out = self._checksum(str(self._block.getValue()))
		self._inGetRawValue = 0
		return out
	
	def getBlock(self):
		'''
		Get block object we act on.
		
		@rtype: Block
		@return: current Block
		'''
		return self._block
	
	def setBlock(self, block):
		'''
		Set block we act on.
		
		@type	block: Block
		@param	block: Block to set.
		'''
		self._block = block
		return self
	

# ############################################################################


import inspect, pyclbr

def RunUnit(obj, clsName):
	print "Unittests for: %s..." % clsName,
	cnt = 0
	try:
		while True:
			s = obj.getValue()
			obj.next()
			cnt+=1
			
	except GeneratorCompleted:
		print "%d tests found." % cnt

if __name__ == "__main__":
	print "\n -- Running A Quick Unittest for %s --\n" % __file__
	mod = inspect.getmodulename(__file__)
	for clsName in pyclbr.readmodule(mod):
		cls = globals()[clsName]
		if str(cls).find('__main__') > -1 and hasattr(cls, 'next') and hasattr(cls, 'getValue'):
			try:
				RunUnit(cls(), clsName)
			except TypeError:
				pass

# end
