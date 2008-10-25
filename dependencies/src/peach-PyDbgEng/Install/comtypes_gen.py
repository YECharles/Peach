import sys
import os
import comtypes
from comtypes.client import gen_dir, GetModule

def clear_gen_dir():
	for root, dirs, files in os.walk(comtypes.client.gen_dir, topdown=False):
		if '__init__.py' in files:
			files.remove('__init__.py')
		for name in files:
			os.remove(os.path.join(root, name))

def gen_py_files(tlb_file):
	comtypes.client.GetModule(tlb_file)

# empty comtypes.gen dir
clear_gen_dir()
	
# generate tlb python interface
for tlb_file in sys.argv[1:]:
	gen_py_files(tlb_file)

