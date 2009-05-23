import os, copy, rfc822, time, cStringIO
from distutils import util
from distutils.core import Command, DEBUG
from distutils.errors import *

from Ft import GetConfigVar
from Ft.Lib import Uri, ImportUtil
from Ft.Lib.DistExt import Structures
from Ft.Lib.DistExt.BuildDocs import ProcessIncludes

class Stylesheet:
    """Class used to hold various attributes of an XSLT stylesheet."""
    def __init__(self, uri, extra_outputs=None, mtime=None):
        self.uri = uri
        self.extra_outputs = extra_outputs
        self.mtime = mtime
        return

class InstallDocs(Command):
    """
    Base class for install sub-commands which install documentation.
    """

    user_options = [
        ('install-dir=', 'd', "directory to install documentation to"),
        ('build-dir=','b', "build directory (where to install from)"),
        ('force', 'f', "force installation (overwrite existing files)"),
        ('skip-build', None, "skip the build steps"),
        ]

    boolean_options = ['force', 'skip-build']

    def initialize_options(self):
        self.install_dir = None
        self.force = None
        self.build_dir = None
        self.skip_build = None

        # Stylesheets used for rendering the document files.
        self.docbook_xslt = None
        self.sdocbook_xslt = None
        self.modules_xslt = None
        self.extensions_xslt = None
        self.commandline_xslt = None
        self.docbook_html_xslt = None
        return

    def finalize_options(self):
        self.set_undefined_options('build_docs',
                                   ('build_dir', 'build_dir'))
        self.set_undefined_options('install',
                                   ('install_docs', 'install_dir'),
                                   ('skip_build', 'skip_build'),
                                   ('force', 'force'))
        self.documents = self.get_documents()

        resourcebundle = GetConfigVar('RESOURCEBUNDLE')
        if resourcebundle is None:
            # building 4Suite itself; use different (hard-wired) directories
            base_uri = Uri.OsPathToUri(os.path.join('Ft', 'Data'))
        else:
            datadir = GetConfigVar('DATADIR')
            datadir = os.path.join(datadir, 'Data', 'Stylesheets')
            if resourcebundle:
                resource = ImportUtil.OsPathToResource(datadir)
                base_uri = Uri.ResourceToUri('Ft.Lib', resource)
            else:
                base_uri = Uri.OsPathToUri(datadir)

        defaults = self.get_default_stylesheets()
        for name in defaults:
            attr = name + '_xslt'
            value = getattr(self, attr)
            if value is None:
                value = base_uri + '/' + defaults[name]
            else:
                pathname = util.convert_path(value)
                value = Uri.OsPathToUri(pathname)
            setattr(self, attr, value)

        self._xslt_processor = None
        self._stylesheets = {}
        return

    def get_documents(self):
        documents = []

        def new_document(category, name):
            """Returns a Document instance for the category/name pair."""
            xmlfile = os.path.join(self.build_dir, category, name + '.xml')
            return Structures.Document(xmlfile, category, category=category)

        for document in self.distribution.doc_files:
            if isinstance(document, Structures.Document):
                document = copy.copy(document)
                document.source = util.convert_path(document.source)
                documents.append(document)
            elif isinstance(document, Structures.ExtensionsDocument):
                documents.append(new_document('extensions', document.name))

        # Add Documents for the installed Python modules.
        if self.distribution.has_pure_modules():
            build_py = self.get_finalized_command('build_py')
            for package, module, filename in build_py.find_all_modules():
                if module == '__init__':
                    module = package
                elif package:
                    module = package + '.' + module
                documents.append(new_document('modules', module))
        if self.distribution.has_ext_modules():
            build_ext = self.get_finalized_command('build_ext')
            for extension in build_ext.extensions:
                name = build_ext.get_ext_fullname(extension.name)
                documents.append(new_document('modules', name))

        # Add the CommandLineApp-based scripts
        for script in self.distribution.scripts:
            if script.application is not None:
                documents.append(new_document('commandline', script.name))
        return documents

    def run(self):
        if not self.skip_build:
            self.run_command('build_docs')

        self.render_documents()
        return

    # -- Top-level worker functions ------------------------------------
    # (called from 'run()')

    def render_documents(self):
        extras = {}
        for document in self.documents:
            # Find the stylesheet to render this document
            stylesheet = self.get_stylesheet_obj(document.stylesheet)

            filename = self.get_output_filename(document)
            destdir = os.path.dirname(filename)
            self.mkpath(destdir)
            try:
                target_mtime = os.path.getmtime(filename)
            except OSError:
                target_mtime = -1
            document.uri = Uri.OsPathToUri(document.source)
            document_mtime = self.get_modification_time(document.uri)
            source_mtime = max(document_mtime, stylesheet.mtime)
            if document_mtime is None:
                self.announce('skipping %s (not documented)' % filename, 3)
            elif self.force or source_mtime > target_mtime:
                self.announce("rendering %s -> %s" % (document.source,
                                                      filename), 2)
                try:
                    self.render_document(document, stylesheet, filename)
                except (KeyboardInterrupt, SystemExit):
                    # Let "exitting" exceptions propagate through.
                    raise
                except Exception, exc:
                    if DEBUG: raise
                    raise DistutilsFileError(
                        "could not render %s (%s)" % (document.source, exc))
            else:
                self.announce('not rendering %s (up-to-date)' % filename, 1)

            # Copy any extra files for the stylesheet to destdir.
            # 'extra_outputs' is a list of URIs.
            for uri in stylesheet.extra_outputs:
                pathname = Uri.Relativize(uri, stylesheet.uri)
                target = os.path.join(destdir, *pathname.split('/'))
                if target not in extras:
                    extras[target] = True
                    self.copy_uri(uri, target)
        return

    def render_document(self, document, stylesheet, outfile):
        """
        This method is responsible for using 'stylesheet' to transform
        'document' to the file 'outfile'.

        Override this method to use a different XSLT rendering engine.
        """
        from Ft.Xml.InputSource import DefaultFactory
        from Ft.Xml.Xslt import Processor

        # Get a "clean" processor object
        if self._xslt_processor is None:
            self._xslt_processor = Processor.Processor()
        else:
            self._xslt_processor.reset()

        # Add the stylesheet to the processor object.
        isrc = DefaultFactory.fromUri(stylesheet.uri)
        try:
            self._xslt_processor.appendStylesheet(isrc)
        finally:
            isrc.close()

        params = {'name' : self.distribution.get_name(),
                  'version' : self.distribution.version,
                  'fullname' : self.distribution.get_fullname(),
                  'author' : self.distribution.author,
                  'author-email' : self.distribution.author_email,
                  }
        params.update(document.params)

        # Render the document
        isrc = DefaultFactory.fromUri(document.uri)
        try:
            if self.dry_run:
                stream = cStringIO.StringIO()
            else:
                self.mkpath(os.path.dirname(outfile))
                stream = open(outfile, 'w')
            try:
                try:
                    self._xslt_processor.run(isrc, topLevelParams=params,
                                             outputStream=stream)
                    stream.write('\n')
                finally:
                    stream.close()
            except:
                if not self.dry_run:
                    os.remove(outfile)
                raise
        finally:
            isrc.close()
        return

    # -- Utility methods ---------------------------------------------

    def get_stylesheet_obj(self, stylesheet):
        if stylesheet in self._stylesheets:
            return self._stylesheets[stylesheet]

        uri = getattr(self, stylesheet + '_xslt', None)
        if uri is None:
            raise DistutilsFileError("no stylesheet file defined for '%s'"
                                     % stylesheet)
        extras = self.get_stylesheet_extras(stylesheet, uri)
        mtime = self.get_modification_time(uri, True)
        obj = self._stylesheets[stylesheet] = Stylesheet(uri, extras, mtime)
        return obj

    def get_stylesheet_extras(self, stylesheet):
        return []

    def get_modification_time(self, uri, xslt=False, _mtimes=None):
        if _mtimes is None:
            _mtimes = {}
        def gather_mtimes(fullurl):
            if fullurl not in _mtimes:
                _mtimes[fullurl] = -1
                self.get_modification_time(fullurl, xslt, _mtimes)
            return
        try:
            source = Uri.UrlOpen(uri)
        except EnvironmentError:
            mtime = None
        else:
            mtime = source.headers.getdate_tz('last-modified')
            mtime = rfc822.mktime_tz(mtime)
            ProcessIncludes(source, gather_mtimes, xslt)
        _mtimes[uri] = mtime
        return max(_mtimes.values())

    def copy_uri(self, uri, filename):
        """
        Copies the contents of the resource given by 'uri' to 'filename'.
        """
        source = Uri.UrlOpen(uri)
        try:
            source_mtime = source.headers.getdate_tz('last-modified')
            source_mtime = rfc822.mktime_tz(source_mtime)
            try:
                target_mtime = os.path.getmtime(filename)
            except OSError:
                target_mtime = -1
            if not (self.force or source_mtime > target_mtime):
                self.announce("not copying %s (output up-to-date)" % uri, 1)
                return filename, False

            self.announce("copying %s -> %s" % (uri, filename), 2)
            if not self.dry_run:
                f = open(filename, 'wb')
                try:
                    f.write(source.read())
                finally:
                    f.close()
        finally:
            source.close()
        return filename, True

    # -- Reporting methods ---------------------------------------------

    def get_source_files(self):
        # The sources are assumed to be reported by 'build_docs'
        return []

    def get_inputs(self):
        build_docs = self.get_finalized_command('build_docs')
        return build_docs.get_outputs()

    def get_outputs(self):
        outputs = []
        extras = {}
        for document in self.documents:
            filename = self.get_output_filename(document)
            outputs.append(filename)
            destdir = os.path.dirname(filename)
            stylesheet = self.get_stylesheet_obj(document.stylesheet)
            for source in stylesheet.extra_outputs:
                target = os.path.join(destdir, os.path.basename(source))
                if target not in extras:
                    extras[target] = True
                    outputs.append(target)
        return outputs