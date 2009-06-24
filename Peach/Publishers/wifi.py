
'''
AirPcap publisher for wifi fuzzing.

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

from Peach.publisher import *

try:
	from ctypes import *
except:
	pass

class Wifi(Publisher):
	'''
	AirPcap I/O inteface.  Supports sending beacons and standard I/O.
	'''
	
	def __init__(self, device, channel = 5):
		Publisher.__init__(self)
		self.device = device
		self.channel = channel
		self.pcap = None
		self.air = None
		
	def start(self):
		self.pcap = cdll.winpcap.pcap_open_live(self.device, 65536, 1, 1000, errbuff)
		self.air = cdll.winpcap.pcap_get_airpcap_handle(self.pcap)
		cdll.airpcap.AirpcapSetDeviceChannel(self.air, self.channel)
		cdll.airpcap.AirpcapSetLinkType(self.air, AIRPCAP_LT_802_11)
		
	def stop(self):
		if self.pcap != None:
			cdll.winpcap.pcap_close(self.pcap)
			self.pcap = None
	
	def send(self, data):
		'''
		Publish some data
		
		@type	data: string
		@param	data: Data to publish
		'''
		cdll.pcap.pcap_sendpacket(self.pcap, data, len(data))
	
	def receive(self, size = None):
		'''
		Receive some data.
		
		@type	size: integer
		@param	size: Number of bytes to return
		@rtype: string
		@return: data received
		'''
		
		while True:
			res = cdll.winpcap.pcap_next_ex(self.pcap, header, pkt_data)
			
			# if broadcast or to us
			#   return
			# else
			#   keep reading.
		
	
	def call(self, method, args):
		
		if method == 'beacon':
			self.beacon = args[0]
			self._startBeacon()
		
		raise PeachException("Action 'call' not supported by publisher")

	def connect(self):
		'''
		Called to connect or open a connection/file.
		'''
		pass
		
	def close(self):
		'''
		Close current stream/connection.
		'''
		pass

# end
