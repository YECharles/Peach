from distutils.core import setup
import py2exe
import Ft.Lib.DistExt.Py2Exe
import glob

setup(
	options={"py2exe": {"optimize":2, "bundle_files":3}},
	console=['peach.py', 'minset.py'],
	windows=['peachvalidator.pyw'],
	
	data_files=[
			("",
			  ["peach.xsd"],
			  ["readme.html"],
			  ["template.xml"],
			  ["defaults.xml"],
			  ),
			("icons",
			 glob.glob("peach/gui/icons/*"))
		]
	)

# end
