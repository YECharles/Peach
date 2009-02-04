#!/usr/bin/python

'''
Peach 2 Console Runtime

This is the Peach Runtime.  The Peach Runtime is one of the many ways
to use Peach XML files.  Currently this runtime is still in development
but already exposes several abilities to the end-user such as performing
simple fuzzer runs, converting WireShark captures into Peach XML and
performing parsing tests of Peach XML files.

@author: Michael Eddington
@version: $Id$
'''

#
# Copyright (c) 2007-2009 Michael Eddington
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

import sys, getopt, os
sys.path.append(".")

PROFILE = False

if PROFILE:
	print " --- PROFILING ENABLED ---- "
	import profile

try:
	import Ft
except:
	print "\nError loading 4Suite XML library.  This library"
	print "can be installed from the dependencies folder or"
	print "downloaded from http://4suite.org/.\n\n"
	sys.exit(0)

def printError(str):
	sys.stderr.write("%s\n" % str)

def usage():
	printError("""
This is the Peach Runtime.  The Peach Runtime is one of the many ways
to use Peach XML files.  Currently this runtime is still in development
but already exposes several abilities to the end-user such as performing
simple fuzzer runs, converting WireShark captures into Peach XML and
performing parsing tests of Peach XML files.

All features exposed by this interface can also be accessed via the
Python API.

Please submit any bugs to Michael Eddington <mike@phed.org>.

Syntax:

  peach.py -a [port] [password]
  peach.py -c peach_xml_file [run_name]
  peach.py -g
  peach.py [-r runspot_file] peach_xml_flie [run_name]
  peach.py -p 10,2 [-r runspot_file] peach_xml_flie [run_name]
  peach.py --skipto 100 peach_xml_flie [run_name]
  peach.py -s pdml protocol > output.xml
  peach.py -t peach_xml_file

  -a,--agent                 Launch Peach Agent
  -c,--count                 Count test cases
  -g,--gui                   Launch Peach Builder
  -s,--shark pdml protocol   Convert a Wireshark capture to Peach XML
  -t,--test xml_file         Test parse a Peach XML file
  -w,--web                   Monitor Fuzzer Runs with WebWatcher 
  -r,--restart [file]        Restart fuzzer at saved position
  -p,--parallel M,N          Parallel fuzzing.  Total of M machines, this
                             is machine N.
  --debug                    Enable debug messages. Usefull when debugging
                             your Peach XML file.  Warning: Messages are very
                             cryptic sometimes.
  --skipto N                 Skip to a specific test #

Peach Agent

  Syntax: peach.py -a
  Syntax: peach.py -a port
  Syntax: peach.py -a port password
  
  Starts up a Peach Agent instance on this current machine.  Defaults to
  port 9000.  When specifying a password, the port # must also be given.

Peach Builder

  Syntax: peach.py -g
  
  Start the Peach DDL Editor.

Performing Fuzzing Run

  Syntax: peach.py peach_xml_flie [run_name]
  Syntax: peach.py [-r restart_file] peach_xml_flie [run_name]
  
  A fuzzing run is started by by specifying the Peach XML file and the
  name of a run to perform.
  
  If a run is interupted for some reason it can be restarted using the
  -r parameter and providing the restart file.  Currently these files are
  called "RunSpotSave_date_time.peach".

Performing A Parellel Fuzzing Run

  Syntax: peach.py -p 10,2 [-r runspot_file] peach_xml_flie [run_name]

  A parallel fuzzing run uses multiple machines to perform the same fuzzing
  which shortens the time required.  To run in parallel mode we will need
  to know the total number of machines and which machine we are.  This
  information is fed into Peach via the "-p" command line argument in the
  format "total_machines,our_machine".

WireShark to Peach XML

  Syntax: peach.py -s pdml protocol > output.xml
  
  Peach can convert PDML saved captures into Peach XML Templates.  To
  perform this conversion follow these steps:
  
    1. Perform a capture in WireShark
    2. Select a single packet and save as PDML
    3. Open the PDML file and locate the <proto> element to convert
       and note the name of the protocol
    4. Run Peach using the provided syntax
    5. Modify generated XML as needed

Validate Peach XML File

  Syntax: peach.py -t peach_xml_file
  
  This will perform a parsing pass of the Peach XML file and display any
  errors that are found.

""")
	sys.exit(0)

printError("\n] Peach 2.3 BETA1 Runtime")
printError("] Copyright (c) Michael Eddington\n")

if sys.version[:3] not in ['2.5', '2.6']:
	printError("Error: Peach requires Python v2.5 or v2.6.")
	sys.exit(0)

noCount = False
verbose = False
webWatcher = False
restartFuzzer = False
restartFuzzerFile = None
parallel = None
startNum = None


# Add our root to the python path
if not (hasattr(sys,"frozen") and sys.frozen == "console_exe"):
	sys.path.append(sys.path[0])
else:
	p = os.path.dirname(os.path.abspath(sys.executable))
	sys.path.append(p)
	sys.path.append( os.path.normpath( os.path.join(p, "..") ) )


try:
	(optlist, args) = getopt.getopt(sys.argv[1:], "p:vstcwagr:", ['strategy=','analyzer=', 'parallel=',
																 'restart=', 'parser=',
																 'test', 'count', 'web', 'agent',
																 'gui', 'debug', 'new', 'skipto='])
except:
	usage()

if len(optlist) < 1 and len(args) < 1:
	usage()

for i in range(len(optlist)):
	if optlist[i][0] == '--analyzer':
		
		# set the analyzer to use
		
		try:	
			analyzer = optlist[i][1]
			if analyzer == None or len(analyzer) == 0:
				analyzer = args[0]
			
			from Peach.Engine.common import *
			from Peach.Analyzers import *
			
			cls = eval(analyzer)
			if cls.supportCommandLine:
				print "[*] Using %s as analyzer" % analyzer
				
				cls = eval("%s()" % analyzer)
				
				a = {}
				
				for arg in args[1:]:
					try:
						k,v = arg.split("=")
						a[k] = v
					except:
						#print arg
						#raise
						pass
				
				cls.asCommandLine(a)
			
			elif cls.supportParser:
				print "[*] Using %s as parser" % analyzer
				Analyzer.DefaultParser = cls
		
		except PeachException, pe:
			print ""
			print pe.msg, "\n"
			
		sys.exit(0)
	
	elif optlist[i][0] == '--parser':
		
		# set the analyzer to use
		
		try:	
			analyzer = optlist[i][1]
			if analyzer == None or len(analyzer) == 0:
				analyzer = args[0]
			
			from Peach.Engine.common import *
			from Peach.Analyzers import *
			
			cls = eval(analyzer)
			if cls.supportParser:
				print "[*] Using %s as parser" % analyzer
				Analyzer.DefaultParser = cls
			
			else:
				raise PeachException("Error: Analyzer %s does not support being a parser!" % analyzer)
		
		except PeachException, pe:
			print ""
			print pe.msg, "\n"
			
		sys.exit(0)
	
	elif optlist[i][0] == '--strategy':
		
		# Set the fuzzing strategy to use
		
		try:	
			strategy = optlist[i][1]
			if strategy == None or len(strategy) == 0:
				strategy = args[0]
			
			from Peach.Engine.common import *
			from Peach.mutatestrategies import *
			from Peach.MutateStrategies import *
			
			exec("MutationStrategy.DefaultStrategy = %s" % strategy)
		
		except:
			print ""
			print "Error using mutation strategy '%s'.\n" % strategy
			#raise
			sys.exit(0)
	
	elif optlist[i][0] == '--debug':
		
		# show debugging messages
		
		from Peach.Engine import *
		from Peach.Engine.common import *
		
		engine.Engine.debug = True
		
	elif optlist[i][0] == '--new':
		
		# use the new match relation stuffs
		
		from Peach.Engine import *
		from Peach.Engine.common import *
		
		engine.Engine.relationsNew = True
		
	elif optlist[i][0] == '--test' or optlist[0][0] == '-t':

		# do a parse test

		from Peach.Engine import *
		from Peach.Engine.common import *
		
		try:
			
			# do the test
			if args[0][:5] != 'file:':
				args[0] = 'file:' + args[0]
			
			#parse = parser.ParseTemplate()
			#
			#if PROFILE:
			#	profile.run("parse.parse(args[0])")
			#else:
			#	peach = parse.parse(args[0])

			parser = Analyzer.DefaultParser()
			parser.asParser(args[0])
			
			print "File parsed with out errors."

		except PeachException, pe:
			print ""
			print pe.msg
		
		except Ft.Xml.ReaderException, e:
			print ""
			print "An error occured parsing the XML file\n" + str(e)
		
		except:
			raise
		
		sys.exit(0)
		
	elif optlist[i][0] == '--count' or optlist[i][0] == '-c':
		
		# count the total test case #
		
		from Peach.Engine import *
		from Peach.Engine.common import *
		
		if args[0][:5] != 'file:':
			args[0] = 'file:' + args[0]
		
		engine = engine.Engine()
		if len(args) > 1:
			if PROFILE:
				profile.run("engine.Count(args[0], args[1])")
			else:
				engine.Count(args[0], args[1])
		else:
			if PROFILE:
				profile.run("engine.Count(args[0], None)")
			else:
				engine.Count(args[0], None)
		
		sys.exit(0)
		
	elif optlist[i][0] == '--gui' or optlist[i][0] == '-g':
		
		# Start peach builder UI
		
		from Peach.Engine import *
		from Peach.Engine.common import *

		import os
		from Peach.Gui import PeachGui

		os.chdir( sys.path[0] + "/peach/gui" )

		PeachGui.RunPeachEditor()
		sys.exit(0)
	
	elif optlist[i][0] == '-w' or optlist[i][0] == '--web':
		
		# enable web watcher
		
		webWatcher = True
		
	elif optlist[i][0] == '-r' or optlist[i][0] == '--restart':
		
		# Restarting a fuzzer run
		
		restartFuzzer = True
		restartFuzzerFile = optlist[i][1]
		
	elif optlist[i][0] == '--skipto':
		
		# Skip to a specific test #
		
		startNum = int(optlist[i][1])
		
	elif optlist[i][0] == '-p' or optlist[i][0] == '--parallel':
		
		# Parallel fuzzing run
		
		parallel = optlist[i][1].split(',')
		parallel[0] = int(parallel[0])
		parallel[1] = int(parallel[1])
		
		if parallel[0] < 1:
			print "Error: Machine count must be >= 2."
			sys.exit(0)
		
		if parallel[0] <= parallel[1]:
			print "Error: When performing parallel fuzzing run, the total number of machines must be less than the current machine."
			sys.exit(0)
		
		print "-- Parallel total machines: %d" % parallel[0]
		print "-- Parallel our machine...: %d\n" % parallel[1]
		
	elif optlist[i][0] == '-a' or optlist[i][0] == '--agent':
		
		from Peach.Engine import *
		from Peach.Engine.common import *
		
		# start a peach agent
		port = 9000
		password = None
		try:
			port = int(args[0])
			if len(args[1]) > 0:
				password = args[1]
		except:
			pass
		
		from Peach.agent import Agent
		agent = Agent(password, port)
		sys.exit(0)
		
	elif optlist[i][0] == '-v':
		verbose = True
	
	else:
		usage()

from Peach.Engine import *
from Peach.Engine.common import *

engine = engine.Engine()
watcher = None

try:
	try:
		if args[0][:5] != 'file:':
			args[0] = 'file:' + args[0]
	except:
		raise PeachException("Error, did you supply the Peach Pit file?")
	
	if webWatcher == True:
		from Peach.Engine.webwatcher import PeachWebWatcher
		watcher = PeachWebWatcher()
	
	if len(args) > 1:
		if PROFILE:
			profile.run("engine.Run(args[0], args[1], verbose, watcher, restartFuzzerFile, noCount, parallel)")
		else:
			engine.Run(args[0], args[1], verbose, watcher, restartFuzzerFile, noCount, parallel, startNum)
	
	else:
		if PROFILE:
			profile.run("engine.Run(args[0], None, verbose, watcher, restartFuzzerFile, noCount, parallel)")
		else:
			engine.Run(args[0], None, verbose, watcher, restartFuzzerFile, noCount, parallel, startNum)

except PeachException, pe:
	print ""
	print pe.msg

except Ft.Xml.ReaderException, e:
	print ""
	print "An error occured parsing the XML file\n" + str(e)

except:
	raise
	
# end