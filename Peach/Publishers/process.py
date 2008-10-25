
'''
Start a process with data as parameter.

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


from Peach.publisher import Publisher
import os

class Command(Publisher):
	'''
	Run a command line program passing generated data as
	parameters.
	'''
	
	def call(self, method, args):
		'''
		Call method on COM object.
		
		@type	method: string
		@param	method: Command to execute
		@type	args: array of objects
		@param	args: Arguments to pass
		'''
		
		realArgs = [method]
		for a in args:
			realArgs.append(a)
		
		return os.spawnv(os.P_WAIT, method, realArgs )

# end
