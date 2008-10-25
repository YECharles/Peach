
# Quick setup for wxPropertyGrid

from distutils.core import setup
setup(name='wxPropertyGrid',
	author='Jaakko Salli',
	author_email='jaakko.salli@pp.inet.fi',
	description='wxPropertyGrid for wxPython',
	version='1.2.9',
#	py_modules=['vix'],
	data_files=[
		('Lib/site-packages/wx-2.8-msw-ansi/wx', ['propgrid.py','wxmsw28h_propgrid_vc.dll','_propgrid.pyd']),
		('Lib/site-packages/wx-2.8-msw-ansi/wx/samples', ['samples/test_propgrid.py']),
		]
	)
