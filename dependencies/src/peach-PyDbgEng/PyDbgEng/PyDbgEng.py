from Defines import *
from DebuggerException import *

from ctypes import *
from comtypes import HRESULT, COMError
from comtypes.client import CreateObject, GetEvents, ShowEvents
from comtypes.hresult import S_OK
from comtypes.automation import IID

try:
	from comtypes.gen import DbgEng
except:
	import os
	import Defines
	import comtypes
	tlb_file = os.path.join(os.path.dirname(Defines.__file__),
							"data", "DbgEng.tlb")
	comtypes.client.GetModule(tlb_file)
	
	from comtypes.gen import DbgEng

import sys,os
import struct

###########################################################
# utility functions
###########################################################
BUFFER_TO_ANSI_STRING = lambda buf: buf[:buf.find("\x00")]
BUFFER_TO_UNI_STRING  = lambda buf: buf[slice(0, buf.find("\x00\x00"), 2)]

###########################################################
class DbgEngDllFinder:
	def get_dbg_eng_dir_from_registry():
		import win32api, win32con
		try:
			hkey = win32api.RegOpenKey(win32con.HKEY_CURRENT_USER, "Software\\Microsoft\\DebuggingTools")
		except:
			
			# Lets try a few common places before failing.
			pgPaths = [
				"c:\\",
				os.environ["SystemDrive"]+"\\",
				os.environ["ProgramFiles"],
				]
			if "ProgramFiles(x86)" in os.environ:
				pgPaths.append(os.environ["ProgramFiles(x86)"])
			
			dbgPaths = [
				"Debuggers",
				"Debugger",
				"Debugging Tools for Windows",
				"Debugging Tools for Windows (x64)",
				"Debugging Tools for Windows (x86)",
				]
			
			for p in pgPaths:
				for d in dbgPaths:
					testPath = os.path.join(p,d)
					
					if os.path.exists(testPath):
						return testPath
			
			raise DebuggerException("Failed to locate Microsoft Debugging Tools in the registry. Please make sure its installed")
		val, type = win32api.RegQueryValueEx(hkey, "WinDbg")
		return val
	get_dbg_eng_dir_from_registry =  staticmethod(get_dbg_eng_dir_from_registry)

###########################################################
class IDebugClientCreator:
	def create_idebug_client(dbgeng_dll):
		# DebugCreate() prototype
		debug_create_prototype = WINFUNCTYPE(HRESULT, POINTER(IID), POINTER(POINTER(DbgEng.IDebugClient)))
		debug_create_func = debug_create_prototype(("DebugCreate", dbgeng_dll))

		# call DebugCreate()
		idebug_client = POINTER(DbgEng.IDebugClient)()
		idebug_client_ptr = POINTER(POINTER(DbgEng.IDebugClient))(idebug_client)
		hr = debug_create_func(DbgEng.IDebugClient._iid_, idebug_client_ptr)
		if (hr != S_OK):
			raise DebuggerException("DebugCreate() failed with %x" % hr)

		# return debug_client of type POINTER(DbgEng.IDebugClient)
		return idebug_client
	create_idebug_client = staticmethod(create_idebug_client)

###########################################################
class IDebugOutputCallbacksSink:
	def Output(self, this, Mask, Text):
		pass

###########################################################
class IDebugEventCallbacksSink:
	def GetInterestMask(self):
		raise DebuggerException("IDebugEventCallbacksSink.GetInterestMask() must be implemented")
	
	def Breakpoint(self, this, Offset, Id, BreakType, ProcType, Flags, DataSize, DataAccessType, PassCount, CurrentPassCount, MatchThread, CommandSize, OffsetExpressionSize):
		pass

	def Exception(self, this, ExceptionCode, ExceptionFlags, ExceptionRecord, ExceptionAddress, NumberParameters, ExceptionInformation0, ExceptionInformation1, ExceptionInformation2, ExceptionInformation3, ExceptionInformation4, ExceptionInformation5, ExceptionInformation6, ExceptionInformation7, ExceptionInformation8, ExceptionInformation9, ExceptionInformation10, ExceptionInformation11, ExceptionInformation12, ExceptionInformation13, ExceptionInformation14, FirstChance):
		pass

	def CreateThread(self, this, Handle, DataOffset, StartOffset):
		pass

	def ExitThread(self, this, ExitCode):
		pass

	def CreateProcess(self, this, ImageFileHandle, Handle, BaseOffset, ModuleSize, ModuleName, ImageName, CheckSum, TimeDateStamp, InitialThreadHandle, ThreadDataOffset, StartOffset):
		pass
	
	def ExitProcess(self, this, ExitCode):
		pass

	def LoadModule(self, this, ImageFileHandle, BaseOffset, ModuleSize, ModuleName, ImageName, CheckSum, TimeDateStamp):
		pass

	def UnloadModule(self, this, ImageBaseName, BaseOffset):
		pass

	def SystemError(self, this, Error, Level):
		pass

	def SessionStatus(self, this, Status):
		pass
		
	def ChangeDebuggeeState(self, this, Flags, Argument):
		pass

	def ChangeEngineState(self, this, Flags, Argument):
		pass

	def ChangeSymbolState(self, this, Flags, Argument):
		pass

###########################################################
class PyDbgEng(IDebugEventCallbacksSink):
	'''
	base class used creating dbgeng interfaces and registring event sink.
	client should NOT use this class directly.
	'''
	
	dbghelp_dll            = None
	dbgeng_dll             = None
	idebug_client          = None
	idebug_control         = None
	idebug_data_spaces     = None
	idebug_registers       = None
	idebug_symbols         = None
	idebug_system_objects  = None

	event_proxy_creator    = None
	output_proxy_creator   = None

	old_event_callbacks    = None
	old_output_callbacks   = None
	
	event_callbacks_sink   = None
	event_callbacks_sink_intereset_mask = 0
	
	dbg_eng_log            = None
	
	breakpoints            = {}       
	
	register_index_map     = {}
	
	def findDbgEngEvent(self):
		import sys,os
		
		fileName = os.path.join("PyDbgEng", "DbgEngEvent.py")
		
		for p in sys.path:
			if os.path.exists(os.path.join(p, fileName)):
				return os.path.join(p, fileName)
		
		return None
	
	
	###########################################################
	def __init__(self, event_callbacks_sink = None, output_callbacks_sink = None, dbg_eng_dll_path = None, symbols_path = None):
		self.dbg_eng_log = lambda msg: None # sys.stdout.write("DBGENG_LOG> " + msg + "\n")
		#self.dbg_eng_log = lambda msg: sys.stdout.write("> " + msg + "\n")
		
		if (dbg_eng_dll_path == None):
			finder = DbgEngDllFinder()
			dbg_eng_dll_path = finder.get_dbg_eng_dir_from_registry()
		
		self.dbg_eng_log("PyDbgEng.__init__: got dbg_eng_dll_path %s" % dbg_eng_dll_path)
		
		# load dbgeng dlls
		self.dbg_eng_log("PyDbgEng.__init__: loading dbgeng dlls")
		self.dbghelp_dll = windll.LoadLibrary(dbg_eng_dll_path + "\\dbghelp.dll")
		self.dbgeng_dll = windll.LoadLibrary(dbg_eng_dll_path + "\\dbgeng.dll")
		
		# create main interfaces
		self.dbg_eng_log("PyDbgEng.__init__: creating interfaces")
		creator = IDebugClientCreator()
		
		try:
			self.idebug_client          = creator.create_idebug_client(self.dbgeng_dll)
		except:
			# Try registering it
			import os, sys
			os.system("call \"%s\" \"%s\" -regserver" % (sys.executable, self.findDbgEngEvent()))
			self.idebug_client          = creator.create_idebug_client(self.dbgeng_dll)
			pass
		
		self.idebug_control         = self.idebug_client.QueryInterface(interface = DbgEng.IDebugControl)
		self.idebug_data_spaces     = self.idebug_client.QueryInterface(interface = DbgEng.IDebugDataSpaces3)
		self.idebug_registers       = self.idebug_client.QueryInterface(interface = DbgEng.IDebugRegisters)
		self.idebug_symbols         = self.idebug_client.QueryInterface(interface = DbgEng.IDebugSymbols)
		self.idebug_system_objects  = self.idebug_client.QueryInterface(interface = DbgEng.IDebugSystemObjects)
		
		if (symbols_path != None):
			self.idebug_symbols.SetSymbolPath(symbols_path)
		
		# create event sink
		if (event_callbacks_sink != None):
			# sanity check on sink
			if (not isinstance(event_callbacks_sink, IDebugEventCallbacksSink)):
				raise DebuggerException("Invalid sink object (event_callbacks_sink)")
			
			self.event_callbacks_sink = event_callbacks_sink
			self.dbg_eng_log("PyDbgEng.__init__: registering event callbacks proxy")
			
			# Updated code to work with latest comtypes and remove native code needs
			# Eddington 5/3/2008
			PyDbgEng.fuzzyWuzzy = self	# HACK!
			try:
				event_proxy = CreateObject("PyDbgEngLib.DbgEngEventCallbacks")
				
			except:
				# Try registering it
				import os, sys
				if not hasattr(sys, "frozen"):
					os.system("call \"%s\" \"%s\" -regserver" % (sys.executable, self.findDbgEngEvent()))
					
					try:
						event_proxy = CreateObject("PyDbgEngLib.DbgEngEventCallbacks")
					except:
						raise Exception("Error: Unable to create: PyDbgEngLib.DbgEngEventCallbacks")
					
					if event_proxy == None:
						raise Exception("Error: Unable to create: PyDbgEngLib.DbgEngEventCallbacks")
				else:
					raise Exception("Error: Unable to create: PyDbgEngLib.DbgEngEventCallbacks")
				
				pass
			
			self.old_event_callbacks = self.idebug_client.GetEventCallbacks()
			self.idebug_client.SetEventCallbacks(Callbacks = event_proxy)
		
		# create output sink
		if (output_callbacks_sink != None):
			# sanity check on sink
			if (not isinstance(output_callbacks_sink, IDebugOutputCallbacksSink)):
				raise DebuggerException("Invalid sink object (output_callbacks_sink)")
			self.dbg_eng_log("PyDbgEng.__init__: registering output callbacks proxy")
			
			# Updated code to work with latest comtypes and remove native code needs
			# Eddington 5/3/2008
			PyDbgEng.fuzzyWuzzy = self	# HACK!
			output_proxy = CreateObject("PyDbgEngLib.DbgEngEventCallbacks")
			self.output_callbacks_sink = output_callbacks_sink
			self.old_event_callbacks = self.idebug_client.GetEventCallbacks()
			self.idebug_client.SetOutputCallbacks(Callbacks = output_proxy)
	
	###########################################################
	def __del__(self):
		self.dbg_eng_log("in PyDbgEng dtor")
		
		if (self.idebug_client != None):
			if (self.old_event_callbacks != None):
				self.idebug_client.SetEventCallbacks(self.old_event_callbacks)
			if (self.old_output_callbacks != None):
				self.idebug_client.SetOutputCallbacks(self.old_output_callbacks)
			self.idebug_client.EndSession(DbgEng.DEBUG_END_PASSIVE)
			self.idebug_client.Release()
			self.idebug_client = None

		if (self.idebug_system_objects != None):
			self.idebug_system_objects.Release()
			self.idebug_system_objects = None
				
		if (self.idebug_symbols != None):
			self.idebug_symbols.Release()
			self.idebug_symbols = None

		if (self.idebug_registers != None):
			self.idebug_registers.Release()
			self.idebug_registers = None

		if (self.idebug_data_spaces != None):
			self.idebug_data_spaces.Release()
			self.idebug_data_spaces = None

		if (self.idebug_control != None):
			self.idebug_control.Release()
			self.idebug_control = None

	###########################################################
	# IDebugEventCallbacksSink
	###########################################################
	def GetInterestMask(self):
		self.event_callbacks_sink_intereset_mask = self.event_callbacks_sink.GetInterestMask()
		return self.event_callbacks_sink_intereset_mask | DbgEng.DEBUG_EVENT_BREAKPOINT
	
	def Breakpoint(self, this, bp):
		bpParams = bp.GetParameters()
		
		if (self.breakpoints.has_key(bpParams.Id)):
			handler = self.breakpoints.get(bpParams.Id)
			handler(self)
			
		if (self.event_callbacks_sink_intereset_mask & DbgEng.DEBUG_EVENT_BREAKPOINT):
			ret = self.event_callbacks_sink.Breakpoint(self, bpParams.Offset, bpParams.Id, bpParams.BreakType, bpParams.ProcType,
													   bpParams.Flags, bpParams.DataSize, bpParams.DataAccessType, bpParams.PassCount,
													   bpParams.CurrentPassCount, bpParams.MatchThread, bpParams.CommandSize,
													   bpParams.OffsetExpressionSize)
			if (ret != None):
				return ret
		
		return DbgEng.DEBUG_STATUS_NO_CHANGE
	
	def Exception(self, this, exception, firstChance):
		exception = exception.contents
		if (self.event_callbacks_sink_intereset_mask & DbgEng.DEBUG_EVENT_EXCEPTION):
			ret = self.event_callbacks_sink.Exception(self, exception.ExceptionCode, exception.ExceptionFlags, exception.ExceptionRecord,
													  exception.ExceptionAddress, exception.NumberParameters, exception.ExceptionInformation[0],
													  exception.ExceptionInformation[1], exception.ExceptionInformation[2], exception.ExceptionInformation[3],
													  exception.ExceptionInformation[4], exception.ExceptionInformation[5], exception.ExceptionInformation[6],
													  exception.ExceptionInformation[7], exception.ExceptionInformation[8], exception.ExceptionInformation[9],
													  exception.ExceptionInformation[10], exception.ExceptionInformation[11], exception.ExceptionInformation[12],
													  exception.ExceptionInformation[13], exception.ExceptionInformation[14], firstChance)
			if (ret != None):
				return ret
		
		return DbgEng.DEBUG_STATUS_NO_CHANGE
	
	def CreateThread(self, this, Handle, DataOffset, StartOffset):
		if (self.event_callbacks_sink_intereset_mask & DbgEng.DEBUG_EVENT_CREATE_THREAD):
			ret = self.event_callbacks_sink.CreateThread(self, Handle, DataOffset, StartOffset)
			if (ret != None):
				return ret
			
		return DbgEng.DEBUG_STATUS_NO_CHANGE
	
	def ExitThread(self, this, ExitCode):
		if (self.event_callbacks_sink_intereset_mask & DbgEng.DEBUG_EVENT_EXIT_THREAD):
			ret = self.event_callbacks_sink.ExitThread(self, ExitCode)
			if (ret != None):
				return ret
			
		return DbgEng.DEBUG_STATUS_NO_CHANGE
	
	def CreateProcess(self, this, ImageFileHandle, Handle, BaseOffset, ModuleSize, ModuleName, ImageName,
					  CheckSum, TimeDateStamp, InitialThreadHandle, ThreadDataOffset, StartOffset):
		
		if (self.event_callbacks_sink_intereset_mask & DbgEng.DEBUG_EVENT_CREATE_PROCESS):
			ret = self.event_callbacks_sink.CreateProcess(self, ImageFileHandle, Handle, BaseOffset,
														  ModuleSize, ModuleName, ImageName, CheckSum,
														  TimeDateStamp, InitialThreadHandle, ThreadDataOffset,
														  StartOffset)
			if (ret != None):
				return ret
			
		return DbgEng.DEBUG_STATUS_NO_CHANGE
	
	def ExitProcess(self, this, ExitCode):
		if (self.event_callbacks_sink_intereset_mask & DbgEng.DEBUG_EXIT_PROCESS):
			ret = self.event_callbacks_sink.ExitProcess(self, ExitCode)
			if (ret != None):
				return ret
			
		return DbgEng.DEBUG_STATUS_NO_CHANGE

	def LoadModule(self, this, ImageFileHandle, BaseOffset, ModuleSize, ModuleName, ImageName, CheckSum, TimeDateStamp):
		if (self.event_callbacks_sink_intereset_mask & DbgEng.DEBUG_EVENT_LOAD_MODULE):
			ret = self.event_callbacks_sink.LoadModule(self, ImageFileHandle, BaseOffset, ModuleSize, ModuleName, ImageName, CheckSum, TimeDateStamp)
			if (ret != None):
				return ret
			
		return DbgEng.DEBUG_STATUS_NO_CHANGE

	def UnloadModule(self, this, ImageBaseName, BaseOffset):
		if (self.event_callbacks_sink_intereset_mask & DbgEng.DEBUG_EVENT_UNLOAD_MODULE):
			ret = self.event_callbacks_sink.UnloadModule(self, ImageBaseName, BaseOffset)
			if (ret != None):
				return ret
			
		return DbgEng.DEBUG_STATUS_NO_CHANGE

	def SystemError(self, this, Error, Level):
		if (self.event_callbacks_sink_intereset_mask & DbgEng.DEBUG_EVENT_SYSTEM_ERROR):
			ret = self.event_callbacks_sink.SystemError(self, Error, Level)
			if (ret != None):
				return ret
			
		return DbgEng.DEBUG_STATUS_NO_CHANGE

	def SessionStatus(self, this, Status):
		if (self.event_callbacks_sink_intereset_mask & DbgEng.DEBUG_EVENT_SESSION_STATUS):
			ret = self.event_callbacks_sink.SessionStatus(self, Status)
			if (ret != None):
				return ret
			
		return DbgEng.DEBUG_STATUS_NO_CHANGE
		
	def ChangeDebuggeeState(self, this, Flags, Argument):
		if (self.event_callbacks_sink_intereset_mask & DbgEng.DEBUG_EVENT_CHANGE_DEBUGGEE_STATE):
			ret = self.event_callbacks_sink.ChangeDebuggeeState(self, Flags, Argument)
			if (ret != None):
				return ret
			
		return DbgEng.DEBUG_STATUS_NO_CHANGE

	def ChangeEngineState(self, this, Flags, Argument):
		if (self.event_callbacks_sink_intereset_mask & DbgEng.DEBUG_EVENT_CHANGE_ENGINE_STATE):
			ret = self.event_callbacks_sink.ChangeEngineState(self, Flags, Argument)
			if (ret != None):
				return ret
			
		return DbgEng.DEBUG_STATUS_NO_CHANGE

	def ChangeSymbolState(self, this, Flags, Argument):
		if (self.event_callbacks_sink_intereset_mask & DbgEng.DEBUG_EVENT_CHANGE_SYMBOL_STATE):
			ret = self.event_callbacks_sink.ChangeSymbolState(self, Flags, Argument)
			if (ret != None):
				return ret
			
		return DbgEng.DEBUG_STATUS_NO_CHANGE

	###########################################################
	# general execute commang
	###########################################################
	def execute(self, command):
		self.idebug_control.Execute(DbgEng.DEBUG_OUTCTL_THIS_CLIENT, Command = command, Flags = DbgEng.DEBUG_EXECUTE_ECHO)

	###########################################################
	# event loops
	###########################################################
	def event_loop_with_user_callback(self, user_callback, user_callback_pool_interval_ms):
		raise DebuggerException("PyDbgEng.event_loop_with_user_callback() must be implemented")

	def event_loop_with_quit_event(self, quit_event):
		print "%%% About to throw exception: event_loop_with_quit_event %%%"
		raise DebuggerException("PyDbgEng.event_loop_with_quit_event() must be implemented")

	###########################################################
	# handle functions
	###########################################################
	def get_handle_data(self, handle):
		raise DebuggerException("PyDbgEng.get_handle_data() must be implemented")

	###########################################################
	# symbol management
	###########################################################
	def resolve_symbol(self, symbol):
		return self.idebug_symbols.GetOffsetByName(symbol)
	
	def get_symbol_with_displacement(self, address):
		name_buf = create_string_buffer(256)
		displacement = c_ulonglong(0)
		self.idebug_symbols.GetNameByOffset(address, name_buf, sizeof(name_buf), byref(displacement))
		name = BUFFER_TO_ANSI_STRING(name_buf.raw)
		return (name, displacement.value)
	
	def get_symbol(self, address):
		(symbol, displacement) = self.get_symbol_with_displacement(address)
		if (displacement):
			return "%s + 0x%x" % (symbol, displacement)
		else:
			return symbol

	###########################################################
	# breakpoint management
	###########################################################

	def bp_set(self, address, preferred_id = DbgEng.DEBUG_ANY_ID, restore = True, handler = None):
		
		# if a list of addresses to set breakpoints on from was supplied
		if type(address) is list:
			# pass each lone address to ourself.
			for idx, addr in enumerate(address):
				# hackorama - each bp will have a unique id
				self.bp_set(addr, preferred_id + idx, restore)
				
			return

		if type(address) is str:
			address = self.resolve_symbol(address)
		
		self.dbg_eng_log("PyDbgEng.bp_set: setting bp at address %xL" % address)

		# its so easy, it should be illegal...
		bp_params = self.idebug_control.AddBreakpoint(Type = DbgEng.DEBUG_BREAKPOINT_CODE, DesiredId = preferred_id)
		flags = DbgEng.DEBUG_BREAKPOINT_ENABLED
		if (not restore):
			flags = flags | DbgEng.DEBUG_BREAKPOINT_ONE_SHOT
		bp_params.AddFlags(flags)
		bp_params.SetOffset(address)
		
		if (handler != None):
			self.breakpoints[ bp_params.GetId() ] = handler

	###########################################################
	# image functions
	###########################################################

	def read_image_nt_headers(self, image_base):
		return self.idebug_data_spaces.ReadImageNtHeaders(image_base)

	###########################################################
	# cpu state functions
	###########################################################
	
	def fill_register_map(self):
		if (len(self.register_index_map) == 0):
			# register index map
			for name in ["eax", "ebx", "ecx", "edx", "esi", "edi", "ebp", "esp"]:
				self.register_index_map[name] = self.idebug_registers.GetIndexByName(name)

	def get_register_value(self, register):
		self.fill_register_map()
		reg_value = self.idebug_registers.GetValue(self.register_index_map[register])
		return reg_value.u.I32
	
	def set_register_value(self, register, value):
		self.fill_register_map()
		reg_value = self.idebug_registers.GetValue(self.register_index_map[register])
		reg_value.u.I32 = value
		reg_value_ptr = POINTER(DbgEng._DEBUG_VALUE)(reg_value)
		self.idebug_registers.SetValue(self.register_index_map[register], reg_value_ptr)
	
	def dump_context_list(self):
		context_list = {}
		for name in ["eax", "ebx", "ecx", "edx", "esi", "edi", "ebp", "esp"]:
			context_list[name] = self.get_register_value(name)
		# todo: explore registers
		return context_list
	
	###########################################################
	# thread functions
	###########################################################
	def get_current_tid(self):
		raise DebuggerException("PyDbgEng.get_current_tid() must be implemented")

	###########################################################
	# memory functions
	###########################################################
	
	def read_virtual_memory(self, address, length):
		read_buf = create_string_buffer(length)
		bytes_read = c_ulong(0)
		
		self.idebug_data_spaces.ReadVirtual( address, read_buf, length, byref(bytes_read) )
		
		if (bytes_read.value != length):
			raise DebuggerException("read_virtual_memory(): ReadVirtual() failed")
		
		return read_buf.raw

	def read_dword(self, pdword):
		buffer = self.read_virtual_memory(pdword, 4)
		return struct.unpack("<I", buffer)[0]
	
	def read_char_string(self, pchar_string, string_len):
		string_buffer = self.read_virtual_memory(pchar_string, string_len)
		return BUFFER_TO_ANSI_STRING( string_buffer + "\x00" )

	def read_wchar_string(self, pwchar_string, string_len):
		string_buffer = self.read_virtual_memory(pwchar_string, string_len)
		return BUFFER_TO_UNI_STRING( string_buffer + "\x00\x00" )
	
	def read_unicode_string(self, punicode_string):
		uni_struct_buffer = self.read_virtual_memory(punicode_string, SIZE_OF_UNICODE_STRING)
		object_name_length = struct.unpack("<H", uni_struct_buffer[UNICODE_STRING_OFFSET_TO_LENGTH:UNICODE_STRING_OFFSET_TO_LENGTH+2])[0]
		object_name_ptr = struct.unpack("<I", uni_struct_buffer[UNICODE_STRING_OFFSET_TO_BUFFER_PTR:UNICODE_STRING_OFFSET_TO_BUFFER_PTR+4])[0]
		return self.read_wchar_string(object_name_ptr, object_name_length)

	def read_object_attributes(self, pobject_attributes):
		object_attributes_buffer = self.read_virtual_memory(pobject_attributes, SIZE_OF_OBJECT_ATTRIBUTES)
		root_handle = struct.unpack("<I", object_attributes_buffer[OBJECT_ATTRIBUTES_OFFSET_TO_ROOT_HANDLE:OBJECT_ATTRIBUTES_OFFSET_TO_ROOT_HANDLE+4])[0]
		uni_struct_object_name_ptr = struct.unpack("<I", object_attributes_buffer[OBJECT_ATTRIBUTES_OFFSET_TO_OBJECT_NAME:OBJECT_ATTRIBUTES_OFFSET_TO_OBJECT_NAME+4])[0]
		object_name = self.read_unicode_string(uni_struct_object_name_ptr)
		return (root_handle, object_name)
	
	def get_arg(self, index):
		esp_value = self.get_register_value("esp")
		return self.read_dword(esp_value + index * 4)


	###########################################################
	# stack trace functions
	###########################################################
	def get_stack_trace(self, frames_count):
		
		frames_buffer = create_string_buffer( frames_count * sizeof(DbgEng._DEBUG_STACK_FRAME) )
		frames_buffer_ptr = cast(frames_buffer, POINTER(DbgEng._DEBUG_STACK_FRAME))
		
		self.idebug_control.GetStackTrace(0, 0, 0, frames_buffer_ptr, frames_count)
		
		frames_list = []
		for i in range(frames_count):
			address_of_frame_buffer = (addressof(frames_buffer) + i*sizeof(DbgEng._DEBUG_STACK_FRAME))
			frame = DbgEng._DEBUG_STACK_FRAME.from_address( address_of_frame_buffer )
			frames_list.append( frame )
			
		return frames_list

