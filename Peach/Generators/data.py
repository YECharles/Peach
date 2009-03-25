
'''
Common data generators.  Includes common bad strings, numbers, etc.

@author: Michael Eddington
@version: $Id$
'''

#
# Copyright (c) 2006-2009 Michael Eddington
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
		u'Peach',
		u'abcdefghijklmnopqrstuvwxyz',
		u'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
		u'0123456789',
		u'',
		u'10',
		u'0.0',		'1.0',
		u'0.1',		'1.1.1',
		u'-2,147,483,648',
		u'-2,147,483,649',
		u'2,147,483,647',
		u'2,147,483,649',
		u'-2147483648',
		u'-2147483649',
		u'2147483647',
		u'2147483649',
		u'-129',
		u'129',
		u'255',
		u'256',
		u'-32769',
		u'-32,769',
		u'32767',
		u'32769',
		u'4,294,967,295',
		u'4294967299',
		u'-9,223,372,036,854,775,809',
		u'-9223372036854775809',
		u'9,223,372,036,854,775,809',
		u'9223372036854775809',
		u'18,446,744,073,709,551,615',
		u'18,446,744,073,709,551,619',
		u'18446744073709551619',
		u'2.305843009213693952',
		u'200000000000000000000.5',
		u'200000000000000000000000000000000000000000000.5',
		u'0xFF',
		u'0xFFFF',
		u'0xFFFFFF',
		u'0xFFFFFFFFFFFFFFFFFFFF',
		u'Yes',
		u'No',
		u'%n',
		u'%n%n%n%n%n%n%n%n%n%n%n%n%n%n%n%n%n%n%n%n%n%n%n%n%n%n%n%n%n%n%n%n%n%n%n',
		u'%n'*1024,
		u'%x',
		u'%x%x%x%x%x%x%x%x',
		u'%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x',
		u'%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x',
		u'%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x',
		u"""<>"/\'""",
		u"""~`!@#$%^&*()_+=-{}|\][:"';<>?/.,""",
		u'\\"',
		u"\\'",
		u"%",
		u"a%",
		u"%a",
		u"COM1",
		u"COM2",
		u"AUX",
		u"COM1:",
		u"COM2:",
		u"AUX:",
		u"\\\\peach\foo\foo.txt",
		u"\\\\\\",
		u"..\\..\\..\\..\\..\\..\\..\\..\\",
		u"../../../../../",
		u"../",
		u"/../../../../../../",
		u"/../../..",
		u"\\..\\..\\..\\..\\..\\",
		u";,;,;,;,;,;,;,;,;,;,;,;,;,;,;,;,;,;,;,;,;,;,;,;,;,;,;,;,;,;,;,;,;,;,;,;,;,;,;,;,;,;,",
		u";,"*256,
		u";,"*512,
		u";,"*1024,
		u"A;A,"*256,
		u"A;A,"*512,
		u"A;A,"*1024,
		u","*256,
		u","*512,
		u","*1024,
		u"|"*256,
		u"|"*512,
		u"|"*1024,
		u"||"*256,
		u"||"*512,
		u"||"*1024,
		u":"*256,
		u":"*512,
		u":"*1024,
		unichr(0),
		unichr(1), 		unichr(2),
		unichr(3), 		unichr(4),
		unichr(5), 		unichr(6),
		unichr(7), 		unichr(8),
		unichr(9), 		unichr(10),
		unichr(11),        unichr(12),
		unichr(13),        unichr(14),
		unichr(15),        unichr(16),
		unichr(17),        unichr(18),
		unichr(19),        unichr(20),
		unichr(21),        unichr(22),
		unichr(23),        unichr(24),
		unichr(25),        unichr(26),
		unichr(27),        unichr(28),
		unichr(29),        unichr(30),
		unichr(31),        unichr(32),
		unichr(33),        unichr(34),
		unichr(35),        unichr(36),
		unichr(37),        unichr(38),
		unichr(39),        unichr(40),
		unichr(41),        unichr(42),
		unichr(43),        unichr(44),
		unichr(45),        unichr(46),
		unichr(47),        unichr(48),
		unichr(49),        unichr(50),
		unichr(51),        unichr(52),
		unichr(53),        unichr(54),
		unichr(55),        unichr(56),
		unichr(57),        unichr(58),
		unichr(59),        unichr(60),
		unichr(61),        unichr(62),
		unichr(63),        unichr(64),
		unichr(65),        unichr(66),
		unichr(67),        unichr(68),
		unichr(69),        unichr(70),
		unichr(71),        unichr(72),
		unichr(73),        unichr(74),
		unichr(75),        unichr(76),
		unichr(77),        unichr(78),
		unichr(79),        unichr(80),
		unichr(81),        unichr(82),
		unichr(83),        unichr(84),
		unichr(85),        unichr(86),
		unichr(87),        unichr(88),
		unichr(89),        unichr(90),
		unichr(91),        unichr(92),
		unichr(93),        unichr(94),
		unichr(95),        unichr(96),
		unichr(97),        unichr(98),
		unichr(99),        unichr(100),
		unichr(101),       unichr(102),
		unichr(103),       unichr(104),
		unichr(105),       unichr(106),
		unichr(107),       unichr(108),
		unichr(109),       unichr(110),
		unichr(111),       unichr(112),
		unichr(113),       unichr(114),
		unichr(115),       unichr(116),
		unichr(117),       unichr(118),
		unichr(119),       unichr(120),
		unichr(121),       unichr(122),
		unichr(123),       unichr(124),
		unichr(125),       unichr(126),
		unichr(127),       unichr(128),
		unichr(129),       unichr(130),
		unichr(131),       unichr(132),
		unichr(133),       unichr(134),
		unichr(135),       unichr(136),
		unichr(137),       unichr(138),
		unichr(139),       unichr(140),
		unichr(141),       unichr(142),
		unichr(143),       unichr(144),
		unichr(145),       unichr(146),
		unichr(147),       unichr(148),
		unichr(149),       unichr(150),
		unichr(151),       unichr(152),
		unichr(153),       unichr(154),
		unichr(155),       unichr(156),
		unichr(157),       unichr(158),
		unichr(159),       unichr(160),
		unichr(161),       unichr(162),
		unichr(163),       unichr(164),
		unichr(165),       unichr(166),
		unichr(167),       unichr(168),
		unichr(169),       unichr(170),
		unichr(171),       unichr(172),
		unichr(173),       unichr(174),
		unichr(175),       unichr(176),
		unichr(177),       unichr(178),
		unichr(179),       unichr(180),
		unichr(181),       unichr(182),
		unichr(183),       unichr(184),
		unichr(185),       unichr(186),
		unichr(187),       unichr(188),
		unichr(189),       unichr(190),
		unichr(191),       unichr(192),
		unichr(193),       unichr(194),
		unichr(195),       unichr(196),
		unichr(197),       unichr(198),
		unichr(199),       unichr(200),
		unichr(201),       unichr(202),
		unichr(203),       unichr(204),
		unichr(205),       unichr(206),
		unichr(207),       unichr(208),
		unichr(209),       unichr(210),
		unichr(211),       unichr(212),
		unichr(213),       unichr(214),
		unichr(215),       unichr(216),
		unichr(217),       unichr(218),
		unichr(219),       unichr(220),
		unichr(221),       unichr(222),
		unichr(223),       unichr(224),
		unichr(225),       unichr(226),
		unichr(227),       unichr(228),
		unichr(229),       unichr(230),
		unichr(231),       unichr(232),
		unichr(233),       unichr(234),
		unichr(235),       unichr(236),
		unichr(237),       unichr(238),
		unichr(239),       unichr(240),
		unichr(241),       unichr(242),
		unichr(243),       unichr(244),
		unichr(245),       unichr(246),
		unichr(247),       unichr(248),
		unichr(249),       unichr(250),
		unichr(251),       unichr(252),
		unichr(253),       unichr(254),
		unichr(255),
		]
	
	_stringChars = [
		unichr(10),    # LF
		unichr(13),    # CR
		unichr(9),     # Tab
		unichr(32),
		unichr(33),     unichr(34),
		unichr(35),     unichr(36),
		unichr(37),     unichr(38),
		unichr(39),     unichr(40),
		unichr(41),     unichr(42),
		unichr(43),     unichr(44),
		unichr(45),     unichr(46),
		unichr(47),     unichr(48),
		unichr(49),     unichr(50),
		unichr(51),     unichr(52),
		unichr(53),     unichr(54),
		unichr(55),     unichr(56),
		unichr(57),     unichr(58),
		unichr(59),     unichr(60),
		unichr(61),     unichr(62),
		unichr(63),     unichr(64),
		unichr(65),     unichr(66),
		unichr(67),     unichr(68),
		unichr(69),     unichr(70),
		unichr(71),     unichr(72),
		unichr(73),     unichr(74),
		unichr(75),     unichr(76),
		unichr(77),     unichr(78),
		unichr(79),     unichr(80),
		unichr(81),     unichr(82),
		unichr(83),     unichr(84),
		unichr(85),     unichr(86),
		unichr(87),     unichr(88),
		unichr(89),     unichr(90),
		unichr(91),     unichr(92),
		unichr(93),     unichr(94),
		unichr(95),     unichr(96),
		unichr(97),     unichr(98),
		unichr(99),     unichr(100),
		unichr(101),    unichr(102),
		unichr(103),    unichr(104),
		unichr(105),    unichr(106),
		unichr(107),    unichr(108),
		unichr(109),    unichr(110),
		unichr(111),    unichr(112),
		unichr(113),    unichr(114),
		unichr(115),    unichr(116),
		unichr(117),    unichr(118),
		unichr(119),    unichr(120),
		unichr(121),    unichr(122),
		unichr(123),    unichr(124),
		unichr(125),
	]
	
	def __init__(self, group = None):
		SimpleGenerator.__init__(self, group)
		
		# Random strings
		self._randStrings = []
		for i in range(100):
			str = u''
			for x in range(random.choice(range(10, 100))):
				str += random.choice(self._stringChars)
			
			self._randStrings.append(str)
		
		self._generator = GeneratorList(None, [
			List(None, self._strings),
			List(None, self._randStrings),
			Repeater(None, Static(u"A"), 10, 200),
			Repeater(None, Static(u"A"), 127, 100),
			Repeater(None, Static(u"A"), 1024, 10),
			Repeater(None, Static(u"\x41\0"), 10, 200),
			Repeater(None, Static(u"\x41\0"), 127, 100),
			Repeater(None, Static(u"\x41\0"), 1024, 10),

			Block2([
				Static(u'\0\0'),
				Static(u'A'*7000)
				]),

			Block2([
				Static(u'%00%00'),
				Static(u'A'*7000)
				]),
			
			BadNumbers(),
			])
	

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


import random

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


# end
