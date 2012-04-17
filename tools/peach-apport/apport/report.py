'''Representation of and data collection for a problem report.'''

# Copyright (C) 2006 - 2009 Canonical Ltd.
# Author: Martin Pitt <martin.pitt@ubuntu.com>
# 
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.  See http://www.gnu.org/copyleft/gpl.html for
# the full text of the license.

import subprocess, tempfile, os.path, urllib, re, pwd, grp, os, sys
import fnmatch, glob, atexit, traceback, errno

import xml.dom, xml.dom.minidom
from xml.parsers.expat import ExpatError

import problem_report
import apport
import apport.fileutils
#import packaging
#from apport.packaging_impl import impl as packaging

_data_dir = os.environ.get('APPORT_DATA_DIR','/usr/share/apport')
_common_hook_dir = '%s/general-hooks/' % (_data_dir)

# programs that we consider interpreters
interpreters = ['sh', 'bash', 'dash', 'csh', 'tcsh', 'python*',
    'ruby*', 'php', 'perl*', 'mono*', 'awk']

#
# helper functions
#

def _transitive_dependencies(package, depends_set):
    '''Recursively add dependencies of package to depends_set.'''

    try:
        cur_ver = packaging.get_version(package)
    except ValueError:
        return
    for d in packaging.get_dependencies(package):
        if not d in depends_set:
            depends_set.add(d)
            _transitive_dependencies(d, depends_set)

def _read_file(path):
    '''Read file content.
    
    Return its content, or return a textual error if it failed.
    '''
    try:
        with open(path) as fd:
            return fd.read().strip()
    except (OSError, IOError) as e:
        return 'Error: ' + str(e)

def _read_maps(pid):
    '''Read /proc/pid/maps.

    Since /proc/$pid/maps may become unreadable unless we are ptracing the
    process, detect this, and attempt to attach/detach.
    '''
    maps = 'Error: unable to read /proc maps file'
    try:
        with open('/proc/%d/maps' % pid) as fd:
            maps = fd.read().strip()
    except (OSError,IOError) as e:
        return 'Error: ' + str(e)
    return maps

def _command_output(command, input = None, stderr = subprocess.STDOUT):
    '''Run command and capture its output.

    Try to execute given command (argv list) and return its stdout, or return
    a textual error if it failed.
    '''
    sp = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=stderr, close_fds=True)

    (out, err) = sp.communicate(input)
    if sp.returncode == 0:
        return out
    else:
        if err:
            err = err.decode('UTF-8', errors='replace')
        else:
            err = ''
        raise OSError('Error: command %s failed with exit code %i: %s' % (
            str(command), sp.returncode, err))

def _check_bug_pattern(report, pattern):
    '''Check if given report matches the given bug pattern XML DOM node.
    
    Return the bug URL on match, otherwise None.
    '''
    if not pattern.attributes.has_key('url'):
        return None

    for c in pattern.childNodes:
        # regular expression condition
        if c.nodeType == xml.dom.Node.ELEMENT_NODE and c.nodeName == 're' and \
            c.attributes.has_key('key'):
            key = c.attributes['key'].nodeValue
            if key not in report:
                return None
            c.normalize()
            if c.hasChildNodes() and \
                c.childNodes[0].nodeType == xml.dom.Node.TEXT_NODE:
                regexp = c.childNodes[0].nodeValue.encode('UTF-8')
                try:
                    v = report[key]
                    if isinstance(v, problem_report.CompressedValue):
                        v = v.get_value()
                    if not re.search(regexp, v):
                        return None
                except:
                    return None

    return pattern.attributes['url'].nodeValue.encode('UTF-8')

def _check_bug_patterns(report, patterns):
    try:
        dom = xml.dom.minidom.parseString(patterns)
    except ExpatError:
        return None

    for pattern in dom.getElementsByTagName('pattern'):
        url = _check_bug_pattern(report, pattern)
        if url:
            return url

    return None

def _dom_remove_space(node):
    '''Recursively remove whitespace from given XML DOM node.'''

    for c in node.childNodes:
        if c.nodeType == xml.dom.Node.TEXT_NODE and c.nodeValue.strip() == '':
            c.unlink()
            node.removeChild(c)
        else:
            _dom_remove_space(c)

#
# Report class
#

class Report(problem_report.ProblemReport):
    '''A problem report specific to apport (crash or bug).

    This class wraps a standard ProblemReport and adds methods for collecting
    standard debugging data.'''

    def __init__(self, type='Crash', date=None):
        '''Initialize a fresh problem report.

        date is the desired date/time string; if None (default), the current
        local time is used.

        If the report is attached to a process ID, this should be set in
        self.pid, so that e. g. hooks can use it to collect additional data.
        '''
        problem_report.ProblemReport.__init__(self, type, date)
        self.pid = None
        self._proc_maps_cache = None

    def _pkg_modified_suffix(self, package):
        '''Return a string suitable for appending to Package/Dependencies.

        If package has only unmodified files, return the empty string. If not,
        return ' [modified: ...]' with a list of modified files.
        '''
        mod = packaging.get_modified_files(package)
        if mod:
            return ' [modified: %s]' % ' '.join(mod)
        else:
            return ''

    def add_package_info(self, package = None):
        '''Add packaging information.

        If package is not given, the report must have ExecutablePath.
        This adds:
        - Package: package name and installed version
        - SourcePackage: source package name
        - PackageArchitecture: processor architecture this package was built
          for
        - Dependencies: package names and versions of all dependencies and
          pre-dependencies; this also checks if the files are unmodified and
          appends a list of all modified files
        '''
        if not package:
            # the kernel does not have a executable path but a package
            if (not 'ExecutablePath' in self and
                self['ProblemType'] == 'KernelCrash'):
                package = self['Package']
            else:
                package = apport.fileutils.find_file_package(self['ExecutablePath'])
            if not package:
                return

        try:
            version = packaging.get_version(package)
        except ValueError:
            # package not installed
            version = None
        self['Package'] = '%s %s%s' % (package, version or '(not installed)',
            self._pkg_modified_suffix(package))
        self['SourcePackage'] = packaging.get_source(package)
        if not version:
            return

        self['PackageArchitecture'] = packaging.get_architecture(package)

        # get set of all transitive dependencies
        dependencies = set([])
        _transitive_dependencies(package, dependencies)

        # get dependency versions
        self['Dependencies'] = ''
        for dep in sorted(dependencies):
            try:
                v = packaging.get_version(dep)
            except ValueError:
                # can happen with uninstalled alternate dependencies
                continue

            if self['Dependencies']:
                self['Dependencies'] += '\n'
            self['Dependencies'] += '%s %s%s' % (dep, v,
                self._pkg_modified_suffix(dep))

    def add_os_info(self):
        '''Add operating system information.

        This adds:
        - DistroRelease: lsb_release -sir output
        - Architecture: system architecture in distro specific notation
        - Uname: uname -srm output
        - NonfreeKernelModules: loaded kernel modules which are not free (if
            there are none, this field will not be present)
        '''
        p = subprocess.Popen(['lsb_release', '-sir'], stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, close_fds=True)
        self['DistroRelease'] = p.communicate()[0].decode().strip().replace('\n', ' ')

        u = os.uname()
        self['Uname'] = '%s %s %s' % (u[0], u[2], u[4])
        self['Architecture'] = 'Unkown' #packaging.get_system_architecture()

    def add_user_info(self):
        '''Add information about the user.

        This adds:
        - UserGroups: system groups the user is in
        '''
        user = pwd.getpwuid(os.getuid()).pw_name
        groups = [name for name, p, gid, memb in grp.getgrall()
            if user in memb and gid < 1000]
        groups.sort()
        self['UserGroups'] = ' '.join(groups)

    def _check_interpreted(self):
        '''Check if process is a script.

        Use ExecutablePath, ProcStatus and ProcCmdline to determine if
        process is an interpreted script. If so, set InterpreterPath
        accordingly.
        '''
        if 'ExecutablePath' not in self:
            return

        exebasename = os.path.basename(self['ExecutablePath'])

        # check if we consider ExecutablePath an interpreter; we have to do
        # this, otherwise 'gedit /tmp/foo.txt' would be detected as interpreted
        # script as well
        if not filter(lambda i: fnmatch.fnmatch(exebasename, i), interpreters):
            return

        # first, determine process name
        name = None
        for l in self['ProcStatus'].splitlines():
            try:
                (k, v) = l.split('\t', 1)
            except ValueError:
                continue
            if k == 'Name:':
                name = v
                break
        if not name:
            return

        cmdargs = self['ProcCmdline'].split('\0')
        bindirs = ['/bin/', '/sbin/', '/usr/bin/', '/usr/sbin/']

        # filter out interpreter options
        while len(cmdargs) >= 2 and cmdargs[1].startswith('-'):
            # check for -m
            if name.startswith('python') and cmdargs[1] == '-m' and len(cmdargs) >= 3:
                path = self._python_module_path(cmdargs[2])
                if path:
                    self['InterpreterPath'] = self['ExecutablePath']
                    self['ExecutablePath'] = path
                else:
                    self['UnreportableReason'] = 'Cannot determine path of python module %s' % cmdargs[2]
                return

            del cmdargs[1]

        # catch scripts explicitly called with interpreter
        if len(cmdargs) >= 2:
            # ensure that cmdargs[1] is an absolute path
            if cmdargs[1].startswith('.') and 'ProcCwd' in self:
                cmdargs[1] = os.path.join(self['ProcCwd'], cmdargs[1])
            if os.access(cmdargs[1], os.R_OK):
                self['InterpreterPath'] = self['ExecutablePath']
                self['ExecutablePath'] = os.path.realpath(cmdargs[1])

        # catch directly executed scripts
        if 'InterpreterPath' not in self and name != exebasename:
            argvexes = filter(lambda p: os.access(p, os.R_OK), [p+cmdargs[0] for p in bindirs])
            if argvexes and os.path.basename(os.path.realpath(argvexes[0])) == name:
                self['InterpreterPath'] = self['ExecutablePath']
                self['ExecutablePath'] = argvexes[0]

        # special case: crashes from twistd are usually the fault of the
        # launched program
        if 'InterpreterPath' in self and os.path.basename(self['ExecutablePath']) == 'twistd':
            self['InterpreterPath'] = self['ExecutablePath']
            exe = self._twistd_executable()
            if exe:
                self['ExecutablePath'] = exe
            else:
                self['UnreportableReason'] = 'Cannot determine twistd client program'

    def _twistd_executable(self):
        '''Determine the twistd client program from ProcCmdline.'''

        args = self['ProcCmdline'].split('\0')[2:]

        # search for a -f/--file, -y/--python or -s/--source argument
        while args:
            arg = args[0].split('=', 1)
            if arg[0].startswith('--file') or arg[0].startswith('--python') or \
               arg[0].startswith('--source'):
                   if len(arg) == 2:
                       return arg[1]
                   else:
                       return args[1]
            elif len(arg[0]) > 1 and arg[0][0] == '-' and arg[0][1] != '-':
                opts = arg[0][1:]
                if 'f' in opts or 'y' in opts or 's' in opts:
                   return args[1]

            args.pop(0)

        return None

    @classmethod
    def _python_module_path(klass, module):
        '''Determine path of given Python module'''

        try:
            m = __import__(module.replace('/', '.'))
        except:
            return None

        # chop off the first component, as it's already covered by m
        path = eval('m.%s.__file__' % '.'.join(module.split('/')[1:]))
        if path.endswith('.pyc'):
            path = path[:-1]
        return path

    def add_proc_info(self, pid=None, extraenv=[]):
        '''Add /proc/pid information.

        If neither pid nor self.pid are given, it defaults to the process'
        current pid and sets self.pid.

        This adds the following fields:
        - ExecutablePath: /proc/pid/exe contents; if the crashed process is
          interpreted, this contains the script path instead
        - InterpreterPath: /proc/pid/exe contents if the crashed process is
          interpreted; otherwise this key does not exist
        - ExecutableTimestamp: time stamp of ExecutablePath, for comparing at
          report time
        - ProcEnviron: A subset of the process' environment (only some standard
          variables that do not disclose potentially sensitive information, plus
          the ones mentioned in extraenv)
        - ProcCmdline: /proc/pid/cmdline contents
        - ProcStatus: /proc/pid/status contents
        - ProcMaps: /proc/pid/maps contents
        - ProcAttrCurrent: /proc/pid/attr/current contents, if not "unconfined"
        '''
        if not pid:
            pid = self.pid or os.getpid()
        if not self.pid:
            self.pid = int(pid)
        pid = str(pid)

        try:
            self['ProcCwd'] = os.readlink('/proc/' + pid + '/cwd')
        except OSError:
            pass
        self.add_proc_environ(pid, extraenv)
        self['ProcStatus'] = _read_file('/proc/' + pid + '/status')
        self['ProcCmdline'] = _read_file('/proc/' + pid + '/cmdline').rstrip('\0')
        self['ProcMaps'] = _read_maps(int(pid))
        try:
            self['ExecutablePath'] = os.readlink('/proc/' + pid + '/exe')
        except OSError as e:
            if e.errno == errno.ENOENT:
                raise ValueError('invalid process')
            else:
                raise
        for p in ('rofs', 'rwfs', 'squashmnt', 'persistmnt'):
            if self['ExecutablePath'].startswith('/%s/' % p):
                self['ExecutablePath'] = self['ExecutablePath'][len('/%s' % p):]
                break
        assert os.path.exists(self['ExecutablePath'])

        # check if we have an interpreted program
        self._check_interpreted()

        self['ExecutableTimestamp'] = str(int(os.stat(self['ExecutablePath']).st_mtime))

        # make ProcCmdline ASCII friendly, do shell escaping
        self['ProcCmdline'] = self['ProcCmdline'].replace('\\', '\\\\').replace(' ', '\\ ').replace('\0', ' ')

        # grab AppArmor or SELinux context
        # If no LSM is loaded, reading will return -EINVAL
        try:
            # On Linux 2.6.28+, 'current' is world readable, but read() gives
            # EPERM; Python 2.5.3+ crashes on that (LP: #314065)
            if os.getuid() == 0:
                with open('/proc/' + pid + '/attr/current') as fd:
                    val = fd.read().strip()
                if val != 'unconfined':
                    self['ProcAttrCurrent'] = val
        except (IOError, OSError):
            pass

    def add_proc_environ(self, pid=None, extraenv=[]):
        '''Add environment information.

        If pid is not given, it defaults to the process' current pid.

        This adds the following fields:
        - ProcEnviron: A subset of the process' environment (only some standard
          variables that do not disclose potentially sensitive information, plus
          the ones mentioned in extraenv)
        '''
        safe_vars = ['SHELL', 'LANGUAGE', 'LANG', 'LC_CTYPE',
            'LC_COLLATE', 'LC_TIME', 'LC_NUMERIC', 'LC_MONETARY', 'LC_MESSAGES',
            'LC_PAPER', 'LC_NAME', 'LC_ADDRESS', 'LC_TELEPHONE', 'LC_MEASUREMENT',
            'LC_IDENTIFICATION', 'LOCPATH'] + extraenv

        if not pid:
            pid = os.getpid()
        pid = str(pid)

        self['ProcEnviron'] = ''
        env = _read_file('/proc/'+ pid + '/environ').replace('\n', '\\n')
        if env.startswith('Error:'):
            self['ProcEnviron'] = env
        else:
            for l in env.split('\0'):
                if l.split('=', 1)[0] in safe_vars:
                    if self['ProcEnviron']:
                        self['ProcEnviron'] += '\n'
                    self['ProcEnviron'] += l
                elif l.startswith('PATH='):
                    p = l.split('=', 1)[1]
                    if '/home' in p or '/tmp' in p:
                        if self['ProcEnviron']:
                            self['ProcEnviron'] += '\n'
                        self['ProcEnviron'] += 'PATH=(custom, user)'
                    elif p != '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games':
                        if self['ProcEnviron']:
                            self['ProcEnviron'] += '\n'
                        self['ProcEnviron'] += 'PATH=(custom, no user)'

    def add_kernel_crash_info(self, debugdir=None):
        '''Add information from kernel crash.

        This needs a VmCore in the Report.
        '''
        if 'VmCore' not in self:
            return
        unlink_core = False
        ret = False
        try:
            if hasattr(self['VmCore'], 'find'):
                (fd, core) = tempfile.mkstemp()
                os.write(fd, self['VmCore'])
                os.close(fd)
                unlink_core = True
            kver = self['Uname'].split()[1]
            command = ['crash',
                       '/usr/lib/debug/boot/vmlinux-%s' % kver,
                       core,
                       ]
            try:
                p = subprocess.Popen(command, 
                                     stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT)
            except OSError:
                return False
            p.stdin.write('bt -a -f\n')
            p.stdin.write('ps\n')
            p.stdin.write('runq\n')
            p.stdin.write('quit\n')
            # FIXME: split it up nicely etc
            out = p.stdout.read()
            ret = (p.wait() == 0)
            if ret:
                self['Stacktrace'] = out
        finally:
            if unlink_core:
                os.unlink(core)
        return ret

    def add_gdb_info(self, rootdir=None):
        '''Add information from gdb.

        This requires that the report has a CoreDump and an
        ExecutablePath. This adds the following fields:
        - Registers: Output of gdb's 'info registers' command
        - Disassembly: Output of gdb's 'x/16i $pc' command
        - Stacktrace: Output of gdb's 'bt full' command
        - ThreadStacktrace: Output of gdb's 'thread apply all bt full' command
        - StacktraceTop: simplified stacktrace (topmost 5 functions) for inline
          inclusion into bug reports and easier processing
        - AssertionMessage: Value of __abort_msg, if present

        The optional rootdir can specify a root directory which has the
        executable, libraries, and debug symbols. This does not require
        chroot() or root privileges, it just instructs gdb to search for the
        files there.
        '''
        if 'CoreDump' not in self or 'ExecutablePath' not in self:
            return

        unlink_core = False
        try:
            if hasattr(self['CoreDump'], 'find'):
                (fd, core) = tempfile.mkstemp()
                unlink_core = True
                os.write(fd, self['CoreDump'])
                os.close(fd)
            elif hasattr(self['CoreDump'], 'gzipvalue'):
                (fd, core) = tempfile.mkstemp()
                unlink_core = True
                os.close(fd)
                self['CoreDump'].write(open(core, 'w'))
            else:
                core = self['CoreDump'][0]

            gdb_reports = {
                           'Registers': 'info registers',
                           'Disassembly': 'x/16i $pc',
                           'Stacktrace': 'bt full',
                           'ThreadStacktrace': 'thread apply all bt full',
                           'AssertionMessage': 'print __abort_msg->msg',
                          }

            command = ['gdb', '--batch']
            executable = self.get('InterpreterPath', self['ExecutablePath'])
            if rootdir:
                command += ['--ex', 'set debug-file-directory %s/usr/lib/debug' % rootdir,
                            '--ex', 'set solib-absolute-prefix ' + rootdir]
                executable = rootdir + '/' + executable
            command += ['--ex', 'file ' + executable, '--ex', 'core-file ' + core]
            # limit maximum backtrace depth (to avoid looped stacks)
            command += ['--ex', 'set backtrace limit 2000']
            value_keys = []
            # append the actual commands and something that acts as a separator
            for name, cmd in gdb_reports.items():
                value_keys.append(name)
                command += ['--ex', 'p -99', '--ex', cmd]

            assert os.path.exists(executable)

            # call gdb
            try:
                out = _command_output(command).decode('UTF-8')
            except OSError:
                return

            # split the output into the various fields
            part_re = re.compile('^\$\d+\s*=\s*-99$', re.MULTILINE)
            parts = part_re.split(out)
            # drop the gdb startup text prior to first separator
            parts.pop(0)
            for part in parts:
                self[value_keys.pop(0)] = part.replace('\n\n', '\n.\n').strip()
        finally:
            if unlink_core:
                os.unlink(core)

        # clean up AssertionMessage
        if 'AssertionMessage' in self:
            # chop off "$n = 0x...." prefix, drop empty ones
            m = re.match('^\$\d+\s+=\s+0x[0-9a-fA-F]+\s+"(.*)"\s*$',
                self['AssertionMessage'])
            if m:
                self['AssertionMessage'] = m.group(1)
                if self['AssertionMessage'].endswith('\\n'):
                    self['AssertionMessage'] = self['AssertionMessage'][0:-2]
            else:
                del self['AssertionMessage']

        if 'Stacktrace' in self:
            self._gen_stacktrace_top()
            addr_signature = self.crash_signature_addresses()
            if addr_signature:
                self['StacktraceAddressSignature'] = addr_signature

    def _gen_stacktrace_top(self):
        '''Build field StacktraceTop as the top five functions of Stacktrace. 

        Signal handler invocations and related functions are skipped since they
        are generally not useful for triaging and duplicate detection.
        '''
        unwind_functions = set(['g_logv', 'g_log', 'IA__g_log', 'IA__g_logv',
            'g_assert_warning', 'IA__g_assert_warning', '__GI_abort', '_XError'])
        toptrace = [''] * 5
        depth = 0
        unwound = False
        unwinding = False
        unwinding_xerror = False
        bt_fn_re = re.compile('^#(\d+)\s+(?:0x(?:\w+)\s+in\s+\*?(.*)|(<signal handler called>)\s*)$')
        bt_fn_noaddr_re = re.compile('^#(\d+)\s+(?:(.*)|(<signal handler called>)\s*)$')
        # some internal functions like the SSE stubs cause unnecessary jitter
        ignore_functions_re = re.compile('^(__.*_s?sse\d+(?:_\w+)?|__kernel_vsyscall)$')

        for line in self['Stacktrace'].splitlines():
            m = bt_fn_re.match(line)
            if not m:
                m = bt_fn_noaddr_re.match(line)
                if not m:
                    continue

            if not unwound or unwinding:
                if m.group(2):
                    fn = m.group(2).split()[0].split('(')[0]
                else:
                    fn = None

                # handle XErrors
                if unwinding_xerror:
                    if fn.startswith('_X') or fn in ['handle_response', 'handle_error', 'XWindowEvent']:
                        continue
                    else:
                        unwinding_xerror = False

                if m.group(3) or fn in unwind_functions:
                    unwinding = True
                    depth = 0
                    toptrace = [''] * 5
                    if m.group(3):
                        # we stop unwinding when we found a <signal handler>,
                        # but we continue unwinding otherwise, as e. g. a glib
                        # abort is usually sitting on top of an XError
                        unwound = True

                    if fn == '_XError':
                        unwinding_xerror = True
                    continue
                else:
                    unwinding = False

            frame = m.group(2) or m.group(3)
            function = frame.split()[0]
            if depth < len(toptrace) and not ignore_functions_re.match(function):
                toptrace[depth] = frame
                depth += 1
        self['StacktraceTop'] = '\n'.join(toptrace).strip()

    def add_hooks_info(self, ui, package=None, srcpackage=None):
        '''Run hook script for collecting package specific data.

        A hook script needs to be in _hook_dir/<Package>.py or in
        _common_hook_dir/*.py and has to contain a function 'add_info(report,
        ui)' that takes and modifies a Report, and gets an UserInterface
        reference for interactivity.

        return True if the hook requested to stop the report filing process,
        False otherwise.
        '''
        symb = {}

        # common hooks
        for hook in glob.glob(_common_hook_dir + '/*.py'):
            try:
                with open(hook) as fd:
                    exec(compile(fd.read(), hook, 'exec'), symb)
                try:
                    symb['add_info'](self, ui)
                except TypeError as e:
                    if str(e).startswith('add_info()'):
                        # older versions of apport did not pass UI, and hooks that
                        # do not require it don't need to take it
                        symb['add_info'](self)
                    else:
                        raise
            except StopIteration:
                return True
            except:
                apport.error('hook %s crashed:', hook)
                traceback.print_exc()
                pass

        # binary package hook
        #if not package:
        #    package = self.get('Package')
        #if package:
        #    hook = '%s/%s.py' % (_hook_dir, package.split()[0])
        #    if os.path.exists(hook):
        #        try:
        #            with open(hook) as fd:
        #                exec(compile(fd.read(), hook, 'exec'), symb)
        #            try:
        #                symb['add_info'](self, ui)
        #            except TypeError as e:
        #                if str(e).startswith('add_info()'):
        #                    # older versions of apport did not pass UI, and hooks that
        #                    # do not require it don't need to take it
        #                    symb['add_info'](self)
        #                else:
        #                    raise
        #        except StopIteration:
        #            return True
        #        except:
        #            apport.error('hook %s crashed:', hook)
        #            traceback.print_exc()
        #            pass

        # source package hook
        #if not srcpackage:
        #    srcpackage = self.get('SourcePackage')
        #if srcpackage:
        #    hook = '%s/source_%s.py' % (_hook_dir, srcpackage.split()[0])
        #    if os.path.exists(hook):
        #        try:
        #            with open(hook) as fd:
        #                exec(compile(fd.read(), hook, 'exec'), symb)
        #            try:
        #                symb['add_info'](self, ui)
        #            except TypeError as e:
        #                if str(e).startswith('add_info()'):
        #                    # older versions of apport did not pass UI, and hooks that
        #                    # do not require it don't need to take it
        #                    symb['add_info'](self)
        #                else:
        #                    raise
        #        except StopIteration:
        #            return True
        #        except:
        #            apport.error('hook %s crashed:', hook)
        #            traceback.print_exc()
        #            pass

        return False



    def _get_ignore_dom(self):
        '''Read ignore list XML file and return a DOM tree. 
        
        Return an empty DOM tree if file does not exist.

        Raises ValueError if the file exists but is invalid XML.
        '''
        ifpath = os.path.expanduser(_ignore_file)
        if not os.access(ifpath, os.R_OK) or os.path.getsize(ifpath) == 0:
            # create a document from scratch
            dom = xml.dom.getDOMImplementation().createDocument(None, 'apport', None)
        else:
            try:
                dom = xml.dom.minidom.parse(ifpath)
            except ExpatError as e:
                raise ValueError('%s has invalid format: %s' % (_ignore_file, str(e)))

        # remove whitespace so that writing back the XML does not accumulate
        # whitespace
        dom.documentElement.normalize()
        _dom_remove_space(dom.documentElement)

        return dom


    def has_useful_stacktrace(self):
        '''Check whether StackTrace can be considered 'useful'.

        The current heuristic is to consider it useless if it either is shorter
        than three lines and has any unknown function, or for longer traces, a
        minority of known functions.
        '''
        if not self.get('StacktraceTop'):
            return False
        
        unknown_fn = [f.startswith('??') for f in self['StacktraceTop'].splitlines()]

        if len(unknown_fn) < 3:
            return unknown_fn.count(True) == 0

        return unknown_fn.count(True) <= len(unknown_fn)/2.

    def stacktrace_top_function(self):
        '''Return topmost function in StacktraceTop'''

        for l in self.get('StacktraceTop', '').splitlines():
            fname = l.split('(')[0].strip()
            if fname != '??':
                return fname

        return None

    def standard_title(self):
        '''Create an appropriate title for a crash database entry.

        This contains the topmost function name from the stack trace and the
        signal (for signal crashes) or the Python exception (for unhandled
        Python exceptions).

        Return None if the report is not a crash or a default title could not
        be generated.
        '''
        # assertion failure
        if self.get('Signal') == '6' and \
                'ExecutablePath' in self and \
                'AssertionMessage' in self:
            return '%s assert failure: %s' % (
                os.path.basename(self['ExecutablePath']),
                self['AssertionMessage'])

        # signal crash
        if 'Signal' in self and \
            'ExecutablePath' in self and \
            'StacktraceTop' in self:

            signal_names = {
                '4': 'SIGILL',
                '6': 'SIGABRT',
                '8': 'SIGFPE',
                '11': 'SIGSEGV',
                '13': 'SIGPIPE'
            }

            fn = self.stacktrace_top_function()
            if fn:
                fn = ' in %s()' % fn
            else:
                fn = ''

            arch_mismatch = ''
            if 'Architecture' in self and \
                'PackageArchitecture' in self and \
                self['Architecture'] != self['PackageArchitecture'] and \
                self['PackageArchitecture'] != 'all':
                arch_mismatch = ' [non-native %s package]' % self['PackageArchitecture']

            return '%s crashed with %s%s%s' % (
                os.path.basename(self['ExecutablePath']),
                signal_names.get(self.get('Signal'),
                    'signal ' + self.get('Signal')),
                fn, arch_mismatch
            )

        # Python exception
        if 'Traceback' in self and \
            'ExecutablePath' in self:

            trace = self['Traceback'].splitlines()

            if len(trace) < 1:
                return None
            if len(trace) < 3:
                return '%s crashed with %s' % (
                    os.path.basename(self['ExecutablePath']),
                    trace[0])

            trace_re = re.compile('^\s*File\s*"(\S+)".* in (.+)$')
            i = len(trace)-1
            function = 'unknown'
            while i >= 0:
                m = trace_re.match(trace[i])
                if m:
                    module_path = m.group(1)
                    function = m.group(2)
                    break
                i -= 1

            path = os.path.basename(self['ExecutablePath'])
            last_line = trace[-1]
            exception = last_line.split(':')[0]
            m = re.match('^%s: (.+)$' % re.escape(exception), last_line)
            if m:
                message = m.group(1)
            else:
                message = None

            if function == '<module>':
                if module_path == self['ExecutablePath']:
                    context = '__main__'
                else:
                    # Maybe use os.path.basename?
                    context = module_path
            else:
                context = '%s()' % function

            title = '%s crashed with %s in %s' % (
                path,
                exception,
                context
            )

            if message:
                title += ': %s' % message

            return title

        # package problem
        if self.get('ProblemType') == 'Package' and \
            'Package' in self:

            title = 'package %s failed to install/upgrade' % \
                self['Package']
            if self.get('ErrorMessage'):
                title += ': ' + self['ErrorMessage'].splitlines()[-1]

            return title

        if self.get('ProblemType') == 'KernelOops' and \
            'OopsText' in self:

            oops = self['OopsText']
            if oops.startswith('------------[ cut here ]------------'):
                title = oops.split('\n', 2)[1]
            else:
                title = oops.split('\n', 1)[0]

            return title

        if self.get('ProblemType') == 'KernelOops' and \
            'Failure' in self:
            
            # Title the report with suspend or hibernate as appropriate,
            # and mention any non-free modules loaded up front.
            title = ''
            if 'MachineType' in self:
                title += '[' + self['MachineType'] + '] '
            title += self['Failure'] + ' failure'
            if 'NonfreeKernelModules' in self:
                title += ' [non-free: ' + self['NonfreeKernelModules'] + ']'
            title += '\n'

            return title


        return None

    def crash_signature(self):
        '''Get a signature string for a crash.
        
        This is suitable for identifying duplicates.

        For signal crashes this the concatenation of ExecutablePath, Signal
        number, and StacktraceTop function names, separated by a colon. If
        StacktraceTop has unknown functions or the report lacks any of those
        fields, return None. In this case, you can use
        crash_signature_addresses() to get a less precise duplicate signature
        based on addresses instead of symbol names.

        For assertion failures, it is the concatenation of ExecutablePath
        and assertion message, separated by colons.
        
        For Python crashes, this concatenates the ExecutablePath, exception
        name, and Traceback function names, again separated by a colon.
        '''
        if ('ExecutablePath' not in self and 
            not self['ProblemType'] == 'KernelCrash'):
            return None

        # kernel crash
        if 'Stacktrace' in self and self['ProblemType'] == 'KernelCrash':
            sig = 'kernel'
            regex = re.compile ('^\s*\#\d+\s\[\w+\]\s(\w+)')
            for line in self['Stacktrace'].splitlines():
                m = regex.match(line)
                if m:
                    sig += ':' + (m.group(1))
            return sig

        # assertion failures
        if self.get('Signal') == '6' and 'AssertionMessage' in self:
            sig = self['ExecutablePath'] + ':' + self['AssertionMessage']
            # filter out addresses, to help match duplicates more sanely
            return re.sub(r'0x[0-9a-f]{6,}','ADDR', sig)

        # signal crashes
        if 'StacktraceTop' in self and 'Signal' in self:
            sig = '%s:%s' % (self['ExecutablePath'], self['Signal'])
            bt_fn_re = re.compile('^(?:([\w:~]+).*|(<signal handler called>)\s*)$')

            lines = self['StacktraceTop'].splitlines()
            if len(lines) < 2:
                return None

            for line in lines:
                m = bt_fn_re.match(line)
                if m:
                    sig += ':' + (m.group(1) or m.group(2))
                else:
                    # this will also catch ??
                    return None
            return sig

        # Python crashes
        if 'Traceback' in self:
            trace = self['Traceback'].splitlines()

            sig = ''
            if len(trace) == 1:
                # sometimes, Python exceptions do not have file references
                m = re.match('(\w+): ', trace[0])
                if m:
                    return self['ExecutablePath'] + ':' + m.group(1)
                else:
                    return None
            elif len(trace) < 3:
                return None

            for l in trace:
                if l.startswith('  File'):
                    sig += ':' + l.split()[-1]

            return self['ExecutablePath'] + ':' + trace[-1].split(':')[0] + sig

        return None

    def crash_signature_addresses(self):
        '''Compute heuristic duplicate signature for a signal crash.

        This should be used if crash_signature() fails, i. e. Stacktrace does
        not have enough symbols.

        This approach only uses addresses in the stack trace and does not rely
        on symbol resolution. As we can't unwind these stack traces, we cannot
        limit them to the top five frames and thus will end up with several or
        many different signatures for a particular crash. But these can be
        computed and synchronously checked with a crash database at the client
        side, which avoids having to upload and process the full report. So on
        the server-side crash database we will only have to deal with all the
        equivalence classes (i. e. same crash producing a number of possible
        signatures) instead of every single report.

        Return None when signature cannot be determined.
        '''
        if not 'ProcMaps' in self or not 'Stacktrace' in self:
            return None

        stack = []
        failed = 0
        for line in self['Stacktrace'].splitlines():
            if line.startswith('#'):
                addr = line.split()[1]
                if not addr.startswith('0x'):
                    continue
                addr = int(addr, 16) # we do want to know about ValueErrors here, so don't catch
                offset = self._address_to_offset(addr)
                if offset:
                    # avoid ':' in ELF paths, we use that as separator
                    stack.append(offset.replace(':', '..'))
                else:
                    failed += 1

            # stack unwinding chops off ~ 5 functions, and we need some more
            # accuracy because we do not have symbols; but beyond a depth of 15
            # we get too much noise, so we can abort there
            if len(stack) >= 15:
                break

        # we only accept a small minority (< 20%) of failed resolutions, otherwise we
        # discard
        if failed > 0 and len(stack)/failed < 4:
            return None

        # we also discard if the trace is too short
        if (failed == 0 and len(stack) < 3) or (failed > 0 and len(stack) < 6):
            return None

        return '%s:%s:%s:%s' % (
                self['ExecutablePath'], 
                self['Signal'],
                os.uname()[4], 
                ':'.join(stack))

    def _address_to_offset(self, addr):
        '''Resolve a memory address to an ELF name and offset.

        This can be used for building duplicate signatures from non-symbolic
        stack traces. These often do not have enough symbols available to
        resolve function names, but taking the raw addresses also is not
        suitable due to ASLR. But the offsets within a library should be
        constant between crashes (assuming the same version of all libraries).

        This needs and uses the "ProcMaps" field to resolve addresses.

        Return 'path+offset' when found, or None if address is not in any
        mapped range.
        '''
        self._build_proc_maps_cache()

        for (start, end, elf) in self._proc_maps_cache:
            if start <= addr and end >= addr:
                return '%s+%x' % (elf, addr-start)

        return None

    def _build_proc_maps_cache(self):
        '''Generate self._proc_maps_cache from ProcMaps field.
        
        This only gets done once.
        '''
        if self._proc_maps_cache:
            return

        assert 'ProcMaps' in self
        self._proc_maps_cache = []
        # library paths might have spaces, so we need to make some assumptions
        # about the intermediate fields. But we know that in between the pre-last
        # data field and the path there are many spaces, while between the
        # other data fields there is only one. So we take 4 or more spaces as
        # the separator of the last data field and the path.
        fmt = re.compile('^([0-9a-fA-F]+)-([0-9a-fA-F]+).*\s{4,}(\S.*$)')
        fmt_unknown = re.compile('^([0-9a-fA-F]+)-([0-9a-fA-F]+)\s')

        for line in self['ProcMaps'].splitlines():
            if not line.strip():
                continue
            m = fmt.match(line)
            if not m:
                # ignore lines with unknown ELF
                if fmt_unknown.match(line):
                    continue
                # but complain otherwise, as this means we encounter an
                # architecture or new kernel version where the format changed
                assert m, 'cannot parse ProcMaps line: ' + line
            self._proc_maps_cache.append((int(m.group(1), 16), 
                int(m.group(2), 16), m.group(3)))


# end
