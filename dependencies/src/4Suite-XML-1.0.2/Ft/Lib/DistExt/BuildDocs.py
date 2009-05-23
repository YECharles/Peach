########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Lib/DistExt/BuildDocs.py,v 1.49.2.4 2006/11/25 23:28:28 jkloth Exp $
"""
Main distutils extensions for generating documentation

Copyright 2005 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

# NOTE: Before anybody gets wild ideas about changing urllib stuff to
# Ft.Lib.Uri, remember that this code is used *BEFORE* Ft is installed.
# It also is "safe" to urllib stuff as it will only be dealing with local
# files and its filename <-> url conversion works within itself.

import sys, os, copy, warnings, re, imp, rfc822, time, cStringIO
from distutils import util
from distutils.core import Command, DEBUG
from distutils.errors import *

from Ft import GetConfigVar
from Ft.Lib import Uri, ImportUtil
from Ft.Lib.DistExt import Structures
from Ft.Lib.DistExt.Formatters import *

__zipsafe__ = True

class BuildDocs(Command):

    command_name = 'build_docs'

    description = "build documentation files (copy or generate XML sources)"

    user_options = [
        ('build-dir=', 'd',
         "directory to \"build\" (generate) to"),
        ('force', 'f',
         "forcibly build everything (ignore file timestamps)"),
        ]

    boolean_options = ['inplace', 'force']

    def initialize_options(self):
        self.build_dir = None
        self.build_lib = None
        self.force = None

        # If 'inplace' is True, the generated documents are considered
        # to be source files as well.
        self.inplace = False

        # Set to true to validate the static XML documents
        self.validate = False
        return

    def finalize_options(self):
        self.set_undefined_options('build',
                                   ('build_docs', 'build_dir'),
                                   ('build_lib', 'build_lib'),
                                   ('force', 'force'))

        # Get the distribution options that are used for build_docs
        # options.
        self.files = [ doc for doc in self.distribution.doc_files
                       if isinstance(doc, Structures.File) ]

        self.static = [ doc for doc in self.distribution.doc_files
                        if isinstance(doc, Structures.Document) ]

        self.modules, self.module_info = self.get_modules()

        self.extensions = [ doc for doc in self.distribution.doc_files
                            if isinstance(doc, Structures.ExtensionsDocument) ]

        self.scripts = [ doc for doc in self.distribution.scripts
                         if isinstance(doc, Structures.Script)
                         and doc.application is not None ]

        # Initialize the properties that are not externally modifiable.
        self._xslt_processor = None
        return

    def get_outputs(self):
        outputs = []
        for name in self.modules:
            xmlfile = self.get_output_filename(name, 'modules')
            outputs.append(xmlfile)
        for ext in self.extensions:
            xmlfile = self.get_output_filename(ext.name, 'extensions')
            outputs.append(xmlfile)
        for script in self.scripts:
            xmlfile = self.get_output_filename(script.name, 'commandline')
            outputs.append(xmlfile)
        index_name = 'index-' + self.distribution.get_name()
        outputs.append(self.get_output_filename(index_name))
        return outputs

    def get_source_files(self):
        sources = []
        for doc in self.distribution.doc_files:
            if isinstance(doc, Structures.File):
                source = util.convert_path(doc.source)
                sources.append(source)
            elif isinstance(doc, Structures.Document):
                source = util.convert_path(doc.source)
                sources.append(source)
                prefix = len(os.getcwd()) + len(os.sep)
                for path in self.find_xml_includes(Uri.OsPathToUri(source)):
                    sources.append(path[prefix:])
        if self.inplace:
            sources.extend(self.get_outputs())
        return sources

    def find_xml_includes(self, uri, _includes=None):
        if _includes is None:
            _includes = {}
        def gather_includes(fullurl):
            if fullurl not in _includes:
                _includes[fullurl] = Uri.UriToOsPath(fullurl)
                self.find_xml_includes(fullurl, _includes)
            return
        ProcessIncludes(uri, gather_includes)
        return _includes.values()

    def run(self):
        if self.modules:
            self.prepare_modules()

        documents = []
        # Add the static XML content
        if self.static:
            documents.extend(self.build_static())

        # Create the XML content for the API reference
        if self.modules:
            documents.extend(self.build_api())

        # Create the XML content for XPath/XSLT extensions
        if self.extensions:
            documents.extend(self.build_extensions())

        # Create the XML content for command-line applications
        if self.scripts:
            documents.extend(self.build_commandline())

        # Create the XML content for the index
        self.build_index(documents)
        return

    def get_modules(self):
        # Locate all installed modules
        modules = []
        sources = {}
        if self.distribution.has_pure_modules():
            build_py = self.get_finalized_command('build_py')
            for package, module, filename in build_py.find_all_modules():
                if module == '__init__':
                    module = package
                    module_type = imp.PKG_DIRECTORY
                elif package:
                    module = package + '.' + module
                    module_type = imp.PY_SOURCE
                modules.append(module)
                package_dir = package.replace('.', os.sep)
                package_dir = os.path.join(build_py.build_lib, package_dir)
                filename = os.path.basename(filename)
                filename = os.path.join(package_dir, filename)
                sources[module] = (filename, module_type)
        if self.distribution.has_ext_modules():
            build_ext = self.get_finalized_command('build_ext')
            for ext in build_ext.extensions:
                module = build_ext.get_ext_fullname(ext.name)
                filename = build_ext.get_ext_filename(module)
                modules.append(module)
                filename = os.path.join(build_ext.build_lib, filename)
                sources[module] = (filename, imp.C_EXTENSION)
        return (modules, sources)

    # -- Top-level worker functions ------------------------------------
    # (called from 'run()')

    def prepare_modules(self):
        if self.distribution.has_pure_modules():
            self.run_command('build_py')
        if self.distribution.has_ext_modules():
            self.run_command('build_ext')

        if self.distribution.config_module:
            from Ft.Lib.DistExt.InstallConfig import METADATA_KEYS
            if self.distribution.config_module not in sys.modules:
                module = imp.new_module(self.distribution.config_module)
                sys.modules[self.distribution.config_module] = module
            else:
                module = sys.modules[self.distribution.config_module]
            for name in METADATA_KEYS:
                value = getattr(self.distribution, 'get_' + name)()
                setattr(module, name.upper(), value)

        # Add the build directory to the search path (sys.path).
        sys.path.insert(0, self.build_lib)

        # Enable importing of modules in namespace packages.
        for package in self.distribution.namespace_packages:
            packages = [package]
            while '.' in package:
                package = '.'.join(package.split('.')[:-1])
                packages.insert(0, package)
            for package in packages:
                path = os.path.join(self.build_lib, *package.split('.'))
                if package not in sys.modules:
                    module = sys.modules[package] = imp.new_module(package)
                    module.__path__ = [path]
                else:
                    module = sys.modules[package]
                    try:
                        search_path = module.__path__
                    except AttributeError:
                        raise DistutilsSetupError("namespace package '%s' is"
                                                  " not a package" % package)
                    search_path.insert(0, path)

        # Any packages that are already imported also need their
        # search path (__path__) adjusted.
        for name in self.modules:
            if name in sys.modules:
                search_path = getattr(sys.modules[name], '__path__', None)
                if search_path is not None:
                    path = os.path.join(self.build_lib, *name.split('.'))
                    search_path.insert(0, path)
        return

    def build_static(self):
        documents = []
        for document in self.static:
            # Building is as simple as creating a new Document instance to
            # reflect the converted paths.
            document = copy.copy(document)
            document.source = util.convert_path(document.source)
            documents.append(document)

        # Validate the content
        if self.validate:
            from xml.sax.handler import feature_validation
            from Ft.Xml.InputSource import DefaultFactory
            from Ft.Xml.Sax import CreateParser

            class ErrorHandler:
                def __init__(self, displayhook):
                    self.displayhook = displayhook
                def warning(self, exception):
                    self.displayhook(exception)
                def error(self, exception):
                    self.displayhook(exception)
                def fatalError(self, exception):
                    raise exception

            parser = CreateParser()
            parser.setFeature(feature_validation, True)
            parser.setErrorHandler(ErrorHandler(self.warn))

            for document in documents:
                self.announce('validating %s' % document.source, 2)
                parser.parse(DefaultFactory.fromUri(document.source))
        return documents

    def build_api(self):
        formatter = ApiFormatter.ApiFormatter(self, self.module_info)
        category = 'modules'

        # Find the top-level package to be documented
        first = min(self.modules)
        last = max(self.modules)
        shortest = min(len(first), len(last))
        for i in xrange(shortest):
            if first[i] != last[i]:
                top_level = first[:i]
                break
        else:
            top_level = first[:shortest]
        if not top_level:
            raise DistutilsInternalError(
                "documenting multiple top-level packages is not supported")
        warnings.filterwarnings('ignore', '', DeprecationWarning, top_level)

        documents = []
        for name in self.modules:
            try:
                module = __import__(name, {}, {}, ['*'])
            except ImportError, error:
                if DEBUG: raise
                self.announce('not documenting %s (%s)' % (name, error), 3)
                continue

            # The build tree source is required for C-extension modules and
            # is safe for pure-Python modules.
            sources = [self.module_info[name][0]]
            xmlfile = self.document(category, name, sources, module, formatter)
            if name == top_level:
                # Only those documents with a title will be listed on the
                # index page
                title = '%s API Reference' % self.distribution.get_name()
                documents.append(Structures.Document(xmlfile,
                                                     stylesheet=category,
                                                     title=title,
                                                     category='general'))
        return documents

    def build_extensions(self):
        """
        Create XML documentation for XPath/XSLT extensions
        """
        formatter = ExtensionFormatter.ExtensionFormatter(self)
        category = 'extensions'

        extension_attrs = ('ExtNamespaces', 'ExtFunctions', 'ExtElements')

        docs = []
        for extension in self.extensions:
            # create a temporary module that will contain the combined
            # extension information
            extension_module = imp.new_module(extension.name)
            for attr in extension_attrs:
                setattr(extension_module, attr, {})
            sources = []
            for name in extension.modules:
                try:
                    module = __import__(name, {}, {}, extension_attrs)
                except ImportError, e:
                    raise DistutilsFileError(
                        "could not import '%s': %s" % (name, e))
                for attr in extension_attrs:
                    if hasattr(module, attr):
                        attrs = getattr(module, attr)
                        getattr(extension_module, attr).update(attrs)
                sources.append(self.module_info[name][0])
            xmlfile = self.document(category, extension.name, sources,
                                    extension_module, formatter)
            docs.append(Structures.Document(xmlfile, stylesheet=category,
                                            title=extension.title,
                                            category=category))
        return docs

    def build_commandline(self):
        formatter = CommandLineFormatter.CommandLineFormatter(self)
        category = 'commandline'

        docs = []
        for script in self.scripts:
            try:
                module = __import__(script.module, {}, {}, [script.application])
            except ImportError, e:
                raise DistutilsFileError(
                    "could not document '%s' script: %s" % (script.name, e))

            # Get the CommandLineApp instance for documenting
            app = getattr(module, script.application)()
            # Get the sources that are used to implement the application
            sources = [self.module_info[script.module][0]]
            for cmd_name, cmd in app.get_help_doc_info():
                source = cmd._fileName
                if source is None:
                    module_name = cmd.__class__.__module__
                    source = self.module_info[module_name][0]
                sources.append(source)
            # Now document the application and its commands, if any.
            xmlfile = self.document(category, script.name, sources, app,
                                    formatter)
            title = script.name + ' - ' +  app.description
            docs.append(Structures.Document(xmlfile, stylesheet=category,
                                            title=title, category=category))
        return docs

    def build_index(self, documents):
        from Ft.Xml.Xslt.BuiltInExtElements import RESERVED_NAMESPACE

        name = 'index-' + self.distribution.get_name()
        xmlfile = self.get_output_filename(name)
        source_mtime = max(os.path.getmtime(self.distribution.script_name),
                           os.path.getmtime(self.distribution.package_file),
                           ImportUtil.GetLastModified(__name__))
        try:
            target_mtime = os.path.getmtime(xmlfile)
        except OSError:
            target_mtime = -1
        if not (self.force or source_mtime > target_mtime):
            self.announce('not creating index (up-to-date)', 1)
            return
        else:
            self.announce("creating index -> %s" % xmlfile, 2)

        index = {}
        index_uri = Uri.OsPathToUri(xmlfile)
        xmlstr = XmlFormatter.XmlRepr().escape
        for doc in documents:
            if 'noindex' not in doc.flags:
                output = os.path.splitext(doc.source)[0] + '.html'
                source_uri = Uri.OsPathToUri(doc.source)
                output_uri = Uri.OsPathToUri(output)
                category = index.setdefault(doc.category, [])
                category.append({
                    'title' : xmlstr(doc.title),
                    'source' : Uri.Relativize(source_uri, index_uri),
                    'output' : Uri.Relativize(output_uri, index_uri),
                    'stylesheet' : xmlstr(doc.stylesheet),
                    })

        sections = []
        for title, category, sort in (
            ('General', 'general', False),
            ('Modules', 'modules', True),
            ('XPath/XSLT Extensions', 'extensions', False),
            ('Command-line Applications', 'commandline', True)
            ):
            if category not in index:
                continue
            items = []
            L = index[category]
            if sort:
                L.sort(lambda a, b: cmp(a['title'], b['title']))
            for info in L:
                repl = {'title' : info['title'],
                        'url' : info['output'],
                        }
                items.append(INDEX_LISTITEM % repl)
            if items:
                # add the section if it contains any entries
                items = ''.join(items)
                repl = {'title' : xmlstr(title),
                        'category' : xmlstr(category),
                        'items' : items,
                        }
                sections.append(INDEX_SECTION % repl)
        sections = ''.join(sections)

        sources = []
        for category in index.values():
            for info in category:
                sources.append(INDEX_SOURCE % info)
        sources = ''.join(sources)

        repl = {'fullname' : xmlstr(self.distribution.get_fullname()),
                'sections' : sections,
                'namespace' : RESERVED_NAMESPACE,
                'sources' : sources,
                }
        index = INDEX_TEMPLATE % repl

        if not self.dry_run:
            f = open(xmlfile, 'wb')
            f.write(index)
            f.close()

        return documents

    def document(self, category, name, sources, object, formatter):
        xmlfile = self.get_output_filename(name, category)
        self.mkpath(os.path.dirname(xmlfile))

        # The dependencies for 'object' are the source for the formatter
        # and, of course, 'sources'.
        formatter_module = formatter.__class__.__module__
        source_mtime = max(ImportUtil.GetLastModified(formatter_module),
                           *map(os.path.getmtime, sources))
        try:
            target_mtime = os.path.getmtime(xmlfile)
        except OSError:
            target_mtime = -1
        if self.force or source_mtime > target_mtime:
            self.announce("documenting %s -> %s" % (name, xmlfile), 2)
            if not self.dry_run:
                try:
                    stream = open(xmlfile, 'w')
                    try:
                        formatter.format(object, stream, encoding='iso-8859-1')
                    finally:
                        stream.close()
                except (KeyboardInterrupt, SystemExit):
                    os.remove(xmlfile)
                    raise
                except Exception, exc:
                    os.remove(xmlfile)
                    if DEBUG: raise
                    raise DistutilsExecError("could not document %s (%s)" %
                                             (name, exc))
        else:
            self.announce('not documenting %s (up-to-date)' % name, 1)
        return xmlfile

    def get_output_filename(self, name, category=None):
        dest_dir = self.build_dir
        if category:
            dest_dir = os.path.join(dest_dir, category)
        return os.path.join(dest_dir, name + '.xml')


def FindIncludes(source_uri, _includes=None):
    if _includes is None:
        _includes = {}
    def gather_includes(fullurl):
        if fullurl not in _includes:
            _includes[fullurl] = True
            FindIncludes(fullurl, _includes)
        return
    ProcessIncludes(source, gather_includes)
    return _includes


def ProcessIncludes(source, callback, xslt=False):
    from xml.sax import make_parser, SAXException, SAXNotRecognizedException
    from xml.sax.handler import ContentHandler, feature_namespaces, \
         feature_validation, feature_external_ges, feature_external_pes
    from xml.sax.xmlreader import InputSource

    # defined as nested to keep things "import clean"
    class InclusionFilter(ContentHandler):

        XSLT_INCLUDES = [
            ("http://www.w3.org/1999/XSL/Transform", "import"),
            ("http://www.w3.org/1999/XSL/Transform", "include"),
            ]

        def startDocument(self):
            url = self._locator.getSystemId()
            self._bases = [url]
            self._scheme = Uri.GetScheme(url)
            self._elements = [
                ("http://www.w3.org/2001/XInclude", "include"),
                ]
            if xslt:
                self._elements.extend(self.XSLT_INCLUDES)
        def startElementNS(self, expandedName, tagName, attrs):
            # Update xml:base stack
            xml_base = ("http://www.w3.org/XML/1998/namespace", "base")
            baseUri = attrs.get(xml_base, self._bases[-1])
            self._bases.append(baseUri)

            if expandedName in self._elements:
                try:
                    href = attrs[(None, 'href')]
                except KeyError:
                    # XInclude same document reference, nothing to do
                    return

                # Ignore XInclude's with parse='text'
                if attrs.get((None, 'parse'), 'xml') == 'text':
                    return

                # Only follow inclusions that have the same scheme as the
                # initial document.
                fullurl = Uri.BaseJoin(baseUri, href)
                if Uri.GetScheme(fullurl) == self._scheme:
                    callback(fullurl)
        def endElementNS(self, expandedName, tagName):
            del self._bases[-1]
    # -- end InclusionFilter --

    try:
        parser = make_parser()
        parser.setFeature(feature_namespaces, True)
        # Attempt to disable all external entity resolution
        for feature in (feature_validation, feature_external_ges,
                        feature_external_pes):
            try:
                parser.setFeature(feature, False)
            except SAXNotRecognizedException:
                pass
    except SAXException, e:
        raise DistutilsModuleError(e.getMessage())

    handler = InclusionFilter()
    parser.setContentHandler(handler)

    if isinstance(source, (str, unicode)):
        try:
            stream = Uri.UrlOpen(source)
        except OSError:
            # Assume part of an XInclude w/fallback.
            return
        source = InputSource(source)
        source.setByteStream(stream)
    elif hasattr(source, 'read'):
        stream = source
        source = InputSource(getattr(stream, 'name', None))
        source.setByteStream(stream)
    parser.parse(source)
    return


INDEX_TEMPLATE = """<?xml version="1.0" encoding="ISO-8859-1"?>
<!DOCTYPE article PUBLIC "-//OASIS//DTD Simplified DocBook XML V1.1//EN"
          "http://docbook.org/xml/simple/1.1/sdocbook.dtd">
<?ftdb-ignore-namespace http://xmlns.4suite.org/reserved?>
<article>
  <title>%(fullname)s Document Index</title>
%(sections)s

  <f:sources xmlns:f="%(namespace)s">
%(sources)s
  </f:sources>

</article>
"""

INDEX_SECTION = """
  <section id="%(category)s">
    <title>%(title)s</title>
    <itemizedlist>
%(items)s
    </itemizedlist>
  </section> <!-- %(category)s -->
"""

INDEX_LISTITEM = """\
      <listitem>
        <ulink url="%(url)s" type="generate">%(title)s</ulink>
      </listitem>
"""

INDEX_SOURCE = """\
    <f:source>
      <f:title>%(title)s</f:title>
      <f:src>%(source)s</f:src>
      <f:dst>%(output)s</f:dst>
      <f:stylesheet>%(stylesheet)s</f:stylesheet>
    </f:source>
"""
