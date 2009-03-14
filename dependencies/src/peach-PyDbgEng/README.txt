PyDbgEng - Python Wrapper For Windows Debugging Engine
======================================================

README FIRST
============

This readme file is way out of date.  The current maintaner (me) has yet
to fully update it.


About
=====
Microsoft releases free and powerfull debugging tools for Windows (1).
The packadge includes the well known 'WinDbg' debugger, which, at its core, runs 
on top the Windows debugging engine - dbgeng.dll.
DbgEng is a powerfull debugger engine. Its features include: user mode / kernel mode, 
local / remote, x86 / x64 debugging capabilities, soft / hard breakpoint support, 
Microsoft symbol server support and more.
DbgEng programming interface is well documented, and one can easily write
their own debugger with DbgEng core. 
PyDbgEng is a Python Wrapper For Microsoft Debug Engine.

Features
========
* Wrapper for DebugCreate() API which creates IDebugClient COM interface.
* Easy access to IDebugClient COM interface
* Easy access to all other DbgEng COM interfaces via IDebugClient.QueryInterface()
* Easy access to all DbgEng structs and enums.
* Receive DbgEng events. Currently supported: IDebugEventCallbacks, IDebugOutputCallbacks

Applications
============
Inspired by DebugStalk (2), PyDbgEng was written with one goal in mind: extend PaiMei's 
PyDbg (3) to stalk kernel targets.
This is of-course just one example. You are invited to write your own unpackers / tracers / fuzzers / 
debuggers with DbgEng and PyDbgEng support.

Technical Details
=====================
DbgEng.dll exports DebugCreate() API which returns IDebugClient COM interface.
A client application can now work with DbgEng via this COM interface.
This interface and all other interfaces are well documented in DbgEng SDK.

	Client =>	DbgEngDll.DebugCreate() => IDebugClient
				IDebugClient.QueryInterface() => IDebugControl,
				IDebugClient.QueryInterface() => IDebugRegisters ...

Although DbgEng exports COM interfaces, it is not a registered COM server. Its COM
interfaces are not exported in a type library (tlb).
The first step is to manually create this tlb file. Basically we take the SDK header file,
and convert it to IDL (Interface Description Language) representation. Then we compile it 
with MIDL and get our DbgEng type library. This work is done in 'DbgEngTlb' folder.

Next, we are going to utilize Python COM client framework. AFAIK, There are two such frameworks:
win32com (4) and comtypes (5). I gave up on win32com after it failed to handle IUnknown COM
interfaces properly. I moved to comtypes, which proved to be a very powerful framework.
At this point we can get the main IDebugClient, actively work with it and the other interfaces:

	==========================================================
	import debug_creator
	from comtypes.gen import DbgEng
	
	debug_client = debug_creator.create_idebugclient()
	debug_control = debug_client.QueryInterface(interface = DbgEng.IDebugControl)
	
	debug_client.CreateProcess(Server=0, CommandLine = "c:\\windows\\system32\\notepad.exe", CreateFlags = DbgEng.DEBUG_ONLY_THIS_PROCESS)
	debug_control.WaitForEvent(DbgEng.DEBUG_WAIT_DEFAULT, -1)
	==========================================================

The last piece of the puzzle is how to handle events. DbgEng can asynchronously notify us 
of various debug events. The main events interface is IDebugEventCallbacks. The client 
can set its events callbacks by calling IDebugControl.SetEventCallbacks() and passing a 
pointer to a class implementing IDebugEventCallbacks.

comtypes can handle COM objects event sinks. Meaning, when a COM object extending 
IConnectionPointContainer fires an event, the comtypes Python wrapper receives
this event, and can optionally pass it to a Python class.
The idea is to create a COM event proxy. One that can return a cpp class extending IDebugEventCallbacks,
and that also fires an event on each method:

	IDebugControl.SetEventCallbacks( DbgEventProxy.CreateIDebugEventCallbacks() )
	DbgEng Event => DbgEventProxy => fire event => comtypes sink => PyDbgEng sink class


Now we can do this:

	==========================================================
	debug_client = debug_creator.create_idebugclient()
	debug_control = debug_client.QueryInterface(interface = DbgEng.IDebugControl)

	class IDebugEventCallbacksSink:
		def CreateThread(self, this, Handle, DataOffset, StartOffset):
			print "CreateThread", Handle, DataOffset, StartOffset
			return DbgEng.DEBUG_STATUS_NO_CHANGE

	sink = IDebugEventCallbacksSink()
	event_proxy_creator = CreateObject("DbgEventProxy.EventCallbacksProxy.1", sink=sink, sourceinterface=DBGEVENTPROXYLib._IEventCallbacksProxyEvents)

	event_proxy_iunknown = event_proxy_creator.CreateIDebugEventCallbacks(DbgEng.DEBUG_EVENT_CREATE_THREAD)
	event_proxy = cast(event_proxy_iunknown, POINTER(DbgEng.IDebugEventCallbacks))
	debug_client.SetEventCallbacks(Callbacks = event_proxy)

	debug_client.CreateProcess(Server=0, CommandLine = "c:\\windows\\system32\\notepad.exe", CreateFlags = DbgEng.DEBUG_ONLY_THIS_PROCESS)
	debug_control.WaitForEvent(DbgEng.DEBUG_WAIT_DEFAULT, -1)
	==========================================================


Install
=======

python setup.py install



References
==========
1. Debugging Tools For Windows: http://www.microsoft.com/whdc/devtools/debugging/default.mspx
2. DebugStalk: http://www.nologin.org/
3. PaiMei: http://pedram.redhive.com/PaiMei/docs/
4. PyWin32 with win32com: http://sourceforge.net/projects/pywin32/
5. comtypes: http://sourceforge.net/projects/comtypes/
6. VC2005 Express: http://msdn.microsoft.com/vstudio/express/visualc/
7. Platform SDK: http://www.microsoft.com/msdownload/platformsdk/sdkupdate/
8. ctypes: http://sourceforge.net/projects/ctypes/

Author
======
    Michael Eddington (mike@phed.org), 2008-2009
	Botten Biss (botten.biss@gmail.com), Dec 2006.

