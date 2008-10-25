import sys
sys.path.append("..")

import PyDbgEng
import threading
import struct
import getopt

###########################################################
# defines
###########################################################

USAGE = "USAGE: KernelFileMon.py <-k|--kern connection_string>"

ERROR = lambda msg: sys.stderr.write("ERROR> " + msg + "\n") or sys.exit(1)

###########################################################
# NtCreateFile
###########################################################
def NtCreateFile_at_entry(dbg, args):
    (root_handle, file_name) = dbg.read_object_attributes( args[2] )
    sys.stdout.write( "NtCreateFile(): file_name: \"%s\"\n" % file_name )

   
###########################################################
# PyDbgEng Event Handler
###########################################################
class DbgEventHandler(PyDbgEng.IDebugOutputCallbacksSink, PyDbgEng.IDebugEventCallbacksSink):

    breakpoints_set = False

    ###########################################################
    # IDebugOutputCallbacksSink
    ###########################################################
    def Output(self, this, Mask, Text):
        sys.stdout.write(Text)

    ###########################################################
    # IDebugEventCallbacksSink
    ###########################################################
    def GetInterestMask(self):
        return  PyDbgEng.DbgEng.DEBUG_EVENT_LOAD_MODULE |    \
                PyDbgEng.DbgEng.DEBUG_EVENT_EXCEPTION

    def LoadModule(self, dbg, ImageFileHandle, BaseOffset, ModuleSize, ModuleName, ImageName, CheckSum, TimeDateStamp):
        sys.stdout.write("LoadModule: ImageName = \"%s\"\n" % ImageName)
        return PyDbgEng.DbgEng.DEBUG_STATUS_NO_CHANGE

    def Exception(self, dbg, ExceptionCode, ExceptionFlags, ExceptionRecord, ExceptionAddress, NumberParameters, ExceptionInformation0, ExceptionInformation1, ExceptionInformation2, ExceptionInformation3, ExceptionInformation4, ExceptionInformation5, ExceptionInformation6, ExceptionInformation7, ExceptionInformation8, ExceptionInformation9, ExceptionInformation10, ExceptionInformation11, ExceptionInformation12, ExceptionInformation13, ExceptionInformation14, FirstChance):
        if (not self.breakpoints_set):
            hooks.add( dbg, "nt!NtCreateFile", 11, NtCreateFile_at_entry, None)
            self.breakpoints_set = True
        return PyDbgEng.DbgEng.DEBUG_STATUS_NO_CHANGE


###########################################################
# main
###########################################################
try:
    opts, args = getopt.getopt(sys.argv[1:], "k:", [])
except getopt.GetoptError:
    ERROR(USAGE)

connection_string = None
hooks    = PyDbgEng.Hooking.hook_container()

for opt, arg in opts:
    if opt in ("-k", "--kern"):  connection_string = arg

if not connection_string:
    connection_string = "com:pipe,port=\\\\.\\pipe\\com_1,resets=0"

event_handler = DbgEventHandler()
dbg = PyDbgEng.KernelAttacher(  connection_string = connection_string, \
                                set_initial_bp = True, \
                                event_callbacks_sink = event_handler, \
                                output_callbacks_sink = event_handler, \
                                symbols_path = "SRV*http://msdl.microsoft.com/download/symbols")

quit_event = threading.Event()
dbg.event_loop_with_quit_event(quit_event)


