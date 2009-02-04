# This is the distutils script for creating a Python-based com (exe or dll)
# server using win32com.  This script should be run like this:
#
#  % python setup.py py2exe
#
# After you run this (from this directory) you will find two directories here:
# "build" and "dist".  The .dll or .exe in dist is what you are looking for.
##############################################################################

from distutils.core import setup
import py2exe
import sys

setup(
    name="DbgEngEvent",
    # the following two parameters embed support files within exe/dll file
    options={"py2exe": {"optimize":2, "bundle_files": 3, }},
    zipfile=None,
    version="0.7",
    description="DbgEngEvent Proxy",
    # author, maintainer, contact go here:
    author="Michael Eddington",
    author_email="mike@phed.org",
    packages=["PyDbgEng"],
    console=['PyDbgEng/DbgEngEvent.py']
    )