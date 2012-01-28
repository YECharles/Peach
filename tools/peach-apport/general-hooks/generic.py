'''Attach generally useful information, not specific to any package.'''

# Copyright (C) 2009 Canonical Ltd.
# Authors: Matt Zimmerman <mdz@canonical.com>
#          Martin Pitt <martin.pitt@ubuntu.com>
#          Brian Murray <brian@ubuntu.com>
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.  See http://www.gnu.org/copyleft/gpl.html for
# the full text of the license.

import os, re
import apport.hookutils, apport.fileutils

def add_info(report, ui):
    nm = apport.hookutils.nonfree_kernel_modules()
    if nm:
        report['NonfreeKernelModules'] = ' '.join(nm)

    # check for low space
    mounts = {'/': 'system',
              '/var': '/var',
             }

    home = os.getenv('HOME')
    if home:
        mounts[home] = 'home'
    treshold = 10

    for mount in mounts:
        st = os.statvfs(mount)
        free_mb = st.f_bavail * st.f_frsize / 1000000

        if free_mb < treshold:
            report['UnreportableReason'] = 'Your %s partition has less than \
%s MB of free space available, which leads to problems using applications \
and installing updates. Please free some space.' % (mounts[mount], free_mb)

    # important glib errors/assertions (which should not have private data)
    if 'ExecutablePath' in report:
        path = report['ExecutablePath']
        if (apport.hookutils.links_with_shared_library(path, 'libgtk') or
            apport.hookutils.links_with_shared_library(path, 'libX11')) and \
           apport.hookutils.in_session_of_problem(report):
            pattern = re.compile('^(\(.*:\d+\): \w+-(WARNING|CRITICAL|ERROR))|(Error: .*No Symbols named)')
            xsession_errors = apport.hookutils.xsession_errors(pattern)
            if xsession_errors:
                report['XsessionErrors'] = xsession_errors

    # using local libraries?
    if 'ProcMaps' in report:
        local_libs = set()
        for lib in re.finditer(r'\s(/[^ ]+\.so[.0-9]*)$', report['ProcMaps'], re.M):
            if not apport.fileutils.likely_packaged(lib.group(1)):
                local_libs.add(lib.group(1))
        if local_libs:
            if not ui.yesno('''The crashed program seems to use third-party or local libraries:

%s

It is highly recommended to check if the problem persists without those first.

Do you want to continue the report process anyway?
''' % '\n'.join(local_libs)):
                raise StopIteration
            report['LocalLibraries'] = ' '.join(local_libs)
            report['Tags'] = (report.get('Tags', '') + ' local-libs').strip()

    # using ecryptfs?
    if os.path.exists(os.path.expanduser('~/.ecryptfs/wrapped-passphrase')):
        report['EcryptfsInUse'] = 'Yes'

    # filter out crashes on missing GLX (LP#327673)
    if '/usr/lib/libGL.so' in (report.get('StacktraceTop') or '\n').splitlines()[0] \
        and 'Loading extension GLX' not in apport.hookutils.read_file('/var/log/Xorg.0.log'):
            report['UnreportableReason'] = 'The X.org server does not support the GLX extension, which the crashed program expected to use.'
    # filter out package install failures due to a segfault
    if 'Segmentation fault' in report.get('ErrorMessage', '') \
        and report['ProblemType'] == 'Package':
            report['UnreportableReason'] = 'The package installation resulted in a segmentation fault which is better reported as a crash report rather than a package install failure.'


if __name__ == '__main__':
    r = {}
    add_info(r, None)
    for k in r:
        print k, ':', r[k]
