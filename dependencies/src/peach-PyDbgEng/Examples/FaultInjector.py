import sys
sys.path.append("..")

import PyDbgEng
import threading
import struct
import getopt
import random

###########################################################
# defines
###########################################################

USAGE = "USAGE: FaultInjector.py <-l|--load filename>"

ERROR = lambda msg: sys.stderr.write("ERROR> " + msg + "\n") or sys.exit(1)

###########################################################
# RtlAllocateHeap
###########################################################
def RtlAllocateHeap_at_exit(dbg, args, ret):
    if (random.randint(0,100) < 5):
        sys.stdout.write( "RtlAllocateHeap(): injecting fault\n" )
        dbg.set_register_value("eax", 0)
   
###########################################################
# PyDbgEng Event Handler
###########################################################
class DbgEventHandler(PyDbgEng.IDebugOutputCallbacksSink, PyDbgEng.IDebugEventCallbacksSink):

    ###########################################################
    # IDebugOutputCallbacksSink
    ###########################################################
    def Output(self, this, Mask, Text):
        sys.stdout.write(Text)

    ###########################################################
    # IDebugEventCallbacksSink
    ###########################################################
    def GetInterestMask(self):
        return  PyDbgEng.DbgEng.DEBUG_EVENT_LOAD_MODULE | \
                PyDbgEng.DbgEng.DEBUG_EVENT_EXCEPTION

    def LoadModule(self, dbg, ImageFileHandle, BaseOffset, ModuleSize, ModuleName, ImageName, CheckSum, TimeDateStamp):
        if (ImageName.lower() == "ntdll.dll"):
            hooks.add( dbg, "ntdll!RtlAllocateHeap", 3, None, RtlAllocateHeap_at_exit)
        
        return PyDbgEng.DbgEng.DEBUG_STATUS_NO_CHANGE

    def Exception(self, dbg, ExceptionCode, ExceptionFlags, ExceptionRecord, ExceptionAddress, NumberParameters, ExceptionInformation0, ExceptionInformation1, ExceptionInformation2, ExceptionInformation3, ExceptionInformation4, ExceptionInformation5, ExceptionInformation6, ExceptionInformation7, ExceptionInformation8, ExceptionInformation9, ExceptionInformation10, ExceptionInformation11, ExceptionInformation12, ExceptionInformation13, ExceptionInformation14, FirstChance):
        sys.stdout.write("Exception: ExceptionCode = %x, ExceptionAddress = %x\n" % (ExceptionCode, ExceptionAddress))
        return PyDbgEng.DbgEng.DEBUG_STATUS_GO_NOT_HANDLED


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


