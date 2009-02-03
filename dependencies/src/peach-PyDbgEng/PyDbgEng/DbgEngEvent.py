
#
# This file implements a callback COM object for the DbgEng.  It
# implements the IDebugEventCallbacks interface.
#
# This also removes the dependency on native event proxy code and
# works with the latest comtypes.
#
# Copyright (c) Michael Eddington (mike@phed.org)
#
# Change log:
# 5/3/2008 - Initial version written
#

import comtypes
from ctypes import *
from comtypes import HRESULT, COMError
from comtypes.client import CreateObject, GetEvents, ShowEvents
from comtypes.hresult import S_OK
from comtypes.automation import IID
from comtypes.gen import DbgEng

import sys
import struct

from comtypes import CoClass, GUID
from PyDbgEng import PyDbgEng

sys.path.append("PyDbgEng")
sys.path.append(".")
sys.path.append("..")
from PyDbgEng.Defines import *
from PyDbgEng.DebuggerException import *

class DbgEngEventCallbacks(CoClass):
	
	_reg_clsid_ = GUID('{EAC5ACAA-7BD0-4f1f-8DEB-DF2862A7E85B}')
	_reg_threading_ = "Both"
	_reg_progid_ = "PyDbgEngLib.DbgEngEventCallbacks.1"
	_reg_novers_progid_ = "PyDbgEngLib.DbgEngEventCallbacks"
	_reg_desc_ = "Callback class!"
	_reg_clsctx_ = comtypes.CLSCTX_INPROC_SERVER
	
	_com_interfaces_ = [DbgEng.IDebugEventCallbacks, DbgEng.IDebugOutputCallbacks]
	
	def IDebugOutputCallbacks_Output(self, unknown, mask, text):
		self._pyDbgEng = PyDbgEng.fuzzyWuzzy
		self._pyDbgEng.output_callbacks_sink.Output(unknown, mask, text)
		return S_OK
	
	def IDebugEventCallbacks_Breakpoint(self, unknown, bp):
		return self._pyDbgEng.Breakpoint(unknown, bp)
	
	def IDebugEventCallbacks_ChangeDebuggeeState(self, unknown, flags, arg):
		return self._pyDbgEng.ChangeDebuggeeState(unknown, flags, arg)
	
	def IDebugEventCallbacks_ChangeEngineState(self, unknown, flags, arg):
		return self._pyDbgEng.ChangeEngineState(unknown, flags, arg)
	
	def IDebugEventCallbacks_Exception(self, unknown, exception, firstChance):
		return self._pyDbgEng.Exception(unknown, exception, firstChance)
	
	def IDebugEventCallbacks_GetInterestMask(self, unknown, mask):
		# Superhack!
		self._pyDbgEng = PyDbgEng.fuzzyWuzzy
		
		mask[0] = self._pyDbgEng.GetInterestMask()
		return S_OK
	
	def IDebugEventCallbacks_LoadModule(self, unknown, imageFileHandle, baseOffset, moduleSize, moduleName, imageName, checkSum, timeDateStamp):
		return self._pyDbgEng.LoadModule(unknown, imageFileHandle, baseOffset, moduleSize, moduleName, imageName, checkSum, timeDateStamp)
	
	def IDebugEventCallbacks_UnloadModule(self, unknown, imageBaseName, baseOffset):
		return self._pyDbgEng.UnloadModule(unknown, imageBaseName, baseOffset)
	
	def IDebugEventCallbacks_CreateProcess(self, unknown, imageFileHandle, handle, baseOffset, moduleSize, moduleName, imageName, checkSum, timeDateStamp,
										   initialThreadHandle, threadDataOffset, startOffset):
		return self._pyDbgEng.CreateProcess(unknown, imageFileHandle, handle, baseOffset, moduleSize, moduleName, imageName, checkSum, timeDateStamp,
										   initialThreadHandle, threadDataOffset, startOffset)
	
	def IDebugEventCallbacks_ExitProcess(self, unknown, exitCode):
		return self._pyDbgEng.ExitProcess(unknown, exitCode)
	
	def IDebugEventCallbacks_SessionStatus(self, unknown, status):
		return self._pyDbgEng.SessionStatus(unknown, status)
	
	def IDebugEventCallbacks_ChangeSymbolState(self, unknown, flags, arg):
		return self._pyDbgEng.ChangeSymbolState(unknown, flags, arg)
	
	def IDebugEventCallbacks_SystemError(self, unknown, error, level):
		return self._pyDbgEng.SystemError(unknown, error, level)
	
	def IDebugEventCallbacks_CreateThread(self, unknown, handle, dataOffset, startOffset):
		return self._pyDbgEng.CreateThread(handle, unknown, dataOffset, startOffset)
	
	def IDebugEventCallbacks_ExitThread(self, unknown, exitCode):
		return self._pyDbgEng.ExitThread(unknown, exitCode)

if __name__ == "__main__":
    try:
        from comtypes.server.register import UseCommandLine
        UseCommandLine(DbgEngEventCallbacks)
    except Exception:
        import traceback
        traceback.print_exc()
        raw_input()

# end
