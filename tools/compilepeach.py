'''
Run after Peach install to pre-compile all .py files to pyc for faster
first-time execution.
'''

import compileall, sys
compileall.compile_dir(sys.argv[1])

# end
