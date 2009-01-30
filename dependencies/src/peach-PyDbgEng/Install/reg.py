import PyDbgEng

cmd = "python %s\\DbgEngEvent.py -regserver" % (PyDbgEng.__path__[0])

import os

os.system(cmd)
