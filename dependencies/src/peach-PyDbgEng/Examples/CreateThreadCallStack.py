import sys
sys.path.append("..")

import PyDbgEng
import threading
import struct
import getopt

###########################################################
# defines
###########################################################

USAGE = "USAGE: CreateThreadCallStack.py <-l|--load filename>"
FRAMES_COUNT = 10

ERROR = lambda msg: sys.stderr.write("ERROR> " + msg + "\n") or sys.exit(1)

###########################################################
# NtCreateThread
###########################################################
def NtCreateThread_at_entry(dbg, args):
    sys.stdout.write("NtCreateThread() called with following call stack:\n")
    stack_frames = dbg.get_stack_trace(FRAMES_COUNT)
    for i in range(FRAMES_COUNT):
        eip = stack_frames[i].InstructionOffset
        if (eip == 0):
            break
        func_symbol = dbg.get_symbol(eip)
        sys.stdout.write("[%d] %s\n" % (i, func_symbol))
    sys.stdout.write("\n")
   
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
        return PyDbgEng.DbgEng.DEBUG_EVENT_LOAD_MODULE

    def LoadModule(self, dbg, ImageFileHandle, BaseOffset, ModuleSize, ModuleName, ImageName, CheckSum, TimeDateStamp):
        if (ImageName.lower() == "ntdll.dll"):
            hooks.add( dbg, "ntdll!NtCreateThread",          8, NtCreateThread_at_entry,          None)
        
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


