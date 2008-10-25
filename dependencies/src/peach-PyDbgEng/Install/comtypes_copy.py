import sys
import os
from distutils.file_util import copy_file
import comtypes

def remove_file(file):
	if (os.path.exists(file)):
		print  "remove ", file
		os.remove(file)

def copy_py_files(src, dst):
	dst = comtypes.__path__[0] + "\\" + dst
	remove_file(dst + ".pyc")
	remove_file(dst + ".pyo")
	print src, " => ", dst + ".py"
	copy_file(src, dst + ".py")
	
# generate tlb python interface
copy_py_files(sys.argv[1], sys.argv[2])

