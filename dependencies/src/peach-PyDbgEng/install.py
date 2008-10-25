import sys
import os, commands
import comtypes
from comtypes.client import gen_dir, GetModule

def clear_gen_dir():
	for root, dirs, files in os.walk(comtypes.client.gen_dir, topdown=False):
		if '__init__.py' in files:
			files.remove('__init__.py')
		for name in files:
			os.remove(os.path.join(root, name))

def gen_py_files(tlb_file):
	print "tlb_file: %s" % tlb_file
	comtypes.client.GetModule(tlb_file)

clear_gen_dir()
path = sys.modules['comtypes'].__file__[:-21]+"PyDbgEng\\"
for tlb_file in [path + "data\\DbgEng.tlb"]:
	gen_py_files(tlb_file)


# end
