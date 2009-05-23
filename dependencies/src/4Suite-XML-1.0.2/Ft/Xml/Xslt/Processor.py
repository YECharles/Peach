########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Xml/Xslt/Processor.py,v 1.78 2006/08/22 00:38:32 jkloth Exp $
"""
XSLT processing engine

Copyright 2005 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

import os, sys, operator, cStringIO, warnings
from xml.dom import Node

# For builtin extension elements/functions
import Exslt, BuiltInExtElements

from Ft import DEFAULT_ENCODING
from Ft.Lib import Uri
from Ft.Xml import InputSource, Domlette, EMPTY_NAMESPACE
from Ft.Xml.Lib import StripElements
from Ft.Xml.Xslt import XsltContext, Error, XsltException, MessageSource
from Ft.Xml.Xslt import OutputHandler, RtfWriter, StringWriter
from Ft.Xml.Xslt.StylesheetReader import StylesheetReader

# Media types that signal that an xml-stylesheet PI points to an XSLT
# document, when the PI contains a type pseudo-attribute.
#
# Note: RFC 3023 suggests application/xslt+xml, and says the +xml
# suffix is not required (but is a SHOULD). If you want to use the
# 'text/xsl' convention, do Processor.XSLT_IMT.append('text/xsl')
# after import, but before instantiating Processor.Processor.
#
XSLT_IMT = ['application/xslt+xml', 'application/xslt',
            'text/xml', 'application/xml']


class Processor(object):
    """
    An XSLT processing engine (4XSLT).

    Typical usage:

    from Ft.Lib.Uri import OsPathToUri
    from Ft.Xml import InputSource
    from Ft.Xml.Xslt import Processor
    # this is just one of several ways to create InputSources
    styuri = OsPathToUri('/absolute/path/to/stylesheet.xslt')
    srcuri = OsPathToUri('/absolute/path/to/doc.xml')
    STY = InputSource.DefaultFactory.fromUri(styuri)
    SRC = InputSource.DefaultFactory.fromUri(srcuri)
    proc = Processor.Processor()
    proc.appendStylesheet(STY)
    result = proc.run(SRC)

    Optional constructor arguments are:

      stylesheetAltUris: a list of alternative base URIs to use when
        resolving relative hrefs in xsl:import/xsl:include instructions.
        These URIs are only tried when the standard XSLT behavior of
        using the base URI of the xsl:import/include element itself
        fails to result in retrieval of a document.

      documentReader: an object that will be used to parse XML source
        documents (not stylesheets). It defaults to
        Ft.Xml.Domlette.NonvalidatingReader, but it can be any object
        that has a parse() method that returns a DOM or Domlette tree.

      implementation: a DOM implementation instance that will be used
        by the processor to create new source tree nodes, such as when
        generating result tree fragments or duplicating the source tree
        when runNode(node, preserveSrc=1) is called. Defaults to
        Ft.Xml.Domlette.implementation. Needs to have a
        createRootNode() method.

    See the run() and runNode() methods for additional runtime options.

    Important instance attributes:

      .extensionParams: a dictionary that allows one to attach
        additional metadata to a processor instance. We use this
        to make invocation-specific data like HTTP query args and
        logfile handles available to XSLT extension functions & elements
        when invoking the processor via the repository's HTTP server.

      .inputSourceFactory: InputSource factory instance used when
        obtaining source documents. Defaults to
        Ft.Xml.InputSource.DefaultFactory.

      .mediaPref: the preferred/target media, for the purpose of
        picking from multiple xml-stylesheet processing instructions.
        Defaults to None. If set to a string, xml-stylesheet PIs
        without that string in their 'media' pseudo-attribute will be
        ignored.

      .msgPrefix and .msgSuffix: strings emitted before and after
        xsl:message output.

      .stylesheet: the complete stylesheet tree.

    """
    # defaults for ExtendedProcessingElements.ExtendedProcessor
    _4xslt_debug = False
    _4xslt_profile = False
    _4xslt_trace = False

    def __init__(self, stylesheetAltUris=None,
                 documentReader=None, implementation=None,
                 stylesheetIncPaths=None):
        self._suppressMsgs = 0
        self.msgPrefix = MessageSource.DEFAULT_MESSAGE_PREFIX
        self.msgSuffix = MessageSource.DEFAULT_MESSAGE_SUFFIX
        self.stylesheet = None
        self.inputSourceFactory = InputSource.DefaultFactory
        self._stylesheetAltUris = stylesheetAltUris or []

        # FIXME: remove all trace of stylesheetIncPaths for 1.0 final
        if stylesheetIncPaths:
            self.warning("Deprecated 'stylesheetIncPaths' argument " \
                         "was used. Use 'stylesheetAltUris' instead.")
            self._stylesheetAltUris.extend(stylesheetIncPaths)

        #Create the default reader for documents
        self._docReader = documentReader or Domlette.NonvalidatingReader

        self._domimp = implementation or Domlette.implementation

        self._lastOutputParams = None

        # preferred xml-stylesheet PI 'media' pseudo-attr value
        self.mediaPref = None

        # has the "built-in template invoked with params" warning been issued?
        self._builtInWarningGiven = 0

        self.extFunctions = {}  #Cache ext functions to give to the context

        self.extElements = {}
        self.extElements.update(Exslt.ExtElements)
        self.extElements.update(BuiltInExtElements.ExtElements)

        self.extensionParams = {}

        # Defer creation in case the user wants to supply their own
        self._styReader = None

        return

    def getStripElements(self):
        if self.stylesheet:
            return self.stylesheet.spaceRules
        else:
            return []

    def registerExtensionModules(self, moduleList):
        """
        Registers a list of Python modules that have public ExtFunctions
        and/or ExtElements dictionaries.

        In a Python module that contains extension implementations,
        define a dictionary named ExtFunctions that, for each extension
        function or element, maps a (namespace-URI, xpath-function-name)
        tuple to a direct reference to the Python function that
        implements the extension. To make the function available to the
        Processor, call this method, passing in ['your.module.name'].

        See Ft.Xml.Xslt.Exslt.*, Ft.Xml.Xslt.BuiltInExtFunctions and
        BuiltInExtElements for working examples of extension modules.
        """
        for mod_name in moduleList:
            if mod_name:
                mod = __import__(mod_name,{},{},['ExtFunctions'])
                if hasattr(mod,'ExtFunctions'):
                    self.extFunctions.update(mod.ExtFunctions)
                if hasattr(mod,'ExtElements'):
                    self.extElements.update(mod.ExtElements)
        return

    def registerExtensionFunction(self, namespace, localName, function):
        """
        Register a single extension function.

        For example, implement your own extension function as a Python
        function that takes an Ft.Xml.XPath.Context.Context instance as
        its first argument. Then, to make the function available to the
        Processor, call this method, passing in the namespace URI and
        local name of the function, and a direct reference to the Python
        function that implements the extension.

        See also registerExtensionModules().
        """
        self.extFunctions[(namespace, localName)] = function
        return

    def registerExtensionElement(self, namespace, localName, klass):
        """
        Register a single extension element.

        For example, implement your own extension element as a subclass
        of Ft.Xml.Xslt.XsltElement. To make the element available to the
        Processor, call this method, passing in the namespace URI and
        local name of the element, and a direct reference to the class
        that implements the extension.

        See also registerExtensionModules().
        """
        self.extElements[(namespace, localName)] = klass
        return

    def setDocumentReader(self, docReader):
        """
        Sets the reader used for source document input sources.

        The reader can be anything with a parse() interface that
        returns a DOM tree. It is normally
        Ft.Xml.Domlette.NonvalidatingReader or whatever was specified in
        the Processor constructor. This method is sometimes used to set
        the reader to Domlette.ValidatingReader.
        """
        self._docReader = docReader
        return

    def getDocumentReader(self):
        """
        Returns the reader used for source document input sources.
        """
        return self._docReader

    def setStylesheetReader(self, reader):
        """
        Sets the reader used for stylesheet document input sources.

        It is normally an instance of
        Ft.Xml.Xslt.StylesheetReader.StylesheetReader
        """
        self._styReader = reader
        return

    def getStylesheetReader(self):
        """
        Returns the reader used for stylesheet document input sources.
        """
        if self._styReader is None:
            self._styReader = StylesheetReader(self._stylesheetAltUris)
        return self._styReader

    def __add_stylesheet(self, stylesheet):
        """
        INTERNAL USE ONLY
        Helper function for adding a stylesheet to the processor.  If a
        stylesheet has already been appended, then this method is equivalent
        to having, in an outer "shell" stylesheet, an xsl:import for the most
        recently appended stylesheet followed by an xsl:import for the given
        stylesheet.
        """
        if self.stylesheet:
            for child in self.stylesheet.children:
                child.importIndex += 1000

            for child in stylesheet.children:
                self.stylesheet.appendChild(child)

            self.stylesheet.reset()
            self.stylesheet.setup()
        else:
            self.stylesheet = stylesheet

        self.outputParams = self.stylesheet.outputParams
        return

    def appendStylesheet(self, iSrc):
        """
        Append a stylesheet from an InputSource.

        This method establishes the stylesheet that the processor will use to
        do the transformation. If a stylesheet has already been appended, then
        this method is equivalent to having, in an outer "shell" stylesheet,
        an xsl:import for the most recently appended stylesheet followed by an
        xsl:import for the stylesheet accessible via the given InputSource.
        """
        reader = self.getStylesheetReader()
        stylesheet = reader.fromSrc(iSrc, self.extElements)
        self.__add_stylesheet(stylesheet)
        return

    def appendStylesheetInstance(self, instance, refUri=''):
        """
        Append an "instant" ("compiled") stylesheet, which is a pickled
        Ft.Xml.Xslt.Stylesheet.Stylesheet object that has had its setup()
        method called already. Such an instance can be obtained from another
        processor, p, as p.stylesheet.root, which you can then pickle, save to
        disk, and reuse in a new processor via this method.

        This method establishes the stylesheet that the processor will use to
        do the transformation. If a stylesheet has already been appended, then
        this method is equivalent to having an xsl:import of the new stylesheet
        in the most recently appended stylesheet.

        An exception will be raised if the same stylesheet is appended more
        than once, just as if the same stylesheet were imported more than once.

        refUri is the base URI to assume for the stylesheet. It defaults to
        the base URI of the root node of the original stylesheet document with
        the highest import precedence.

        Note: Using the instant stylesheet tends to be less efficient than
        using the original document and appendStylesheet(), unless the
        stylesheet is large and complex, like DocBook XSL.
        """
        baseUri = refUri
        if not baseUri:
            # StylesheetTree nodes only ever have baseUri
            # (not baseURI, documentURI, or refUri)
            if hasattr(instance.root, 'baseUri'):
                baseUri = instance.root.baseUri
        reader = self.getStylesheetReader()
        stylesheet = reader.fromInstant(instance, baseUri=baseUri, is_import=True)
        self.__add_stylesheet(stylesheet)
        return

    def appendStylesheetNode(self, node, refUri='', factory=None):
        """
        Append a stylesheet given as a DOM or Domlette Document node.

        This method establishes the stylesheet that the processor will use to
        do the transformation. If a stylesheet has already been appended, then
        this method is equivalent to having an xsl:import of the new stylesheet
        in the most recently appended stylesheet.

        An exception will be raised if the same stylesheet is appended more
        than once, just as if the same stylesheet were imported more than once.

        refUri is the base URI to assume for the stylesheet. It defaults to
        the base URI of the given node.

        The given InputSourceFactory will be used in order to read external
        entities. It defaults to Ft.Xml.InputSource.DefaultFactory.
        """
        document = node.ownerDocument or node
        reader = self.getStylesheetReader()
        stylesheet = reader.fromDocument(document, refUri, factory)
        self.__add_stylesheet(stylesheet)
        return

    def run(self, iSrc, ignorePis=0, topLevelParams=None,
            writer=None, outputStream=None):
        """
        Transform a source document as given via an InputSource.

        Assumes that either the Processor instance has already had
        stylesheets appended (via appendStylesheet(), for example), or
        the source document contains xml-stylesheet processing
        instructions that are not being ignored.

        The ignorePis flag, if set, will cause xml-stylesheet
        processing instructions in the source document to be ignored.

        The topLevelParams argument is an optional dictionary of
        stylesheet parameters, the keys of which may be given as
        strings if they have no namespace, or as (uri, localname)
        tuples otherwise.

        The optional writer argument is a SAX-like event handler that
        is an Ft.Xml.Xslt.NullWriter subclass. The default writer is
        either an Ft.Xml.Xslt.XmlWriter, HtmlWriter or PlainTextWriter,
        depending on the stylesheet(s).

        The optional outputStream argument is a Python file-like object
        to be used as the destination for the writer's output.
        """
        #Update the strip elements
        #Assume that the ones from XSLT have higher priority
        ns = self.getStripElements()
        for s in iSrc.stripElements:
            ns.append(s)
        iSrc.stripElements = ns
        try:
            src = self._docReader.parse(iSrc)
        except Exception, e:
            raise XsltException(Error.SOURCE_PARSE_ERROR,
                                iSrc.uri or '<Python string>', e)
        if not ignorePis and self.__checkStylesheetPis(src, iSrc):
            #Do it again with updates WS strip lists

            #NOTE:  There is a case where this will produce the wrong results.  If, there were
            #previous stylesheets that defined removing white space, then the
            #processing instruction referenced a stylesheet that overrode some of these
            #whitespace processing rules, the original trimmed space will be lost

            #Regardless, we need to remove any new whitespace defined in the PI
            self._stripElements(src)

        return self.execute(src, iSrc, ignorePis, topLevelParams,
                            writer, outputStream)

    def runNode(self, node, sourceUri=None, ignorePis=0,
                topLevelParams=None, writer=None, outputStream=None,
                preserveSrc=0, docInputSource=None):
        """
        Transform a source document as given via a Domlette document
        node.

        Use Ft.Xml.Domlette.ConvertDocument() to create a Domlette
        from some other type of DOM.

        Assumes that either the Processor instance has already had
        stylesheets appended (via appendStylesheet(), for example), or
        the source document contains xml-stylesheet processing
        instructions that are not being ignored.

        sourceUri - The absolute URI of the document
        entity that the node represents, and should be explicitly
        provided, even if it is available from the node itself.

        ignorePis - (flag) If set, will cause xml-stylesheet
        processing instructions in the source document to be ignored.

        topLevelParams - optional dictionary of
        stylesheet parameters, the keys of which may be given as
        strings if they have no namespace, or as (uri, localname)
        tuples otherwise.

        writer - optional SAX-like event handler that
        is an Ft.Xml.Xslt.NullWriter subclass. The default writer is
        either an Ft.Xml.Xslt.XmlWriter, HtmlWriter or PlainTextWriter,
        depending on the stylesheet(s).

        outputStream - optional Python file-like object
        to be used as the destination for the writer's output.

        preserveSrc - (flag) If set signals that the source DOM should not be
        mutated, as would normally happen when honoring XSLT whitespace
        stripping requirements. Setting preserveSrc results in the
        creation of a copy of the source DOM.

        isrc - optional input source used strictly for further resolution
        relative the given DOM
        """

        if node.nodeType != Node.DOCUMENT_NODE:
            raise ValueError(MessageSource.g_errorMessages[
                             Error.CANNOT_TRANSFORM_FRAGMENT])

        if hasattr(node, 'baseURI'):
            node_baseUri = node.baseURI
        elif hasattr(node, 'refUri'):
            node_baseUri = node.refUri
        else:
            node_baseUri = None

        #A base URI must be absolute, but DOM L3 Load & Save allows
        # implementation-dependent behavior if the URI is actually
        # relative, empty or missing. We'll generate a URN for the
        # InputSource's benefit if the base URI is empty/missing.
        # Relative URIs can pass through; the resolvers will handle
        # them appropriately (we hope).
        if not sourceUri:
            sourceUri = node_baseUri or Uri.BASIC_RESOLVER.generate()

        if preserveSrc:
            #preserve the node's baseURI so our DOM is a true copy
            newDoc = self._domimp.createRootNode(node_baseUri)
            for child in node.childNodes:
                new_node = newDoc.importNode(child,1)
                newDoc.appendChild(new_node)
                node = newDoc

        self._stripElements(node)

        if not docInputSource:
            #Create a dummy iSrc
            docInputSource = InputSource.InputSource(
                None, sourceUri, processIncludes=1,
                stripElements=self.getStripElements(),
                factory=self.inputSourceFactory)

        if not ignorePis and self.__checkStylesheetPis(node, docInputSource):
            #Do it again with updated WS strip lists

            #NOTE:  There is a case where this will produce the wrong results.  If, there were
            #previous stylesheets that defined removing white space, then the
            #processing instruction referenced a stylesheet that overrode some of these
            #whitespace processing rules, the original trimmed space will be lost

            #Regardless, we need to remove any new whitespace defined in the PI
            self._stripElements(node)


        return self.execute(node,
                            docInputSource,
                            ignorePis=ignorePis,
                            topLevelParams=topLevelParams,
                            writer=writer,
                            outputStream=outputStream)

    def __cmp_stys(self, a, b):
        """
        Internal function to assist in sorting xml-stylesheet
        processing instructions. See __checkStylesheetPis().
        """
        # sort by priority (natural order)
        return cmp(a[0], b[0])
        ##
        ## For future reference, to support more advanced
        ## preferences, such as having an ordered list of
        ## preferred target media values rather than just one,
        ## and using the Internet media type list in a similar
        ## fashion, we can sort on multiple pseudo-attrs like
        ## this:
        ##
        ## sort by priority (natural order)
        #if cmp(a[0], b[0]):
        #    return cmp(a[0], b[0])
        ## then media (natural order)
        #elif cmp(a[1], b[1]):
        #    return cmp(a[1], b[1])
        ## then type (XSLT_IMT order)
        #else:
        #    for imt in XSLT_IMT:
        #        if a[2] == imt:
        #            return b[2] != imt
        #        else:
        #            return -(b[2] == imt)

    def __checkStylesheetPis(self, node, inputSource):
        """
        Looks for xml-stylesheet processing instructions that are
        children of the given node's root node, and calls
        appendStylesheet() for each one, unless it does not have an
        RFC 3023 compliant 'type' pseudo-attribute or does not have
        a 'media' pseudo-attribute that matches the preferred media
        type that was set as Processor.mediaPref. Uses the given
        InputSource to resolve the 'href' pseudo-attribute. If the
        instruction has an alternate="yes" pseudo-attribute, it is
        treated as a candidate for the first stylesheet only.
        """
        # relevant links:
        # http://www.w3.org/TR/xml-stylesheet/
        # http://lists.fourthought.com/pipermail/4suite/2001-January/001283.html
        # http://lists.fourthought.com/pipermail/4suite/2003-February/005088.html
        # http://lists.fourthought.com/pipermail/4suite/2003-February/005108.html
        #
        # The xml-stylsheet spec defers to HTML 4.0's LINK element
        # for semantics. It is not clear in HTML how the user-agent
        # should interpret multiple LINK elements with rel="stylesheet"
        # and without alternate="yes". In XSLT processing, we, like
        # Saxon, choose to treat such subsequent non-alternates as
        # imports (i.e. each non-alternate stylesheet is imported by
        # the previous one).
        #
        # Given that alternates can appear before or after the
        # non-alternate, there's no way to know whether they apply
        # to the preceding or following non-alternate. So we choose
        # to just treat alternates as only applying to the selection
        # of the first stylesheet.
        #
        # Also, the absence of processing guidelines means we can't
        # know whether to treat the absence of a 'media' pseudo-attr
        # as implying that this is a default stylesheet (e.g. when the
        # preferred media is "foo" and there is no "foo", you use
        # this stylesheet), or whether to treat it as only being the
        # appropriate stylesheet when no media preference is given to
        # the processor.
        #
        # Furthermore, if more than one candidate for the first
        # stylesheet is a match on the 'media' preference (or lack
        # thereof), it's not clear what to do. Do we give preference
        # to the one with a 'type' that is considered more favorable
        # due to its position in the XSLT_IMT list? Do we just use the
        # first one? The last one? For now, if there's one that does
        # not have alternate="yes", we use that one; otherwise we use
        # the first one. Thus, given
        #  <?xml-stylesheet type="application/xslt+xml" href="sty0"?>
        #  <?xml-stylesheet type="application/xslt+xml" href="sty1"
        #    alternate="yes"?>
        # sty0 is used, even if the PIs are swapped; whereas if the
        # only choices are
        #  <?xml-stylesheet type="application/xslt+xml" href="sty1"
        #    alternate="yes"?>
        #  <?xml-stylesheet type="application/xslt+xml" href="sty2"
        #    alternate="yes"?>
        # then sty1 is used because it comes first.
        root = node.rootNode
        c = 1 # count of alternates, +1
        found_nonalt = 0
        stys = []
        for child in root.childNodes:
            # only look at prolog, not anything that comes after it
            if child.nodeType == Node.ELEMENT_NODE:
                break
            # build dict of pseudo-attrs for the xml-stylesheet PIs
            if child.nodeType == Node.PROCESSING_INSTRUCTION_NODE:
                if child.target == 'xml-stylesheet':
                    data = child.data.split()
                    pseudo_attrs = {}
                    for d in data:
                        seg = d.split('=')
                        if len(seg) == 2:
                            pseudo_attrs[seg[0]] = seg[1][1:-1]

                    # PI must have both href, type pseudo-attributes;
                    # type pseudo-attr must match valid XSLT types;
                    # media pseudo-attr must match preferred media
                    # (which can be None)
                    if pseudo_attrs.has_key('href') and \
                        pseudo_attrs.has_key('type'):
                        href = pseudo_attrs['href']
                        imt = pseudo_attrs['type']
                        media = pseudo_attrs.get('media') # defaults to None
                        if media == self.mediaPref and imt in XSLT_IMT:
                            if pseudo_attrs.has_key('alternate') and \
                                pseudo_attrs['alternate'] == 'yes':
                                stys.append((1, media, imt,
                                             pseudo_attrs['href']))
                            elif found_nonalt:
                                c += 1
                                stys.append((c, media, imt,
                                             pseudo_attrs['href']))
                            else:
                                stys.append((0, media, imt,
                                             pseudo_attrs['href']))
                                found_nonalt = 1

        stys.sort(self.__cmp_stys)

        # Assume stylesheets for irrelevant media and disallowed IMTs
        # are filtered out. Assume stylesheets are in ascending order
        # by level. Now just use first stylesheet at each level, but
        # treat levels 0 and 1 the same. Meaning of the levels:
        #  level 0 is first without alternate="yes"
        #  level 1 is all with alternate="yes"
        #  levels 2 and up are the others without alternate="yes"
        hrefs = []
        last_level = -1
        #print "stys=",repr(stys)
        for sty in stys:
            level = sty[0]
            if level == 1 and last_level == 0:
                # we want to ignore level 1s if we had a level 0
                last_level = 1
            if level == last_level:
                # proceed to next level (effectively, we only use
                # the first stylesheet at each level)
                continue
            last_level = level
            hrefs.append(sty[3])

        if hrefs:
            self.getStylesheetReader()._import_index += 1
            for href in hrefs:
                # Resolve the PI with the InputSource for the document
                # containing the PI, so relative hrefs work correctly
                new_source = inputSource.resolve(href,
                                                 hint='xml-stylesheet PI')
                self.appendStylesheet(new_source)

        # Return true if any xml-stylesheet PIs were processed
        # (i.e., the stylesheets they reference are going to be used)
        return not not hrefs

    def execute(self, node, docInputSource, ignorePis=0, topLevelParams=None,
                writer=None, outputStream=None):
        """
        Warning: do not call this method directly unless you know what
        you're doing.  If unsure, you probably want the runNode method.

        Runs the stylesheet processor against the given XML DOM node with the
        stylesheets that have been registered. It does not mutate the source.
        If writer is given, it is used in place of the default output method
        decisions for choosing the proper writer.
        """
        #QUESTION: What about ws stripping?
        #ANSWER: Whitespace stripping happens only in the run*() interfaces.
        #  This method is use-at-your-own-risk. The XSLT conformance of the
        #  source is maintained by the caller. This exists as a performance
        #  hook.
        topLevelParams = topLevelParams or {}

        self.attributeSets = {}
        self.keys = {}

        #See f:chain-to extension element
        self.chainTo = None
        self.chainParams = None

        if not self.stylesheet:
            raise XsltException(Error.NO_STYLESHEET)

        # Use an internal stream to gather the output only if the caller
        # didn't supply other means of retrieving it.
        internalStream = writer is None and outputStream is None

        if not writer:
            # Use OutputHandler to determine the real writer to use.
            outputStream = outputStream or cStringIO.StringIO()
            writer = OutputHandler.OutputHandler(self.outputParams,
                                                 outputStream)
        self.writers = [writer]

        # Setup the named templates
        self._namedTemplates = self.stylesheet.getNamedTemplates()

        # Initialize any stylesheet parameters
        tlp = topLevelParams.copy()
        self._normalizeParams(tlp)
        self._documentInputSource = docInputSource

        # Prepare the stylesheet for processing
        self.stylesheet.primeStylesheet(node, self, tlp, docInputSource.uri)

        # Create the context used for processing
        variables = self.stylesheet.getGlobalVariables()
        functions = self.stylesheet.getInitialFunctions()
        context = XsltContext.XsltContext(node, 1, 1, None,
                                          varBindings=variables,
                                          processor=self,
                                          extFunctionMap=functions)
        context.documents.update(self.stylesheet.root.sourceNodes)
        context.addDocument(node, docInputSource.uri)

        # Process the document
        self.writers[-1].startDocument()
        self.applyTemplates(context)
        self.writers[-1].endDocument()

        # Perform cleanup
        self.stylesheet.idle(node, self, docInputSource.uri)

        #How does this contrast with access to self.outputParams ?
        self._lastOutputParams = self.writers[-1]._outputParams

        del self.writers[:]

        if internalStream:
            # Get the result from our cStringIO 'stream'.
            result = outputStream.getvalue()
        else:
            # It is the callers responsibility to get the result
            result = u""
        return result

    def applyTemplates(self, context, params=None):
        """
        Intended to be used by XSLT instruction implementations only.

        Implements the xsl:apply-templates instruction by attempting to
        let the stylesheet apply its own template for the given context.
        If the stylesheet does not have a matching template, the
        built-in templates are invoked.

        context is an XsltContext instance. params is a dictionary of
        parameters being passed in, defaulting to None.
        """
        params = params or {}
        if not self.stylesheet.applyTemplates(context, self, params):
            # No matching templates found, use builtin templates
            if params and not self._builtInWarningGiven:
                self.warning(MessageSource.BUILTIN_TEMPLATE_WITH_PARAMS)
                self._builtInWarningGiven = 1
            if context.node.nodeType == Node.TEXT_NODE:
                self.writers[-1].text(context.node.data)
            elif context.node.nodeType in [Node.ELEMENT_NODE, Node.DOCUMENT_NODE]:
                state = context.copy()
                node_set = context.node.childNodes
                size = len(node_set)
                pos = 1
                for node in node_set:
                    context.node, context.position, context.size = \
                                  node, pos, size
                    self.applyTemplates(context)
                    pos += 1
                context.set(state)
            elif context.node.nodeType == Node.ATTRIBUTE_NODE:
                self.writers[-1].text(context.node.value)
        return

    def xslMessage(self, msg):
        """
        Intended to be used by XSLT instruction implementations only.

        Used by xsl:message to emit a message to sys.stderr, unless such
        messages are suppressed (see messageControl()). Uses the
        msgPrefix & msgSuffix instance attributes.
        """
        if not self._suppressMsgs:
            sys.stderr.write(self.msgPrefix)
            sys.stderr.write(msg)
            sys.stderr.write(self.msgSuffix)
            sys.stderr.flush()
        return

    #FIXME: make this _warning?
    def warning(self, message):
        """
        Emits a warning via Python's warnings framework, unless warnings
        are suppressed (see messageControl()).

        Used, for example, to announce that built-in templates are being
        invoked with params.
        """
        if not self._suppressMsgs:
            # Using level=2 to show the stack where the warning occured.
            warnings.warn(message, stacklevel=2)
        return

    def messageControl(self, suppress):
        """
        Controls whether the processor emits warnings and xsl:message
        messages. Call with suppress=1 to suppress such output.
        """
        self._suppressMsgs = suppress
        return

    def addHandler(self, outputParams, stream):
        """
        Intended to be used by XSLT instruction implementations only.

        Sets up the processor to start processing subsequently
        generated content with an output writer wrapper that first
        determines which XSLT output method is going to be used (i.e.,
        by looking at the output parameters or waiting to see if an
        'html' element is the first new node generated), then replaces
        itself with the appropriate writer instance.

        outputParams is an Ft.Xml.Xslt.OutputParameters instance.

        stream will be passed on to the constructor of the real writer.
        """
        handler = OutputHandler.OutputHandler(outputParams, stream)
        self.writers.append(handler)
        handler.startDocument()
        return

    def removeHandler(self):
        """
        Intended to be used by XSLT instruction implementations only.

        Deletes the most recently added output writer.
        """
        self.writers[-1].endDocument()
        del self.writers[-1]
        return

    def pushResultTree(self, baseUri, implementation=None):
        """
        Intended to be used by XSLT instruction implementations only.

        Sets up the processor to start processing subsequently
        generated content with a new output writer that produces
        a separate document. The new document will have the given
        baseUri as its URI. This is used to generate result tree
        fragments.

        Allows specifying an alternative DOM implementation for the
        creation of the new document.
        """
        writer = RtfWriter.RtfWriter(self.outputParams, baseUri,
                                     implementation or self._domimp)
        self.writers.append(writer)
        return

    def pushResultString(self):
        """
        Intended to be used by XSLT instruction implementations only.

        Sets up the processor to start processing subsequently
        generated content with an output writer that buffers the text
        from text events and keeps track of whether non-text events
        occurred. This is used by the implementations of XSLT
        instructions such as xsl:attribute.
        """
        writer = StringWriter.StringWriter(self.outputParams)
        self.writers.append(writer)
        return

    def pushResult(self, handler=None):
        """
        Intended to be used by XSLT instruction implementations only.

        Sets up the processor to start processing subsequently
        generated content with a new output writer (the given handler
        of SAX-like output events).
        """
        if handler is None:
            warnings.warn("Use pushResultTree(uri) to create RTFs",
                          DeprecationWarning, stacklevel=2)
            handler = RtfWriter.RtfWriter(self.outputParams,
                                          self.stylesheet.baseUri)
        self.writers.append(handler)
        handler.startDocument()
        return

    def popResult(self):
        """
        Intended to be used by XSLT instruction implementations only.

        Ends temporary output writing that was started with
        pushResultString(), pushResultTree(), or pushResult(), and
        returns the result.
        """
        handler = self.writers.pop()
        handler.endDocument()
        return handler.getResult()

    def output(self):
        warnings.warn("output() deprecated; use writer",
                      DeprecationWarning, 2)
        return self.writer

    def writer(self):
        """
        Intended to be used by XSLT instruction implementations only.

        Returns the current output writer.
        """
        return self.writers[-1]

    writer = property(writer)

    def _stripElements(self, node):
        stripElements = self.getStripElements()
        if stripElements:
            StripElements.StripElements(node, stripElements)
        return

    def _normalizeParams(self, params):
        """
        params is a dictionary of top-level parameters.  The main task is to
        check this dictionary for lists of strings and convert these to
        a node set of text nodes
        """

        def to_unicode(s):
            try:
                # Try UTF-8
                return unicode(s, 'UTF-8')
            except ValueError:
                # Use encoding from locale
                try:
                    return unicode(s, DEFAULT_ENCODING)
                except ValueError:
                    #FIXME: l10n
                    raise ValueError(
                        "String parameters must be Unicode objects or "
                        "strings encoded as UTF-8 or %s." %
                        DEFAULT_ENCODING)

        for k, v in params.items():
            if v:
                if isinstance(v, str):
                    params[k] = to_unicode(v)
                elif isinstance(v, list) and isinstance(v[0], (str, unicode)):
                    doc = self._domimp.createRootNode(self.stylesheet.baseUri)
                    nodeset = []
                    for text in v:
                        if isinstance(text, str):
                            text = to_unicode(text)
                        nodeset.append(doc.createTextNode(text))
                    params[k] = nodeset
        return

    def reset(self):
        """
        Returns the processor to a state where it can be used to do a
        new transformation with a new stylesheet. Deletes the current
        stylesheet tree, and may do other cleanup.
        """
        self.stylesheet = None
        self.getStylesheetReader().reset()
        return
