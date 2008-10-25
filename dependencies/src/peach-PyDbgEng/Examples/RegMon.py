import sys

#sys.path.append(".")

import PyDbgEng
import threading
import struct
import getopt
from ctypes import *
from comtypes import HRESULT, COMError
from comtypes.client import CreateObject, GetEvents#, ReleaseEvents
from comtypes.hresult import S_OK
from comtypes.automation import IID
from comtypes.gen import DbgEng
from comtypes.gen import DBGEVENTPROXYLib

###########################################################
# defines
###########################################################

USAGE = "USAGE: RegMon.py <-l|--load filename>"

ERROR = lambda msg: sys.stderr.write("ERROR> " + msg + "\n") or sys.exit(1)

###########################################################
# NtOpenKey
###########################################################
def NtOpenKey_at_entry(dbg, args):
    #(root_handle, key_name) = dbg.read_object_attributes( args[2] )
    #try:
    #    root_key_name = dbg.get_handle_data( root_handle )
    #    key_name = root_key_name + "\\" + key_name
    #except:
    #    pass
    #sys.stdout.write( "NtOpenKey(): key_name: \"%s\"\n" % key_name )
    
    sys.stdout.write("NtOpenKey() called\n")
    
    ### STUFF WE SHOULD DO FROM PEACH
    #################################
    
    # 1. Calculate no. of frames
    
    frames_filled = 0
    stack_frames = dbg.get_stack_trace(100)
    for i in range(100):
        eip = stack_frames[i].InstructionOffset
        if (eip == 0):
            break
        frames_filled += 1
    
    try:
        # identity doesn't do anything :(
        #dbg.idebug_client.OutputIdentity(DbgEng.DEBUG_OUTCTL_THIS_CLIENT, 0, "Identity: %s\n")
        
        # 2. Output registers
        
        dbg.idebug_registers.OutputRegisters(DbgEng.DEBUG_OUTCTL_THIS_CLIENT, DbgEng.DEBUG_REGISTERS_ALL)
        
        # 3. Ouput stack trace
        
        frames_count = 100
        frames_buffer = create_string_buffer( frames_count * sizeof(DbgEng._DEBUG_STACK_FRAME) )
        frames_buffer_ptr = cast(frames_buffer, POINTER(DbgEng._DEBUG_STACK_FRAME))
        
        dbg.idebug_control.GetStackTrace(0, 0, 0, frames_buffer_ptr, frames_count)
        dbg.idebug_control.OutputStackTrace(DbgEng.DEBUG_OUTCTL_THIS_CLIENT, frames_buffer_ptr, frames_filled,
            DbgEng.DEBUG_STACK_ARGUMENTS |
            DbgEng.DEBUG_STACK_FUNCTION_INFO |
            DbgEng.DEBUG_STACK_SOURCE_LINE |
            DbgEng.DEBUG_STACK_FRAME_ADDRESSES |
            DbgEng.DEBUG_STACK_COLUMN_NAMES |
            DbgEng.DEBUG_STACK_FRAME_NUMBERS |
            DbgEng.DEBUG_STACK_PARAMETERS )
        
        # 4. Write dump file
        
        dbg.idebug_client.WriteDumpFile(c_char_p("dumpfile.core"), DbgEng.DEBUG_DUMP_SMALL)
        
        # 5. !analyze -v
        
        sys.stdout.write("2\n")
        handle = dbg.idebug_control.AddExtension(c_char_p("C:\Program Files\\Debugging Tools for Windows\\winext\\ext.dll"), 0)
        try:
            sys.stdout.write("3\n")
            #dbg.idebug_control.CallExtension(handle, c_char_p("analyze"), c_char_p(" -v "))
            #dbg.idebug_control.CallExtension(handle, c_char_p("analyze"))
            #dbg.idebug_control.CallExtension(0, c_char_p("analyze"), "-v")
            dbg.idebug_control.Execute(DbgEng.DEBUG_OUTCTL_THIS_CLIENT, c_char_p("!analyze -v"), DbgEng.DEBUG_EXECUTE_ECHO)
            sys.stdout.write("3.1\n")
        except:
            sys.stdout.write("3.2\n")
            pass
        
        dbg.idebug_control.RemoveExtension(handle)
        
        sys.stdout.write("4\n")
        
    except:
        sys.stdout.write("\n5\n")
        sys.stdout.write(repr(sys.exc_info()[0]) + "\n")
        pass
    sys.exit(0)
    
###########################################################
# NtQueryValueKey
###########################################################
def NtQueryValueKey_at_entry(dbg, args):
    #key_name = dbg.get_handle_data(args[0])
    #value_name = dbg.read_unicode_string(args[1])
    #sys.stdout.write( "NtQueryValueKey(): reading \"%s\" from \"%s\"\n" % (value_name, key_name) )
    pass
    
###########################################################
# PyDbgEng Event Handler
###########################################################
class DbgEventHandler(PyDbgEng.IDebugOutputCallbacksSink, PyDbgEng.IDebugEventCallbacksSink):

    ###########################################################
    # IDebugOutputCallbacksSink
    ###########################################################
    def Output(self, this, Mask, Text):
        #print "Output:"
        sys.stdout.write(Text)
        #pass

    ###########################################################
    # IDebugEventCallbacksSink
    ###########################################################
    def GetInterestMask(self):
        print " >>> GetInterestMask <<<"
        print " >>> GetInterestMask <<< %d - %d" % (PyDbgEng.DbgEng.DEBUG_EVENT_LOAD_MODULE, PyDbgEng.DbgEng.DEBUG_FILTER_INITIAL_BREAKPOINT)
        return PyDbgEng.DbgEng.DEBUG_EVENT_LOAD_MODULE | PyDbgEng.DbgEng.DEBUG_FILTER_INITIAL_BREAKPOINT
    
    def LoadModule(self, dbg, ImageFileHandle, BaseOffset, ModuleSize, ModuleName, ImageName, CheckSum, TimeDateStamp):
        print " >>> Adding hooks <<<"
        print " >>> Adding hooks <<<"
        print " >>> Adding hooks <<<"
        if (ImageName.lower() == "ntdll.dll"):
            hooks.add( dbg, "ntdll!NtOpenKey",          3, NtOpenKey_at_entry,          None)
            hooks.add( dbg, "ntdll!NtQueryValueKey",    6, NtQueryValueKey_at_entry,    None)
        
        return PyDbgEng.DbgEng.DEBUG_STATUS_NO_CHANGE


###########################################################
# main
###########################################################
try:
    opts, args = getopt.getopt(sys.argv[1:], "l:", [])
except getopt.GetoptError:
    ERROR(USAGE)

filename = None
hooks    = PyDbgEng.Hooking.hook_container()

for opt, arg in opts:
    if opt in ("-l", "--load"):  filename = arg

if not filename:
    ERROR(USAGE)

event_handler = DbgEventHandler()
dbg = PyDbgEng.ProcessCreator(  command_line = filename, \
                                follow_forks = True, \
                                event_callbacks_sink = event_handler, \
                                output_callbacks_sink = event_handler, \
                                symbols_path = "SRV*http://msdl.microsoft.com/download/symbols")

quit_event = threading.Event()
dbg.event_loop_with_quit_event(quit_event)


