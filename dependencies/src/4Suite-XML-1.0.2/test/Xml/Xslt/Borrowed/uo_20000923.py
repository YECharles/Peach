#Uche Ogbuji's docbook test: pretty much just checking one small plot of performance scale

from Xml.Xslt import test_harness

sheet_1 = """<?xml version="1.0"?>
<!--

 File Name:            docbook_html1.xslt

 Documentation:        http://docs.4suite.org/stylesheets/docbook_html1.xslt.html

 Simple DocBook Stylesheet
 WWW: http://4suite.org/4XSLT        e-mail: support@4suite.org

 Copyright (c) 1999-2001 Fourthought Inc, USA.   All Rights Reserved.
 See  http://4suite.org/COPYRIGHT  for license and copyright information
-->

<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:doc="http://docbook.org/docbook/xml/4.0/namespace"
  version="1.0"
>

  <xsl:output method="html" encoding="ISO-8859-1"/>

  <xsl:param name="top-level-html" select="1"/>

  <xsl:template match="/">
    <xsl:choose>
      <xsl:when test="$top-level-html">
        <HTML>
        <HEAD>
          <TITLE><xsl:value-of select='doc:article/doc:artheader/doc:title'/></TITLE>
          <META HTTP-EQUIV="content-type" CONTENT="text/html" charset="UTF-8"/>
          <META NAME="author" CONTENT="{doc:article/doc:artheader/doc:author}"/>
        </HEAD>
        <BODY>
          <H1><xsl:value-of select='doc:article/doc:artheader/doc:title'/></H1>
          <xsl:apply-templates/>
        </BODY>
        </HTML>
      </xsl:when>
      <xsl:otherwise>
        <xsl:apply-templates/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:attribute-set name="doc:ol-style">
    <xsl:attribute name="start">1</xsl:attribute>
    <xsl:attribute name="type">1</xsl:attribute>
  </xsl:attribute-set>

  <xsl:template match="doc:sect1">
    <H3><xsl:value-of select="doc:title"/></H3>
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="doc:sect2">
    <H4><xsl:value-of select="doc:title"/></H4>
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="doc:orderedlist">
    <OL xsl:use-attribute-sets="doc:ol-style"><xsl:apply-templates/></OL>
  </xsl:template>

  <xsl:template match="doc:itemizedlist">
    <UL><xsl:apply-templates/></UL>
  </xsl:template>

  <xsl:template match="doc:listitem">
    <LI><xsl:apply-templates/></LI>
  </xsl:template>

  <xsl:template match="doc:para">
    <P><xsl:apply-templates/></P>
  </xsl:template>

  <xsl:template match="doc:computeroutput">
    <SAMP><xsl:apply-templates/></SAMP>
  </xsl:template>

  <xsl:template match="doc:filename">
    <SAMP><xsl:apply-templates/></SAMP>
  </xsl:template>

  <xsl:template match="doc:screen">
    <PRE><xsl:apply-templates/></PRE>
  </xsl:template>

  <xsl:template match="doc:glosslist">
    <DL><xsl:apply-templates/></DL>
  </xsl:template>

  <xsl:template match="doc:glossentry">
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="doc:glossterm">
    <DT><I><xsl:apply-templates/></I></DT>
  </xsl:template>

  <xsl:template match="doc:glossdef">
    <DD><xsl:apply-templates/></DD>
  </xsl:template>

  <xsl:template match='doc:emph'>
    <I><xsl:apply-templates/></I>
  </xsl:template>

  <xsl:template match='doc:mediaobject'>
    <IMG SRC='{doc:imageobject/@fileref}' ALT='{doc:textobject/doc:phrase}'></IMG>
  </xsl:template>

  <xsl:template match='doc:strong'>
    <B><xsl:apply-templates/></B>
  </xsl:template>

  <xsl:template match='doc:link'>
    <A HREF="{@linkend}"><xsl:apply-templates/></A>
  </xsl:template>

  <xsl:template match='doc:align'>
    <DIV ALIGN="{@style}"><xsl:apply-templates/></DIV>
  </xsl:template>

  <xsl:template match='doc:separator'>
    <HR/>
  </xsl:template>

  <xsl:template match='doc:simplelist'>
    <DL><xsl:apply-templates/></DL>
  </xsl:template>
  
  <xsl:template match='doc:member'>
    <DD><xsl:apply-templates/></DD>
  </xsl:template>
  
  <xsl:template match='doc:note'>
    <BLOCKQUOTE>
      <I><B>
      <!-- Emphasize the title -->
      <xsl:choose>
        <xsl:when test='doc:title'>
          <xsl:value-of select='doc:title'/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:text>Note</xsl:text>
        </xsl:otherwise>
      </xsl:choose>
      </B></I>
      <xsl:apply-templates/>
    </BLOCKQUOTE>
  </xsl:template>

  <!-- ignore any other docbook tags -->
  <xsl:template match="doc:*" priority="-1.0">
    <!-- <xsl:message>Hi!</xsl:message> -->
    <xsl:apply-templates select="doc:*"/>
  </xsl:template>

</xsl:stylesheet>
"""


source_1 = """<article xmlns="http://docbook.org/docbook/xml/4.0/namespace">
<artheader>
<title>Practical XML with Linux, Part 3: A survey of the tools</title><author>Uche Ogbuji</author>
</artheader>

<sect1>

<para>
On re-reading my first two XML articles, just over a year ago in this journal and in its sister, Sunworld, I'm struck by how much they represented a justification of XML as the great tin opener of closed data formats.  In under a year, it looks as if all the light-bulbs went on at once.  XML is in the computer news every day, every company seems to be scrambling to ink XML into their brochures, and XML standards organizations such as the World-Wide Web consortium (W3C) practically have to turn people away.  At this point I hardly think any more justification of XML for open data exchange is required.  It's pretty much a fact of information technology.  The remaining questions are how to use XML to solve real problems better than with any other means.
</para>

<para>
As I mentioned in my most recent article, the W3C and other standards organizations are working very quickly to complete specifications for technologies complementary to XML.  I mentioned namespaces, which are a key facility for managing global names and are now used in almost every XML technology.  I also mentioned DOM and XSLT.  Since then, XLink, XPointer, XML Schemas, SVG and other specs are almost complete.  I shall discuss these later in the series as well as RDF, Schematron and other beasts in the XML menagerie.  The XML community has also matured greatly, and as one example, there are many new, high-quality information and news sites, some of which I list in Resources section.  If you are highly interested in XML, I highly recommend regular visits to xmlhack, in particular.
</para>

</sect1>

<sect1>
<title>The Triumph of Open Standards</title>

<para>
The most amazing thing about XML's incredible rise, in my opinion sharper than that of the PC, Java, or even the Web, is the fact that it has remained as open as when it started.  Even though XML in its early days was positioned as a tool for encouraging data interchange by providing both human and machine readibility, odds always were that a powerful company, or group of companies would foul the waters.  Many vertical industries such as the automobile inustry (which recently surprised analysts by announcing a huge, XML-driven on-line exchange), health-care and chemicals have been moving to XML as data-exchange format.  If the likes of Microsoft (early and on-going XML champion) and Oracle, could co-opt standards for XML processing, they could gain even more domination than they currently had in such industries, all under the guise of openness.  The perfect monopolistic trojan horse.
</para>

<para>
And this was never just an idle menace.  Last year, Microsoft nearly suceeded in derailing XSLT by bundling a mutation of XSLT into its Internet Explorer 5 browser which was different from the emerging standards, and laden with Microsoft extensions.  Many Linux advocates cried loudly over Microsoft's "embrace-extend-extinguish" move on Kerberos, but this was a weak jab compared to the MS-XSL ploy.  Since Internet Explorer is by far the most popular browser, Microsoft ensured that most of the world's experience of XSLT came through their own proprietary version, and nearly made this proprietary version the de-facto standard.  There was many a flame-war on the xsl-list mailing list (see Resources) when IE users arrived in droves asking questions about what they perceived to be proper XSLT.
</para>

<para>
But then something surprising happened.  Microsoft started to hear loudly and clearly from its customers that they didn't want an MS flavor of XSLT.  They wanted the standard.  The first signs of this were that Microsoft slowly started migrating to the standard in Internet Explorer updates.  Then MS developers announced publicly that their design goal was now full compliance with the XSLT standard.  Finally, after some prodding on xsl-list, several of Microsoft's developers admitted that they had been receiving numerous e-mail messages asking them to get in line.
</para>

<para>
Now I know Linux users aren't used to expecting such sophistication and independent thought from large numbers of MS users, and I'm no exception to that (possibly bigoted) attitude.  I credit this remarkable episode to the power of the promise of openness in XML.  Of course, this doesn't prevent Microsoft from amusing gaffes such as claiming to have invented XML (as reported by The Washington Post in May), but such things are far less dangerous than standards pollution..
</para>

<para>
Similar stories are repeated over and over throughout XML's brief history.  In fact, Microsoft, not having learned all its lessons from the XSLT fiasco, is currently being bludgeoned into abandoning its proprietary XML schema format, XML-Data, in favor of XML Schemas, which has come almost all the way through the W3C standards track.  The battle hit fever pitch with Microsoft's loud announcement of BizTalk, an ambitious repository and toolkit for XML schemas.  But day by day, it looks more as if the open standard will win out.
</para>

<para>
But enough about the wide, wild world.  Let's have a look at what's happening at home.  Another striking change from my first XML article in these Web pages is that I pretty much had to apologize for the lack of XML tools for Linux.  This problem has been corrected to an astonishing degree.
</para>

<para>
This article briefly introduces a selection of XML tools for Linux in a few basic categories: parsers, web servers, application servers, GUIs and bare-bones tools.  Most users' introduction to XML will be for purposes of better managing Web pages, from which they may choose to migrate to complete, all-inclusive appication servers or construct custom systems from the various XML toolkits available and the usual UNIX duct tape and wire ties.  In all cases there is usually some content to manage, and though you may see no reason to leave the world of Emacs or vi to churn out documents, since content-managers are often non-technical, it's a very good thing that there is a good selection of GUI XML editors for all tastes.
</para>

</sect1>

<sect1>
<title>Just the Parsers, Ma'am</title>

<para>
XML processing starts with the parser, and Linux has many to choose from.  Basically all you have to do is pick a language.  C, C++, Java, Python, PHP, Perl, TCL, or even Javascript (and this is hardly an exhaustive list).  The next thing to choose is whether and how to validate your XML documents.  Validation is the process of ensuring that all the elements and attributes in an XML document conform to a schema.  The traditional XML validation method is the Document-Type Definition (DTD).  The W3C, as I mentioned, has almost completed XML Schemas, which have the advantages of XML format (DTDs are in a different format) and "modern" data-typing, with the disadvantage of complexity and immaturity.
</para>

<para>
C users are well served by the old standby from James Clark, Expat, which is a barebones parser and arguably the fastest in existence, but provides no validation.  Significantly, almost every language under the sun, from Python to Eiffel, provides a front-end to Expat.  But even Expat is facing some tough "coopetition" from entries such as the capable libxml project, led by Daniel Viellard of the W3C.  This library, most prominently used in GNOME, offers many options for fine-tuning parsing, and supports DTD validation.  There is also Richard Tobin's RXP, which supports DTD.  C++ users have Xerces-C++, which is based on XML4C code IBM donated to the Apache/XML project.  Xerces-C++ supports both DTD and Schemas.  In fact, if you want to start using XML Schemas in Linux, Xerces is probably your best bet.  Individual efforts include Michael Fink's xmlpp, which is quite new and doesn't support validation.
</para>

<para>
There is a Java version of Xerces with similar pedigree.  Java users are pretty much drowned in choice.  The media has made much of the "marriage" between Java and XML, but the most likely explanation for the huge number of XML tools for Java is that XML emerged right as Java was cresting as a programming language.  Besides Xerces-J, there are Java parsers from Oracle, Sun, DataChannel, and others.  Individual efforts include Thomas Weidenfeller's XMLtp (Tiny XML Parser), which is designed for embedding into other Java apps (as was the pioneering but now moribund Aelfred from Microstar).  Mr. Weidenfeller also provides one of the neatest summaries of OSS license I've seen: "Do what you like with the software, but don't sue me".  Then there is The Wilson Partnership's MinML, designed to be even smaller, for use in embedded systems.
</para>

<para>
Python still has the growing and evolving PyXML package as well as my own company's 4Suite.  XML considerations are helping shape many grand trends of Python such as unicode support and improved memory-management.  The perl community has definitely taken to XML.  The main parser is, appropriately, XML::Parser, but you can pretty much take any XML buzzword, prepend "XML::", and find a corresponding perl package.
</para>

</sect1>

<sect1>
<title>Serving up XML Pages</title>

<para>
XML's early promise to the media was as a way to tame the Web.  Structured documents, separation of content from presentation, and more manageable searching and autonomous Web agents.  Some of this has been drowned out by all the recent interest in XML for database integration and message-based middleware, but XML is still an excellent way to manage structured content on the Web.  And Linux is a pretty good operating system on which to host the content. 
</para>

<para>
The big dog among the XML Web servers is also the well known big dog of Web servers, period.  Apache is absolutely swarming with XML activity lately.  I've already mentioned Xerces, the XML parser from the Apache/XML project.  There is also an XSLT processor, Xalan, with roots in IBM/Lotus's LotusXSL.  There is also Formatting-Object Processor (FOP), a tool for converting XML documents to the popular PDF document, by way of XSL formatting objects, a special XML vocabulary for presentation.  Apache has added support for the Simple Object Access Protocol (SOAP), an XML messaging protocol that can be used to make HTTP-based queries to a server in an XML format.  As a side note, SOAP, and open protocol, is heavily contributed to and championed by Microsoft, in one of the many positive contributions that company has made to XML while not trying to embrace and extend.
</para>

<para>
These bits and pieces are combined into an Apache-based XML Web publishing solution called Cocoon.  Cocoon allows XML documents to be developed, and then published on the Web, for wireless applications through Wireless Application Protocol (WAP), and to print-ready PDF format through FOP.
</para>

<para>
Perl hackers already have the proliferation of "XML::*" packages I've already mentioned, but Matt Sergeant has also put together a comprehensive toolkit for XML processing: Axkit.  Axkit is specialized for use with Apache and mod_perl, and provides XSLT transformation as well as other non-standard transform approaches such as "XPathScript".
</para>

</sect1>

<sect1>
<title>Full-blown application servers</title>

<para>
Enterprises that want an end-to-end solution for developing and deploying applications using XML data have several options under Linux.  Application servers build on basic Web servers such as described above by adding database integration, version control, distributed transactions and other such facilities.
</para>

<para>
The grey and respectable Hewelett Packard found an open-source, Web-hip side with its e-speak project, a tool for distributed XML applications with Java, Python and C APIs for development and extension.
</para>

<para>
A smaller company that has found the advantages of open-source for promoting its XML services is Lutris, Inc., developers of Enhydra.  Enhydra, about which I've reported in a previous LinuxWorld article, is a Java application server for XML processing.  It has some neat innovations such as XMLC, a way to "compile" XML into an intermediate binary form for efficient processing.  It is also one of the first open-source implementations of Java 2's Enterprise Edition services, including Enterprise JavaBeans.
</para>

<para>
XML Blaster is a messaging-oriented middleware (MOM) suite for XML applications.  It uses an XML transport in a publish/subscribe system for exchanging text and binary data.  It uses CORBA for network and inter-process communication and supports components written in Java, Perl, Python and TCL.
</para>

<para>
Conglomerate, developed by Styx, is a somewhat less ambitious but interesting project for an XML application server more attuned for document management.  It includes a nifty GUI editor and provides a proprietary transformation language that can generate HTML, TeX and other formats.
</para>

</sect1>

<sect1>
<title>Oo-wee!  GUI!</title>

<para>
One area in which I lamented Linux's lag in XML tools last year was in the area of GUI browsers and editors.  While I personally use a 4XSLT script and XEmacs for these respective tasks, I frequently work with clients who want to use more friendly GUIs for XML editing and ask whether my preferred Linux platform has anything available.  Fortunately, there are more choices than ever on our favorite OS.  Again much of the succour comes in the form of Java's cross-platform GUI support.
</para>

<para>
GEXml is a Java XML editor which allows programmers use pluggable Java modules for editing their own special tag sets.  It uses a pretty standard layout for XML editors: a multi-pane window with a section for the tree-view, and sections for attributes and a section for CDATA.
</para>

<para>
Merlot, by Channelpoint, Inc., is another Java-based XML editor that emphasizes modeling XML documents around their DTDs, abstracting the actual XML file from the user.  It supports pluggable extension modules for custom DTDs.
</para>

<para>
Lunatech's Morphon is yet another DTD-based XML editor and modeling tool.  Hopefully all these DTD-based tools will expand to accommodate XML schemas and other validation methods as well in order to make life easier for those of us who use XML namespaces.  Morphon is similar to the other editors described here with a couple of nice twists: it allows you to specify cascading stylesheets for the editor appearance and document preview, and it mixes the ubiquitous tree view with a friendly view of the XML document being edited.  Morphon, however, is not open-source, though available for Linux.
</para>

<para>
IBM's Alphaworks keeps on churning out free (beer) XML tools, one of which, XML Viewer, allows users to view XML documents using (once again) the tree-view and specialized panes for element and attribute data.  XML Viewer is written in Java.  It also allows linking the XML source and DTD to allow viewing such items as element and attribute definitions.  There is also XSL Editor, a specialized java-based XML editor for XSLT stylesheets.  It also incorporates advanced features such as syntax highlighting and an XSLT debugger.
</para>

<para>
TreeNotes is an XML text editor that uses a series of widgets to open up XML's tree structure, elements and attributes, and of course character data, to editing.
</para>

<para>
DocZilla is an interesting project: an extension of the Mozilla project for Web-based XML document applications.  It promises XML browsing support on par with Internet Explorer's including an extension and plug-in framework.  DocZilla started out very strongly, but now seems to have lagged a bit.  Part of the reason might be that Mozilla is increasing its XML focus.  Mozilla has always supported XML+Cascading Style-Sheets (CSS), but now, with Transformiix (an XSLT processor for Mozilla) and other such projects, it is making its own bid to replace Explorer as king of XML browsers.
</para>

<para>
There is also KXMLViewer, a KDE XML viewer written in Python, but I'll cover this in more detail when I discuss GNOME and KDE XML support in a coming article in this series.
</para>

</sect1>

<sect1>
<title>In the Hacker Spirit</title>

<para>
So we've looked at lumbering app servers and pretty GUI tools.  All very nice for easing into XML, but we all know that Linux (and UNIX) users typically prefer sterner stuff.  Small, manageable, versatile, no-nonsense packages that can be strung together to get a larger job done.  Luckily for the desperate hacker, the nuts-and-bolts toolkit is growing just as quickly as the rest of XML space.
</para>

<para>
A key and quite mature entry is LT XML, developed by the Edinburgh Language Technology Group.  LT XML is a set of stand-along tools and libraries for C programmers using XML.  It supports both tree-based and stream-oriented processing, covering a wide variety of application types.  The LT XML repertoire would be quite familiar and pleasant to those who love nothing more than to string together GNU textutils to produce some neat text transformation.  There is the mandatory XML-aware grep, sggrep (the "sg" for SGML), as well as sgsort, sgcount, sgtoken, etc, which should be self-explanatory.  Python bindings for LT XML should be available by the time you read this.
</para>

<para>
Speaking of grep, there is also fxgrep, a powerful XML querying tool written in Standard ML, a well-regarded functional programming language from Bell Labs (XML provides a rather fitting problem space for functional languages).  fxgrep uses the XML parser fxp, also written in SML.  fxgrep supports specialized XML searching and query using its own pattern syntax.
</para>

<para>
Paul Tchistopolskii makes clear there is no mistake as to his target user-base for Ux: "Ux is UNIX, revisited with XML".  Ux is a set of small XML components written in Java (OK, we're leaking some UNIX heritage right there).  The components are designed to be piped together for database storage and extraction, XSLT transformation, query, etc.
</para>

<para>
Pyxie is an XML parsing and processing toolkit in Python by Sean McGrath and highlighted in his book, <emph>XML Processing with Python</emph>.  Pyxie's main distiction is that it builds on earlier work by James Clark by focusing on a line-based view of XML rather than the "natural" tokens that emerge from the spec.  This can provide a useful optimization if occasional complications.
</para>

<para>
For those looking askance at XML in a TeX environment, IBM's Alphaworks might have a useful introduction.  TeXML is a tool that allows you to define an XSLT transform for converting XML files to a specialized vocabulary, the results of which are converted to TeX.  Also, thanks to Alphaworks, there is an XML diff as well as a grep.  XML Tree Diff shows the differences between documents based on their DOM tree representation.  It's more of a collection of Javabeans for performing diffs than a stand-alone application, but it's relatively straightforward to use.
</para>

<para>
And there is my own company's 4Suite, a set of libraries for Python users to construct their own XML applications using DOM, XPath and XSLT, among other tools.  I covered 4XSLT in my last XML article (though the spec and 4XSLT have changed since then), and 4Suite libraries are now standard components in the Python XML distribution.
</para>

</sect1>

<sect1>
<title>Conclusion</title>

<para>
Hopefully this tour will help find XML resources for Linux users of all levels.  In upcoming articles (hopefully not as delayed as this one), I shall cover XML and Databases, XML and KDE/GNOME, and mnore topics on how to put XML to work in a Linux environment.
</para>

<para>
By the way this very article is available in XML form (using the DocBook standard).  I've also put up a simplified DocBook XSLT stylesheet that can be used to render this article to HTML (see Resources for both).  Note that I use the "doc" file extension for DocBook files.  I encourage you to use DocBook (O'Reilly and Associates publishes an excellent book on the topic by Norman Walsh) and the ".doc" extension, chopping at the hegemony of the proprietary Microsoft Word format.  Just another small way XML can open up data to the world.
</para>

</sect1>

<sect1>
<title>Resources</title>

<sect2>
<title>Parsers</title>

<glosslist>
<glossterm>Expat</glossterm><glossdef>http://www.jclark.com/xml/expat.html</glossdef>
<glossterm>Xerces C++</glossterm><glossdef>http://xml.apache.org/xerces-c/index.html</glossdef>
<glossterm>Xerces-Java</glossterm><glossdef>http://xml.apache.org/xerces-j/index.html</glossdef>
<glossterm>xmlpp</glossterm><glossdef>http://www.vividos.de/xmlpp/</glossdef>
<glossterm>libxml</glossterm><glossdef>http://www.xmlsoft.org/</glossdef>
<glossterm>RXP</glossterm><glossdef>http://www.cogsci.ed.ac.uk/~richard/rxp.html</glossdef>
<glossterm>XMLtp</glossterm><glossdef>http://mitglied.tripod.de/xmltp/</glossdef>
<glossterm>MinML</glossterm><glossdef>http://www.wilson.co.uk/xml/minml.htm</glossdef>
</glosslist>

</sect2>

<sect2>
<title>Web Servers</title>

<glosslist>
<glossterm>Axkit</glossterm><glossdef>http://axkit.org/</glossdef>
<glossterm>XML/Apache</glossterm><glossdef>http://xml.apache.org</glossdef>
</glosslist>

</sect2>

<sect2>
<title>App Servers</title>

<glosslist>
<glossterm>Conglomerate</glossterm><glossdef>http://www.conglomerate.org/</glossdef>
<glossterm>e-speak</glossterm><glossdef>http://www.e-speak.net/</glossdef>
<glossterm>Enhydra</glossterm><glossdef>http://www.enhydra.org/</glossdef>
<glossterm>XML Blaster</glossterm><glossdef>http://www.xmlBlaster.org/</glossdef>
</glosslist>

</sect2>

<sect2>
<title>Low-Level Tools</title>

<glosslist>
<glossterm>LT XML</glossterm><glossdef>http://www.ltg.ed.ac.uk/software/xml/index.html</glossdef>
<glossterm>fxgrep</glossterm><glossdef>http://www.informatik.uni-trier.de/~neumann/Fxgrep/</glossdef>
<glossterm>Ux</glossterm><glossdef>http://www.pault.com/Ux/</glossdef>
<glossterm>Pyxie</glossterm><glossdef>http://www.digitome.com/pyxie.html</glossdef>
</glosslist>

</sect2>

<sect2>
<title>GUIs</title>

<glosslist>
<glossterm>TreeNotes</glossterm><glossdef>http://pikosoft.dragontiger.com/en/treenotes/</glossdef>
<glossterm>DocZilla</glossterm><glossdef>http://www.doczilla.com/</glossdef>
<glossterm>GEXml</glossterm><glossdef>http://gexml.cx/</glossdef>
<glossterm>Merlot</glossterm><glossdef>http://www.merlotxml.org/</glossdef>
<glossterm>Morphon</glossterm><glossdef>http://www.morphon.com/</glossdef>
</glosslist>

</sect2>

<sect2>
<title>Et Cetera</title>

<glosslist>
<glossterm>There is more to XML than roll-your-own HTML</glossterm><glossdef>http://www.linuxworld.com/linuxworld/lw-1999-03/lw-03-xml.html</glossdef>
<glossterm>Practical XML with Linux, Part 1</glossterm><glossdef>http://www.linuxworld.com/linuxworld/lw-1999-09/lw-09-xml2.html</glossdef>
<glossterm>The xsl-list mailing list</glossterm><glossdef>http://www.mulberrytech.com/xsl/xsl-list</glossdef>
<glossterm>DocBook and stylesheet for this article</glossterm><glossdef>http://www.Fourthought.com/Publications/lw-xml2</glossdef>
<glossterm>The Apache/XML Project</glossterm><glossdef>http://xml.apache.org/</glossdef>
<glossterm>SOAP</glossterm><glossdef>http://www.w3.org/TR/SOAP/</glossdef>
<glossterm>xmlhack</glossterm><glossdef>http://www.xmlhack.com</glossdef>
<glossterm>XML Pit Stop</glossterm><glossdef>http://www.xmlpitstop.com/</glossdef>
<glossterm>xslt.com</glossterm><glossdef>http://www.xslt.com</glossdef>
<glossterm>XML Times</glossterm><glossdef>http://www.xmltimes.com/</glossdef>
<glossterm>The XML Cover Pages</glossterm><glossdef>http://www.oasis-open.org/cover</glossdef>
<glossterm>IBM's Alphaworks (including XML Viewer, XSL Edirot, XML Tree Diff and TeXML)</glossterm><glossdef>http://alphaworks.ibm.com</glossdef>
</glosslist>

</sect2>

</sect1>

</article>
"""


source_2 = """<article xmlns="http://docbook.org/docbook/xml/4.0/namespace">
<artheader>
<title>The Schematron: A Fresh Approach Towards XML Validation and Reporting</title><author>Uche Ogbuji</author>
</artheader>

<sect1>

<para>
XML is certainly an emerging and quick-changing technology.  One of the knocks against it has been the churn of standards and methodologies.  Certainly there is no greater evidence that XML is in flux than the fact that there is so much development and debate about how to validate XML documents, given that validation is one of the cornerstones of XML.
</para>

<para>
This article introduces The Schematron, one of the currently available validation methodologies.  It will assume familiarity with XML, XML DTDs, and some familiarity with XPath and XSLT transforms.  For those who might need some grounding on one or more of those areas I've added some helpful links in the Resources section.
</para>

</sect1>

<sect1>
<title>A Bit of Background</title>

<para>
Although, as I pointed out in my last XML article on SunWorld (see Resources), XML doesn't introduce any notable innovation in data-processing, it has, through its popularity, introduced many useful disciplines inherited from SGML.  Perhaps the core discipline in this regard is in native support for validation.  One of XML's early promises in terms of easing information-management woes involved it's support for bundling the data schema with the data, and by providing for some standard schema discovery in cases where this bundling was not done.  Of course, the real-world has proven that this facility, while useful, is no panacea.  Even if one can a schema for machine-interpretation of a data set, how does one determine the semantics associated with that schema.  A further problem was the particular schema methodology that XML ended up being bundled with: Document-Type Definition (DTD).
</para>

<para>
DTDs are an odd mix of very generic and very specific expression.  For instance, simple tasks such as specifying that an element can have a number of particular child elements within a given range can be very cumbersome using DTDs.  Yet they are generic enough to allow such elegant design patterns as architectural forms (see Resources).  The expressive shortcomings of DTDs, along with arguments that XML validation should not require a separate computer language (DTDs of course differ in syntax from XML instances), encouraged the W3C, XML's major standards body, to develop a new schema language for XML, using XML syntax.  The resulting XML Schema specification is currently in "Candidate Recommendation" phase and presumably will soon hit version 1.0 (although based on experience with the DOM spec one should hardly rely on this).
</para>

<para>
One of the key XML developments since XML 1.0 that has affected the schema story is XML Namespaces 1.0.  This recommendation provides a mechanism for disambiguating XML names, but does so in a way that is rather unfriendly to DTD users.  There are tricks for using namespaces with DTDs, but they are quite arcane.  Of course it must be noted that many of the SGML old school have argued that namespaces are a rather brittle solution, and furthermore they solve a rather narrow problem to justify such disruption in XML technologies.  The reality, however, is that with XML-related standards from XSLT to XLink relying heavily on namespaces, we shall have to develop solutions to the core problems that take namespaces into account.
</para>

<para>
But back to validation.  The W3C Schema specification has been a long time in development, and along the way there began to be rumblings about the complexity of the emerging model.  XML Schemas did fill a very ambitious charter: covering document structure, data-typing worthy of databases, and even abstract data-modeling such as subclassing.
</para>

<para>
And so because of the gap between the emergence of namespaces and the completion of XML Schemas, and because of fears that the coming specification was far too complex, the XML community, one with a remarkable history of practical problem-solving, went to work.
</para>

<para>
One of the developments was Murata Makoto's Regular Language description for XML (RELAX) (see Resources).  Relax provides a system for developing grammars to describe XML documents.  It uses XML-like syntax and ofers similar featues to DTDs, adding some of the facilities offered by XML Schemas, such as schema annotation (basically, built-in documentation) and data-typing (for example specifying that an attribute value be an integer), and coming up with some exotic additions of its own such as "hedge grammars".  RELAX supports namespaces and provides a clean and inherently modular approach to validation and so has become rather popular, with its own mailing lists and contributed tools such as a DTD to RELAX translator (see Resources).
</para>

</sect1>

<sect1>
<title>A Different Approach: Harnessing the Power of XPath</title>

<para>
In the mean time XSLT emerged as a W3C standard, and immediately established itself as one of their most successful XML-related products.  Most people are familiar with XSLT as a tool to display XML content on "legacy" HTML-only browsers, but there is so much more to XSLT, largely because XPath, which it uses to express patterns in the XML source, is such a well-conceived tool.
</para>

<para>
In fact, since XPath is such a comprehensive system for indicating and selecting from patterns in XML, there is no reason it could not express similar structural concepts as does DTD.  Take the following DTD, listing 1.
</para>

<screen>
<![CDATA[
<!ELEMENT ADDRBOOK (ENTRY*)>
<!ELEMENT ENTRY (NAME, ADDRESS, PHONENUM+, EMAIL)>
<!ATTLIST ENTRY
    ID ID #REQUIRED
>
<!ELEMENT NAME (#PCDATA)>
<!ELEMENT ADDRESS (#PCDATA)>
<!ELEMENT PHONENUM (#PCDATA)>
<!ATTLIST PHONENUM
    DESC CDATA #REQUIRED
>
<!ELEMENT EMAIL (#PCDATA)>
]]>
</screen>

<para>
A sample document valid against this DTD is as follows, listing 2.
</para>

<screen>
<![CDATA[
<?xml version = "1.0"?>
<!DOCTYPE ADDRBOOK SYSTEM "addr_book.dtd">
<ADDRBOOK>
        <ENTRY ID="pa">
                <NAME>Pieter Aaron</NAME>
                <ADDRESS>404 Error Way</ADDRESS>
                <PHONENUM DESC="Work">404-555-1234</PHONENUM>
                <PHONENUM DESC="Fax">404-555-4321</PHONENUM>
                <PHONENUM DESC="Pager">404-555-5555</PHONENUM>
                <EMAIL>pieter.aaron@inter.net</EMAIL>
        </ENTRY>
        <ENTRY ID="en">
                <NAME>Emeka Ndubuisi</NAME>
                <ADDRESS>42 Spam Blvd</ADDRESS>
                <PHONENUM DESC="Work">767-555-7676</PHONENUM>
                <PHONENUM DESC="Fax">767-555-7642</PHONENUM>
                <PHONENUM DESC="Pager">800-SKY-PAGEx767676</PHONENUM>
                <EMAIL>endubuisi@spamtron.com</EMAIL>
        </ENTRY>
</ADDRBOOK>
]]>
</screen>

<para>
Examine the declaration of the ADDRBOOK element.  It basically says that such elements must have at least four child elements, a NAME, an ADDRESS, one or more PHONENUM and an EMAIL.  This can be expressed in XPath with a combination of the following three boolean expressions (using the ADDRBOOK element as the context):
</para>

<screen>
1. count(NAME) = 1 and count(ADDRESS) = 1 and count(EMAIL) = 1
2. NAME[following-sibling::ADDRESS] and ADDRESS[following-sibling::PHONENUM] and PHONENUM[following-sibling::EMAIL]
3. count(NAME|ADDRESS|PHONENUM|EMAIL) = count(*)
</screen>

<para>
The first is true if and only if (iff) there is exactly one each of NAME, ADDRESS, and EMAIL.  This establishes the occurrence rule for these children.  The second is true iff there is a NAME followed by an ADDRESS, an ADDRESS followed by a PHONENUM and a PHONENUM followed by an EMAIL.  This establishes the sequence rule for the children.  Note that the preceding-sibling axis could have been used just as well.  The third expression is true iff there are no other elements besides the NAME ADDRESS PHONENUM EMAIL.  This establishes the (implied) DTD rule that elements are not permitted except where specified in the content model by name or with the ANY symbol.
</para>

<para>
You first reaction might be that the XPath expressions are so much more verbose than the equivalent DTD specification.  This is so in this case, though one can easily come up with situations where the DTD equivalent would be more verbose than the equivalent XPath expressions.  However, this is entirely beside the point.  The DTD version is more concise because it is carefully designed to model such occurrence and sequence patterns.  XPath has far more general purpose and we are actually building the DTD equivalent through a series of primitives each of which operate at a more granular conceptual level than the DTD equivalent.  So it may be more wordy, but it has far greater expressive power.  Let's say we wanted to specify that there can be multiple ADDRESS and EMAIL children, but that they must be of the same number.  This task, which seems a simple enough extension of the previous content-midel, is pretty much beyond the abilities of DTD.  Not so XPath.  Since XPath gives a primitive but complete model of the document, it's an easy enough addition.
</para>

<screen>
1. count(NAME) = 1 and count(ADDRESS) = count(EMAIL)
2. NAME[following-sibling::ADDRESS] and ADDRESS[following-sibling::PHONENUM] and PHONENUM[following-sibling::EMAIL]
3. count(NAME|ADDRESS|PHONENUM|EMAIL) = count(*)
</screen>

<para>
The only change is in expression 1, and should be self-explanatory.  This small foray beyond the scope of DTD illustrates the additional power offered by XPath.  Of course XPath can handle the attribute declarations as well.  For example, the attribute declaration for PHONENUM in the DTD can be expressed as follows (again using the ADDRBOOK element as context):
</para>

<screen>
PHONENUM/@DESC
</screen>

<para>
All these XPath expressions are very well in the abstract, but how would one actually use them for validation?  The most convenient way is to write an XSLT transform that uses them to determine validity.  Here's an example, listing 3, which represents a sub-set of the address book DTD.
</para>

<screen>
<![CDATA[
<?xml version="1.0"?>
<xsl:transform xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">

  <xsl:template match="/">
    <xsl:if test='not(ADDRBOOK)'>
      Validation error: there must be an ADDRBOOK element at the root of the document.
    </xsl:if>
    <xsl:apply-templates select='*'/>
  </xsl:template>

  <xsl:template match="ENTRY">
    <xsl:if test='not(count(NAME) = 1)'>
      Validation error: ENTRY element missing a NAME child.
    </xsl:if>
    <xsl:if test='not(count(ADDRESS) = 1)'>
      Validation error: ENTRY element missing an ADDRESS child.
    </xsl:if>
    <xsl:if test='not(count(EMAIL) = 1)'>
      Validation error: ENTRY element missing an EMAIL child.
    </xsl:if>
    <xsl:if test='not(NAME[following-sibling::ADDRESS] and ADDRESS[following-sibling::PHONENUM] and PHONENUM[following-sibling::EMAIL])'>
      Validation error: ENTRY must have a NAME, ADDRESS, one or more PHONENUM, and an EMAIL in sequence
    </xsl:if>
    <xsl:if test='not(count(NAME|ADDRESS|PHONENUM|EMAIL) = count(*))'>
      Validation error: there is an extraneous element child of ENTRY
    </xsl:if>
    <xsl:apply-templates select='*'/>
  </xsl:template>

  <xsl:template match="PHONENUM">
    <xsl:if test='not(@DESC)'>
      Validation error: PHONENUM must have a DESC attribute
    </xsl:if>
    <xsl:apply-templates select='*'/>
  </xsl:template>

  <xsl:template match="*">
    <xsl:apply-templates select='*'/>
  </xsl:template>

</xsl:transform>
]]>
</screen>

<para>
When run with a valid document, such as the example above, this stylesheet would produce no output.  When run, however, with an invalid document such as the following, listing 4, however, it's a different story.
</para>

<screen>
<![CDATA[
<?xml version = "1.0"?>
<ADDRBOOK>
        <ENTRY ID="pa">
                <NAME>Pieter Aaron</NAME>
                <PHONENUM DESC="Work">404-555-1234</PHONENUM>
                <PHONENUM DESC="Fax">404-555-4321</PHONENUM>
                <PHONENUM DESC="Pager">404-555-5555</PHONENUM>
                <EMAIL>pieter.aaron@inter.net</EMAIL>
        </ENTRY>
        <ENTRY ID="en">
                <NAME>Emeka Ndubuisi</NAME>
                <PHONENUM DESC="Work">767-555-7676</PHONENUM>
                <PHONENUM DESC="Fax">767-555-7642</PHONENUM>
                <PHONENUM DESC="Pager">800-SKY-PAGEx767676</PHONENUM>
                <EMAIL>endubuisi@spamtron.com</EMAIL>
                <ADDRESS>42 Spam Blvd</ADDRESS>
                <SPAM>Make money fast</SPAM>
        </ENTRY>
        <EXTRA/>
</ADDRBOOK>
]]>
</screen>

<para>
Note that all the XPath expressions we came up with are placed in if statements and negated.  This is because they represent conditions such that we want a message put out if they are <emph>not</emph> met.  Running this source against the validation transform using an XSLT processor results in the following output:
</para>

<screen>

      Validation error: ENTRY element missing an ADDRESS child.
    
      Validation error: ENTRY must have a NAME, ADDRESS, one or more PHONENUM, and an EMAIL in sequence
    
      Validation error: ENTRY must have a NAME, ADDRESS, one or more PHONENUM, and an EMAIL in sequence
    
      Validation error: there must be an ENTRY element at the root of the document.
    

</screen>

<para>
And so we have our validation result.  Note that it's pretty much a report of the document, such as we set it up to be.  One nice thing about this is that you can see all the validation errors at once.  Using most XML parsers you only get one error at a time.  But the real power of this XSLT-based validation report is that it's just that: a report.  We happened to use it for DTD-based XML validation, but it's not hard to see how this could be extended to more sophisticated data-management needs.  For instance, suppose we wanted to examine address-book documents for e-mail addresses in the .gov domain.  This is pretty much entirely beyond the realm of validation, but it is an example, as database programmers will immediately recognize, of reporting.
</para>

<para>
While it might be argued one way or another whether validation and reporting are cut from the same conceptual cloth, it is pretty clear that in practice, XML document validation can be treated as a subset of XML document reporting, and furthermore that XPath and XSLT provide a powerful toolkit for document validation.
</para>

</sect1>

<sect1>
<title>Introducing the Schematron</title>

<para>
This re-casting of validation as a reporting problem is a core insight of the Schematron (see Resources).  The Schematron is a validation and reporting methodology and toolkit developed by Rick Jeliffe who, interestingly enough, is a member of the W3C Schema working group.  Without denigrating the efforts of his group, Mr. Jeliffe has pointed out that XML Schemas may be too complex for many users, and approaches validation from the same old approach as DTD.  He developed the Schematron as a simple tool to harness the power of XPath, attacking the schema problem from a new angle.  As he put it on his site, "The Schematron differs in basic concept from other schema languages in that it not based on grammars but on finding tree patterns in the parsed document. This approach allows many kinds of structures to be represented which are inconvenient and difficult in grammar-based schema languages."
</para>

<para>
The Schematron is really no more than an XML vocabulary that can be used as an instruction set for generating stylesheets such as the one presented above.  For instance, the following, listing 5, is how our XPath-based validation might look like in The Schematron.
</para>

<screen>
<![CDATA[
<schema xmlns='http://www.ascc.net/xml/schematron'>
        <pattern name="Structural Validation">
                <!-- Use a hack to set the root context.  Necessary because of
                     a bug in the schematron 1.3 meta-transforms. -->
                <rule context="/*">
                        <assert test="../addr:ADDRBOOK">Validation error: there must be an ADDRBOOK element at the root of the document.</assert>
                </rule>
                <rule context="ENTRY">
                        <assert test="count(NAME) = 1">Validation error: <name/> element missing a NAME child.</assert>
                        <assert test="count(ADDRESS) = 1">Validation error: <name/> element missing an ADDRESS child.</assert>
                        <assert test="count(EMAIL) = 1">Validation error: <name/> element missing an EMAIL child.</assert>
                        <assert test="NAME[following-sibling::ADDRESS] and ADDRESS[following-sibling::PHONENUM] and PHONENUM[following-sibling::EMAIL]">Validation error: <name/> must have a NAME, ADDRESS, one or more PHONENUM, and an EMAIL in sequence</assert>
                        <assert test="count(NAME|ADDRESS|PHONENUM|EMAIL) = count(*)">Validation error: there is an extraneous element child of ENTRY</assert>
                </rule>
                <rule context="PHONENUM">
                        <assert test="@DESC">Validation error: <name/> must have a DESC attribute</assert>
                </rule>
        </pattern>
</schema>
]]>
</screen>

<para>
The root element in schematron is the schema element in the appropriate namespace.  It contains one or more patterns, each of which represents a conceptual grouping of declarations.  Patterns contain one or more rules, each of which sets a context for a series of declarations.  This is not only a conceptual context, but also the context that is used for the XPath expressions in declarations within each rule.
</para>

<para>
Each rule contains a collection of asserts, reports and keys.  You can see asserts at work in our example.  Asserts are similar to asserts in C.  They represent a declaration that a condition is true, and if it is not true, a signal is made to such effect.  In the Schematron, assert elements specify that if the condition in their test attribute is not true, the content of the assert elements will be copied to the result.  You'll note that the assert messages contain empty <screen>name</screen> elements.  This is a convenient short-hand for the name of the current context node, given by the parent rule element.  This makes it easy to reuse asserts from context to context.  Reports are similar to asserts, except that they output their contents when the condition in their test attribute is true rather than false.  They also allow the use of the empty name element.  Reports, as their name implies, tend to make sense for structural reporting tasks.  For instance, to implement our eariler example of reporting e-mail addresses in the .gov domain we might add the following rule to our Schematron:
</para>

<screen>
<![CDATA[
                <rule context="EMAIL">
                        <report test="contains(., '.gov') and not(substring-after(., '.gov'))">This address book contains government contacts.</report>
                </rule>
]]>
</screen>

<para>
Of course I already mentioned that namespaces are an important reason to seek a different validation methodology than DTDs.  Schematron supports namespaces through XPath's support for namespaces.  For instance, if we wanted to validate that all child elements of ENTRY in our address book document were in a particular namespace, we could do so so by adding an assert which checks the count of elements in a particular namespace.  Assume that the prefix "addr" is bound to the target namespace in the following example:
</para>

<screen>
count(addr:*) = count(*)
</screen>

<para>
Maybe that's too draconian for your practical needs and you want to also allow elements in a particular namespace reserved for extansions.
</para>

<screen>
count(addr:*) + count(ext:*) = count(*)
</screen>

<para>
Maybe rather than permitting a single particular extension namespace, you want to instead allow any elements with namespaces whose URI contains the string "extension":
</para>

<screen>
count(addr:*) + count(*[contains(namespace(.), 'extension')]) = count(*)
</screen>

<para>
With this latter addition and the addition of a report for e-mail addresses in the .gov address our schematron looks as follows, listing 6.
</para>

<screen>
<![CDATA[
<schema xmlns='http://www.ascc.net/xml/schematron'>

        <ns prefix='addr' uri='http://addressbookns.com'/>

        <pattern name="Structural Validation">
                <!-- Use a hack to set the root context.  Necessary because of
                     a bug in the schematron 1.3 meta-transforms. -->
                <rule context="/*">
                        <assert test="../addr:ADDRBOOK">Validation error: there must be an ADDRBOOK element at the root of the document.</assert>
                </rule>
                <rule context="addr:ENTRY">
                        <assert test="count(addr:*) + count(*[contains(namespace-uri(.), 'extension')]) = count(*)">
Validation error: all children of <name/> must either be in the namespace 'http://addressbookns.com' or in a namespace containing the substring 'extension'.
                        </assert>
                        <assert test="count(addr:NAME) = 1">
Validation error: <name/> element missing a NAME child.
                        </assert>
                        <assert test="count(addr:ADDRESS) = 1">
Validation error: <name/> element missing an ADDRESS child.
                        </assert>
                        <assert test="count(addr:EMAIL) = 1">
Validation error: <name/> element missing an EMAIL child.
                        </assert>
                        <assert test="addr:NAME[following-sibling::addr:ADDRESS] and addr:ADDRESS[following-sibling::addr:PHONENUM] and addr:PHONENUM[following-sibling::addr:EMAIL]">
Validation error: <name/> must have a NAME, ADDRESS, one or more PHONENUM, and an EMAIL in sequence
                        </assert>
                        <assert test="count(addr:NAME|addr:ADDRESS|addr:PHONENUM|addr:EMAIL) = count(*)">
Validation error: there is an extraneous element child of ENTRY
                        </assert>
                </rule>
                <rule context="addr:PHONENUM">
                        <assert test="@DESC">
Validation error: <name/> must have a DESC attribute
                        </assert>
                </rule>
        </pattern>
        <pattern name="Government Contact Report">
                <rule context="addr:EMAIL">
                        <report test="contains(., '.gov') and not(substring-after(., '.gov'))">
This address book contains government contacts.
                        </report>
                </rule>
        </pattern>
</schema>
]]>
</screen>

<para>
Note the new top-level element, ns.  We use this to declare the namespace that we'll be incorporating into the schematron rules.  If you have multiple such namespaces to declare, use one ns element for each.  Note that there are some advanced uses of schematron namespace declarations about which you can read on theSchematron site.
</para>

<para>
This was a pretty quick whirl through The Schematron.  This shouldn't be much of a problem since it is so simple.  However, for a bit more instruction, there is the tidy tutorial put together by Dr Miloslav Nic (see Resouces.  Note that the good Doctor has tutorials on many other XML-related topics at his page).  There are also a few examples linked from the Schematron home page.
</para>

</sect1>

<sect1>
<title>Putting The Schematron to Work</title>

<para>
So how do we use The Schematron?  Rememeber that a Schematron document could be thought of as a instructions for generating special validation and report transforms such as we introduced earlier.  This is in fact the most common way of using The Schematron in practice.  Conveniently enough, XSLT has all the power to convert Schematron specifications to XSLT-based validators.  There is a meta-transform available at the Schematron Web site which, when run against a schematron specification, will generate a specialized validator/reporter transform which can be then run against target source documents.  For instance, suppose I have the above schematron specification as "addrbook.schematron".  I can turn it into a validator/reporter transform as follows:
</para>

<screen>
[uogbuji@borgia code]$ 4xslt.py listing6.schematron ~/devel/Ft/Xslt/test_suite/borrowed/schematron-skel-ns.xslt > addrbook.validator.xslt
</screen>

<para>
Here and for all other examples in this article, I am using the 4XSLT processor.  4XSLT (see Resources) is an XSLT 1.0-compliant processor written in Python and distributed as open source by my company, Fourthought, Inc.  I ran the above from Linux and the first argument to 4xslt.py is the XML source document: in this case the schematron specification in listing 6.  The second argument is the transform to be used, in this case the Schematron namespace-aware meta-transform.  I then redirect the standard output to the file addrbook.validator.xslt, which thus becomes my validator/reporter transform.  I can then run the validator transform against the following source document, listing 7.
</para>

<screen>
<![CDATA[
<?xml version = "1.0"?>
<ADDRBOOK xmlns='http://addressbookns.com'>
        <ENTRY ID="pa">
                <NAME xmlns='http://bogus.com'>Pieter Aaron</NAME>
                <ADDRESS>404 Error Way</ADDRESS>
                <PHONENUM DESC="Work">404-555-1234</PHONENUM>
                <PHONENUM DESC="Fax">404-555-4321</PHONENUM>
                <PHONENUM DESC="Pager">404-555-5555</PHONENUM>
                <EMAIL>pieter.aaron@inter.net</EMAIL>
        </ENTRY>
        <ENTRY ID="en">
                <NAME xmlns='http://bogus.com'>Emeka Ndubuisi</NAME>
                <ADDRESS>42 Spam Blvd</ADDRESS>
                <PHONENUM DESC="Work">767-555-7676</PHONENUM>
                <PHONENUM DESC="Fax">767-555-7642</PHONENUM>
                <PHONENUM DESC="Pager">800-SKY-PAGEx767676</PHONENUM>
                <EMAIL>endubuisi@spamtron.com</EMAIL>
        </ENTRY>
</ADDRBOOK>
]]>
</screen>

<para>
Yielding the following output:
</para>

<screen>
[uogbuji@borgia code]$ 4xslt.py listing7.xml addrbook.validator.xslt 
Validation error: all children of ENTRY must either be in the namespace 'http://addressbookns.com' or in a namespace containing the substring 'extension'.Validation error: ENTRY element missing a NAME child.Validation error: ENTRY must have a NAME, ADDRESS, one or more PHONENUM, and an EMAIL in sequenceValidation error: there is an extraneous element child of ENTRYValidation error: all children of ENTRY must either be in the namespace 'http://addressbookns.com' or in a namespace containing the substring 'extension'.Validation error: ENTRY element missing a NAME child.Validation error: ENTRY must have a NAME, ADDRESS, one or more PHONENUM, and an EMAIL in sequenceValidation error: there is an extraneous element child of ENTRY
</screen>

<para>
Hmm.  Rather a mess, what?  Looks as if there were quite a few messages combined without clear separation.  There were actually two sets of messages, one for each ENTRY in the source document, since we caused the same cascade of validation errors in both by messing with the namespace of the NAME element.  The reason the two messages run together so is that we used the skeleton Schematron meta-transform.  The skeleton comes with only basic output support, and in particular, it normalizes space in all output, running the results together.
</para>

<para>
There's a good chance this is not what you want, and luckily Schematron is designed to be quite extensible.  There are several schematron meta-transforms on the Schematron home page that build on the skeleton by importing it.  They range from basic, clearer text messages to HTML for browser-integration.  Using the sch-basic meta-transform rather than the skeleton yields:
</para>

<screen>
[uogbuji@borgia code]$ 4xslt.py listing6.schematron ~/devel/Ft/Xslt/test_suite/borrowed/sch-basic.xslt > addrbook.validator.xslt
[uogbuji@borgia code]$ 4xslt.py listing7.xml addrbook.validator.xslt 
In pattern Structural Validation:
   Validation error: all children of ENTRY must either be in the namespace 'http://addressbookns.com' or in a namespace containing the substring 'extension'.
In pattern Structural Validation:
   Validation error: ENTRY element missing a NAME child.
In pattern Structural Validation:
   Validation error: ENTRY must have a NAME, ADDRESS, one or more PHONENUM, and an EMAIL in sequence
In pattern Structural Validation:
   Validation error: there is an extraneous element child of ENTRY
In pattern Structural Validation:
   Validation error: all children of ENTRY must either be in the namespace 'http://addressbookns.com' or in a namespace containing the substring 'extension'.
In pattern Structural Validation:
   Validation error: ENTRY element missing a NAME child.
In pattern Structural Validation:
   Validation error: ENTRY must have a NAME, ADDRESS, one or more PHONENUM, and an EMAIL in sequence
In pattern Structural Validation:
   Validation error: there is an extraneous element child of ENTRY

</screen>

<para>
To round things up, here is an example, listing 8, of a source document that validates cleanly against our sample schematron.
</para>

<screen>
<![CDATA[
<?xml version = "1.0"?>
<ADDRBOOK xmlns='http://addressbookns.com'>
        <ENTRY ID="pa">
                <NAME>Pieter Aaron</NAME>
                <ADDRESS>404 Error Way</ADDRESS>
                <PHONENUM DESC="Work">404-555-1234</PHONENUM>
                <PHONENUM DESC="Fax">404-555-4321</PHONENUM>
                <PHONENUM DESC="Pager">404-555-5555</PHONENUM>
                <EMAIL>pieter.aaron@inter.net</EMAIL>
        </ENTRY>
        <ENTRY ID="en">
                <NAME>Manfredo Manfredi</NAME>
                <ADDRESS>4414 Palazzo Terrace</ADDRESS>
                <PHONENUM DESC="Work">888-555-7676</PHONENUM>
                <PHONENUM DESC="Fax">888-555-7677</PHONENUM>
                <EMAIL>mpm@scudetto.dom.gov</EMAIL>
        </ENTRY>
</ADDRBOOK>
]]>
</screen>

<para>
Which we test as follows.
</para>

<screen>
[uogbuji@borgia code]$ 4xslt.py listing8.xml addrbook.validator.xslt 
In pattern Government Contact Report:
   This address book contains government contacts.

</screen>

<para>
Now everything is in the correct namespace so we get no validation errors.  However, notice that we did get the report from the e-mail address in the .gov domain.
</para>

<para>
This is all very well, but no doubt you're wondering whether XSLT is fast enought to suit your real-world validation needs.  This will of course depend on your needs.  In my experience, it is very rarely necessary to validate a document every time it is processed.  If you have attributes with default value, or you have no control at all over the sources of your data throughout your processing applications then you may have no choice.  In this case, validation by an XML 1.0-compliant validating parser such as xmlproc (see Resources) is almost certainly faster than XSLT-based Schematron.  But then again, there is no hard requirement that a Schematron processor use XSLT.  It would not be terribly difficult, given an efficient XPath library, to write a specialized Schematron application that doesn't need translation from meta-transforms.
</para>

<para>
But just to give a quick comparison, I parsed a 170K address book example similar to the above but with more entries.  Using xmlproc and DTD validation it took 7.25 seconds.  Parsing this document without validation and then applying the schematron transform took 10.61 seconds.  Hardly so great a penalty.
</para>

<para>
Of course there are several things that DTDs provide that Schematron cannot.  The most notable are entity and notation definitions and fixed or default attribute values.  RELAX does not provide any of these facilities either, but XML Schemas do provide all of them as it must since it is positioned as a DTD replacement.  RELAX makes no such claim and indeed the RELAX documentation has a section on using RELAX in concert with DTD.  We have already discussed that Schematron, far from claiming to be a DTD replacement, is positioned as an entirely fresh approach to validation.  Nevertheless, attribute-value defaulting can be a useful way to reduce the clutter of XML documents for human readability so we shall examine one way to provide default attributes in association with Schematron.
</para>

<para>
Remember that you're always free to combine DTD with Schematron to get the best of both worlds, but if you want to to leave DTD entirely behind, you can still get attribute-defaulting at the cost of one more pass through the document when the values are to be substituted.  This can easily be done by a transform that turns a source document to a result that is identical except that all default attribute values are given.
</para>

<para>
There are other features of Schematron for those interested in further exploration.  For instance it supports keys: a mechanism similar to DTD's ID and IDREF.  There are some hooks for embedding and control through external applications.  Certainly a more formal introduction to Schematron is available in the Schematron specification (see Resources).
</para>

</sect1>

<sect1>
<title>Conclusion</title>

<para>
We at Fourthought pretty much stopped using DTD about a year ago when we started using namespaces in earnest.  We soon seized on Schematron and have used it in deployed work product for our clients and internally.  Since we already do a lot of work with XSLT it's a very comfortable system and the training required for XPath isn't much of an issue.  To match most of the basic features of DTD, not much more knowledge should be required than path expressions, predicates, unions, the sibling and attribute axes, and a handful of functions such as count.  Performance has not been an issue because we typically have strong control over XML data in our systems and hardly ever use defaulted attributes.  This allows us to validate only when a new XML datum is input, or an existing datum modified our systems, reducing performance concerns.
</para>

<para>
Schematron is a clean, well-considered approache to the problems of validation and simple reporting.  XML Schemas are a significant development, but it is debatable whether such an entirely new and complex system is required for such a straightforward task as validation.  RELAX and The Schematron both present simpler approaches coming from different angles and they might be a better fit for quick integration into XML systems.  In any case, Schematron once again demonstrates the extraordinary reach of XSLT and the flexibility of XML in general as a data-management technology.
</para>

</sect1>

<sect1>
<title>Resources</title>

<glosslist>
<glossterm>RELAX XML Schema System</glossterm><glossdef>http://www.xml.gr.jp/relax/</glossdef>
<glossterm>W3C XML Schemas: Primer</glossterm><glossdef>http://www.w3.org/TR/xmlschema-0/</glossdef>
<glossterm>W3C XML Schemas Part 1: Structures</glossterm><glossdef>http://www.w3.org/TR/xmlschema-1/</glossdef>
<glossterm>W3C XML Schemas Part 2: Datatypes</glossterm><glossdef>http://www.w3.org/TR/xmlschema-2/</glossdef>
<glossterm>DTD2RELAX</glossterm><glossdef>http://www.horobi.com/Projects/RELAX/Archive/DTD2RELAX.html</glossdef>
<glossterm>The Schematron home page</glossterm><glossdef>http://www.ascc.net/xml/resource/schematron/schematron.html</glossdef>
<glossterm>Rick Jelliffe's Comparison of Various Schema Methods</glossterm><glossdef>http://www.ascc.net/%7ericko/XMLSchemaInContext.html</glossdef>
<glossterm>4XSLT</glossterm><glossdef>http://www.fourthought.com/4XSLT</glossdef>
<glossterm>4Suite</glossterm><glossdef>http://www.fourthought.com/4Suite</glossdef>
<glossterm>Schematron Tutorial</glossterm><glossdef>http://www.zvon.org/HTMLonly/SchematronTutorial/General/contents.html</glossdef>
<glossterm>Other ZVON Tutorials for XML-related topics</glossterm><glossdef>http://www.zvon.org/</glossdef>
<glossterm>The Schematron Specification</glossterm><glossdef>http://www.ascc.net/xml/resource/schematron/Schematron2000.html</glossdef>
<glossterm>General news, product info, etc. concerning XSLT</glossterm><glossdef>http://www.xslt.com</glossdef>
<glossterm>General news, product info, etc. concerning XML</glossterm><glossdef>http://www.xmlhack.com</glossdef>
<glossterm>Slides from an XSLT introduction by the author</glossterm><glossdef>http://fourthought.com/Presentations/xmlforum-xslt-20000830</glossdef>
<glossterm>The XSLT FAQ</glossterm><glossdef>http://www.dpawson.freeserve.co.uk/xsl/xslfaq.html</glossdef>
<glossterm>Zvon XSLT Reference</glossterm><glossdef>http://www.zvon.org/xxl/XSLTreference/Output/index.html</glossdef>
<glossterm>Zvon DTD tutorial</glossterm><glossdef>http://www.zvon.org/xxl/DTDTutorial/General/book.html</glossdef>
<glossterm>Zvon namespace tutorial</glossterm><glossdef>http://www.zvon.org/xxl/NamespaceTutorial/Output/index.html</glossdef>
<glossterm>Zvon XML tutorial</glossterm><glossdef>http://www.zvon.org/xxl/XMLTutorial/General/book_en.html</glossdef>
<glossterm>Zvon XPath tutorial</glossterm><glossdef>http://www.zvon.org/xxl/XPathTutorial/General/examples.html</glossdef>
<glossterm>Zvon XSLT tutorial</glossterm><glossdef>http://www.zvon.org/xxl/XSLTutorial/Books/Book1/index.html</glossdef>
<glossterm>Links related to architectural forms</glossterm><glossdef>http://www.xml.com/pub/Guide/Architectural_Forms</glossdef>
</glosslist>

</sect1>

<!-- Append another article -->

<sect1>

<para>
On re-reading my first two XML articles, just over a year ago in this journal and in its sister, Sunworld, I'm struck by how much they represented a justification of XML as the great tin opener of closed data formats.  In under a year, it looks as if all the light-bulbs went on at once.  XML is in the computer news every day, every company seems to be scrambling to ink XML into their brochures, and XML standards organizations such as the World-Wide Web consortium (W3C) practically have to turn people away.  At this point I hardly think any more justification of XML for open data exchange is required.  It's pretty much a fact of information technology.  The remaining questions are how to use XML to solve real problems better than with any other means.
</para>

<para>
As I mentioned in my most recent article, the W3C and other standards organizations are working very quickly to complete specifications for technologies complementary to XML.  I mentioned namespaces, which are a key facility for managing global names and are now used in almost every XML technology.  I also mentioned DOM and XSLT.  Since then, XLink, XPointer, XML Schemas, SVG and other specs are almost complete.  I shall discuss these later in the series as well as RDF, Schematron and other beasts in the XML menagerie.  The XML community has also matured greatly, and as one example, there are many new, high-quality information and news sites, some of which I list in Resources section.  If you are highly interested in XML, I highly recommend regular visits to xmlhack, in particular.
</para>

</sect1>

<sect1>
<title>The Triumph of Open Standards</title>

<para>
The most amazing thing about XML's incredible rise, in my opinion sharper than that of the PC, Java, or even the Web, is the fact that it has remained as open as when it started.  Even though XML in its early days was positioned as a tool for encouraging data interchange by providing both human and machine readibility, odds always were that a powerful company, or group of companies would foul the waters.  Many vertical industries such as the automobile inustry (which recently surprised analysts by announcing a huge, XML-driven on-line exchange), health-care and chemicals have been moving to XML as data-exchange format.  If the likes of Microsoft (early and on-going XML champion) and Oracle, could co-opt standards for XML processing, they could gain even more domination than they currently had in such industries, all under the guise of openness.  The perfect monopolistic trojan horse.
</para>

<para>
And this was never just an idle menace.  Last year, Microsoft nearly suceeded in derailing XSLT by bundling a mutation of XSLT into its Internet Explorer 5 browser which was different from the emerging standards, and laden with Microsoft extensions.  Many Linux advocates cried loudly over Microsoft's "embrace-extend-extinguish" move on Kerberos, but this was a weak jab compared to the MS-XSL ploy.  Since Internet Explorer is by far the most popular browser, Microsoft ensured that most of the world's experience of XSLT came through their own proprietary version, and nearly made this proprietary version the de-facto standard.  There was many a flame-war on the xsl-list mailing list (see Resources) when IE users arrived in droves asking questions about what they perceived to be proper XSLT.
</para>

<para>
But then something surprising happened.  Microsoft started to hear loudly and clearly from its customers that they didn't want an MS flavor of XSLT.  They wanted the standard.  The first signs of this were that Microsoft slowly started migrating to the standard in Internet Explorer updates.  Then MS developers announced publicly that their design goal was now full compliance with the XSLT standard.  Finally, after some prodding on xsl-list, several of Microsoft's developers admitted that they had been receiving numerous e-mail messages asking them to get in line.
</para>

<para>
Now I know Linux users aren't used to expecting such sophistication and independent thought from large numbers of MS users, and I'm no exception to that (possibly bigoted) attitude.  I credit this remarkable episode to the power of the promise of openness in XML.  Of course, this doesn't prevent Microsoft from amusing gaffes such as claiming to have invented XML (as reported by The Washington Post in May), but such things are far less dangerous than standards pollution..
</para>

<para>
Similar stories are repeated over and over throughout XML's brief history.  In fact, Microsoft, not having learned all its lessons from the XSLT fiasco, is currently being bludgeoned into abandoning its proprietary XML schema format, XML-Data, in favor of XML Schemas, which has come almost all the way through the W3C standards track.  The battle hit fever pitch with Microsoft's loud announcement of BizTalk, an ambitious repository and toolkit for XML schemas.  But day by day, it looks more as if the open standard will win out.
</para>

<para>
But enough about the wide, wild world.  Let's have a look at what's happening at home.  Another striking change from my first XML article in these Web pages is that I pretty much had to apologize for the lack of XML tools for Linux.  This problem has been corrected to an astonishing degree.
</para>

<para>
This article briefly introduces a selection of XML tools for Linux in a few basic categories: parsers, web servers, application servers, GUIs and bare-bones tools.  Most users' introduction to XML will be for purposes of better managing Web pages, from which they may choose to migrate to complete, all-inclusive appication servers or construct custom systems from the various XML toolkits available and the usual UNIX duct tape and wire ties.  In all cases there is usually some content to manage, and though you may see no reason to leave the world of Emacs or vi to churn out documents, since content-managers are often non-technical, it's a very good thing that there is a good selection of GUI XML editors for all tastes.
</para>

</sect1>

<sect1>
<title>Just the Parsers, Ma'am</title>

<para>
XML processing starts with the parser, and Linux has many to choose from.  Basically all you have to do is pick a language.  C, C++, Java, Python, PHP, Perl, TCL, or even Javascript (and this is hardly an exhaustive list).  The next thing to choose is whether and how to validate your XML documents.  Validation is the process of ensuring that all the elements and attributes in an XML document conform to a schema.  The traditional XML validation method is the Document-Type Definition (DTD).  The W3C, as I mentioned, has almost completed XML Schemas, which have the advantages of XML format (DTDs are in a different format) and "modern" data-typing, with the disadvantage of complexity and immaturity.
</para>

<para>
C users are well served by the old standby from James Clark, Expat, which is a barebones parser and arguably the fastest in existence, but provides no validation.  Significantly, almost every language under the sun, from Python to Eiffel, provides a front-end to Expat.  But even Expat is facing some tough "coopetition" from entries such as the capable libxml project, led by Daniel Viellard of the W3C.  This library, most prominently used in GNOME, offers many options for fine-tuning parsing, and supports DTD validation.  There is also Richard Tobin's RXP, which supports DTD.  C++ users have Xerces-C++, which is based on XML4C code IBM donated to the Apache/XML project.  Xerces-C++ supports both DTD and Schemas.  In fact, if you want to start using XML Schemas in Linux, Xerces is probably your best bet.  Individual efforts include Michael Fink's xmlpp, which is quite new and doesn't support validation.
</para>

<para>
There is a Java version of Xerces with similar pedigree.  Java users are pretty much drowned in choice.  The media has made much of the "marriage" between Java and XML, but the most likely explanation for the huge number of XML tools for Java is that XML emerged right as Java was cresting as a programming language.  Besides Xerces-J, there are Java parsers from Oracle, Sun, DataChannel, and others.  Individual efforts include Thomas Weidenfeller's XMLtp (Tiny XML Parser), which is designed for embedding into other Java apps (as was the pioneering but now moribund Aelfred from Microstar).  Mr. Weidenfeller also provides one of the neatest summaries of OSS license I've seen: "Do what you like with the software, but don't sue me".  Then there is The Wilson Partnership's MinML, designed to be even smaller, for use in embedded systems.
</para>

<para>
Python still has the growing and evolving PyXML package as well as my own company's 4Suite.  XML considerations are helping shape many grand trends of Python such as unicode support and improved memory-management.  The perl community has definitely taken to XML.  The main parser is, appropriately, XML::Parser, but you can pretty much take any XML buzzword, prepend "XML::", and find a corresponding perl package.
</para>

</sect1>

<sect1>
<title>Serving up XML Pages</title>

<para>
XML's early promise to the media was as a way to tame the Web.  Structured documents, separation of content from presentation, and more manageable searching and autonomous Web agents.  Some of this has been drowned out by all the recent interest in XML for database integration and message-based middleware, but XML is still an excellent way to manage structured content on the Web.  And Linux is a pretty good operating system on which to host the content. 
</para>

<para>
The big dog among the XML Web servers is also the well known big dog of Web servers, period.  Apache is absolutely swarming with XML activity lately.  I've already mentioned Xerces, the XML parser from the Apache/XML project.  There is also an XSLT processor, Xalan, with roots in IBM/Lotus's LotusXSL.  There is also Formatting-Object Processor (FOP), a tool for converting XML documents to the popular PDF document, by way of XSL formatting objects, a special XML vocabulary for presentation.  Apache has added support for the Simple Object Access Protocol (SOAP), an XML messaging protocol that can be used to make HTTP-based queries to a server in an XML format.  As a side note, SOAP, and open protocol, is heavily contributed to and championed by Microsoft, in one of the many positive contributions that company has made to XML while not trying to embrace and extend.
</para>

<para>
These bits and pieces are combined into an Apache-based XML Web publishing solution called Cocoon.  Cocoon allows XML documents to be developed, and then published on the Web, for wireless applications through Wireless Application Protocol (WAP), and to print-ready PDF format through FOP.
</para>

<para>
Perl hackers already have the proliferation of "XML::*" packages I've already mentioned, but Matt Sergeant has also put together a comprehensive toolkit for XML processing: Axkit.  Axkit is specialized for use with Apache and mod_perl, and provides XSLT transformation as well as other non-standard transform approaches such as "XPathScript".
</para>

</sect1>

<sect1>
<title>Full-blown application servers</title>

<para>
Enterprises that want an end-to-end solution for developing and deploying applications using XML data have several options under Linux.  Application servers build on basic Web servers such as described above by adding database integration, version control, distributed transactions and other such facilities.
</para>

<para>
The grey and respectable Hewelett Packard found an open-source, Web-hip side with its e-speak project, a tool for distributed XML applications with Java, Python and C APIs for development and extension.
</para>

<para>
A smaller company that has found the advantages of open-source for promoting its XML services is Lutris, Inc., developers of Enhydra.  Enhydra, about which I've reported in a previous LinuxWorld article, is a Java application server for XML processing.  It has some neat innovations such as XMLC, a way to "compile" XML into an intermediate binary form for efficient processing.  It is also one of the first open-source implementations of Java 2's Enterprise Edition services, including Enterprise JavaBeans.
</para>

<para>
XML Blaster is a messaging-oriented middleware (MOM) suite for XML applications.  It uses an XML transport in a publish/subscribe system for exchanging text and binary data.  It uses CORBA for network and inter-process communication and supports components written in Java, Perl, Python and TCL.
</para>

<para>
Conglomerate, developed by Styx, is a somewhat less ambitious but interesting project for an XML application server more attuned for document management.  It includes a nifty GUI editor and provides a proprietary transformation language that can generate HTML, TeX and other formats.
</para>

</sect1>

<sect1>
<title>Oo-wee!  GUI!</title>

<para>
One area in which I lamented Linux's lag in XML tools last year was in the area of GUI browsers and editors.  While I personally use a 4XSLT script and XEmacs for these respective tasks, I frequently work with clients who want to use more friendly GUIs for XML editing and ask whether my preferred Linux platform has anything available.  Fortunately, there are more choices than ever on our favorite OS.  Again much of the succour comes in the form of Java's cross-platform GUI support.
</para>

<para>
GEXml is a Java XML editor which allows programmers use pluggable Java modules for editing their own special tag sets.  It uses a pretty standard layout for XML editors: a multi-pane window with a section for the tree-view, and sections for attributes and a section for CDATA.
</para>

<para>
Merlot, by Channelpoint, Inc., is another Java-based XML editor that emphasizes modeling XML documents around their DTDs, abstracting the actual XML file from the user.  It supports pluggable extension modules for custom DTDs.
</para>

<para>
Lunatech's Morphon is yet another DTD-based XML editor and modeling tool.  Hopefully all these DTD-based tools will expand to accommodate XML schemas and other validation methods as well in order to make life easier for those of us who use XML namespaces.  Morphon is similar to the other editors described here with a couple of nice twists: it allows you to specify cascading stylesheets for the editor appearance and document preview, and it mixes the ubiquitous tree view with a friendly view of the XML document being edited.  Morphon, however, is not open-source, though available for Linux.
</para>

<para>
IBM's Alphaworks keeps on churning out free (beer) XML tools, one of which, XML Viewer, allows users to view XML documents using (once again) the tree-view and specialized panes for element and attribute data.  XML Viewer is written in Java.  It also allows linking the XML source and DTD to allow viewing such items as element and attribute definitions.  There is also XSL Editor, a specialized java-based XML editor for XSLT stylesheets.  It also incorporates advanced features such as syntax highlighting and an XSLT debugger.
</para>

<para>
TreeNotes is an XML text editor that uses a series of widgets to open up XML's tree structure, elements and attributes, and of course character data, to editing.
</para>

<para>
DocZilla is an interesting project: an extension of the Mozilla project for Web-based XML document applications.  It promises XML browsing support on par with Internet Explorer's including an extension and plug-in framework.  DocZilla started out very strongly, but now seems to have lagged a bit.  Part of the reason might be that Mozilla is increasing its XML focus.  Mozilla has always supported XML+Cascading Style-Sheets (CSS), but now, with Transformiix (an XSLT processor for Mozilla) and other such projects, it is making its own bid to replace Explorer as king of XML browsers.
</para>

<para>
There is also KXMLViewer, a KDE XML viewer written in Python, but I'll cover this in more detail when I discuss GNOME and KDE XML support in a coming article in this series.
</para>

</sect1>

<sect1>
<title>In the Hacker Spirit</title>

<para>
So we've looked at lumbering app servers and pretty GUI tools.  All very nice for easing into XML, but we all know that Linux (and UNIX) users typically prefer sterner stuff.  Small, manageable, versatile, no-nonsense packages that can be strung together to get a larger job done.  Luckily for the desperate hacker, the nuts-and-bolts toolkit is growing just as quickly as the rest of XML space.
</para>

<para>
A key and quite mature entry is LT XML, developed by the Edinburgh Language Technology Group.  LT XML is a set of stand-along tools and libraries for C programmers using XML.  It supports both tree-based and stream-oriented processing, covering a wide variety of application types.  The LT XML repertoire would be quite familiar and pleasant to those who love nothing more than to string together GNU textutils to produce some neat text transformation.  There is the mandatory XML-aware grep, sggrep (the "sg" for SGML), as well as sgsort, sgcount, sgtoken, etc, which should be self-explanatory.  Python bindings for LT XML should be available by the time you read this.
</para>

<para>
Speaking of grep, there is also fxgrep, a powerful XML querying tool written in Standard ML, a well-regarded functional programming language from Bell Labs (XML provides a rather fitting problem space for functional languages).  fxgrep uses the XML parser fxp, also written in SML.  fxgrep supports specialized XML searching and query using its own pattern syntax.
</para>

<para>
Paul Tchistopolskii makes clear there is no mistake as to his target user-base for Ux: "Ux is UNIX, revisited with XML".  Ux is a set of small XML components written in Java (OK, we're leaking some UNIX heritage right there).  The components are designed to be piped together for database storage and extraction, XSLT transformation, query, etc.
</para>

<para>
Pyxie is an XML parsing and processing toolkit in Python by Sean McGrath and highlighted in his book, <emph>XML Processing with Python</emph>.  Pyxie's main distiction is that it builds on earlier work by James Clark by focusing on a line-based view of XML rather than the "natural" tokens that emerge from the spec.  This can provide a useful optimization if occasional complications.
</para>

<para>
For those looking askance at XML in a TeX environment, IBM's Alphaworks might have a useful introduction.  TeXML is a tool that allows you to define an XSLT transform for converting XML files to a specialized vocabulary, the results of which are converted to TeX.  Also, thanks to Alphaworks, there is an XML diff as well as a grep.  XML Tree Diff shows the differences between documents based on their DOM tree representation.  It's more of a collection of Javabeans for performing diffs than a stand-alone application, but it's relatively straightforward to use.
</para>

<para>
And there is my own company's 4Suite, a set of libraries for Python users to construct their own XML applications using DOM, XPath and XSLT, among other tools.  I covered 4XSLT in my last XML article (though the spec and 4XSLT have changed since then), and 4Suite libraries are now standard components in the Python XML distribution.
</para>

</sect1>

<sect1>
<title>Conclusion</title>

<para>
Hopefully this tour will help find XML resources for Linux users of all levels.  In upcoming articles (hopefully not as delayed as this one), I shall cover XML and Databases, XML and KDE/GNOME, and mnore topics on how to put XML to work in a Linux environment.
</para>

<para>
By the way this very article is available in XML form (using the DocBook standard).  I've also put up a simplified DocBook XSLT stylesheet that can be used to render this article to HTML (see Resources for both).  Note that I use the "doc" file extension for DocBook files.  I encourage you to use DocBook (O'Reilly and Associates publishes an excellent book on the topic by Norman Walsh) and the ".doc" extension, chopping at the hegemony of the proprietary Microsoft Word format.  Just another small way XML can open up data to the world.
</para>

</sect1>

<sect1>
<title>Resources</title>

<sect2>
<title>Parsers</title>

<glosslist>
<glossterm>Expat</glossterm><glossdef>http://www.jclark.com/xml/expat.html</glossdef>
<glossterm>Xerces C++</glossterm><glossdef>http://xml.apache.org/xerces-c/index.html</glossdef>
<glossterm>Xerces-Java</glossterm><glossdef>http://xml.apache.org/xerces-j/index.html</glossdef>
<glossterm>xmlpp</glossterm><glossdef>http://www.vividos.de/xmlpp/</glossdef>
<glossterm>libxml</glossterm><glossdef>http://www.xmlsoft.org/</glossdef>
<glossterm>RXP</glossterm><glossdef>http://www.cogsci.ed.ac.uk/~richard/rxp.html</glossdef>
<glossterm>XMLtp</glossterm><glossdef>http://mitglied.tripod.de/xmltp/</glossdef>
<glossterm>MinML</glossterm><glossdef>http://www.wilson.co.uk/xml/minml.htm</glossdef>
</glosslist>

</sect2>

<sect2>
<title>Web Servers</title>

<glosslist>
<glossterm>Axkit</glossterm><glossdef>http://axkit.org/</glossdef>
<glossterm>XML/Apache</glossterm><glossdef>http://xml.apache.org</glossdef>
</glosslist>

</sect2>

<sect2>
<title>App Servers</title>

<glosslist>
<glossterm>Conglomerate</glossterm><glossdef>http://www.conglomerate.org/</glossdef>
<glossterm>e-speak</glossterm><glossdef>http://www.e-speak.net/</glossdef>
<glossterm>Enhydra</glossterm><glossdef>http://www.enhydra.org/</glossdef>
<glossterm>XML Blaster</glossterm><glossdef>http://www.xmlBlaster.org/</glossdef>
</glosslist>

</sect2>

<sect2>
<title>Low-Level Tools</title>

<glosslist>
<glossterm>LT XML</glossterm><glossdef>http://www.ltg.ed.ac.uk/software/xml/index.html</glossdef>
<glossterm>fxgrep</glossterm><glossdef>http://www.informatik.uni-trier.de/~neumann/Fxgrep/</glossdef>
<glossterm>Ux</glossterm><glossdef>http://www.pault.com/Ux/</glossdef>
<glossterm>Pyxie</glossterm><glossdef>http://www.digitome.com/pyxie.html</glossdef>
</glosslist>

</sect2>

<sect2>
<title>GUIs</title>

<glosslist>
<glossterm>TreeNotes</glossterm><glossdef>http://pikosoft.dragontiger.com/en/treenotes/</glossdef>
<glossterm>DocZilla</glossterm><glossdef>http://www.doczilla.com/</glossdef>
<glossterm>GEXml</glossterm><glossdef>http://gexml.cx/</glossdef>
<glossterm>Merlot</glossterm><glossdef>http://www.merlotxml.org/</glossdef>
<glossterm>Morphon</glossterm><glossdef>http://www.morphon.com/</glossdef>
</glosslist>

</sect2>

<sect2>
<title>Et Cetera</title>

<glosslist>
<glossterm>There is more to XML than roll-your-own HTML</glossterm><glossdef>http://www.linuxworld.com/linuxworld/lw-1999-03/lw-03-xml.html</glossdef>
<glossterm>Practical XML with Linux, Part 1</glossterm><glossdef>http://www.linuxworld.com/linuxworld/lw-1999-09/lw-09-xml2.html</glossdef>
<glossterm>The xsl-list mailing list</glossterm><glossdef>http://www.mulberrytech.com/xsl/xsl-list</glossdef>
<glossterm>DocBook and stylesheet for this article</glossterm><glossdef>http://www.Fourthought.com/Publications/lw-xml2</glossdef>
<glossterm>The Apache/XML Project</glossterm><glossdef>http://xml.apache.org/</glossdef>
<glossterm>SOAP</glossterm><glossdef>http://www.w3.org/TR/SOAP/</glossdef>
<glossterm>xmlhack</glossterm><glossdef>http://www.xmlhack.com</glossdef>
<glossterm>XML Pit Stop</glossterm><glossdef>http://www.xmlpitstop.com/</glossdef>
<glossterm>xslt.com</glossterm><glossdef>http://www.xslt.com</glossdef>
<glossterm>XML Times</glossterm><glossdef>http://www.xmltimes.com/</glossdef>
<glossterm>The XML Cover Pages</glossterm><glossdef>http://www.oasis-open.org/cover</glossdef>
<glossterm>IBM's Alphaworks (including XML Viewer, XSL Edirot, XML Tree Diff and TeXML)</glossterm><glossdef>http://alphaworks.ibm.com</glossdef>
</glosslist>

</sect2>

</sect1>

</article>

"""


source_3 = """<article xmlns="http://docbook.org/docbook/xml/4.0/namespace">
<artheader>
<title>An Overview of IBM DB2 Universal Database 7.1 for Linux</title><author>Uche Ogbuji</author>
</artheader>

<sect1>

<para>
IBM has become legendary in the Linux community with its repeated announcments and re-announcements of Linux support.  It seems every six months at some Linux show ro even general PC show IBM pledges across the board Linux support.  All very odd because since Big Blue's first altar conversion a couple of years ago, it has done a great deal for the Linux community (despite purported resistance fro the AIX group), but by constantly re-proclaiming its allegiance, it gives the impression that it never followed through on prior pledges.  The truth is that IBM's many contributions to Linux have been typical big blue: very practical and thus very boring.  Jikes, IBM JDK, Apache patches and a Linux port to IBM 370 Mainframes (someone was <emph>very</emph> bored) are not exactly the sorts of goodies that have a Linux pundit hopping up and down, but they provide real, solid bases for businesses looking at Linux for critical tasks.  Not that IBM is incapable of splashy software: its remarkable Alphaworks project has constributed rather nifty stuff to the Java and XML communities (pretty much all of which runs on Linux).  See my recent article on XML and Linux for more details.
</para>

<para>
The second side of the coin, besides contributing to free Linux software has ben supporting Linux with its popular and well-respected ("nobody ever got fired for buying IBM") commercial offerings.  IBM has made moves in this direction from the hardware end such as Thinkpads to the software end such as the subject of this article: DB2.  IBM first ported its Universal Database to Linux in version 6.0, in the great 1998/99 wave commercial database ports which also featured Oracle, Informix, Borland and Sybase.  In fact, DB2 for Linux was originally to be available at no charge and only became payware after IBM noticed high demand from corporate customers.  Big Blue has followed through with Linux versions of each subsequent release.  Promising the full panolpy of enterprise database features from a robust ANSI SQL 92 core to Object Database (if not yet SQL-99) extensions to administration, network, performance tuning, and replication tools, to extenders for geospacial systems, XML, hard-core financial number-crunching, et cetera, et cetera, et cetera.
</para>

<para>
I downloaded IBM DB2 personal edition from the source (see Resources).  There was an option to order a CD, but the last time I ordered a DB2 CD from IBM (UDB 6.2), it took over two months, and I wanted to have a look this year.  Besides, linuxpecmn.tar was a pretty modest-sized download (relative to its peers) at 75 MB.  You might be wondering why IBM doesn't gzip it as well, but it turns out that most of the archive contents are RPMs, which already compress their contents.
</para>

</sect1>

<sect1>
<title>Installation</title>

<para>
My review machine is a Pentium II 500 with 256MB RAM and 4GB of disk space available for DB2.  The operating system is the KRUD distribution July 2000 release, based on Red Hat 6.2 (see my last Oracle article --linked in Resources-- for more on KRUD).
</para>

<para>
If you caught my Oracle article you'll remember how harshly I criticized the 8.1.5 Linux release for installation and database creation difficulties ("tortures" would be more accurate, if too colorful).  In that article I might have mentioned that Oracle's terrible installation process on Linux was probably no worse than that of IBM DB2 Universal Database for Linux 6.1, which I actually gave up on trying to install and set-up.
</para>

<para>
Part of the problem was the infamous confusion Red Hat introduced through its botched handling of the migration to Glibc 6.0 in Red Hat 6.1.  But even after dodging the bullets this sent at the DB2 user in either of two ways: by trying an install under Red hat 6.0 or by following detailed, unofficial instructions for install under Red Hat 6.1, there were many remaining problems with the installer and in the DB2 tools.  Judging from my experience and the size of the resulting DB2 6.1 fixpaks, it was pretty much of beta quality.  And so I sat down to install DB2 7.1 with some trepidation.  Was I in for more of the IBM DB2 6.1 and Oracle 8.1.5 treatment?  (See the side-bar for a brief update on whether Oracle 8.1.6 is any more lenient on the mortal user).
</para>

<para>
The fact that I was able to get Oracle 8.1.5 installed and not DB2 6.1 was probably not because Oracle demanded less indulgence but because in addition to Dejanews and Technet there were the excellent third-party HOWTOs by people such as Jesus Salvo.  DB2 had rather few such resources that I could find until recently.
</para>

<para>
This time there is a HOWTO put together by Daniel Scott of IBM and
available from the Linux Documentation Project (see Resources).  Knowing
IBM's culture of brilliant individuals within a stultifying bureaucracy,
Mr. Scott probably got tired of DB2/Linux frustrations and took the
initative to put together the HOWTO, but regardless, it's an excellent
resource.  As a bonus, it covers a wide range of distributions, including
Caldera OpenLinux, Debian, Red Hat, SuSE and Turbo Linux.
</para>

<para>
Armed with this, I dove into the install, starting with the installation
of the pdksh RPM from the KRUD CD.
</para>

<screen>
[root@euro /root]# rpm -i /mnt/cdrom/RedHat/RPMS/pdksh-5.2.14-2.i386.rpm 
</screen>

<para>
Then I ran db2setup from the untarred DB2 Personal Edition root directory
</para>

<screen>
[root@euro s000510.personal]# ./db2setup &amp;
</screen>

<para>
This brought up the text-mode installer (see figure 1).  This of course is less flashy than the Java-based installers Oracle and Sybase have moved to, but it's far more readable and less idiosyncratic for all that.
</para>

<mediaobject><imageobject fileref='db2-install.tiff' format='TIFF'/><textobject><phrase>Figure 1: The DB2 Installer</phrase></textobject></mediaobject>

<para>
I selected the "Administration Client", then "Customize", and enabled
"Control Center".  I selected "DB2 Personal Edition", then "Customize", 
and enabled all options except for the "Local Control Warehouse
Database" and Asian code page options.  I then selected "DB2 Application
Development Client", then "Customize", and selected "Create Links for DB2
Libraries".  The next screen allowed automatic creation of a database
instance, which I opted for using the default user names for the
administration.  I also opted to add sample data to the created
instance.  I opted to set up distributed join on the database instance,
which allows SQL statements to involve multiple database instances.  I
also opted to "Create the Administration Server", with all default
options.
</para>

<para>
Finally, after a stern "are you sure?" warning, the installation went
merrilly off, displaying a single-line status message witht he current
installing component.  It left a comprehensive log of its actions at
/tmp/db2setup.log.
</para>

<para>
So far, so good.  None of the problems I ran into with DB2 6.1: freezes and screen-scrawling.  With considerable relief, I found I had what appeared to be a working DB2 install and database instance with little or no fuss.
</para>

<para>
One final and often neglected aspect of installation is "de-installation".  It's nice to know
that if you ever cease to need a package or decide against using it after
installation, that you can remove it cleanly from your system.  Windows
users have the capable InstallShield for this, but Linux packagers often have to
each find do their own thing.  Luckily, since the DB2 is RPM-based,
uninstallation is simple enough, and accomplished by running the
db2_deinstall script from the package, CD, or installed location.  Oracle also 
provided uninstallation support, but through a custom interface.
</para>

</sect1>

<sect1>
<title>Getting Started</title>

<para>
DB2 comes with many nice GUI utilities, all using Java for display (which
seems to be the standard modus operandi of Linux database companies).  To
use it you must use IBM's JDK 1.1.8 for Linux, no other version, no
other vendor.  Write once, run anywhere on any JVM, right?  Ha.  At any
rate, IBM's JDK is the fastest available for Linux, and they hope to have
a 1.3 version soon (not that you'll be able to use it with DB2 UDB
7.1) See resources for the download link.
</para>

<para>
I downloaded the RPM and installed it:
</para>

<screen>
[root@euro V7.1]# rpm -i /root/packages/IBMJava118-SDK-1.1.8-4.0.i386.rpm 
</screen>

<para>Then I added the following lines environment entries to the various DB2
users:
</para>

<screen>
export JAVA_HOME=/usr/jdk118
export PATH=$PATH:$JAVA_HOME/bin
export CLASSPATH=$CLASSPATH:$JAVA_HOME/lib/classes.zip
</screen>

<para>
This should set up the environment for bash.  Note that if you're
using some other shell you might need a different format of commands to
set up the environment.
</para>

<para>
Note that the DB2 installer places its environment set-up script in the
~/.bashrc script rather than ~/.bash_profile.
</para>

<para>
After setting up the environment I logged in to the db2 administration
user and fired up the DB2 control center.
</para>

<screen>
[db2@euro db2]$ db2cc &amp;
</screen>

<para>
And I promptly ran into problems.  The DB2 splash window panel came up and
seemed to be hung until I noticed that there were the outlines of another
window behind it.  I wondered whether it was an error message of some
sort, but the splash screen obscured any controls for bringing it to the
front. and refused to get out of the way.  I was running the default
Enlightenment window manager under GNOME so I ended up switching it to
Sawfish (with which I'm more familiar) and I played with the config until I was able to force the error
message dialog to the front.
</para>

<para>
So there is was in all its ignominy: "[IBM][JDBC Driver] CLI0602E  Memory allocation error on Server" (see figure 2).  Eh what?  Again this is a machine with 256MB RAM and though top did show that all RAM was soaked up (most of it hogged by the JRE, of course), there was 120MB of swap space free.  So I shrugged and closed the error window expecting to have to get out my medieval system
administration tools to get to the bottom of it, when to my surprise the
control center started up just fine despite the dire warning.
</para>

<mediaobject><imageobject fileref='jdbc-mem-error.tiff' format='TIFF'/><textobject><phrase>Figure 2: Spurious JDBC Memory Error from DB2 Control Center</phrase></textobject></mediaobject>

<para>
But now the DB2 control center window was empty.  I was familiar with this
tool and knew that I should have seen entries representing my system and
the database instances set up therein, but there was nothing.  I closed
the control center and re-started, wondering whether the memory error was
the culprit.  On restarting I got the memory error again, but this time I
did get the entries I expected for my system and sample database
instance.  The bother didn't stop there, though.  On clicking on the
database instance icon I got a message that the database was not
started.  Odd, since I opted to have the database start on boot-up.
</para>

<para>
So I went digging.  DB2 sets up an /etc/rc.db2, and adds an entry to the
/etc/inittab to start DB2 in runlevels 2, 3 and 4.  Of course, X Windows
on Red Hat (and most distros) operates in run level 5, and so DB2 wasn't
getting started.  I checked just to be positive, and surely enough, DB2 didn't
start after an explicit run level change (using telinit), nor after a reboot.
</para>

<para>
But one thing the reboot did seem to cure was the JDBC memory error on control-center startup.  I
guess the installer must have siezed resources it refused to give up when
done.  Unless you want to spend time figuring out exactly what
rogue processes are involved, I'd suggest a reboot after DB2 install (what
a shame!)
</para>

<para>
At any rate, although I expect not many people besides database reviewers
run datbases on machines with X Windows, for those that do, one can fix
DB2's auto-start by changing the /etc/inittab to entry from
</para>

<screen>
db:234:once:/etc/rc.db2 > /dev/console 2>&amp;1 # Autostart DB2 Services
</screen>

<para>
to
</para>

<screen>
db:2345:once:/etc/rc.db2 > /dev/console 2>&amp;1 # Autostart DB2 Services
</screen>

<para>
Note the added "5".
</para>

<para>
At this point control center was content, and I as well because
control center is quite nice.  It's generally more responsive and
has more options than the very similar tool from Sybase, and it abstracts
all the  command-line and editing tasks that help make Oracle such a
pain.  There are still times that it takes ages to pop up windows and
refresh screens, but there was no clear pattern to this behavior.  See
figure 3 for a screen shot.
</para>

<mediaobject><imageobject fileref='db2cc.tiff' format='TIFF'/><textobject><phrase>Figure 3: DB2 Control Center Screen Shot</phrase></textobject></mediaobject>

<para>
One of the tools in the Control Center is the Command Center, which is a
GUI-based SQL query tool.  It allows you enter individual commands and
scripts to DB2 instances, and presents the results in a nice
spreadhsheet-like display.  For instance, firing up the Command Center,
using the connect tool to connect to the SAMPLE database (or just entering
"connect to SAMPLE;" in the "Command" text box; then entering
</para>

<para>
One of the tools in the Control Center is the Command Center, which is a
GUI-based query tool for Dynamic SQL, IBM's extended ANSI SQL command set.  It allows you enter individual commands and scripts to DB2 instances, and presents the results in a nice
spreadsheet-like display.  For instance, firing up the Command Center,
using the DB2 browser tool to connect to the SAMPLE database (or just entering
"connect to SAMPLE;" in the "Command" text box; then entering
</para>

<screen>
select * from staff;
</screen>

<para>
and then pressing CTRL-ENTER to execute the contents of the "Command" text box, resulted in the window in figure
4.  I must keep harping on how slow these Java tools are.  The Command
Center window was very sluggish displaying the result set.  I remember
using a very similar DB2 tool under OS/2 Presentation Manager years ago (and several cycles of Moore's Law ago) which
displayed results with considerable alacrity.  I guess that's the price of
cross-platform UI.
</para>

<mediaobject><imageobject fileref='cc-query-result.tiff' format='TIFF'/><textobject><phrase>Figure 4: DB2 Command Center Query Result</phrase></textobject></mediaobject>

<para>
But most UNIX purists won't even bother because they'll be too busy enjoying the command line tools DB2 provides.  The main ingredient is the "db2" command, which can manage database commands across invocations, maintaining the session,
which provides great administrative power, especially when database
management and programming needs to be integrated into scripts.  A sample
session is very simple.  First the database connection is made:
</para>

<para>

</para>

<screen>
[db2@euro db2]$ db2 CONNECT TO SAMPLE

   Database Connection Information

 Database server        = DB2/LINUX 7.1.0
 SQL authorization ID   = DB2
 Local database alias   = SAMPLE

[db2@euro db2]$ 
</screen>

<para>
and then subsequent commands can be issued
</para>

<screen>
[db2@euro db2]$ db2 "select * from staff where id &lt; 100"

ID     NAME      DEPT   JOB   YEARS  SALARY    COMM     
------ --------- ------ ----- ------ --------- ---------
    10 Sanders       20 Mgr        7  18357.50         -
    20 Pernal        20 Sales      8  18171.25    612.45
    30 Marenghi      38 Mgr        5  17506.75         -
    40 O'Brien       38 Sales      6  18006.00    846.55
    50 Hanes         15 Mgr       10  20659.80         -
    60 Quigley       38 Sales      -  16808.30    650.25
    70 Rothman       15 Sales      7  16502.83   1152.00
    80 James         20 Clerk      -  13504.60    128.20
    90 Koonitz       42 Sales      6  18001.75   1386.70

  9 record(s) selected.

[db2@euro db2]$ 
</screen>

<para>
At any time, you can jump into interactive mode:
</para>

<screen>
[db2@euro db2]$ db2
(c) Copyright IBM Corporation 1993,2000
Command Line Processor for DB2 SDK 7.1.0

You can issue database manager commands and SQL statements from the
command 
prompt. For example:
    db2 => connect to sample
    db2 => bind sample.bnd

For general help, type: ?.
For command help, type: ? command, where command can be
the first few keywords of a database manager command. For example:
 ? CATALOG DATABASE for help on the CATALOG DATABASE command
 ? CATALOG          for help on all of the CATALOG commands.

To exit db2 interactive mode, type QUIT at the command prompt. Outside 
interactive mode, all commands must be prefixed with 'db2'.
To list the current command option settings, type LIST COMMAND OPTIONS.

For more detailed help, refer to the Online Reference Manual.

db2 => select * from staff where dept = 20

ID     NAME      DEPT   JOB   YEARS  SALARY    COMM     
------ --------- ------ ----- ------ --------- ---------
    10 Sanders       20 Mgr        7  18357.50         -
    20 Pernal        20 Sales      8  18171.25    612.45
    80 James         20 Clerk      -  13504.60    128.20
   190 Sneider       20 Clerk      8  14252.75    126.50

  4 record(s) selected.

db2 => quit
DB20000I  The QUIT command completed successfully.
[db2@euro db2]$ 
</screen>

<para>
As you can see, just issue Dynamic SQL commands at the "db2 => " ptompt, or "quit" when you're done.  In either mode, to close the database connection, just use the "DISCONNECT" command:
</para>

<screen>
[db2@euro db2]$ db2 disconnect SAMPLE
DB20000I  The SQL DISCONNECT command completed successfully.
[db2@euro db2]$ 
</screen>

</sect1>

<sect1>
<title>On-line Information</title>

<para>
DB2 combines system information and on-line documentation into the
Information Center tool, which you can invoke form the command line as
follows:
</para>

<screen>
[db2@euro db2]$ db2ic &amp;
</screen>

<para>
Which brings up a huge index.  The Information Center looks like a
Web/Java evolution of IBM's venerable Bookmanager documentation system, 
and sure enough, the DB2 information is very well organized, indexed and
associated in several views with each tree-view icon launching a chapter
in my Web browser.  The search function does not seem to come with
DB2 Personal Edition, reducing the utility of the information center
somewhat.
</para>

</sect1>

<sect1>
<title>Waaah!  No XML For Linux</title>

<para>
DB2 has not been left behind in the stampede to support XML.  Oracle, IBM,
Software AG and Informix have all announced major XML integration tools
and initiatives.  Oracle's XSQL, Intermedia and other facilities are
available for Linux already, but everyone else seems to have trouble
seeing past Windows XML users: Software AG might have been a Linux database pioneer
with Adabas, but their intriguing Tamino "Native XML" DBMS is NT and
Solaris only so far, and alas, IBM's DB2 XML Extender is Windows
only.  I had hoped to make the developer's section of this review
focus on XML, but this will have to wait until IBM is ready.  More on this
sad state of Linux/XML/DBMS affairs in another article.
</para>

</sect1>

<sect1>
<title>Conclusion</title>

<para>
IBM's DB2 is probably the most mature DBMS on the market, and it
shows in many respects.  It feels like a weird cross between the
old, unhip IBM and the new e-Business IBM (even though all my DB2 
experience has been using SQLC, using DB2 on Linux I almost feel as if I
should be firing up GNU COBOL for application programming).  I've reported
on several glitches I ran into during post-installation, but after this, and if one discounts the occasional
slow-downs in the management tools, DB2 proved solid and accessible during
management and programming.  IBM's pricing structure, which is uniform
across most platforms, is also very flexible, ranging from the $359
Personal Edition to the Developer's Edition, at $499 until December 13th,
to the grand Enterprise Extended Edition, and including revenue-sharing
options and other dot-com friendly packages.
</para>

<para>
One nice thing about using IBM products is that IBM takes defect
management _very_ seriously.  You always have a clear idea of how to
proceed after troubleshooting.  You look for an APAR (Authorized Program
Analysis Report): IBM-ese for a "bug-report", which defines a very clear
path through remediation.  A couple of handy references which I link to
below are the Technical Library for DB2 and the DB2 downloads page where
you can find fixpaks and add-ons.  Also, if you use DB2 heavily, it might be a good idea to keep up with the International DB2 User's Group.
</para>

<para>
There are a few third-party Linux DB2 tools such as J Enterprise Technologies' 
DataBrowser and DataManager 2.1, Java tools for browsing and managing a variety of databases including DB2 and MySQL.  Easysoft's SQLEngine allows queries and applications to work across heterogeneous databases including DB2 Postgres and MySQL.  I've already discussed OpenLink's ODBC drivers for Linux, which support DB2 as well as Oracle, Sybase and others.  All of these are commercial and listed in the Resources section.
</para>

<para>
Nowadays the hardest choice for the prospective commercial Linux database user is deciding which product to use.  At the very high end it is a very close matter between Oracle and DB2, and though Oracle still has more of its enterprise add-ons ported to Linux so far, DB2 UDB 7.1 gives IBM the edge for Linux users by providing superior ease of use, stability and variety of tools.
</para>

</sect1>

<sect1>
<title>Resources</title>

<glosslist>
<glossterm>Daniel Scott's DB2 HOWTO</glossterm><glossdef>http://www.linuxdoc.org/HOWTO/DB2-HOWTO/index.html</glossdef>
<glossterm>A practical guide to Oracle8i for Linux</glossterm><glossdef>http://www.linuxworld.com/linuxworld/lw-2000-04/lw-04-oracle8i.html</glossdef>
<glossterm>IBM JDK 1.1.8 for Linux</glossterm><glossdef>http://www.ibm.com/java/jdk/118/linux/</glossdef>
<glossterm>IBM Technical Library for DB2</glossterm><glossdef>http://www-4.ibm.com/cgi-bin/db2www/data/db2/udb/winos2unix/support/techlib.d2w/report</glossdef>
<glossterm>DB2 Downloads Page</glossterm><glossdef>http://www-4.ibm.com/software/data/db2/udb/downloads.html</glossdef>
<glossterm>International DB2 User's Group</glossterm><glossdef>http://www.idug.org/</glossdef>
<glossterm>DataBrowser/DataManager 2.1</glossterm><glossdef>http://www.jetools.com/products/databrowser/</glossdef>
<glossterm>Easysoft's SQLEngine</glossterm><glossdef>http://www.easysoft.com/products/sql_engine/main.phtml</glossdef>
<glossterm>OpenLink's Universal Data Access Driver Suite</glossterm><glossdef>http://www.openlinksw.com/main/softdld.htm</glossdef>
<glossterm>A bit of pro-DB2/Linux Propaganda</glossterm><glossdef>http://www.vnunet.com/News/1104396</glossdef>
</glosslist>

</sect1>

<!-- append the previous articles -->

<sect1>

<para>
XML is certainly an emerging and quick-changing technology.  One of the knocks against it has been the churn of standards and methodologies.  Certainly there is no greater evidence that XML is in flux than the fact that there is so much development and debate about how to validate XML documents, given that validation is one of the cornerstones of XML.
</para>

<para>
This article introduces The Schematron, one of the currently available validation methodologies.  It will assume familiarity with XML, XML DTDs, and some familiarity with XPath and XSLT transforms.  For those who might need some grounding on one or more of those areas I've added some helpful links in the Resources section.
</para>

</sect1>

<sect1>
<title>A Bit of Background</title>

<para>
Although, as I pointed out in my last XML article on SunWorld (see Resources), XML doesn't introduce any notable innovation in data-processing, it has, through its popularity, introduced many useful disciplines inherited from SGML.  Perhaps the core discipline in this regard is in native support for validation.  One of XML's early promises in terms of easing information-management woes involved it's support for bundling the data schema with the data, and by providing for some standard schema discovery in cases where this bundling was not done.  Of course, the real-world has proven that this facility, while useful, is no panacea.  Even if one can a schema for machine-interpretation of a data set, how does one determine the semantics associated with that schema.  A further problem was the particular schema methodology that XML ended up being bundled with: Document-Type Definition (DTD).
</para>

<para>
DTDs are an odd mix of very generic and very specific expression.  For instance, simple tasks such as specifying that an element can have a number of particular child elements within a given range can be very cumbersome using DTDs.  Yet they are generic enough to allow such elegant design patterns as architectural forms (see Resources).  The expressive shortcomings of DTDs, along with arguments that XML validation should not require a separate computer language (DTDs of course differ in syntax from XML instances), encouraged the W3C, XML's major standards body, to develop a new schema language for XML, using XML syntax.  The resulting XML Schema specification is currently in "Candidate Recommendation" phase and presumably will soon hit version 1.0 (although based on experience with the DOM spec one should hardly rely on this).
</para>

<para>
One of the key XML developments since XML 1.0 that has affected the schema story is XML Namespaces 1.0.  This recommendation provides a mechanism for disambiguating XML names, but does so in a way that is rather unfriendly to DTD users.  There are tricks for using namespaces with DTDs, but they are quite arcane.  Of course it must be noted that many of the SGML old school have argued that namespaces are a rather brittle solution, and furthermore they solve a rather narrow problem to justify such disruption in XML technologies.  The reality, however, is that with XML-related standards from XSLT to XLink relying heavily on namespaces, we shall have to develop solutions to the core problems that take namespaces into account.
</para>

<para>
But back to validation.  The W3C Schema specification has been a long time in development, and along the way there began to be rumblings about the complexity of the emerging model.  XML Schemas did fill a very ambitious charter: covering document structure, data-typing worthy of databases, and even abstract data-modeling such as subclassing.
</para>

<para>
And so because of the gap between the emergence of namespaces and the completion of XML Schemas, and because of fears that the coming specification was far too complex, the XML community, one with a remarkable history of practical problem-solving, went to work.
</para>

<para>
One of the developments was Murata Makoto's Regular Language description for XML (RELAX) (see Resources).  Relax provides a system for developing grammars to describe XML documents.  It uses XML-like syntax and ofers similar featues to DTDs, adding some of the facilities offered by XML Schemas, such as schema annotation (basically, built-in documentation) and data-typing (for example specifying that an attribute value be an integer), and coming up with some exotic additions of its own such as "hedge grammars".  RELAX supports namespaces and provides a clean and inherently modular approach to validation and so has become rather popular, with its own mailing lists and contributed tools such as a DTD to RELAX translator (see Resources).
</para>

</sect1>

<sect1>
<title>A Different Approach: Harnessing the Power of XPath</title>

<para>
In the mean time XSLT emerged as a W3C standard, and immediately established itself as one of their most successful XML-related products.  Most people are familiar with XSLT as a tool to display XML content on "legacy" HTML-only browsers, but there is so much more to XSLT, largely because XPath, which it uses to express patterns in the XML source, is such a well-conceived tool.
</para>

<para>
In fact, since XPath is such a comprehensive system for indicating and selecting from patterns in XML, there is no reason it could not express similar structural concepts as does DTD.  Take the following DTD, listing 1.
</para>

<screen>
<![CDATA[
<!ELEMENT ADDRBOOK (ENTRY*)>
<!ELEMENT ENTRY (NAME, ADDRESS, PHONENUM+, EMAIL)>
<!ATTLIST ENTRY
    ID ID #REQUIRED
>
<!ELEMENT NAME (#PCDATA)>
<!ELEMENT ADDRESS (#PCDATA)>
<!ELEMENT PHONENUM (#PCDATA)>
<!ATTLIST PHONENUM
    DESC CDATA #REQUIRED
>
<!ELEMENT EMAIL (#PCDATA)>
]]>
</screen>

<para>
A sample document valid against this DTD is as follows, listing 2.
</para>

<screen>
<![CDATA[
<?xml version = "1.0"?>
<!DOCTYPE ADDRBOOK SYSTEM "addr_book.dtd">
<ADDRBOOK>
        <ENTRY ID="pa">
                <NAME>Pieter Aaron</NAME>
                <ADDRESS>404 Error Way</ADDRESS>
                <PHONENUM DESC="Work">404-555-1234</PHONENUM>
                <PHONENUM DESC="Fax">404-555-4321</PHONENUM>
                <PHONENUM DESC="Pager">404-555-5555</PHONENUM>
                <EMAIL>pieter.aaron@inter.net</EMAIL>
        </ENTRY>
        <ENTRY ID="en">
                <NAME>Emeka Ndubuisi</NAME>
                <ADDRESS>42 Spam Blvd</ADDRESS>
                <PHONENUM DESC="Work">767-555-7676</PHONENUM>
                <PHONENUM DESC="Fax">767-555-7642</PHONENUM>
                <PHONENUM DESC="Pager">800-SKY-PAGEx767676</PHONENUM>
                <EMAIL>endubuisi@spamtron.com</EMAIL>
        </ENTRY>
</ADDRBOOK>
]]>
</screen>

<para>
Examine the declaration of the ADDRBOOK element.  It basically says that such elements must have at least four child elements, a NAME, an ADDRESS, one or more PHONENUM and an EMAIL.  This can be expressed in XPath with a combination of the following three boolean expressions (using the ADDRBOOK element as the context):
</para>

<screen>
1. count(NAME) = 1 and count(ADDRESS) = 1 and count(EMAIL) = 1
2. NAME[following-sibling::ADDRESS] and ADDRESS[following-sibling::PHONENUM] and PHONENUM[following-sibling::EMAIL]
3. count(NAME|ADDRESS|PHONENUM|EMAIL) = count(*)
</screen>

<para>
The first is true if and only if (iff) there is exactly one each of NAME, ADDRESS, and EMAIL.  This establishes the occurrence rule for these children.  The second is true iff there is a NAME followed by an ADDRESS, an ADDRESS followed by a PHONENUM and a PHONENUM followed by an EMAIL.  This establishes the sequence rule for the children.  Note that the preceding-sibling axis could have been used just as well.  The third expression is true iff there are no other elements besides the NAME ADDRESS PHONENUM EMAIL.  This establishes the (implied) DTD rule that elements are not permitted except where specified in the content model by name or with the ANY symbol.
</para>

<para>
You first reaction might be that the XPath expressions are so much more verbose than the equivalent DTD specification.  This is so in this case, though one can easily come up with situations where the DTD equivalent would be more verbose than the equivalent XPath expressions.  However, this is entirely beside the point.  The DTD version is more concise because it is carefully designed to model such occurrence and sequence patterns.  XPath has far more general purpose and we are actually building the DTD equivalent through a series of primitives each of which operate at a more granular conceptual level than the DTD equivalent.  So it may be more wordy, but it has far greater expressive power.  Let's say we wanted to specify that there can be multiple ADDRESS and EMAIL children, but that they must be of the same number.  This task, which seems a simple enough extension of the previous content-midel, is pretty much beyond the abilities of DTD.  Not so XPath.  Since XPath gives a primitive but complete model of the document, it's an easy enough addition.
</para>

<screen>
1. count(NAME) = 1 and count(ADDRESS) = count(EMAIL)
2. NAME[following-sibling::ADDRESS] and ADDRESS[following-sibling::PHONENUM] and PHONENUM[following-sibling::EMAIL]
3. count(NAME|ADDRESS|PHONENUM|EMAIL) = count(*)
</screen>

<para>
The only change is in expression 1, and should be self-explanatory.  This small foray beyond the scope of DTD illustrates the additional power offered by XPath.  Of course XPath can handle the attribute declarations as well.  For example, the attribute declaration for PHONENUM in the DTD can be expressed as follows (again using the ADDRBOOK element as context):
</para>

<screen>
PHONENUM/@DESC
</screen>

<para>
All these XPath expressions are very well in the abstract, but how would one actually use them for validation?  The most convenient way is to write an XSLT transform that uses them to determine validity.  Here's an example, listing 3, which represents a sub-set of the address book DTD.
</para>

<screen>
<![CDATA[
<?xml version="1.0"?>
<xsl:transform xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">

  <xsl:template match="/">
    <xsl:if test='not(ADDRBOOK)'>
      Validation error: there must be an ADDRBOOK element at the root of the document.
    </xsl:if>
    <xsl:apply-templates select='*'/>
  </xsl:template>

  <xsl:template match="ENTRY">
    <xsl:if test='not(count(NAME) = 1)'>
      Validation error: ENTRY element missing a NAME child.
    </xsl:if>
    <xsl:if test='not(count(ADDRESS) = 1)'>
      Validation error: ENTRY element missing an ADDRESS child.
    </xsl:if>
    <xsl:if test='not(count(EMAIL) = 1)'>
      Validation error: ENTRY element missing an EMAIL child.
    </xsl:if>
    <xsl:if test='not(NAME[following-sibling::ADDRESS] and ADDRESS[following-sibling::PHONENUM] and PHONENUM[following-sibling::EMAIL])'>
      Validation error: ENTRY must have a NAME, ADDRESS, one or more PHONENUM, and an EMAIL in sequence
    </xsl:if>
    <xsl:if test='not(count(NAME|ADDRESS|PHONENUM|EMAIL) = count(*))'>
      Validation error: there is an extraneous element child of ENTRY
    </xsl:if>
    <xsl:apply-templates select='*'/>
  </xsl:template>

  <xsl:template match="PHONENUM">
    <xsl:if test='not(@DESC)'>
      Validation error: PHONENUM must have a DESC attribute
    </xsl:if>
    <xsl:apply-templates select='*'/>
  </xsl:template>

  <xsl:template match="*">
    <xsl:apply-templates select='*'/>
  </xsl:template>

</xsl:transform>
]]>
</screen>

<para>
When run with a valid document, such as the example above, this stylesheet would produce no output.  When run, however, with an invalid document such as the following, listing 4, however, it's a different story.
</para>

<screen>
<![CDATA[
<?xml version = "1.0"?>
<ADDRBOOK>
        <ENTRY ID="pa">
                <NAME>Pieter Aaron</NAME>
                <PHONENUM DESC="Work">404-555-1234</PHONENUM>
                <PHONENUM DESC="Fax">404-555-4321</PHONENUM>
                <PHONENUM DESC="Pager">404-555-5555</PHONENUM>
                <EMAIL>pieter.aaron@inter.net</EMAIL>
        </ENTRY>
        <ENTRY ID="en">
                <NAME>Emeka Ndubuisi</NAME>
                <PHONENUM DESC="Work">767-555-7676</PHONENUM>
                <PHONENUM DESC="Fax">767-555-7642</PHONENUM>
                <PHONENUM DESC="Pager">800-SKY-PAGEx767676</PHONENUM>
                <EMAIL>endubuisi@spamtron.com</EMAIL>
                <ADDRESS>42 Spam Blvd</ADDRESS>
                <SPAM>Make money fast</SPAM>
        </ENTRY>
        <EXTRA/>
</ADDRBOOK>
]]>
</screen>

<para>
Note that all the XPath expressions we came up with are placed in if statements and negated.  This is because they represent conditions such that we want a message put out if they are <emph>not</emph> met.  Running this source against the validation transform using an XSLT processor results in the following output:
</para>

<screen>

      Validation error: ENTRY element missing an ADDRESS child.
    
      Validation error: ENTRY must have a NAME, ADDRESS, one or more PHONENUM, and an EMAIL in sequence
    
      Validation error: ENTRY must have a NAME, ADDRESS, one or more PHONENUM, and an EMAIL in sequence
    
      Validation error: there must be an ENTRY element at the root of the document.
    

</screen>

<para>
And so we have our validation result.  Note that it's pretty much a report of the document, such as we set it up to be.  One nice thing about this is that you can see all the validation errors at once.  Using most XML parsers you only get one error at a time.  But the real power of this XSLT-based validation report is that it's just that: a report.  We happened to use it for DTD-based XML validation, but it's not hard to see how this could be extended to more sophisticated data-management needs.  For instance, suppose we wanted to examine address-book documents for e-mail addresses in the .gov domain.  This is pretty much entirely beyond the realm of validation, but it is an example, as database programmers will immediately recognize, of reporting.
</para>

<para>
While it might be argued one way or another whether validation and reporting are cut from the same conceptual cloth, it is pretty clear that in practice, XML document validation can be treated as a subset of XML document reporting, and furthermore that XPath and XSLT provide a powerful toolkit for document validation.
</para>

</sect1>

<sect1>
<title>Introducing the Schematron</title>

<para>
This re-casting of validation as a reporting problem is a core insight of the Schematron (see Resources).  The Schematron is a validation and reporting methodology and toolkit developed by Rick Jeliffe who, interestingly enough, is a member of the W3C Schema working group.  Without denigrating the efforts of his group, Mr. Jeliffe has pointed out that XML Schemas may be too complex for many users, and approaches validation from the same old approach as DTD.  He developed the Schematron as a simple tool to harness the power of XPath, attacking the schema problem from a new angle.  As he put it on his site, "The Schematron differs in basic concept from other schema languages in that it not based on grammars but on finding tree patterns in the parsed document. This approach allows many kinds of structures to be represented which are inconvenient and difficult in grammar-based schema languages."
</para>

<para>
The Schematron is really no more than an XML vocabulary that can be used as an instruction set for generating stylesheets such as the one presented above.  For instance, the following, listing 5, is how our XPath-based validation might look like in The Schematron.
</para>

<screen>
<![CDATA[
<schema xmlns='http://www.ascc.net/xml/schematron'>
        <pattern name="Structural Validation">
                <!-- Use a hack to set the root context.  Necessary because of
                     a bug in the schematron 1.3 meta-transforms. -->
                <rule context="/*">
                        <assert test="../addr:ADDRBOOK">Validation error: there must be an ADDRBOOK element at the root of the document.</assert>
                </rule>
                <rule context="ENTRY">
                        <assert test="count(NAME) = 1">Validation error: <name/> element missing a NAME child.</assert>
                        <assert test="count(ADDRESS) = 1">Validation error: <name/> element missing an ADDRESS child.</assert>
                        <assert test="count(EMAIL) = 1">Validation error: <name/> element missing an EMAIL child.</assert>
                        <assert test="NAME[following-sibling::ADDRESS] and ADDRESS[following-sibling::PHONENUM] and PHONENUM[following-sibling::EMAIL]">Validation error: <name/> must have a NAME, ADDRESS, one or more PHONENUM, and an EMAIL in sequence</assert>
                        <assert test="count(NAME|ADDRESS|PHONENUM|EMAIL) = count(*)">Validation error: there is an extraneous element child of ENTRY</assert>
                </rule>
                <rule context="PHONENUM">
                        <assert test="@DESC">Validation error: <name/> must have a DESC attribute</assert>
                </rule>
        </pattern>
</schema>
]]>
</screen>

<para>
The root element in schematron is the schema element in the appropriate namespace.  It contains one or more patterns, each of which represents a conceptual grouping of declarations.  Patterns contain one or more rules, each of which sets a context for a series of declarations.  This is not only a conceptual context, but also the context that is used for the XPath expressions in declarations within each rule.
</para>

<para>
Each rule contains a collection of asserts, reports and keys.  You can see asserts at work in our example.  Asserts are similar to asserts in C.  They represent a declaration that a condition is true, and if it is not true, a signal is made to such effect.  In the Schematron, assert elements specify that if the condition in their test attribute is not true, the content of the assert elements will be copied to the result.  You'll note that the assert messages contain empty <screen>name</screen> elements.  This is a convenient short-hand for the name of the current context node, given by the parent rule element.  This makes it easy to reuse asserts from context to context.  Reports are similar to asserts, except that they output their contents when the condition in their test attribute is true rather than false.  They also allow the use of the empty name element.  Reports, as their name implies, tend to make sense for structural reporting tasks.  For instance, to implement our eariler example of reporting e-mail addresses in the .gov domain we might add the following rule to our Schematron:
</para>

<screen>
<![CDATA[
                <rule context="EMAIL">
                        <report test="contains(., '.gov') and not(substring-after(., '.gov'))">This address book contains government contacts.</report>
                </rule>
]]>
</screen>

<para>
Of course I already mentioned that namespaces are an important reason to seek a different validation methodology than DTDs.  Schematron supports namespaces through XPath's support for namespaces.  For instance, if we wanted to validate that all child elements of ENTRY in our address book document were in a particular namespace, we could do so so by adding an assert which checks the count of elements in a particular namespace.  Assume that the prefix "addr" is bound to the target namespace in the following example:
</para>

<screen>
count(addr:*) = count(*)
</screen>

<para>
Maybe that's too draconian for your practical needs and you want to also allow elements in a particular namespace reserved for extansions.
</para>

<screen>
count(addr:*) + count(ext:*) = count(*)
</screen>

<para>
Maybe rather than permitting a single particular extension namespace, you want to instead allow any elements with namespaces whose URI contains the string "extension":
</para>

<screen>
count(addr:*) + count(*[contains(namespace(.), 'extension')]) = count(*)
</screen>

<para>
With this latter addition and the addition of a report for e-mail addresses in the .gov address our schematron looks as follows, listing 6.
</para>

<screen>
<![CDATA[
<schema xmlns='http://www.ascc.net/xml/schematron'>

        <ns prefix='addr' uri='http://addressbookns.com'/>

        <pattern name="Structural Validation">
                <!-- Use a hack to set the root context.  Necessary because of
                     a bug in the schematron 1.3 meta-transforms. -->
                <rule context="/*">
                        <assert test="../addr:ADDRBOOK">Validation error: there must be an ADDRBOOK element at the root of the document.</assert>
                </rule>
                <rule context="addr:ENTRY">
                        <assert test="count(addr:*) + count(*[contains(namespace-uri(.), 'extension')]) = count(*)">
Validation error: all children of <name/> must either be in the namespace 'http://addressbookns.com' or in a namespace containing the substring 'extension'.
                        </assert>
                        <assert test="count(addr:NAME) = 1">
Validation error: <name/> element missing a NAME child.
                        </assert>
                        <assert test="count(addr:ADDRESS) = 1">
Validation error: <name/> element missing an ADDRESS child.
                        </assert>
                        <assert test="count(addr:EMAIL) = 1">
Validation error: <name/> element missing an EMAIL child.
                        </assert>
                        <assert test="addr:NAME[following-sibling::addr:ADDRESS] and addr:ADDRESS[following-sibling::addr:PHONENUM] and addr:PHONENUM[following-sibling::addr:EMAIL]">
Validation error: <name/> must have a NAME, ADDRESS, one or more PHONENUM, and an EMAIL in sequence
                        </assert>
                        <assert test="count(addr:NAME|addr:ADDRESS|addr:PHONENUM|addr:EMAIL) = count(*)">
Validation error: there is an extraneous element child of ENTRY
                        </assert>
                </rule>
                <rule context="addr:PHONENUM">
                        <assert test="@DESC">
Validation error: <name/> must have a DESC attribute
                        </assert>
                </rule>
        </pattern>
        <pattern name="Government Contact Report">
                <rule context="addr:EMAIL">
                        <report test="contains(., '.gov') and not(substring-after(., '.gov'))">
This address book contains government contacts.
                        </report>
                </rule>
        </pattern>
</schema>
]]>
</screen>

<para>
Note the new top-level element, ns.  We use this to declare the namespace that we'll be incorporating into the schematron rules.  If you have multiple such namespaces to declare, use one ns element for each.  Note that there are some advanced uses of schematron namespace declarations about which you can read on theSchematron site.
</para>

<para>
This was a pretty quick whirl through The Schematron.  This shouldn't be much of a problem since it is so simple.  However, for a bit more instruction, there is the tidy tutorial put together by Dr Miloslav Nic (see Resouces.  Note that the good Doctor has tutorials on many other XML-related topics at his page).  There are also a few examples linked from the Schematron home page.
</para>

</sect1>

<sect1>
<title>Putting The Schematron to Work</title>

<para>
So how do we use The Schematron?  Rememeber that a Schematron document could be thought of as a instructions for generating special validation and report transforms such as we introduced earlier.  This is in fact the most common way of using The Schematron in practice.  Conveniently enough, XSLT has all the power to convert Schematron specifications to XSLT-based validators.  There is a meta-transform available at the Schematron Web site which, when run against a schematron specification, will generate a specialized validator/reporter transform which can be then run against target source documents.  For instance, suppose I have the above schematron specification as "addrbook.schematron".  I can turn it into a validator/reporter transform as follows:
</para>

<screen>
[uogbuji@borgia code]$ 4xslt.py listing6.schematron ~/devel/Ft/Xslt/test_suite/borrowed/schematron-skel-ns.xslt > addrbook.validator.xslt
</screen>

<para>
Here and for all other examples in this article, I am using the 4XSLT processor.  4XSLT (see Resources) is an XSLT 1.0-compliant processor written in Python and distributed as open source by my company, Fourthought, Inc.  I ran the above from Linux and the first argument to 4xslt.py is the XML source document: in this case the schematron specification in listing 6.  The second argument is the transform to be used, in this case the Schematron namespace-aware meta-transform.  I then redirect the standard output to the file addrbook.validator.xslt, which thus becomes my validator/reporter transform.  I can then run the validator transform against the following source document, listing 7.
</para>

<screen>
<![CDATA[
<?xml version = "1.0"?>
<ADDRBOOK xmlns='http://addressbookns.com'>
        <ENTRY ID="pa">
                <NAME xmlns='http://bogus.com'>Pieter Aaron</NAME>
                <ADDRESS>404 Error Way</ADDRESS>
                <PHONENUM DESC="Work">404-555-1234</PHONENUM>
                <PHONENUM DESC="Fax">404-555-4321</PHONENUM>
                <PHONENUM DESC="Pager">404-555-5555</PHONENUM>
                <EMAIL>pieter.aaron@inter.net</EMAIL>
        </ENTRY>
        <ENTRY ID="en">
                <NAME xmlns='http://bogus.com'>Emeka Ndubuisi</NAME>
                <ADDRESS>42 Spam Blvd</ADDRESS>
                <PHONENUM DESC="Work">767-555-7676</PHONENUM>
                <PHONENUM DESC="Fax">767-555-7642</PHONENUM>
                <PHONENUM DESC="Pager">800-SKY-PAGEx767676</PHONENUM>
                <EMAIL>endubuisi@spamtron.com</EMAIL>
        </ENTRY>
</ADDRBOOK>
]]>
</screen>

<para>
Yielding the following output:
</para>

<screen>
[uogbuji@borgia code]$ 4xslt.py listing7.xml addrbook.validator.xslt 
Validation error: all children of ENTRY must either be in the namespace 'http://addressbookns.com' or in a namespace containing the substring 'extension'.Validation error: ENTRY element missing a NAME child.Validation error: ENTRY must have a NAME, ADDRESS, one or more PHONENUM, and an EMAIL in sequenceValidation error: there is an extraneous element child of ENTRYValidation error: all children of ENTRY must either be in the namespace 'http://addressbookns.com' or in a namespace containing the substring 'extension'.Validation error: ENTRY element missing a NAME child.Validation error: ENTRY must have a NAME, ADDRESS, one or more PHONENUM, and an EMAIL in sequenceValidation error: there is an extraneous element child of ENTRY
</screen>

<para>
Hmm.  Rather a mess, what?  Looks as if there were quite a few messages combined without clear separation.  There were actually two sets of messages, one for each ENTRY in the source document, since we caused the same cascade of validation errors in both by messing with the namespace of the NAME element.  The reason the two messages run together so is that we used the skeleton Schematron meta-transform.  The skeleton comes with only basic output support, and in particular, it normalizes space in all output, running the results together.
</para>

<para>
There's a good chance this is not what you want, and luckily Schematron is designed to be quite extensible.  There are several schematron meta-transforms on the Schematron home page that build on the skeleton by importing it.  They range from basic, clearer text messages to HTML for browser-integration.  Using the sch-basic meta-transform rather than the skeleton yields:
</para>

<screen>
[uogbuji@borgia code]$ 4xslt.py listing6.schematron ~/devel/Ft/Xslt/test_suite/borrowed/sch-basic.xslt > addrbook.validator.xslt
[uogbuji@borgia code]$ 4xslt.py listing7.xml addrbook.validator.xslt 
In pattern Structural Validation:
   Validation error: all children of ENTRY must either be in the namespace 'http://addressbookns.com' or in a namespace containing the substring 'extension'.
In pattern Structural Validation:
   Validation error: ENTRY element missing a NAME child.
In pattern Structural Validation:
   Validation error: ENTRY must have a NAME, ADDRESS, one or more PHONENUM, and an EMAIL in sequence
In pattern Structural Validation:
   Validation error: there is an extraneous element child of ENTRY
In pattern Structural Validation:
   Validation error: all children of ENTRY must either be in the namespace 'http://addressbookns.com' or in a namespace containing the substring 'extension'.
In pattern Structural Validation:
   Validation error: ENTRY element missing a NAME child.
In pattern Structural Validation:
   Validation error: ENTRY must have a NAME, ADDRESS, one or more PHONENUM, and an EMAIL in sequence
In pattern Structural Validation:
   Validation error: there is an extraneous element child of ENTRY

</screen>

<para>
To round things up, here is an example, listing 8, of a source document that validates cleanly against our sample schematron.
</para>

<screen>
<![CDATA[
<?xml version = "1.0"?>
<ADDRBOOK xmlns='http://addressbookns.com'>
        <ENTRY ID="pa">
                <NAME>Pieter Aaron</NAME>
                <ADDRESS>404 Error Way</ADDRESS>
                <PHONENUM DESC="Work">404-555-1234</PHONENUM>
                <PHONENUM DESC="Fax">404-555-4321</PHONENUM>
                <PHONENUM DESC="Pager">404-555-5555</PHONENUM>
                <EMAIL>pieter.aaron@inter.net</EMAIL>
        </ENTRY>
        <ENTRY ID="en">
                <NAME>Manfredo Manfredi</NAME>
                <ADDRESS>4414 Palazzo Terrace</ADDRESS>
                <PHONENUM DESC="Work">888-555-7676</PHONENUM>
                <PHONENUM DESC="Fax">888-555-7677</PHONENUM>
                <EMAIL>mpm@scudetto.dom.gov</EMAIL>
        </ENTRY>
</ADDRBOOK>
]]>
</screen>

<para>
Which we test as follows.
</para>

<screen>
[uogbuji@borgia code]$ 4xslt.py listing8.xml addrbook.validator.xslt 
In pattern Government Contact Report:
   This address book contains government contacts.

</screen>

<para>
Now everything is in the correct namespace so we get no validation errors.  However, notice that we did get the report from the e-mail address in the .gov domain.
</para>

<para>
This is all very well, but no doubt you're wondering whether XSLT is fast enought to suit your real-world validation needs.  This will of course depend on your needs.  In my experience, it is very rarely necessary to validate a document every time it is processed.  If you have attributes with default value, or you have no control at all over the sources of your data throughout your processing applications then you may have no choice.  In this case, validation by an XML 1.0-compliant validating parser such as xmlproc (see Resources) is almost certainly faster than XSLT-based Schematron.  But then again, there is no hard requirement that a Schematron processor use XSLT.  It would not be terribly difficult, given an efficient XPath library, to write a specialized Schematron application that doesn't need translation from meta-transforms.
</para>

<para>
But just to give a quick comparison, I parsed a 170K address book example similar to the above but with more entries.  Using xmlproc and DTD validation it took 7.25 seconds.  Parsing this document without validation and then applying the schematron transform took 10.61 seconds.  Hardly so great a penalty.
</para>

<para>
Of course there are several things that DTDs provide that Schematron cannot.  The most notable are entity and notation definitions and fixed or default attribute values.  RELAX does not provide any of these facilities either, but XML Schemas do provide all of them as it must since it is positioned as a DTD replacement.  RELAX makes no such claim and indeed the RELAX documentation has a section on using RELAX in concert with DTD.  We have already discussed that Schematron, far from claiming to be a DTD replacement, is positioned as an entirely fresh approach to validation.  Nevertheless, attribute-value defaulting can be a useful way to reduce the clutter of XML documents for human readability so we shall examine one way to provide default attributes in association with Schematron.
</para>

<para>
Remember that you're always free to combine DTD with Schematron to get the best of both worlds, but if you want to to leave DTD entirely behind, you can still get attribute-defaulting at the cost of one more pass through the document when the values are to be substituted.  This can easily be done by a transform that turns a source document to a result that is identical except that all default attribute values are given.
</para>

<para>
There are other features of Schematron for those interested in further exploration.  For instance it supports keys: a mechanism similar to DTD's ID and IDREF.  There are some hooks for embedding and control through external applications.  Certainly a more formal introduction to Schematron is available in the Schematron specification (see Resources).
</para>

</sect1>

<sect1>
<title>Conclusion</title>

<para>
We at Fourthought pretty much stopped using DTD about a year ago when we started using namespaces in earnest.  We soon seized on Schematron and have used it in deployed work product for our clients and internally.  Since we already do a lot of work with XSLT it's a very comfortable system and the training required for XPath isn't much of an issue.  To match most of the basic features of DTD, not much more knowledge should be required than path expressions, predicates, unions, the sibling and attribute axes, and a handful of functions such as count.  Performance has not been an issue because we typically have strong control over XML data in our systems and hardly ever use defaulted attributes.  This allows us to validate only when a new XML datum is input, or an existing datum modified our systems, reducing performance concerns.
</para>

<para>
Schematron is a clean, well-considered approache to the problems of validation and simple reporting.  XML Schemas are a significant development, but it is debatable whether such an entirely new and complex system is required for such a straightforward task as validation.  RELAX and The Schematron both present simpler approaches coming from different angles and they might be a better fit for quick integration into XML systems.  In any case, Schematron once again demonstrates the extraordinary reach of XSLT and the flexibility of XML in general as a data-management technology.
</para>

</sect1>

<sect1>
<title>Resources</title>

<glosslist>
<glossterm>RELAX XML Schema System</glossterm><glossdef>http://www.xml.gr.jp/relax/</glossdef>
<glossterm>W3C XML Schemas: Primer</glossterm><glossdef>http://www.w3.org/TR/xmlschema-0/</glossdef>
<glossterm>W3C XML Schemas Part 1: Structures</glossterm><glossdef>http://www.w3.org/TR/xmlschema-1/</glossdef>
<glossterm>W3C XML Schemas Part 2: Datatypes</glossterm><glossdef>http://www.w3.org/TR/xmlschema-2/</glossdef>
<glossterm>DTD2RELAX</glossterm><glossdef>http://www.horobi.com/Projects/RELAX/Archive/DTD2RELAX.html</glossdef>
<glossterm>The Schematron home page</glossterm><glossdef>http://www.ascc.net/xml/resource/schematron/schematron.html</glossdef>
<glossterm>Rick Jelliffe's Comparison of Various Schema Methods</glossterm><glossdef>http://www.ascc.net/%7ericko/XMLSchemaInContext.html</glossdef>
<glossterm>4XSLT</glossterm><glossdef>http://www.fourthought.com/4XSLT</glossdef>
<glossterm>4Suite</glossterm><glossdef>http://www.fourthought.com/4Suite</glossdef>
<glossterm>Schematron Tutorial</glossterm><glossdef>http://www.zvon.org/HTMLonly/SchematronTutorial/General/contents.html</glossdef>
<glossterm>Other ZVON Tutorials for XML-related topics</glossterm><glossdef>http://www.zvon.org/</glossdef>
<glossterm>The Schematron Specification</glossterm><glossdef>http://www.ascc.net/xml/resource/schematron/Schematron2000.html</glossdef>
<glossterm>General news, product info, etc. concerning XSLT</glossterm><glossdef>http://www.xslt.com</glossdef>
<glossterm>General news, product info, etc. concerning XML</glossterm><glossdef>http://www.xmlhack.com</glossdef>
<glossterm>Slides from an XSLT introduction by the author</glossterm><glossdef>http://fourthought.com/Presentations/xmlforum-xslt-20000830</glossdef>
<glossterm>The XSLT FAQ</glossterm><glossdef>http://www.dpawson.freeserve.co.uk/xsl/xslfaq.html</glossdef>
<glossterm>Zvon XSLT Reference</glossterm><glossdef>http://www.zvon.org/xxl/XSLTreference/Output/index.html</glossdef>
<glossterm>Zvon DTD tutorial</glossterm><glossdef>http://www.zvon.org/xxl/DTDTutorial/General/book.html</glossdef>
<glossterm>Zvon namespace tutorial</glossterm><glossdef>http://www.zvon.org/xxl/NamespaceTutorial/Output/index.html</glossdef>
<glossterm>Zvon XML tutorial</glossterm><glossdef>http://www.zvon.org/xxl/XMLTutorial/General/book_en.html</glossdef>
<glossterm>Zvon XPath tutorial</glossterm><glossdef>http://www.zvon.org/xxl/XPathTutorial/General/examples.html</glossdef>
<glossterm>Zvon XSLT tutorial</glossterm><glossdef>http://www.zvon.org/xxl/XSLTutorial/Books/Book1/index.html</glossdef>
<glossterm>Links related to architectural forms</glossterm><glossdef>http://www.xml.com/pub/Guide/Architectural_Forms</glossdef>
</glosslist>

</sect1>

<!-- Append another article -->

<sect1>

<para>
On re-reading my first two XML articles, just over a year ago in this journal and in its sister, Sunworld, I'm struck by how much they represented a justification of XML as the great tin opener of closed data formats.  In under a year, it looks as if all the light-bulbs went on at once.  XML is in the computer news every day, every company seems to be scrambling to ink XML into their brochures, and XML standards organizations such as the World-Wide Web consortium (W3C) practically have to turn people away.  At this point I hardly think any more justification of XML for open data exchange is required.  It's pretty much a fact of information technology.  The remaining questions are how to use XML to solve real problems better than with any other means.
</para>

<para>
As I mentioned in my most recent article, the W3C and other standards organizations are working very quickly to complete specifications for technologies complementary to XML.  I mentioned namespaces, which are a key facility for managing global names and are now used in almost every XML technology.  I also mentioned DOM and XSLT.  Since then, XLink, XPointer, XML Schemas, SVG and other specs are almost complete.  I shall discuss these later in the series as well as RDF, Schematron and other beasts in the XML menagerie.  The XML community has also matured greatly, and as one example, there are many new, high-quality information and news sites, some of which I list in Resources section.  If you are highly interested in XML, I highly recommend regular visits to xmlhack, in particular.
</para>

</sect1>

<sect1>
<title>The Triumph of Open Standards</title>

<para>
The most amazing thing about XML's incredible rise, in my opinion sharper than that of the PC, Java, or even the Web, is the fact that it has remained as open as when it started.  Even though XML in its early days was positioned as a tool for encouraging data interchange by providing both human and machine readibility, odds always were that a powerful company, or group of companies would foul the waters.  Many vertical industries such as the automobile inustry (which recently surprised analysts by announcing a huge, XML-driven on-line exchange), health-care and chemicals have been moving to XML as data-exchange format.  If the likes of Microsoft (early and on-going XML champion) and Oracle, could co-opt standards for XML processing, they could gain even more domination than they currently had in such industries, all under the guise of openness.  The perfect monopolistic trojan horse.
</para>

<para>
And this was never just an idle menace.  Last year, Microsoft nearly suceeded in derailing XSLT by bundling a mutation of XSLT into its Internet Explorer 5 browser which was different from the emerging standards, and laden with Microsoft extensions.  Many Linux advocates cried loudly over Microsoft's "embrace-extend-extinguish" move on Kerberos, but this was a weak jab compared to the MS-XSL ploy.  Since Internet Explorer is by far the most popular browser, Microsoft ensured that most of the world's experience of XSLT came through their own proprietary version, and nearly made this proprietary version the de-facto standard.  There was many a flame-war on the xsl-list mailing list (see Resources) when IE users arrived in droves asking questions about what they perceived to be proper XSLT.
</para>

<para>
But then something surprising happened.  Microsoft started to hear loudly and clearly from its customers that they didn't want an MS flavor of XSLT.  They wanted the standard.  The first signs of this were that Microsoft slowly started migrating to the standard in Internet Explorer updates.  Then MS developers announced publicly that their design goal was now full compliance with the XSLT standard.  Finally, after some prodding on xsl-list, several of Microsoft's developers admitted that they had been receiving numerous e-mail messages asking them to get in line.
</para>

<para>
Now I know Linux users aren't used to expecting such sophistication and independent thought from large numbers of MS users, and I'm no exception to that (possibly bigoted) attitude.  I credit this remarkable episode to the power of the promise of openness in XML.  Of course, this doesn't prevent Microsoft from amusing gaffes such as claiming to have invented XML (as reported by The Washington Post in May), but such things are far less dangerous than standards pollution..
</para>

<para>
Similar stories are repeated over and over throughout XML's brief history.  In fact, Microsoft, not having learned all its lessons from the XSLT fiasco, is currently being bludgeoned into abandoning its proprietary XML schema format, XML-Data, in favor of XML Schemas, which has come almost all the way through the W3C standards track.  The battle hit fever pitch with Microsoft's loud announcement of BizTalk, an ambitious repository and toolkit for XML schemas.  But day by day, it looks more as if the open standard will win out.
</para>

<para>
But enough about the wide, wild world.  Let's have a look at what's happening at home.  Another striking change from my first XML article in these Web pages is that I pretty much had to apologize for the lack of XML tools for Linux.  This problem has been corrected to an astonishing degree.
</para>

<para>
This article briefly introduces a selection of XML tools for Linux in a few basic categories: parsers, web servers, application servers, GUIs and bare-bones tools.  Most users' introduction to XML will be for purposes of better managing Web pages, from which they may choose to migrate to complete, all-inclusive appication servers or construct custom systems from the various XML toolkits available and the usual UNIX duct tape and wire ties.  In all cases there is usually some content to manage, and though you may see no reason to leave the world of Emacs or vi to churn out documents, since content-managers are often non-technical, it's a very good thing that there is a good selection of GUI XML editors for all tastes.
</para>

</sect1>

<sect1>
<title>Just the Parsers, Ma'am</title>

<para>
XML processing starts with the parser, and Linux has many to choose from.  Basically all you have to do is pick a language.  C, C++, Java, Python, PHP, Perl, TCL, or even Javascript (and this is hardly an exhaustive list).  The next thing to choose is whether and how to validate your XML documents.  Validation is the process of ensuring that all the elements and attributes in an XML document conform to a schema.  The traditional XML validation method is the Document-Type Definition (DTD).  The W3C, as I mentioned, has almost completed XML Schemas, which have the advantages of XML format (DTDs are in a different format) and "modern" data-typing, with the disadvantage of complexity and immaturity.
</para>

<para>
C users are well served by the old standby from James Clark, Expat, which is a barebones parser and arguably the fastest in existence, but provides no validation.  Significantly, almost every language under the sun, from Python to Eiffel, provides a front-end to Expat.  But even Expat is facing some tough "coopetition" from entries such as the capable libxml project, led by Daniel Viellard of the W3C.  This library, most prominently used in GNOME, offers many options for fine-tuning parsing, and supports DTD validation.  There is also Richard Tobin's RXP, which supports DTD.  C++ users have Xerces-C++, which is based on XML4C code IBM donated to the Apache/XML project.  Xerces-C++ supports both DTD and Schemas.  In fact, if you want to start using XML Schemas in Linux, Xerces is probably your best bet.  Individual efforts include Michael Fink's xmlpp, which is quite new and doesn't support validation.
</para>

<para>
There is a Java version of Xerces with similar pedigree.  Java users are pretty much drowned in choice.  The media has made much of the "marriage" between Java and XML, but the most likely explanation for the huge number of XML tools for Java is that XML emerged right as Java was cresting as a programming language.  Besides Xerces-J, there are Java parsers from Oracle, Sun, DataChannel, and others.  Individual efforts include Thomas Weidenfeller's XMLtp (Tiny XML Parser), which is designed for embedding into other Java apps (as was the pioneering but now moribund Aelfred from Microstar).  Mr. Weidenfeller also provides one of the neatest summaries of OSS license I've seen: "Do what you like with the software, but don't sue me".  Then there is The Wilson Partnership's MinML, designed to be even smaller, for use in embedded systems.
</para>

<para>
Python still has the growing and evolving PyXML package as well as my own company's 4Suite.  XML considerations are helping shape many grand trends of Python such as unicode support and improved memory-management.  The perl community has definitely taken to XML.  The main parser is, appropriately, XML::Parser, but you can pretty much take any XML buzzword, prepend "XML::", and find a corresponding perl package.
</para>

</sect1>

<sect1>
<title>Serving up XML Pages</title>

<para>
XML's early promise to the media was as a way to tame the Web.  Structured documents, separation of content from presentation, and more manageable searching and autonomous Web agents.  Some of this has been drowned out by all the recent interest in XML for database integration and message-based middleware, but XML is still an excellent way to manage structured content on the Web.  And Linux is a pretty good operating system on which to host the content. 
</para>

<para>
The big dog among the XML Web servers is also the well known big dog of Web servers, period.  Apache is absolutely swarming with XML activity lately.  I've already mentioned Xerces, the XML parser from the Apache/XML project.  There is also an XSLT processor, Xalan, with roots in IBM/Lotus's LotusXSL.  There is also Formatting-Object Processor (FOP), a tool for converting XML documents to the popular PDF document, by way of XSL formatting objects, a special XML vocabulary for presentation.  Apache has added support for the Simple Object Access Protocol (SOAP), an XML messaging protocol that can be used to make HTTP-based queries to a server in an XML format.  As a side note, SOAP, and open protocol, is heavily contributed to and championed by Microsoft, in one of the many positive contributions that company has made to XML while not trying to embrace and extend.
</para>

<para>
These bits and pieces are combined into an Apache-based XML Web publishing solution called Cocoon.  Cocoon allows XML documents to be developed, and then published on the Web, for wireless applications through Wireless Application Protocol (WAP), and to print-ready PDF format through FOP.
</para>

<para>
Perl hackers already have the proliferation of "XML::*" packages I've already mentioned, but Matt Sergeant has also put together a comprehensive toolkit for XML processing: Axkit.  Axkit is specialized for use with Apache and mod_perl, and provides XSLT transformation as well as other non-standard transform approaches such as "XPathScript".
</para>

</sect1>

<sect1>
<title>Full-blown application servers</title>

<para>
Enterprises that want an end-to-end solution for developing and deploying applications using XML data have several options under Linux.  Application servers build on basic Web servers such as described above by adding database integration, version control, distributed transactions and other such facilities.
</para>

<para>
The grey and respectable Hewelett Packard found an open-source, Web-hip side with its e-speak project, a tool for distributed XML applications with Java, Python and C APIs for development and extension.
</para>

<para>
A smaller company that has found the advantages of open-source for promoting its XML services is Lutris, Inc., developers of Enhydra.  Enhydra, about which I've reported in a previous LinuxWorld article, is a Java application server for XML processing.  It has some neat innovations such as XMLC, a way to "compile" XML into an intermediate binary form for efficient processing.  It is also one of the first open-source implementations of Java 2's Enterprise Edition services, including Enterprise JavaBeans.
</para>

<para>
XML Blaster is a messaging-oriented middleware (MOM) suite for XML applications.  It uses an XML transport in a publish/subscribe system for exchanging text and binary data.  It uses CORBA for network and inter-process communication and supports components written in Java, Perl, Python and TCL.
</para>

<para>
Conglomerate, developed by Styx, is a somewhat less ambitious but interesting project for an XML application server more attuned for document management.  It includes a nifty GUI editor and provides a proprietary transformation language that can generate HTML, TeX and other formats.
</para>

</sect1>

<sect1>
<title>Oo-wee!  GUI!</title>

<para>
One area in which I lamented Linux's lag in XML tools last year was in the area of GUI browsers and editors.  While I personally use a 4XSLT script and XEmacs for these respective tasks, I frequently work with clients who want to use more friendly GUIs for XML editing and ask whether my preferred Linux platform has anything available.  Fortunately, there are more choices than ever on our favorite OS.  Again much of the succour comes in the form of Java's cross-platform GUI support.
</para>

<para>
GEXml is a Java XML editor which allows programmers use pluggable Java modules for editing their own special tag sets.  It uses a pretty standard layout for XML editors: a multi-pane window with a section for the tree-view, and sections for attributes and a section for CDATA.
</para>

<para>
Merlot, by Channelpoint, Inc., is another Java-based XML editor that emphasizes modeling XML documents around their DTDs, abstracting the actual XML file from the user.  It supports pluggable extension modules for custom DTDs.
</para>

<para>
Lunatech's Morphon is yet another DTD-based XML editor and modeling tool.  Hopefully all these DTD-based tools will expand to accommodate XML schemas and other validation methods as well in order to make life easier for those of us who use XML namespaces.  Morphon is similar to the other editors described here with a couple of nice twists: it allows you to specify cascading stylesheets for the editor appearance and document preview, and it mixes the ubiquitous tree view with a friendly view of the XML document being edited.  Morphon, however, is not open-source, though available for Linux.
</para>

<para>
IBM's Alphaworks keeps on churning out free (beer) XML tools, one of which, XML Viewer, allows users to view XML documents using (once again) the tree-view and specialized panes for element and attribute data.  XML Viewer is written in Java.  It also allows linking the XML source and DTD to allow viewing such items as element and attribute definitions.  There is also XSL Editor, a specialized java-based XML editor for XSLT stylesheets.  It also incorporates advanced features such as syntax highlighting and an XSLT debugger.
</para>

<para>
TreeNotes is an XML text editor that uses a series of widgets to open up XML's tree structure, elements and attributes, and of course character data, to editing.
</para>

<para>
DocZilla is an interesting project: an extension of the Mozilla project for Web-based XML document applications.  It promises XML browsing support on par with Internet Explorer's including an extension and plug-in framework.  DocZilla started out very strongly, but now seems to have lagged a bit.  Part of the reason might be that Mozilla is increasing its XML focus.  Mozilla has always supported XML+Cascading Style-Sheets (CSS), but now, with Transformiix (an XSLT processor for Mozilla) and other such projects, it is making its own bid to replace Explorer as king of XML browsers.
</para>

<para>
There is also KXMLViewer, a KDE XML viewer written in Python, but I'll cover this in more detail when I discuss GNOME and KDE XML support in a coming article in this series.
</para>

</sect1>

<sect1>
<title>In the Hacker Spirit</title>

<para>
So we've looked at lumbering app servers and pretty GUI tools.  All very nice for easing into XML, but we all know that Linux (and UNIX) users typically prefer sterner stuff.  Small, manageable, versatile, no-nonsense packages that can be strung together to get a larger job done.  Luckily for the desperate hacker, the nuts-and-bolts toolkit is growing just as quickly as the rest of XML space.
</para>

<para>
A key and quite mature entry is LT XML, developed by the Edinburgh Language Technology Group.  LT XML is a set of stand-along tools and libraries for C programmers using XML.  It supports both tree-based and stream-oriented processing, covering a wide variety of application types.  The LT XML repertoire would be quite familiar and pleasant to those who love nothing more than to string together GNU textutils to produce some neat text transformation.  There is the mandatory XML-aware grep, sggrep (the "sg" for SGML), as well as sgsort, sgcount, sgtoken, etc, which should be self-explanatory.  Python bindings for LT XML should be available by the time you read this.
</para>

<para>
Speaking of grep, there is also fxgrep, a powerful XML querying tool written in Standard ML, a well-regarded functional programming language from Bell Labs (XML provides a rather fitting problem space for functional languages).  fxgrep uses the XML parser fxp, also written in SML.  fxgrep supports specialized XML searching and query using its own pattern syntax.
</para>

<para>
Paul Tchistopolskii makes clear there is no mistake as to his target user-base for Ux: "Ux is UNIX, revisited with XML".  Ux is a set of small XML components written in Java (OK, we're leaking some UNIX heritage right there).  The components are designed to be piped together for database storage and extraction, XSLT transformation, query, etc.
</para>

<para>
Pyxie is an XML parsing and processing toolkit in Python by Sean McGrath and highlighted in his book, <emph>XML Processing with Python</emph>.  Pyxie's main distiction is that it builds on earlier work by James Clark by focusing on a line-based view of XML rather than the "natural" tokens that emerge from the spec.  This can provide a useful optimization if occasional complications.
</para>

<para>
For those looking askance at XML in a TeX environment, IBM's Alphaworks might have a useful introduction.  TeXML is a tool that allows you to define an XSLT transform for converting XML files to a specialized vocabulary, the results of which are converted to TeX.  Also, thanks to Alphaworks, there is an XML diff as well as a grep.  XML Tree Diff shows the differences between documents based on their DOM tree representation.  It's more of a collection of Javabeans for performing diffs than a stand-alone application, but it's relatively straightforward to use.
</para>

<para>
And there is my own company's 4Suite, a set of libraries for Python users to construct their own XML applications using DOM, XPath and XSLT, among other tools.  I covered 4XSLT in my last XML article (though the spec and 4XSLT have changed since then), and 4Suite libraries are now standard components in the Python XML distribution.
</para>

</sect1>

<sect1>
<title>Conclusion</title>

<para>
Hopefully this tour will help find XML resources for Linux users of all levels.  In upcoming articles (hopefully not as delayed as this one), I shall cover XML and Databases, XML and KDE/GNOME, and mnore topics on how to put XML to work in a Linux environment.
</para>

<para>
By the way this very article is available in XML form (using the DocBook standard).  I've also put up a simplified DocBook XSLT stylesheet that can be used to render this article to HTML (see Resources for both).  Note that I use the "doc" file extension for DocBook files.  I encourage you to use DocBook (O'Reilly and Associates publishes an excellent book on the topic by Norman Walsh) and the ".doc" extension, chopping at the hegemony of the proprietary Microsoft Word format.  Just another small way XML can open up data to the world.
</para>

</sect1>

<sect1>
<title>Resources</title>

<sect2>
<title>Parsers</title>

<glosslist>
<glossterm>Expat</glossterm><glossdef>http://www.jclark.com/xml/expat.html</glossdef>
<glossterm>Xerces C++</glossterm><glossdef>http://xml.apache.org/xerces-c/index.html</glossdef>
<glossterm>Xerces-Java</glossterm><glossdef>http://xml.apache.org/xerces-j/index.html</glossdef>
<glossterm>xmlpp</glossterm><glossdef>http://www.vividos.de/xmlpp/</glossdef>
<glossterm>libxml</glossterm><glossdef>http://www.xmlsoft.org/</glossdef>
<glossterm>RXP</glossterm><glossdef>http://www.cogsci.ed.ac.uk/~richard/rxp.html</glossdef>
<glossterm>XMLtp</glossterm><glossdef>http://mitglied.tripod.de/xmltp/</glossdef>
<glossterm>MinML</glossterm><glossdef>http://www.wilson.co.uk/xml/minml.htm</glossdef>
</glosslist>

</sect2>

<sect2>
<title>Web Servers</title>

<glosslist>
<glossterm>Axkit</glossterm><glossdef>http://axkit.org/</glossdef>
<glossterm>XML/Apache</glossterm><glossdef>http://xml.apache.org</glossdef>
</glosslist>

</sect2>

<sect2>
<title>App Servers</title>

<glosslist>
<glossterm>Conglomerate</glossterm><glossdef>http://www.conglomerate.org/</glossdef>
<glossterm>e-speak</glossterm><glossdef>http://www.e-speak.net/</glossdef>
<glossterm>Enhydra</glossterm><glossdef>http://www.enhydra.org/</glossdef>
<glossterm>XML Blaster</glossterm><glossdef>http://www.xmlBlaster.org/</glossdef>
</glosslist>

</sect2>

<sect2>
<title>Low-Level Tools</title>

<glosslist>
<glossterm>LT XML</glossterm><glossdef>http://www.ltg.ed.ac.uk/software/xml/index.html</glossdef>
<glossterm>fxgrep</glossterm><glossdef>http://www.informatik.uni-trier.de/~neumann/Fxgrep/</glossdef>
<glossterm>Ux</glossterm><glossdef>http://www.pault.com/Ux/</glossdef>
<glossterm>Pyxie</glossterm><glossdef>http://www.digitome.com/pyxie.html</glossdef>
</glosslist>

</sect2>

<sect2>
<title>GUIs</title>

<glosslist>
<glossterm>TreeNotes</glossterm><glossdef>http://pikosoft.dragontiger.com/en/treenotes/</glossdef>
<glossterm>DocZilla</glossterm><glossdef>http://www.doczilla.com/</glossdef>
<glossterm>GEXml</glossterm><glossdef>http://gexml.cx/</glossdef>
<glossterm>Merlot</glossterm><glossdef>http://www.merlotxml.org/</glossdef>
<glossterm>Morphon</glossterm><glossdef>http://www.morphon.com/</glossdef>
</glosslist>

</sect2>

<sect2>
<title>Et Cetera</title>

<glosslist>
<glossterm>There is more to XML than roll-your-own HTML</glossterm><glossdef>http://www.linuxworld.com/linuxworld/lw-1999-03/lw-03-xml.html</glossdef>
<glossterm>Practical XML with Linux, Part 1</glossterm><glossdef>http://www.linuxworld.com/linuxworld/lw-1999-09/lw-09-xml2.html</glossdef>
<glossterm>The xsl-list mailing list</glossterm><glossdef>http://www.mulberrytech.com/xsl/xsl-list</glossdef>
<glossterm>DocBook and stylesheet for this article</glossterm><glossdef>http://www.Fourthought.com/Publications/lw-xml2</glossdef>
<glossterm>The Apache/XML Project</glossterm><glossdef>http://xml.apache.org/</glossdef>
<glossterm>SOAP</glossterm><glossdef>http://www.w3.org/TR/SOAP/</glossdef>
<glossterm>xmlhack</glossterm><glossdef>http://www.xmlhack.com</glossdef>
<glossterm>XML Pit Stop</glossterm><glossdef>http://www.xmlpitstop.com/</glossdef>
<glossterm>xslt.com</glossterm><glossdef>http://www.xslt.com</glossdef>
<glossterm>XML Times</glossterm><glossdef>http://www.xmltimes.com/</glossdef>
<glossterm>The XML Cover Pages</glossterm><glossdef>http://www.oasis-open.org/cover</glossdef>
<glossterm>IBM's Alphaworks (including XML Viewer, XSL Edirot, XML Tree Diff and TeXML)</glossterm><glossdef>http://alphaworks.ibm.com</glossdef>
</glosslist>

</sect2>

</sect1>

</article>

"""



expected_1 = """\
<HTML xmlns:doc="http://docbook.org/docbook/xml/4.0/namespace">
  <HEAD>
    <META HTTP-EQUIV='Content-Type' CONTENT='text/html; charset=ISO-8859-1'>
    <TITLE>Practical XML with Linux, Part 3: A survey of the tools</TITLE>
    <META CONTENT='text/html' charset='UTF-8' HTTP-EQUIV='content-type'>
    <META NAME='author' CONTENT='Uche Ogbuji'>
  </HEAD>
  <BODY>
    <H1>Practical XML with Linux, Part 3: A survey of the tools</H1>
    <H3></H3>
    <P>
On re-reading my first two XML articles, just over a year ago in this journal and in its sister, Sunworld, I'm struck by how much they represented a justification of XML as the great tin opener of closed data formats.  In under a year, it looks as if all the light-bulbs went on at once.  XML is in the computer news every day, every company seems to be scrambling to ink XML into their brochures, and XML standards organizations such as the World-Wide Web consortium (W3C) practically have to turn people away.  At this point I hardly think any more justification of XML for open data exchange is required.  It's pretty much a fact of information technology.  The remaining questions are how to use XML to solve real problems better than with any other means.
</P>
    <P>
As I mentioned in my most recent article, the W3C and other standards organizations are working very quickly to complete specifications for technologies complementary to XML.  I mentioned namespaces, which are a key facility for managing global names and are now used in almost every XML technology.  I also mentioned DOM and XSLT.  Since then, XLink, XPointer, XML Schemas, SVG and other specs are almost complete.  I shall discuss these later in the series as well as RDF, Schematron and other beasts in the XML menagerie.  The XML community has also matured greatly, and as one example, there are many new, high-quality information and news sites, some of which I list in Resources section.  If you are highly interested in XML, I highly recommend regular visits to xmlhack, in particular.
</P>
    <H3>The Triumph of Open Standards</H3>
    <P>
The most amazing thing about XML's incredible rise, in my opinion sharper than that of the PC, Java, or even the Web, is the fact that it has remained as open as when it started.  Even though XML in its early days was positioned as a tool for encouraging data interchange by providing both human and machine readibility, odds always were that a powerful company, or group of companies would foul the waters.  Many vertical industries such as the automobile inustry (which recently surprised analysts by announcing a huge, XML-driven on-line exchange), health-care and chemicals have been moving to XML as data-exchange format.  If the likes of Microsoft (early and on-going XML champion) and Oracle, could co-opt standards for XML processing, they could gain even more domination than they currently had in such industries, all under the guise of openness.  The perfect monopolistic trojan horse.
</P>
    <P>
And this was never just an idle menace.  Last year, Microsoft nearly suceeded in derailing XSLT by bundling a mutation of XSLT into its Internet Explorer 5 browser which was different from the emerging standards, and laden with Microsoft extensions.  Many Linux advocates cried loudly over Microsoft's "embrace-extend-extinguish" move on Kerberos, but this was a weak jab compared to the MS-XSL ploy.  Since Internet Explorer is by far the most popular browser, Microsoft ensured that most of the world's experience of XSLT came through their own proprietary version, and nearly made this proprietary version the de-facto standard.  There was many a flame-war on the xsl-list mailing list (see Resources) when IE users arrived in droves asking questions about what they perceived to be proper XSLT.
</P>
    <P>
But then something surprising happened.  Microsoft started to hear loudly and clearly from its customers that they didn't want an MS flavor of XSLT.  They wanted the standard.  The first signs of this were that Microsoft slowly started migrating to the standard in Internet Explorer updates.  Then MS developers announced publicly that their design goal was now full compliance with the XSLT standard.  Finally, after some prodding on xsl-list, several of Microsoft's developers admitted that they had been receiving numerous e-mail messages asking them to get in line.
</P>
    <P>
Now I know Linux users aren't used to expecting such sophistication and independent thought from large numbers of MS users, and I'm no exception to that (possibly bigoted) attitude.  I credit this remarkable episode to the power of the promise of openness in XML.  Of course, this doesn't prevent Microsoft from amusing gaffes such as claiming to have invented XML (as reported by The Washington Post in May), but such things are far less dangerous than standards pollution..
</P>
    <P>
Similar stories are repeated over and over throughout XML's brief history.  In fact, Microsoft, not having learned all its lessons from the XSLT fiasco, is currently being bludgeoned into abandoning its proprietary XML schema format, XML-Data, in favor of XML Schemas, which has come almost all the way through the W3C standards track.  The battle hit fever pitch with Microsoft's loud announcement of BizTalk, an ambitious repository and toolkit for XML schemas.  But day by day, it looks more as if the open standard will win out.
</P>
    <P>
But enough about the wide, wild world.  Let's have a look at what's happening at home.  Another striking change from my first XML article in these Web pages is that I pretty much had to apologize for the lack of XML tools for Linux.  This problem has been corrected to an astonishing degree.
</P>
    <P>
This article briefly introduces a selection of XML tools for Linux in a few basic categories: parsers, web servers, application servers, GUIs and bare-bones tools.  Most users' introduction to XML will be for purposes of better managing Web pages, from which they may choose to migrate to complete, all-inclusive appication servers or construct custom systems from the various XML toolkits available and the usual UNIX duct tape and wire ties.  In all cases there is usually some content to manage, and though you may see no reason to leave the world of Emacs or vi to churn out documents, since content-managers are often non-technical, it's a very good thing that there is a good selection of GUI XML editors for all tastes.
</P>
    <H3>Just the Parsers, Ma'am</H3>
    <P>
XML processing starts with the parser, and Linux has many to choose from.  Basically all you have to do is pick a language.  C, C++, Java, Python, PHP, Perl, TCL, or even Javascript (and this is hardly an exhaustive list).  The next thing to choose is whether and how to validate your XML documents.  Validation is the process of ensuring that all the elements and attributes in an XML document conform to a schema.  The traditional XML validation method is the Document-Type Definition (DTD).  The W3C, as I mentioned, has almost completed XML Schemas, which have the advantages of XML format (DTDs are in a different format) and "modern" data-typing, with the disadvantage of complexity and immaturity.
</P>
    <P>
C users are well served by the old standby from James Clark, Expat, which is a barebones parser and arguably the fastest in existence, but provides no validation.  Significantly, almost every language under the sun, from Python to Eiffel, provides a front-end to Expat.  But even Expat is facing some tough "coopetition" from entries such as the capable libxml project, led by Daniel Viellard of the W3C.  This library, most prominently used in GNOME, offers many options for fine-tuning parsing, and supports DTD validation.  There is also Richard Tobin's RXP, which supports DTD.  C++ users have Xerces-C++, which is based on XML4C code IBM donated to the Apache/XML project.  Xerces-C++ supports both DTD and Schemas.  In fact, if you want to start using XML Schemas in Linux, Xerces is probably your best bet.  Individual efforts include Michael Fink's xmlpp, which is quite new and doesn't support validation.
</P>
    <P>
There is a Java version of Xerces with similar pedigree.  Java users are pretty much drowned in choice.  The media has made much of the "marriage" between Java and XML, but the most likely explanation for the huge number of XML tools for Java is that XML emerged right as Java was cresting as a programming language.  Besides Xerces-J, there are Java parsers from Oracle, Sun, DataChannel, and others.  Individual efforts include Thomas Weidenfeller's XMLtp (Tiny XML Parser), which is designed for embedding into other Java apps (as was the pioneering but now moribund Aelfred from Microstar).  Mr. Weidenfeller also provides one of the neatest summaries of OSS license I've seen: "Do what you like with the software, but don't sue me".  Then there is The Wilson Partnership's MinML, designed to be even smaller, for use in embedded systems.
</P>
    <P>
Python still has the growing and evolving PyXML package as well as my own company's 4Suite.  XML considerations are helping shape many grand trends of Python such as unicode support and improved memory-management.  The perl community has definitely taken to XML.  The main parser is, appropriately, XML::Parser, but you can pretty much take any XML buzzword, prepend "XML::", and find a corresponding perl package.
</P>
    <H3>Serving up XML Pages</H3>
    <P>
XML's early promise to the media was as a way to tame the Web.  Structured documents, separation of content from presentation, and more manageable searching and autonomous Web agents.  Some of this has been drowned out by all the recent interest in XML for database integration and message-based middleware, but XML is still an excellent way to manage structured content on the Web.  And Linux is a pretty good operating system on which to host the content. 
</P>
    <P>
The big dog among the XML Web servers is also the well known big dog of Web servers, period.  Apache is absolutely swarming with XML activity lately.  I've already mentioned Xerces, the XML parser from the Apache/XML project.  There is also an XSLT processor, Xalan, with roots in IBM/Lotus's LotusXSL.  There is also Formatting-Object Processor (FOP), a tool for converting XML documents to the popular PDF document, by way of XSL formatting objects, a special XML vocabulary for presentation.  Apache has added support for the Simple Object Access Protocol (SOAP), an XML messaging protocol that can be used to make HTTP-based queries to a server in an XML format.  As a side note, SOAP, and open protocol, is heavily contributed to and championed by Microsoft, in one of the many positive contributions that company has made to XML while not trying to embrace and extend.
</P>
    <P>
These bits and pieces are combined into an Apache-based XML Web publishing solution called Cocoon.  Cocoon allows XML documents to be developed, and then published on the Web, for wireless applications through Wireless Application Protocol (WAP), and to print-ready PDF format through FOP.
</P>
    <P>
Perl hackers already have the proliferation of "XML::*" packages I've already mentioned, but Matt Sergeant has also put together a comprehensive toolkit for XML processing: Axkit.  Axkit is specialized for use with Apache and mod_perl, and provides XSLT transformation as well as other non-standard transform approaches such as "XPathScript".
</P>
    <H3>Full-blown application servers</H3>
    <P>
Enterprises that want an end-to-end solution for developing and deploying applications using XML data have several options under Linux.  Application servers build on basic Web servers such as described above by adding database integration, version control, distributed transactions and other such facilities.
</P>
    <P>
The grey and respectable Hewelett Packard found an open-source, Web-hip side with its e-speak project, a tool for distributed XML applications with Java, Python and C APIs for development and extension.
</P>
    <P>
A smaller company that has found the advantages of open-source for promoting its XML services is Lutris, Inc., developers of Enhydra.  Enhydra, about which I've reported in a previous LinuxWorld article, is a Java application server for XML processing.  It has some neat innovations such as XMLC, a way to "compile" XML into an intermediate binary form for efficient processing.  It is also one of the first open-source implementations of Java 2's Enterprise Edition services, including Enterprise JavaBeans.
</P>
    <P>
XML Blaster is a messaging-oriented middleware (MOM) suite for XML applications.  It uses an XML transport in a publish/subscribe system for exchanging text and binary data.  It uses CORBA for network and inter-process communication and supports components written in Java, Perl, Python and TCL.
</P>
    <P>
Conglomerate, developed by Styx, is a somewhat less ambitious but interesting project for an XML application server more attuned for document management.  It includes a nifty GUI editor and provides a proprietary transformation language that can generate HTML, TeX and other formats.
</P>
    <H3>Oo-wee!  GUI!</H3>
    <P>
One area in which I lamented Linux's lag in XML tools last year was in the area of GUI browsers and editors.  While I personally use a 4XSLT script and XEmacs for these respective tasks, I frequently work with clients who want to use more friendly GUIs for XML editing and ask whether my preferred Linux platform has anything available.  Fortunately, there are more choices than ever on our favorite OS.  Again much of the succour comes in the form of Java's cross-platform GUI support.
</P>
    <P>
GEXml is a Java XML editor which allows programmers use pluggable Java modules for editing their own special tag sets.  It uses a pretty standard layout for XML editors: a multi-pane window with a section for the tree-view, and sections for attributes and a section for CDATA.
</P>
    <P>
Merlot, by Channelpoint, Inc., is another Java-based XML editor that emphasizes modeling XML documents around their DTDs, abstracting the actual XML file from the user.  It supports pluggable extension modules for custom DTDs.
</P>
    <P>
Lunatech's Morphon is yet another DTD-based XML editor and modeling tool.  Hopefully all these DTD-based tools will expand to accommodate XML schemas and other validation methods as well in order to make life easier for those of us who use XML namespaces.  Morphon is similar to the other editors described here with a couple of nice twists: it allows you to specify cascading stylesheets for the editor appearance and document preview, and it mixes the ubiquitous tree view with a friendly view of the XML document being edited.  Morphon, however, is not open-source, though available for Linux.
</P>
    <P>
IBM's Alphaworks keeps on churning out free (beer) XML tools, one of which, XML Viewer, allows users to view XML documents using (once again) the tree-view and specialized panes for element and attribute data.  XML Viewer is written in Java.  It also allows linking the XML source and DTD to allow viewing such items as element and attribute definitions.  There is also XSL Editor, a specialized java-based XML editor for XSLT stylesheets.  It also incorporates advanced features such as syntax highlighting and an XSLT debugger.
</P>
    <P>
TreeNotes is an XML text editor that uses a series of widgets to open up XML's tree structure, elements and attributes, and of course character data, to editing.
</P>
    <P>
DocZilla is an interesting project: an extension of the Mozilla project for Web-based XML document applications.  It promises XML browsing support on par with Internet Explorer's including an extension and plug-in framework.  DocZilla started out very strongly, but now seems to have lagged a bit.  Part of the reason might be that Mozilla is increasing its XML focus.  Mozilla has always supported XML+Cascading Style-Sheets (CSS), but now, with Transformiix (an XSLT processor for Mozilla) and other such projects, it is making its own bid to replace Explorer as king of XML browsers.
</P>
    <P>
There is also KXMLViewer, a KDE XML viewer written in Python, but I'll cover this in more detail when I discuss GNOME and KDE XML support in a coming article in this series.
</P>
    <H3>In the Hacker Spirit</H3>
    <P>
So we've looked at lumbering app servers and pretty GUI tools.  All very nice for easing into XML, but we all know that Linux (and UNIX) users typically prefer sterner stuff.  Small, manageable, versatile, no-nonsense packages that can be strung together to get a larger job done.  Luckily for the desperate hacker, the nuts-and-bolts toolkit is growing just as quickly as the rest of XML space.
</P>
    <P>
A key and quite mature entry is LT XML, developed by the Edinburgh Language Technology Group.  LT XML is a set of stand-along tools and libraries for C programmers using XML.  It supports both tree-based and stream-oriented processing, covering a wide variety of application types.  The LT XML repertoire would be quite familiar and pleasant to those who love nothing more than to string together GNU textutils to produce some neat text transformation.  There is the mandatory XML-aware grep, sggrep (the "sg" for SGML), as well as sgsort, sgcount, sgtoken, etc, which should be self-explanatory.  Python bindings for LT XML should be available by the time you read this.
</P>
    <P>
Speaking of grep, there is also fxgrep, a powerful XML querying tool written in Standard ML, a well-regarded functional programming language from Bell Labs (XML provides a rather fitting problem space for functional languages).  fxgrep uses the XML parser fxp, also written in SML.  fxgrep supports specialized XML searching and query using its own pattern syntax.
</P>
    <P>
Paul Tchistopolskii makes clear there is no mistake as to his target user-base for Ux: "Ux is UNIX, revisited with XML".  Ux is a set of small XML components written in Java (OK, we're leaking some UNIX heritage right there).  The components are designed to be piped together for database storage and extraction, XSLT transformation, query, etc.
</P>
    <P>
Pyxie is an XML parsing and processing toolkit in Python by Sean McGrath and highlighted in his book, <I>XML Processing with Python</I>.  Pyxie's main distiction is that it builds on earlier work by James Clark by focusing on a line-based view of XML rather than the "natural" tokens that emerge from the spec.  This can provide a useful optimization if occasional complications.
</P>
    <P>
For those looking askance at XML in a TeX environment, IBM's Alphaworks might have a useful introduction.  TeXML is a tool that allows you to define an XSLT transform for converting XML files to a specialized vocabulary, the results of which are converted to TeX.  Also, thanks to Alphaworks, there is an XML diff as well as a grep.  XML Tree Diff shows the differences between documents based on their DOM tree representation.  It's more of a collection of Javabeans for performing diffs than a stand-alone application, but it's relatively straightforward to use.
</P>
    <P>
And there is my own company's 4Suite, a set of libraries for Python users to construct their own XML applications using DOM, XPath and XSLT, among other tools.  I covered 4XSLT in my last XML article (though the spec and 4XSLT have changed since then), and 4Suite libraries are now standard components in the Python XML distribution.
</P>
    <H3>Conclusion</H3>
    <P>
Hopefully this tour will help find XML resources for Linux users of all levels.  In upcoming articles (hopefully not as delayed as this one), I shall cover XML and Databases, XML and KDE/GNOME, and mnore topics on how to put XML to work in a Linux environment.
</P>
    <P>
By the way this very article is available in XML form (using the DocBook standard).  I've also put up a simplified DocBook XSLT stylesheet that can be used to render this article to HTML (see Resources for both).  Note that I use the "doc" file extension for DocBook files.  I encourage you to use DocBook (O'Reilly and Associates publishes an excellent book on the topic by Norman Walsh) and the ".doc" extension, chopping at the hegemony of the proprietary Microsoft Word format.  Just another small way XML can open up data to the world.
</P>
    <H3>Resources</H3>
    <H4>Parsers</H4>
    <DL>
      <DT><I>Expat</I></DT>
      <DD>http://www.jclark.com/xml/expat.html</DD>
      <DT><I>Xerces C++</I></DT>
      <DD>http://xml.apache.org/xerces-c/index.html</DD>
      <DT><I>Xerces-Java</I></DT>
      <DD>http://xml.apache.org/xerces-j/index.html</DD>
      <DT><I>xmlpp</I></DT>
      <DD>http://www.vividos.de/xmlpp/</DD>
      <DT><I>libxml</I></DT>
      <DD>http://www.xmlsoft.org/</DD>
      <DT><I>RXP</I></DT>
      <DD>http://www.cogsci.ed.ac.uk/~richard/rxp.html</DD>
      <DT><I>XMLtp</I></DT>
      <DD>http://mitglied.tripod.de/xmltp/</DD>
      <DT><I>MinML</I></DT>
      <DD>http://www.wilson.co.uk/xml/minml.htm</DD>
    </DL>
    <H4>Web Servers</H4>
    <DL>
      <DT><I>Axkit</I></DT>
      <DD>http://axkit.org/</DD>
      <DT><I>XML/Apache</I></DT>
      <DD>http://xml.apache.org</DD>
    </DL>
    <H4>App Servers</H4>
    <DL>
      <DT><I>Conglomerate</I></DT>
      <DD>http://www.conglomerate.org/</DD>
      <DT><I>e-speak</I></DT>
      <DD>http://www.e-speak.net/</DD>
      <DT><I>Enhydra</I></DT>
      <DD>http://www.enhydra.org/</DD>
      <DT><I>XML Blaster</I></DT>
      <DD>http://www.xmlBlaster.org/</DD>
    </DL>
    <H4>Low-Level Tools</H4>
    <DL>
      <DT><I>LT XML</I></DT>
      <DD>http://www.ltg.ed.ac.uk/software/xml/index.html</DD>
      <DT><I>fxgrep</I></DT>
      <DD>http://www.informatik.uni-trier.de/~neumann/Fxgrep/</DD>
      <DT><I>Ux</I></DT>
      <DD>http://www.pault.com/Ux/</DD>
      <DT><I>Pyxie</I></DT>
      <DD>http://www.digitome.com/pyxie.html</DD>
    </DL>
    <H4>GUIs</H4>
    <DL>
      <DT><I>TreeNotes</I></DT>
      <DD>http://pikosoft.dragontiger.com/en/treenotes/</DD>
      <DT><I>DocZilla</I></DT>
      <DD>http://www.doczilla.com/</DD>
      <DT><I>GEXml</I></DT>
      <DD>http://gexml.cx/</DD>
      <DT><I>Merlot</I></DT>
      <DD>http://www.merlotxml.org/</DD>
      <DT><I>Morphon</I></DT>
      <DD>http://www.morphon.com/</DD>
    </DL>
    <H4>Et Cetera</H4>
    <DL>
      <DT><I>There is more to XML than roll-your-own HTML</I></DT>
      <DD>http://www.linuxworld.com/linuxworld/lw-1999-03/lw-03-xml.html</DD>
      <DT><I>Practical XML with Linux, Part 1</I></DT>
      <DD>http://www.linuxworld.com/linuxworld/lw-1999-09/lw-09-xml2.html</DD>
      <DT><I>The xsl-list mailing list</I></DT>
      <DD>http://www.mulberrytech.com/xsl/xsl-list</DD>
      <DT><I>DocBook and stylesheet for this article</I></DT>
      <DD>http://www.Fourthought.com/Publications/lw-xml2</DD>
      <DT><I>The Apache/XML Project</I></DT>
      <DD>http://xml.apache.org/</DD>
      <DT><I>SOAP</I></DT>
      <DD>http://www.w3.org/TR/SOAP/</DD>
      <DT><I>xmlhack</I></DT>
      <DD>http://www.xmlhack.com</DD>
      <DT><I>XML Pit Stop</I></DT>
      <DD>http://www.xmlpitstop.com/</DD>
      <DT><I>xslt.com</I></DT>
      <DD>http://www.xslt.com</DD>
      <DT><I>XML Times</I></DT>
      <DD>http://www.xmltimes.com/</DD>
      <DT><I>The XML Cover Pages</I></DT>
      <DD>http://www.oasis-open.org/cover</DD>
      <DT><I>IBM's Alphaworks (including XML Viewer, XSL Edirot, XML Tree Diff and TeXML)</I></DT>
      <DD>http://alphaworks.ibm.com</DD>
    </DL>
  </BODY>
</HTML>"""


expected_2="""\
<HTML xmlns:doc="http://docbook.org/docbook/xml/4.0/namespace">
  <HEAD>
    <META HTTP-EQUIV='Content-Type' CONTENT='text/html; charset=ISO-8859-1'>
    <TITLE>The Schematron: A Fresh Approach Towards XML Validation and Reporting</TITLE>
    <META CONTENT='text/html' charset='UTF-8' HTTP-EQUIV='content-type'>
    <META NAME='author' CONTENT='Uche Ogbuji'>
  </HEAD>
  <BODY>
    <H1>The Schematron: A Fresh Approach Towards XML Validation and Reporting</H1>
    <H3></H3>
    <P>
XML is certainly an emerging and quick-changing technology.  One of the knocks against it has been the churn of standards and methodologies.  Certainly there is no greater evidence that XML is in flux than the fact that there is so much development and debate about how to validate XML documents, given that validation is one of the cornerstones of XML.
</P>
    <P>
This article introduces The Schematron, one of the currently available validation methodologies.  It will assume familiarity with XML, XML DTDs, and some familiarity with XPath and XSLT transforms.  For those who might need some grounding on one or more of those areas I've added some helpful links in the Resources section.
</P>
    <H3>A Bit of Background</H3>
    <P>
Although, as I pointed out in my last XML article on SunWorld (see Resources), XML doesn't introduce any notable innovation in data-processing, it has, through its popularity, introduced many useful disciplines inherited from SGML.  Perhaps the core discipline in this regard is in native support for validation.  One of XML's early promises in terms of easing information-management woes involved it's support for bundling the data schema with the data, and by providing for some standard schema discovery in cases where this bundling was not done.  Of course, the real-world has proven that this facility, while useful, is no panacea.  Even if one can a schema for machine-interpretation of a data set, how does one determine the semantics associated with that schema.  A further problem was the particular schema methodology that XML ended up being bundled with: Document-Type Definition (DTD).
</P>
    <P>
DTDs are an odd mix of very generic and very specific expression.  For instance, simple tasks such as specifying that an element can have a number of particular child elements within a given range can be very cumbersome using DTDs.  Yet they are generic enough to allow such elegant design patterns as architectural forms (see Resources).  The expressive shortcomings of DTDs, along with arguments that XML validation should not require a separate computer language (DTDs of course differ in syntax from XML instances), encouraged the W3C, XML's major standards body, to develop a new schema language for XML, using XML syntax.  The resulting XML Schema specification is currently in "Candidate Recommendation" phase and presumably will soon hit version 1.0 (although based on experience with the DOM spec one should hardly rely on this).
</P>
    <P>
One of the key XML developments since XML 1.0 that has affected the schema story is XML Namespaces 1.0.  This recommendation provides a mechanism for disambiguating XML names, but does so in a way that is rather unfriendly to DTD users.  There are tricks for using namespaces with DTDs, but they are quite arcane.  Of course it must be noted that many of the SGML old school have argued that namespaces are a rather brittle solution, and furthermore they solve a rather narrow problem to justify such disruption in XML technologies.  The reality, however, is that with XML-related standards from XSLT to XLink relying heavily on namespaces, we shall have to develop solutions to the core problems that take namespaces into account.
</P>
    <P>
But back to validation.  The W3C Schema specification has been a long time in development, and along the way there began to be rumblings about the complexity of the emerging model.  XML Schemas did fill a very ambitious charter: covering document structure, data-typing worthy of databases, and even abstract data-modeling such as subclassing.
</P>
    <P>
And so because of the gap between the emergence of namespaces and the completion of XML Schemas, and because of fears that the coming specification was far too complex, the XML community, one with a remarkable history of practical problem-solving, went to work.
</P>
    <P>
One of the developments was Murata Makoto's Regular Language description for XML (RELAX) (see Resources).  Relax provides a system for developing grammars to describe XML documents.  It uses XML-like syntax and ofers similar featues to DTDs, adding some of the facilities offered by XML Schemas, such as schema annotation (basically, built-in documentation) and data-typing (for example specifying that an attribute value be an integer), and coming up with some exotic additions of its own such as "hedge grammars".  RELAX supports namespaces and provides a clean and inherently modular approach to validation and so has become rather popular, with its own mailing lists and contributed tools such as a DTD to RELAX translator (see Resources).
</P>
    <H3>A Different Approach: Harnessing the Power of XPath</H3>
    <P>
In the mean time XSLT emerged as a W3C standard, and immediately established itself as one of their most successful XML-related products.  Most people are familiar with XSLT as a tool to display XML content on "legacy" HTML-only browsers, but there is so much more to XSLT, largely because XPath, which it uses to express patterns in the XML source, is such a well-conceived tool.
</P>
    <P>
In fact, since XPath is such a comprehensive system for indicating and selecting from patterns in XML, there is no reason it could not express similar structural concepts as does DTD.  Take the following DTD, listing 1.
</P>
    <PRE>

&lt;!ELEMENT ADDRBOOK (ENTRY*)>
&lt;!ELEMENT ENTRY (NAME, ADDRESS, PHONENUM+, EMAIL)>
&lt;!ATTLIST ENTRY
    ID ID #REQUIRED
>
&lt;!ELEMENT NAME (#PCDATA)>
&lt;!ELEMENT ADDRESS (#PCDATA)>
&lt;!ELEMENT PHONENUM (#PCDATA)>
&lt;!ATTLIST PHONENUM
    DESC CDATA #REQUIRED
>
&lt;!ELEMENT EMAIL (#PCDATA)>

</PRE>

<P>
A sample document valid against this DTD is as follows, listing 2.
</P>
    <PRE>

&lt;?xml version = "1.0"?>
&lt;!DOCTYPE ADDRBOOK SYSTEM "addr_book.dtd">
&lt;ADDRBOOK>
        &lt;ENTRY ID="pa">
                &lt;NAME>Pieter Aaron&lt;/NAME>
                &lt;ADDRESS>404 Error Way&lt;/ADDRESS>
                &lt;PHONENUM DESC="Work">404-555-1234&lt;/PHONENUM>
                &lt;PHONENUM DESC="Fax">404-555-4321&lt;/PHONENUM>
                &lt;PHONENUM DESC="Pager">404-555-5555&lt;/PHONENUM>
                &lt;EMAIL>pieter.aaron@inter.net&lt;/EMAIL>
        &lt;/ENTRY>
        &lt;ENTRY ID="en">
                &lt;NAME>Emeka Ndubuisi&lt;/NAME>
                &lt;ADDRESS>42 Spam Blvd&lt;/ADDRESS>
                &lt;PHONENUM DESC="Work">767-555-7676&lt;/PHONENUM>
                &lt;PHONENUM DESC="Fax">767-555-7642&lt;/PHONENUM>
                &lt;PHONENUM DESC="Pager">800-SKY-PAGEx767676&lt;/PHONENUM>
                &lt;EMAIL>endubuisi@spamtron.com&lt;/EMAIL>
        &lt;/ENTRY>
&lt;/ADDRBOOK>

</PRE>

<P>
Examine the declaration of the ADDRBOOK element.  It basically says that such elements must have at least four child elements, a NAME, an ADDRESS, one or more PHONENUM and an EMAIL.  This can be expressed in XPath with a combination of the following three boolean expressions (using the ADDRBOOK element as the context):
</P>
    <PRE>
1. count(NAME) = 1 and count(ADDRESS) = 1 and count(EMAIL) = 1
2. NAME[following-sibling::ADDRESS] and ADDRESS[following-sibling::PHONENUM] and PHONENUM[following-sibling::EMAIL]
3. count(NAME|ADDRESS|PHONENUM|EMAIL) = count(*)
</PRE>

<P>
The first is true if and only if (iff) there is exactly one each of NAME, ADDRESS, and EMAIL.  This establishes the occurrence rule for these children.  The second is true iff there is a NAME followed by an ADDRESS, an ADDRESS followed by a PHONENUM and a PHONENUM followed by an EMAIL.  This establishes the sequence rule for the children.  Note that the preceding-sibling axis could have been used just as well.  The third expression is true iff there are no other elements besides the NAME ADDRESS PHONENUM EMAIL.  This establishes the (implied) DTD rule that elements are not permitted except where specified in the content model by name or with the ANY symbol.
</P>
    <P>
You first reaction might be that the XPath expressions are so much more verbose than the equivalent DTD specification.  This is so in this case, though one can easily come up with situations where the DTD equivalent would be more verbose than the equivalent XPath expressions.  However, this is entirely beside the point.  The DTD version is more concise because it is carefully designed to model such occurrence and sequence patterns.  XPath has far more general purpose and we are actually building the DTD equivalent through a series of primitives each of which operate at a more granular conceptual level than the DTD equivalent.  So it may be more wordy, but it has far greater expressive power.  Let's say we wanted to specify that there can be multiple ADDRESS and EMAIL children, but that they must be of the same number.  This task, which seems a simple enough extension of the previous content-midel, is pretty much beyond the abilities of DTD.  Not so XPath.  Since XPath gives a primitive but complete model of the document, it's an easy enough addition.
</P>
    <PRE>
1. count(NAME) = 1 and count(ADDRESS) = count(EMAIL)
2. NAME[following-sibling::ADDRESS] and ADDRESS[following-sibling::PHONENUM] and PHONENUM[following-sibling::EMAIL]
3. count(NAME|ADDRESS|PHONENUM|EMAIL) = count(*)
</PRE>

<P>
The only change is in expression 1, and should be self-explanatory.  This small foray beyond the scope of DTD illustrates the additional power offered by XPath.  Of course XPath can handle the attribute declarations as well.  For example, the attribute declaration for PHONENUM in the DTD can be expressed as follows (again using the ADDRBOOK element as context):
</P>
    <PRE>
PHONENUM/@DESC
</PRE>

<P>
All these XPath expressions are very well in the abstract, but how would one actually use them for validation?  The most convenient way is to write an XSLT transform that uses them to determine validity.  Here's an example, listing 3, which represents a sub-set of the address book DTD.
</P>
    <PRE>

&lt;?xml version="1.0"?>
&lt;xsl:transform xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">

  &lt;xsl:template match="/">
    &lt;xsl:if test='not(ADDRBOOK)'>
      Validation error: there must be an ADDRBOOK element at the root of the document.
    &lt;/xsl:if>
    &lt;xsl:apply-templates select='*'/>
  &lt;/xsl:template>

  &lt;xsl:template match="ENTRY">
    &lt;xsl:if test='not(count(NAME) = 1)'>
      Validation error: ENTRY element missing a NAME child.
    &lt;/xsl:if>
    &lt;xsl:if test='not(count(ADDRESS) = 1)'>
      Validation error: ENTRY element missing an ADDRESS child.
    &lt;/xsl:if>
    &lt;xsl:if test='not(count(EMAIL) = 1)'>
      Validation error: ENTRY element missing an EMAIL child.
    &lt;/xsl:if>
    &lt;xsl:if test='not(NAME[following-sibling::ADDRESS] and ADDRESS[following-sibling::PHONENUM] and PHONENUM[following-sibling::EMAIL])'>
      Validation error: ENTRY must have a NAME, ADDRESS, one or more PHONENUM, and an EMAIL in sequence
    &lt;/xsl:if>
    &lt;xsl:if test='not(count(NAME|ADDRESS|PHONENUM|EMAIL) = count(*))'>
      Validation error: there is an extraneous element child of ENTRY
    &lt;/xsl:if>
    &lt;xsl:apply-templates select='*'/>
  &lt;/xsl:template>

  &lt;xsl:template match="PHONENUM">
    &lt;xsl:if test='not(@DESC)'>
      Validation error: PHONENUM must have a DESC attribute
    &lt;/xsl:if>
    &lt;xsl:apply-templates select='*'/>
  &lt;/xsl:template>

  &lt;xsl:template match="*">
    &lt;xsl:apply-templates select='*'/>
  &lt;/xsl:template>

&lt;/xsl:transform>

</PRE>

<P>
When run with a valid document, such as the example above, this stylesheet would produce no output.  When run, however, with an invalid document such as the following, listing 4, however, it's a different story.
</P>
    <PRE>

&lt;?xml version = "1.0"?>
&lt;ADDRBOOK>
        &lt;ENTRY ID="pa">
                &lt;NAME>Pieter Aaron&lt;/NAME>
                &lt;PHONENUM DESC="Work">404-555-1234&lt;/PHONENUM>
                &lt;PHONENUM DESC="Fax">404-555-4321&lt;/PHONENUM>
                &lt;PHONENUM DESC="Pager">404-555-5555&lt;/PHONENUM>
                &lt;EMAIL>pieter.aaron@inter.net&lt;/EMAIL>
        &lt;/ENTRY>
        &lt;ENTRY ID="en">
                &lt;NAME>Emeka Ndubuisi&lt;/NAME>
                &lt;PHONENUM DESC="Work">767-555-7676&lt;/PHONENUM>
                &lt;PHONENUM DESC="Fax">767-555-7642&lt;/PHONENUM>
                &lt;PHONENUM DESC="Pager">800-SKY-PAGEx767676&lt;/PHONENUM>
                &lt;EMAIL>endubuisi@spamtron.com&lt;/EMAIL>
                &lt;ADDRESS>42 Spam Blvd&lt;/ADDRESS>
                &lt;SPAM>Make money fast&lt;/SPAM>
        &lt;/ENTRY>
        &lt;EXTRA/>
&lt;/ADDRBOOK>

</PRE>

<P>
Note that all the XPath expressions we came up with are placed in if statements and negated.  This is because they represent conditions such that we want a message put out if they are <I>not</I> met.  Running this source against the validation transform using an XSLT processor results in the following output:
</P>
    <PRE>

      Validation error: ENTRY element missing an ADDRESS child.
    
      Validation error: ENTRY must have a NAME, ADDRESS, one or more PHONENUM, and an EMAIL in sequence
    
      Validation error: ENTRY must have a NAME, ADDRESS, one or more PHONENUM, and an EMAIL in sequence
    
      Validation error: there must be an ENTRY element at the root of the document.
    

</PRE>

<P>
And so we have our validation result.  Note that it's pretty much a report of the document, such as we set it up to be.  One nice thing about this is that you can see all the validation errors at once.  Using most XML parsers you only get one error at a time.  But the real power of this XSLT-based validation report is that it's just that: a report.  We happened to use it for DTD-based XML validation, but it's not hard to see how this could be extended to more sophisticated data-management needs.  For instance, suppose we wanted to examine address-book documents for e-mail addresses in the .gov domain.  This is pretty much entirely beyond the realm of validation, but it is an example, as database programmers will immediately recognize, of reporting.
</P>
    <P>
While it might be argued one way or another whether validation and reporting are cut from the same conceptual cloth, it is pretty clear that in practice, XML document validation can be treated as a subset of XML document reporting, and furthermore that XPath and XSLT provide a powerful toolkit for document validation.
</P>
    <H3>Introducing the Schematron</H3>
    <P>
This re-casting of validation as a reporting problem is a core insight of the Schematron (see Resources).  The Schematron is a validation and reporting methodology and toolkit developed by Rick Jeliffe who, interestingly enough, is a member of the W3C Schema working group.  Without denigrating the efforts of his group, Mr. Jeliffe has pointed out that XML Schemas may be too complex for many users, and approaches validation from the same old approach as DTD.  He developed the Schematron as a simple tool to harness the power of XPath, attacking the schema problem from a new angle.  As he put it on his site, "The Schematron differs in basic concept from other schema languages in that it not based on grammars but on finding tree patterns in the parsed document. This approach allows many kinds of structures to be represented which are inconvenient and difficult in grammar-based schema languages."
</P>
    <P>
The Schematron is really no more than an XML vocabulary that can be used as an instruction set for generating stylesheets such as the one presented above.  For instance, the following, listing 5, is how our XPath-based validation might look like in The Schematron.
</P>
    <PRE>

&lt;schema xmlns='http://www.ascc.net/xml/schematron'>
        &lt;pattern name="Structural Validation">
                &lt;!-- Use a hack to set the root context.  Necessary because of
                     a bug in the schematron 1.3 meta-transforms. -->
                &lt;rule context="/*">
                        &lt;assert test="../addr:ADDRBOOK">Validation error: there must be an ADDRBOOK element at the root of the document.&lt;/assert>
                &lt;/rule>
                &lt;rule context="ENTRY">
                        &lt;assert test="count(NAME) = 1">Validation error: &lt;name/> element missing a NAME child.&lt;/assert>
                        &lt;assert test="count(ADDRESS) = 1">Validation error: &lt;name/> element missing an ADDRESS child.&lt;/assert>
                        &lt;assert test="count(EMAIL) = 1">Validation error: &lt;name/> element missing an EMAIL child.&lt;/assert>
                        &lt;assert test="NAME[following-sibling::ADDRESS] and ADDRESS[following-sibling::PHONENUM] and PHONENUM[following-sibling::EMAIL]">Validation error: &lt;name/> must have a NAME, ADDRESS, one or more PHONENUM, and an EMAIL in sequence&lt;/assert>
                        &lt;assert test="count(NAME|ADDRESS|PHONENUM|EMAIL) = count(*)">Validation error: there is an extraneous element child of ENTRY&lt;/assert>
                &lt;/rule>
                &lt;rule context="PHONENUM">
                        &lt;assert test="@DESC">Validation error: &lt;name/> must have a DESC attribute&lt;/assert>
                &lt;/rule>
        &lt;/pattern>
&lt;/schema>

</PRE>

<P>
The root element in schematron is the schema element in the appropriate namespace.  It contains one or more patterns, each of which represents a conceptual grouping of declarations.  Patterns contain one or more rules, each of which sets a context for a series of declarations.  This is not only a conceptual context, but also the context that is used for the XPath expressions in declarations within each rule.
</P>
    <P>
Each rule contains a collection of asserts, reports and keys.  You can see asserts at work in our example.  Asserts are similar to asserts in C.  They represent a declaration that a condition is true, and if it is not true, a signal is made to such effect.  In the Schematron, assert elements specify that if the condition in their test attribute is not true, the content of the assert elements will be copied to the result.  You'll note that the assert messages contain empty <PRE>name</PRE> elements.  This is a convenient short-hand for the name of the current context node, given by the parent rule element.  This makes it easy to reuse asserts from context to context.  Reports are similar to asserts, except that they output their contents when the condition in their test attribute is true rather than false.  They also allow the use of the empty name element.  Reports, as their name implies, tend to make sense for structural reporting tasks.  For instance, to implement our eariler example of reporting e-mail addresses in the .gov domain we might add the following rule to our Schematron:
</P>

<PRE>

                &lt;rule context="EMAIL">
                        &lt;report test="contains(., '.gov') and not(substring-after(., '.gov'))">This address book contains government contacts.&lt;/report>
                &lt;/rule>

</PRE>

<P>
Of course I already mentioned that namespaces are an important reason to seek a different validation methodology than DTDs.  Schematron supports namespaces through XPath's support for namespaces.  For instance, if we wanted to validate that all child elements of ENTRY in our address book document were in a particular namespace, we could do so so by adding an assert which checks the count of elements in a particular namespace.  Assume that the prefix "addr" is bound to the target namespace in the following example:
</P>
    <PRE>
count(addr:*) = count(*)
</PRE>

<P>
Maybe that's too draconian for your practical needs and you want to also allow elements in a particular namespace reserved for extansions.
</P>
    <PRE>
count(addr:*) + count(ext:*) = count(*)
</PRE>

<P>
Maybe rather than permitting a single particular extension namespace, you want to instead allow any elements with namespaces whose URI contains the string "extension":
</P>
    <PRE>
count(addr:*) + count(*[contains(namespace(.), 'extension')]) = count(*)
</PRE>

<P>
With this latter addition and the addition of a report for e-mail addresses in the .gov address our schematron looks as follows, listing 6.
</P>
    <PRE>

&lt;schema xmlns='http://www.ascc.net/xml/schematron'>

        &lt;ns prefix='addr' uri='http://addressbookns.com'/>

        &lt;pattern name="Structural Validation">
                &lt;!-- Use a hack to set the root context.  Necessary because of
                     a bug in the schematron 1.3 meta-transforms. -->
                &lt;rule context="/*">
                        &lt;assert test="../addr:ADDRBOOK">Validation error: there must be an ADDRBOOK element at the root of the document.&lt;/assert>
                &lt;/rule>
                &lt;rule context="addr:ENTRY">
                        &lt;assert test="count(addr:*) + count(*[contains(namespace-uri(.), 'extension')]) = count(*)">
Validation error: all children of &lt;name/> must either be in the namespace 'http://addressbookns.com' or in a namespace containing the substring 'extension'.
                        &lt;/assert>
                        &lt;assert test="count(addr:NAME) = 1">
Validation error: &lt;name/> element missing a NAME child.
                        &lt;/assert>
                        &lt;assert test="count(addr:ADDRESS) = 1">
Validation error: &lt;name/> element missing an ADDRESS child.
                        &lt;/assert>
                        &lt;assert test="count(addr:EMAIL) = 1">
Validation error: &lt;name/> element missing an EMAIL child.
                        &lt;/assert>
                        &lt;assert test="addr:NAME[following-sibling::addr:ADDRESS] and addr:ADDRESS[following-sibling::addr:PHONENUM] and addr:PHONENUM[following-sibling::addr:EMAIL]">
Validation error: &lt;name/> must have a NAME, ADDRESS, one or more PHONENUM, and an EMAIL in sequence
                        &lt;/assert>
                        &lt;assert test="count(addr:NAME|addr:ADDRESS|addr:PHONENUM|addr:EMAIL) = count(*)">
Validation error: there is an extraneous element child of ENTRY
                        &lt;/assert>
                &lt;/rule>
                &lt;rule context="addr:PHONENUM">
                        &lt;assert test="@DESC">
Validation error: &lt;name/> must have a DESC attribute
                        &lt;/assert>
                &lt;/rule>
        &lt;/pattern>
        &lt;pattern name="Government Contact Report">
                &lt;rule context="addr:EMAIL">
                        &lt;report test="contains(., '.gov') and not(substring-after(., '.gov'))">
This address book contains government contacts.
                        &lt;/report>
                &lt;/rule>
        &lt;/pattern>
&lt;/schema>

</PRE>

<P>
Note the new top-level element, ns.  We use this to declare the namespace that we'll be incorporating into the schematron rules.  If you have multiple such namespaces to declare, use one ns element for each.  Note that there are some advanced uses of schematron namespace declarations about which you can read on theSchematron site.
</P>
    <P>
This was a pretty quick whirl through The Schematron.  This shouldn't be much of a problem since it is so simple.  However, for a bit more instruction, there is the tidy tutorial put together by Dr Miloslav Nic (see Resouces.  Note that the good Doctor has tutorials on many other XML-related topics at his page).  There are also a few examples linked from the Schematron home page.
</P>
    <H3>Putting The Schematron to Work</H3>
    <P>
So how do we use The Schematron?  Rememeber that a Schematron document could be thought of as a instructions for generating special validation and report transforms such as we introduced earlier.  This is in fact the most common way of using The Schematron in practice.  Conveniently enough, XSLT has all the power to convert Schematron specifications to XSLT-based validators.  There is a meta-transform available at the Schematron Web site which, when run against a schematron specification, will generate a specialized validator/reporter transform which can be then run against target source documents.  For instance, suppose I have the above schematron specification as "addrbook.schematron".  I can turn it into a validator/reporter transform as follows:
</P>
    <PRE>
[uogbuji@borgia code]$ 4xslt.py listing6.schematron ~/devel/Ft/Xslt/test_suite/borrowed/schematron-skel-ns.xslt > addrbook.validator.xslt
</PRE>

<P>
Here and for all other examples in this article, I am using the 4XSLT processor.  4XSLT (see Resources) is an XSLT 1.0-compliant processor written in Python and distributed as open source by my company, Fourthought, Inc.  I ran the above from Linux and the first argument to 4xslt.py is the XML source document: in this case the schematron specification in listing 6.  The second argument is the transform to be used, in this case the Schematron namespace-aware meta-transform.  I then redirect the standard output to the file addrbook.validator.xslt, which thus becomes my validator/reporter transform.  I can then run the validator transform against the following source document, listing 7.
</P>
    <PRE>

&lt;?xml version = "1.0"?>
&lt;ADDRBOOK xmlns='http://addressbookns.com'>
        &lt;ENTRY ID="pa">
                &lt;NAME xmlns='http://bogus.com'>Pieter Aaron&lt;/NAME>
                &lt;ADDRESS>404 Error Way&lt;/ADDRESS>
                &lt;PHONENUM DESC="Work">404-555-1234&lt;/PHONENUM>
                &lt;PHONENUM DESC="Fax">404-555-4321&lt;/PHONENUM>
                &lt;PHONENUM DESC="Pager">404-555-5555&lt;/PHONENUM>
                &lt;EMAIL>pieter.aaron@inter.net&lt;/EMAIL>
        &lt;/ENTRY>
        &lt;ENTRY ID="en">
                &lt;NAME xmlns='http://bogus.com'>Emeka Ndubuisi&lt;/NAME>
                &lt;ADDRESS>42 Spam Blvd&lt;/ADDRESS>
                &lt;PHONENUM DESC="Work">767-555-7676&lt;/PHONENUM>
                &lt;PHONENUM DESC="Fax">767-555-7642&lt;/PHONENUM>
                &lt;PHONENUM DESC="Pager">800-SKY-PAGEx767676&lt;/PHONENUM>
                &lt;EMAIL>endubuisi@spamtron.com&lt;/EMAIL>
        &lt;/ENTRY>
&lt;/ADDRBOOK>

</PRE>

<P>
Yielding the following output:
</P>
    <PRE>
[uogbuji@borgia code]$ 4xslt.py listing7.xml addrbook.validator.xslt 
Validation error: all children of ENTRY must either be in the namespace 'http://addressbookns.com' or in a namespace containing the substring 'extension'.Validation error: ENTRY element missing a NAME child.Validation error: ENTRY must have a NAME, ADDRESS, one or more PHONENUM, and an EMAIL in sequenceValidation error: there is an extraneous element child of ENTRYValidation error: all children of ENTRY must either be in the namespace 'http://addressbookns.com' or in a namespace containing the substring 'extension'.Validation error: ENTRY element missing a NAME child.Validation error: ENTRY must have a NAME, ADDRESS, one or more PHONENUM, and an EMAIL in sequenceValidation error: there is an extraneous element child of ENTRY
</PRE>

<P>
Hmm.  Rather a mess, what?  Looks as if there were quite a few messages combined without clear separation.  There were actually two sets of messages, one for each ENTRY in the source document, since we caused the same cascade of validation errors in both by messing with the namespace of the NAME element.  The reason the two messages run together so is that we used the skeleton Schematron meta-transform.  The skeleton comes with only basic output support, and in particular, it normalizes space in all output, running the results together.
</P>
    <P>
There's a good chance this is not what you want, and luckily Schematron is designed to be quite extensible.  There are several schematron meta-transforms on the Schematron home page that build on the skeleton by importing it.  They range from basic, clearer text messages to HTML for browser-integration.  Using the sch-basic meta-transform rather than the skeleton yields:
</P>
    <PRE>
[uogbuji@borgia code]$ 4xslt.py listing6.schematron ~/devel/Ft/Xslt/test_suite/borrowed/sch-basic.xslt > addrbook.validator.xslt
[uogbuji@borgia code]$ 4xslt.py listing7.xml addrbook.validator.xslt 
In pattern Structural Validation:
   Validation error: all children of ENTRY must either be in the namespace 'http://addressbookns.com' or in a namespace containing the substring 'extension'.
In pattern Structural Validation:
   Validation error: ENTRY element missing a NAME child.
In pattern Structural Validation:
   Validation error: ENTRY must have a NAME, ADDRESS, one or more PHONENUM, and an EMAIL in sequence
In pattern Structural Validation:
   Validation error: there is an extraneous element child of ENTRY
In pattern Structural Validation:
   Validation error: all children of ENTRY must either be in the namespace 'http://addressbookns.com' or in a namespace containing the substring 'extension'.
In pattern Structural Validation:
   Validation error: ENTRY element missing a NAME child.
In pattern Structural Validation:
   Validation error: ENTRY must have a NAME, ADDRESS, one or more PHONENUM, and an EMAIL in sequence
In pattern Structural Validation:
   Validation error: there is an extraneous element child of ENTRY

</PRE>

<P>
To round things up, here is an example, listing 8, of a source document that validates cleanly against our sample schematron.
</P>
    <PRE>

&lt;?xml version = "1.0"?>
&lt;ADDRBOOK xmlns='http://addressbookns.com'>
        &lt;ENTRY ID="pa">
                &lt;NAME>Pieter Aaron&lt;/NAME>
                &lt;ADDRESS>404 Error Way&lt;/ADDRESS>
                &lt;PHONENUM DESC="Work">404-555-1234&lt;/PHONENUM>
                &lt;PHONENUM DESC="Fax">404-555-4321&lt;/PHONENUM>
                &lt;PHONENUM DESC="Pager">404-555-5555&lt;/PHONENUM>
                &lt;EMAIL>pieter.aaron@inter.net&lt;/EMAIL>
        &lt;/ENTRY>
        &lt;ENTRY ID="en">
                &lt;NAME>Manfredo Manfredi&lt;/NAME>
                &lt;ADDRESS>4414 Palazzo Terrace&lt;/ADDRESS>
                &lt;PHONENUM DESC="Work">888-555-7676&lt;/PHONENUM>
                &lt;PHONENUM DESC="Fax">888-555-7677&lt;/PHONENUM>
                &lt;EMAIL>mpm@scudetto.dom.gov&lt;/EMAIL>
        &lt;/ENTRY>
&lt;/ADDRBOOK>

</PRE>

<P>
Which we test as follows.
</P>
    <PRE>
[uogbuji@borgia code]$ 4xslt.py listing8.xml addrbook.validator.xslt 
In pattern Government Contact Report:
   This address book contains government contacts.

</PRE>

<P>
Now everything is in the correct namespace so we get no validation errors.  However, notice that we did get the report from the e-mail address in the .gov domain.
</P>
    <P>
This is all very well, but no doubt you're wondering whether XSLT is fast enought to suit your real-world validation needs.  This will of course depend on your needs.  In my experience, it is very rarely necessary to validate a document every time it is processed.  If you have attributes with default value, or you have no control at all over the sources of your data throughout your processing applications then you may have no choice.  In this case, validation by an XML 1.0-compliant validating parser such as xmlproc (see Resources) is almost certainly faster than XSLT-based Schematron.  But then again, there is no hard requirement that a Schematron processor use XSLT.  It would not be terribly difficult, given an efficient XPath library, to write a specialized Schematron application that doesn't need translation from meta-transforms.
</P>
    <P>
But just to give a quick comparison, I parsed a 170K address book example similar to the above but with more entries.  Using xmlproc and DTD validation it took 7.25 seconds.  Parsing this document without validation and then applying the schematron transform took 10.61 seconds.  Hardly so great a penalty.
</P>
    <P>
Of course there are several things that DTDs provide that Schematron cannot.  The most notable are entity and notation definitions and fixed or default attribute values.  RELAX does not provide any of these facilities either, but XML Schemas do provide all of them as it must since it is positioned as a DTD replacement.  RELAX makes no such claim and indeed the RELAX documentation has a section on using RELAX in concert with DTD.  We have already discussed that Schematron, far from claiming to be a DTD replacement, is positioned as an entirely fresh approach to validation.  Nevertheless, attribute-value defaulting can be a useful way to reduce the clutter of XML documents for human readability so we shall examine one way to provide default attributes in association with Schematron.
</P>
    <P>
Remember that you're always free to combine DTD with Schematron to get the best of both worlds, but if you want to to leave DTD entirely behind, you can still get attribute-defaulting at the cost of one more pass through the document when the values are to be substituted.  This can easily be done by a transform that turns a source document to a result that is identical except that all default attribute values are given.
</P>
    <P>
There are other features of Schematron for those interested in further exploration.  For instance it supports keys: a mechanism similar to DTD's ID and IDREF.  There are some hooks for embedding and control through external applications.  Certainly a more formal introduction to Schematron is available in the Schematron specification (see Resources).
</P>
    <H3>Conclusion</H3>
    <P>
We at Fourthought pretty much stopped using DTD about a year ago when we started using namespaces in earnest.  We soon seized on Schematron and have used it in deployed work product for our clients and internally.  Since we already do a lot of work with XSLT it's a very comfortable system and the training required for XPath isn't much of an issue.  To match most of the basic features of DTD, not much more knowledge should be required than path expressions, predicates, unions, the sibling and attribute axes, and a handful of functions such as count.  Performance has not been an issue because we typically have strong control over XML data in our systems and hardly ever use defaulted attributes.  This allows us to validate only when a new XML datum is input, or an existing datum modified our systems, reducing performance concerns.
</P>
    <P>
Schematron is a clean, well-considered approache to the problems of validation and simple reporting.  XML Schemas are a significant development, but it is debatable whether such an entirely new and complex system is required for such a straightforward task as validation.  RELAX and The Schematron both present simpler approaches coming from different angles and they might be a better fit for quick integration into XML systems.  In any case, Schematron once again demonstrates the extraordinary reach of XSLT and the flexibility of XML in general as a data-management technology.
</P>
    <H3>Resources</H3>
    <DL>
      <DT><I>RELAX XML Schema System</I></DT>
      <DD>http://www.xml.gr.jp/relax/</DD>
      <DT><I>W3C XML Schemas: Primer</I></DT>
      <DD>http://www.w3.org/TR/xmlschema-0/</DD>
      <DT><I>W3C XML Schemas Part 1: Structures</I></DT>
      <DD>http://www.w3.org/TR/xmlschema-1/</DD>
      <DT><I>W3C XML Schemas Part 2: Datatypes</I></DT>
      <DD>http://www.w3.org/TR/xmlschema-2/</DD>
      <DT><I>DTD2RELAX</I></DT>
      <DD>http://www.horobi.com/Projects/RELAX/Archive/DTD2RELAX.html</DD>
      <DT><I>The Schematron home page</I></DT>
      <DD>http://www.ascc.net/xml/resource/schematron/schematron.html</DD>
      <DT><I>Rick Jelliffe's Comparison of Various Schema Methods</I></DT>
      <DD>http://www.ascc.net/%7ericko/XMLSchemaInContext.html</DD>
      <DT><I>4XSLT</I></DT>
      <DD>http://www.fourthought.com/4XSLT</DD>
      <DT><I>4Suite</I></DT>
      <DD>http://www.fourthought.com/4Suite</DD>
      <DT><I>Schematron Tutorial</I></DT>
      <DD>http://www.zvon.org/HTMLonly/SchematronTutorial/General/contents.html</DD>
      <DT><I>Other ZVON Tutorials for XML-related topics</I></DT>
      <DD>http://www.zvon.org/</DD>
      <DT><I>The Schematron Specification</I></DT>
      <DD>http://www.ascc.net/xml/resource/schematron/Schematron2000.html</DD>
      <DT><I>General news, product info, etc. concerning XSLT</I></DT>
      <DD>http://www.xslt.com</DD>
      <DT><I>General news, product info, etc. concerning XML</I></DT>
      <DD>http://www.xmlhack.com</DD>
      <DT><I>Slides from an XSLT introduction by the author</I></DT>
      <DD>http://fourthought.com/Presentations/xmlforum-xslt-20000830</DD>
      <DT><I>The XSLT FAQ</I></DT>
      <DD>http://www.dpawson.freeserve.co.uk/xsl/xslfaq.html</DD>
      <DT><I>Zvon XSLT Reference</I></DT>
      <DD>http://www.zvon.org/xxl/XSLTreference/Output/index.html</DD>
      <DT><I>Zvon DTD tutorial</I></DT>
      <DD>http://www.zvon.org/xxl/DTDTutorial/General/book.html</DD>
      <DT><I>Zvon namespace tutorial</I></DT>
      <DD>http://www.zvon.org/xxl/NamespaceTutorial/Output/index.html</DD>
      <DT><I>Zvon XML tutorial</I></DT>
      <DD>http://www.zvon.org/xxl/XMLTutorial/General/book_en.html</DD>
      <DT><I>Zvon XPath tutorial</I></DT>
      <DD>http://www.zvon.org/xxl/XPathTutorial/General/examples.html</DD>
      <DT><I>Zvon XSLT tutorial</I></DT>
      <DD>http://www.zvon.org/xxl/XSLTutorial/Books/Book1/index.html</DD>
      <DT><I>Links related to architectural forms</I></DT>
      <DD>http://www.xml.com/pub/Guide/Architectural_Forms</DD>
    </DL>
    <H3></H3>
    <P>
On re-reading my first two XML articles, just over a year ago in this journal and in its sister, Sunworld, I'm struck by how much they represented a justification of XML as the great tin opener of closed data formats.  In under a year, it looks as if all the light-bulbs went on at once.  XML is in the computer news every day, every company seems to be scrambling to ink XML into their brochures, and XML standards organizations such as the World-Wide Web consortium (W3C) practically have to turn people away.  At this point I hardly think any more justification of XML for open data exchange is required.  It's pretty much a fact of information technology.  The remaining questions are how to use XML to solve real problems better than with any other means.
</P>
    <P>
As I mentioned in my most recent article, the W3C and other standards organizations are working very quickly to complete specifications for technologies complementary to XML.  I mentioned namespaces, which are a key facility for managing global names and are now used in almost every XML technology.  I also mentioned DOM and XSLT.  Since then, XLink, XPointer, XML Schemas, SVG and other specs are almost complete.  I shall discuss these later in the series as well as RDF, Schematron and other beasts in the XML menagerie.  The XML community has also matured greatly, and as one example, there are many new, high-quality information and news sites, some of which I list in Resources section.  If you are highly interested in XML, I highly recommend regular visits to xmlhack, in particular.
</P>
    <H3>The Triumph of Open Standards</H3>
    <P>
The most amazing thing about XML's incredible rise, in my opinion sharper than that of the PC, Java, or even the Web, is the fact that it has remained as open as when it started.  Even though XML in its early days was positioned as a tool for encouraging data interchange by providing both human and machine readibility, odds always were that a powerful company, or group of companies would foul the waters.  Many vertical industries such as the automobile inustry (which recently surprised analysts by announcing a huge, XML-driven on-line exchange), health-care and chemicals have been moving to XML as data-exchange format.  If the likes of Microsoft (early and on-going XML champion) and Oracle, could co-opt standards for XML processing, they could gain even more domination than they currently had in such industries, all under the guise of openness.  The perfect monopolistic trojan horse.
</P>
    <P>
And this was never just an idle menace.  Last year, Microsoft nearly suceeded in derailing XSLT by bundling a mutation of XSLT into its Internet Explorer 5 browser which was different from the emerging standards, and laden with Microsoft extensions.  Many Linux advocates cried loudly over Microsoft's "embrace-extend-extinguish" move on Kerberos, but this was a weak jab compared to the MS-XSL ploy.  Since Internet Explorer is by far the most popular browser, Microsoft ensured that most of the world's experience of XSLT came through their own proprietary version, and nearly made this proprietary version the de-facto standard.  There was many a flame-war on the xsl-list mailing list (see Resources) when IE users arrived in droves asking questions about what they perceived to be proper XSLT.
</P>
    <P>
But then something surprising happened.  Microsoft started to hear loudly and clearly from its customers that they didn't want an MS flavor of XSLT.  They wanted the standard.  The first signs of this were that Microsoft slowly started migrating to the standard in Internet Explorer updates.  Then MS developers announced publicly that their design goal was now full compliance with the XSLT standard.  Finally, after some prodding on xsl-list, several of Microsoft's developers admitted that they had been receiving numerous e-mail messages asking them to get in line.
</P>
    <P>
Now I know Linux users aren't used to expecting such sophistication and independent thought from large numbers of MS users, and I'm no exception to that (possibly bigoted) attitude.  I credit this remarkable episode to the power of the promise of openness in XML.  Of course, this doesn't prevent Microsoft from amusing gaffes such as claiming to have invented XML (as reported by The Washington Post in May), but such things are far less dangerous than standards pollution..
</P>
    <P>
Similar stories are repeated over and over throughout XML's brief history.  In fact, Microsoft, not having learned all its lessons from the XSLT fiasco, is currently being bludgeoned into abandoning its proprietary XML schema format, XML-Data, in favor of XML Schemas, which has come almost all the way through the W3C standards track.  The battle hit fever pitch with Microsoft's loud announcement of BizTalk, an ambitious repository and toolkit for XML schemas.  But day by day, it looks more as if the open standard will win out.
</P>
    <P>
But enough about the wide, wild world.  Let's have a look at what's happening at home.  Another striking change from my first XML article in these Web pages is that I pretty much had to apologize for the lack of XML tools for Linux.  This problem has been corrected to an astonishing degree.
</P>
    <P>
This article briefly introduces a selection of XML tools for Linux in a few basic categories: parsers, web servers, application servers, GUIs and bare-bones tools.  Most users' introduction to XML will be for purposes of better managing Web pages, from which they may choose to migrate to complete, all-inclusive appication servers or construct custom systems from the various XML toolkits available and the usual UNIX duct tape and wire ties.  In all cases there is usually some content to manage, and though you may see no reason to leave the world of Emacs or vi to churn out documents, since content-managers are often non-technical, it's a very good thing that there is a good selection of GUI XML editors for all tastes.
</P>
    <H3>Just the Parsers, Ma'am</H3>
    <P>
XML processing starts with the parser, and Linux has many to choose from.  Basically all you have to do is pick a language.  C, C++, Java, Python, PHP, Perl, TCL, or even Javascript (and this is hardly an exhaustive list).  The next thing to choose is whether and how to validate your XML documents.  Validation is the process of ensuring that all the elements and attributes in an XML document conform to a schema.  The traditional XML validation method is the Document-Type Definition (DTD).  The W3C, as I mentioned, has almost completed XML Schemas, which have the advantages of XML format (DTDs are in a different format) and "modern" data-typing, with the disadvantage of complexity and immaturity.
</P>
    <P>
C users are well served by the old standby from James Clark, Expat, which is a barebones parser and arguably the fastest in existence, but provides no validation.  Significantly, almost every language under the sun, from Python to Eiffel, provides a front-end to Expat.  But even Expat is facing some tough "coopetition" from entries such as the capable libxml project, led by Daniel Viellard of the W3C.  This library, most prominently used in GNOME, offers many options for fine-tuning parsing, and supports DTD validation.  There is also Richard Tobin's RXP, which supports DTD.  C++ users have Xerces-C++, which is based on XML4C code IBM donated to the Apache/XML project.  Xerces-C++ supports both DTD and Schemas.  In fact, if you want to start using XML Schemas in Linux, Xerces is probably your best bet.  Individual efforts include Michael Fink's xmlpp, which is quite new and doesn't support validation.
</P>
    <P>
There is a Java version of Xerces with similar pedigree.  Java users are pretty much drowned in choice.  The media has made much of the "marriage" between Java and XML, but the most likely explanation for the huge number of XML tools for Java is that XML emerged right as Java was cresting as a programming language.  Besides Xerces-J, there are Java parsers from Oracle, Sun, DataChannel, and others.  Individual efforts include Thomas Weidenfeller's XMLtp (Tiny XML Parser), which is designed for embedding into other Java apps (as was the pioneering but now moribund Aelfred from Microstar).  Mr. Weidenfeller also provides one of the neatest summaries of OSS license I've seen: "Do what you like with the software, but don't sue me".  Then there is The Wilson Partnership's MinML, designed to be even smaller, for use in embedded systems.
</P>
    <P>
Python still has the growing and evolving PyXML package as well as my own company's 4Suite.  XML considerations are helping shape many grand trends of Python such as unicode support and improved memory-management.  The perl community has definitely taken to XML.  The main parser is, appropriately, XML::Parser, but you can pretty much take any XML buzzword, prepend "XML::", and find a corresponding perl package.
</P>
    <H3>Serving up XML Pages</H3>
    <P>
XML's early promise to the media was as a way to tame the Web.  Structured documents, separation of content from presentation, and more manageable searching and autonomous Web agents.  Some of this has been drowned out by all the recent interest in XML for database integration and message-based middleware, but XML is still an excellent way to manage structured content on the Web.  And Linux is a pretty good operating system on which to host the content. 
</P>
    <P>
The big dog among the XML Web servers is also the well known big dog of Web servers, period.  Apache is absolutely swarming with XML activity lately.  I've already mentioned Xerces, the XML parser from the Apache/XML project.  There is also an XSLT processor, Xalan, with roots in IBM/Lotus's LotusXSL.  There is also Formatting-Object Processor (FOP), a tool for converting XML documents to the popular PDF document, by way of XSL formatting objects, a special XML vocabulary for presentation.  Apache has added support for the Simple Object Access Protocol (SOAP), an XML messaging protocol that can be used to make HTTP-based queries to a server in an XML format.  As a side note, SOAP, and open protocol, is heavily contributed to and championed by Microsoft, in one of the many positive contributions that company has made to XML while not trying to embrace and extend.
</P>
    <P>
These bits and pieces are combined into an Apache-based XML Web publishing solution called Cocoon.  Cocoon allows XML documents to be developed, and then published on the Web, for wireless applications through Wireless Application Protocol (WAP), and to print-ready PDF format through FOP.
</P>
    <P>
Perl hackers already have the proliferation of "XML::*" packages I've already mentioned, but Matt Sergeant has also put together a comprehensive toolkit for XML processing: Axkit.  Axkit is specialized for use with Apache and mod_perl, and provides XSLT transformation as well as other non-standard transform approaches such as "XPathScript".
</P>
    <H3>Full-blown application servers</H3>
    <P>
Enterprises that want an end-to-end solution for developing and deploying applications using XML data have several options under Linux.  Application servers build on basic Web servers such as described above by adding database integration, version control, distributed transactions and other such facilities.
</P>
    <P>
The grey and respectable Hewelett Packard found an open-source, Web-hip side with its e-speak project, a tool for distributed XML applications with Java, Python and C APIs for development and extension.
</P>
    <P>
A smaller company that has found the advantages of open-source for promoting its XML services is Lutris, Inc., developers of Enhydra.  Enhydra, about which I've reported in a previous LinuxWorld article, is a Java application server for XML processing.  It has some neat innovations such as XMLC, a way to "compile" XML into an intermediate binary form for efficient processing.  It is also one of the first open-source implementations of Java 2's Enterprise Edition services, including Enterprise JavaBeans.
</P>
    <P>
XML Blaster is a messaging-oriented middleware (MOM) suite for XML applications.  It uses an XML transport in a publish/subscribe system for exchanging text and binary data.  It uses CORBA for network and inter-process communication and supports components written in Java, Perl, Python and TCL.
</P>
    <P>
Conglomerate, developed by Styx, is a somewhat less ambitious but interesting project for an XML application server more attuned for document management.  It includes a nifty GUI editor and provides a proprietary transformation language that can generate HTML, TeX and other formats.
</P>
    <H3>Oo-wee!  GUI!</H3>
    <P>
One area in which I lamented Linux's lag in XML tools last year was in the area of GUI browsers and editors.  While I personally use a 4XSLT script and XEmacs for these respective tasks, I frequently work with clients who want to use more friendly GUIs for XML editing and ask whether my preferred Linux platform has anything available.  Fortunately, there are more choices than ever on our favorite OS.  Again much of the succour comes in the form of Java's cross-platform GUI support.
</P>
    <P>
GEXml is a Java XML editor which allows programmers use pluggable Java modules for editing their own special tag sets.  It uses a pretty standard layout for XML editors: a multi-pane window with a section for the tree-view, and sections for attributes and a section for CDATA.
</P>
    <P>
Merlot, by Channelpoint, Inc., is another Java-based XML editor that emphasizes modeling XML documents around their DTDs, abstracting the actual XML file from the user.  It supports pluggable extension modules for custom DTDs.
</P>
    <P>
Lunatech's Morphon is yet another DTD-based XML editor and modeling tool.  Hopefully all these DTD-based tools will expand to accommodate XML schemas and other validation methods as well in order to make life easier for those of us who use XML namespaces.  Morphon is similar to the other editors described here with a couple of nice twists: it allows you to specify cascading stylesheets for the editor appearance and document preview, and it mixes the ubiquitous tree view with a friendly view of the XML document being edited.  Morphon, however, is not open-source, though available for Linux.
</P>
    <P>
IBM's Alphaworks keeps on churning out free (beer) XML tools, one of which, XML Viewer, allows users to view XML documents using (once again) the tree-view and specialized panes for element and attribute data.  XML Viewer is written in Java.  It also allows linking the XML source and DTD to allow viewing such items as element and attribute definitions.  There is also XSL Editor, a specialized java-based XML editor for XSLT stylesheets.  It also incorporates advanced features such as syntax highlighting and an XSLT debugger.
</P>
    <P>
TreeNotes is an XML text editor that uses a series of widgets to open up XML's tree structure, elements and attributes, and of course character data, to editing.
</P>
    <P>
DocZilla is an interesting project: an extension of the Mozilla project for Web-based XML document applications.  It promises XML browsing support on par with Internet Explorer's including an extension and plug-in framework.  DocZilla started out very strongly, but now seems to have lagged a bit.  Part of the reason might be that Mozilla is increasing its XML focus.  Mozilla has always supported XML+Cascading Style-Sheets (CSS), but now, with Transformiix (an XSLT processor for Mozilla) and other such projects, it is making its own bid to replace Explorer as king of XML browsers.
</P>
    <P>
There is also KXMLViewer, a KDE XML viewer written in Python, but I'll cover this in more detail when I discuss GNOME and KDE XML support in a coming article in this series.
</P>
    <H3>In the Hacker Spirit</H3>
    <P>
So we've looked at lumbering app servers and pretty GUI tools.  All very nice for easing into XML, but we all know that Linux (and UNIX) users typically prefer sterner stuff.  Small, manageable, versatile, no-nonsense packages that can be strung together to get a larger job done.  Luckily for the desperate hacker, the nuts-and-bolts toolkit is growing just as quickly as the rest of XML space.
</P>
    <P>
A key and quite mature entry is LT XML, developed by the Edinburgh Language Technology Group.  LT XML is a set of stand-along tools and libraries for C programmers using XML.  It supports both tree-based and stream-oriented processing, covering a wide variety of application types.  The LT XML repertoire would be quite familiar and pleasant to those who love nothing more than to string together GNU textutils to produce some neat text transformation.  There is the mandatory XML-aware grep, sggrep (the "sg" for SGML), as well as sgsort, sgcount, sgtoken, etc, which should be self-explanatory.  Python bindings for LT XML should be available by the time you read this.
</P>
    <P>
Speaking of grep, there is also fxgrep, a powerful XML querying tool written in Standard ML, a well-regarded functional programming language from Bell Labs (XML provides a rather fitting problem space for functional languages).  fxgrep uses the XML parser fxp, also written in SML.  fxgrep supports specialized XML searching and query using its own pattern syntax.
</P>
    <P>
Paul Tchistopolskii makes clear there is no mistake as to his target user-base for Ux: "Ux is UNIX, revisited with XML".  Ux is a set of small XML components written in Java (OK, we're leaking some UNIX heritage right there).  The components are designed to be piped together for database storage and extraction, XSLT transformation, query, etc.
</P>
    <P>
Pyxie is an XML parsing and processing toolkit in Python by Sean McGrath and highlighted in his book, <I>XML Processing with Python</I>.  Pyxie's main distiction is that it builds on earlier work by James Clark by focusing on a line-based view of XML rather than the "natural" tokens that emerge from the spec.  This can provide a useful optimization if occasional complications.
</P>
    <P>
For those looking askance at XML in a TeX environment, IBM's Alphaworks might have a useful introduction.  TeXML is a tool that allows you to define an XSLT transform for converting XML files to a specialized vocabulary, the results of which are converted to TeX.  Also, thanks to Alphaworks, there is an XML diff as well as a grep.  XML Tree Diff shows the differences between documents based on their DOM tree representation.  It's more of a collection of Javabeans for performing diffs than a stand-alone application, but it's relatively straightforward to use.
</P>
    <P>
And there is my own company's 4Suite, a set of libraries for Python users to construct their own XML applications using DOM, XPath and XSLT, among other tools.  I covered 4XSLT in my last XML article (though the spec and 4XSLT have changed since then), and 4Suite libraries are now standard components in the Python XML distribution.
</P>
    <H3>Conclusion</H3>
    <P>
Hopefully this tour will help find XML resources for Linux users of all levels.  In upcoming articles (hopefully not as delayed as this one), I shall cover XML and Databases, XML and KDE/GNOME, and mnore topics on how to put XML to work in a Linux environment.
</P>
    <P>
By the way this very article is available in XML form (using the DocBook standard).  I've also put up a simplified DocBook XSLT stylesheet that can be used to render this article to HTML (see Resources for both).  Note that I use the "doc" file extension for DocBook files.  I encourage you to use DocBook (O'Reilly and Associates publishes an excellent book on the topic by Norman Walsh) and the ".doc" extension, chopping at the hegemony of the proprietary Microsoft Word format.  Just another small way XML can open up data to the world.
</P>
    <H3>Resources</H3>
    <H4>Parsers</H4>
    <DL>
      <DT><I>Expat</I></DT>
      <DD>http://www.jclark.com/xml/expat.html</DD>
      <DT><I>Xerces C++</I></DT>
      <DD>http://xml.apache.org/xerces-c/index.html</DD>
      <DT><I>Xerces-Java</I></DT>
      <DD>http://xml.apache.org/xerces-j/index.html</DD>
      <DT><I>xmlpp</I></DT>
      <DD>http://www.vividos.de/xmlpp/</DD>
      <DT><I>libxml</I></DT>
      <DD>http://www.xmlsoft.org/</DD>
      <DT><I>RXP</I></DT>
      <DD>http://www.cogsci.ed.ac.uk/~richard/rxp.html</DD>
      <DT><I>XMLtp</I></DT>
      <DD>http://mitglied.tripod.de/xmltp/</DD>
      <DT><I>MinML</I></DT>
      <DD>http://www.wilson.co.uk/xml/minml.htm</DD>
    </DL>
    <H4>Web Servers</H4>
    <DL>
      <DT><I>Axkit</I></DT>
      <DD>http://axkit.org/</DD>
      <DT><I>XML/Apache</I></DT>
      <DD>http://xml.apache.org</DD>
    </DL>
    <H4>App Servers</H4>
    <DL>
      <DT><I>Conglomerate</I></DT>
      <DD>http://www.conglomerate.org/</DD>
      <DT><I>e-speak</I></DT>
      <DD>http://www.e-speak.net/</DD>
      <DT><I>Enhydra</I></DT>
      <DD>http://www.enhydra.org/</DD>
      <DT><I>XML Blaster</I></DT>
      <DD>http://www.xmlBlaster.org/</DD>
    </DL>
    <H4>Low-Level Tools</H4>
    <DL>
      <DT><I>LT XML</I></DT>
      <DD>http://www.ltg.ed.ac.uk/software/xml/index.html</DD>
      <DT><I>fxgrep</I></DT>
      <DD>http://www.informatik.uni-trier.de/~neumann/Fxgrep/</DD>
      <DT><I>Ux</I></DT>
      <DD>http://www.pault.com/Ux/</DD>
      <DT><I>Pyxie</I></DT>
      <DD>http://www.digitome.com/pyxie.html</DD>
    </DL>
    <H4>GUIs</H4>
    <DL>
      <DT><I>TreeNotes</I></DT>
      <DD>http://pikosoft.dragontiger.com/en/treenotes/</DD>
      <DT><I>DocZilla</I></DT>
      <DD>http://www.doczilla.com/</DD>
      <DT><I>GEXml</I></DT>
      <DD>http://gexml.cx/</DD>
      <DT><I>Merlot</I></DT>
      <DD>http://www.merlotxml.org/</DD>
      <DT><I>Morphon</I></DT>
      <DD>http://www.morphon.com/</DD>
    </DL>
    <H4>Et Cetera</H4>
    <DL>
      <DT><I>There is more to XML than roll-your-own HTML</I></DT>
      <DD>http://www.linuxworld.com/linuxworld/lw-1999-03/lw-03-xml.html</DD>
      <DT><I>Practical XML with Linux, Part 1</I></DT>
      <DD>http://www.linuxworld.com/linuxworld/lw-1999-09/lw-09-xml2.html</DD>
      <DT><I>The xsl-list mailing list</I></DT>
      <DD>http://www.mulberrytech.com/xsl/xsl-list</DD>
      <DT><I>DocBook and stylesheet for this article</I></DT>
      <DD>http://www.Fourthought.com/Publications/lw-xml2</DD>
      <DT><I>The Apache/XML Project</I></DT>
      <DD>http://xml.apache.org/</DD>
      <DT><I>SOAP</I></DT>
      <DD>http://www.w3.org/TR/SOAP/</DD>
      <DT><I>xmlhack</I></DT>
      <DD>http://www.xmlhack.com</DD>
      <DT><I>XML Pit Stop</I></DT>
      <DD>http://www.xmlpitstop.com/</DD>
      <DT><I>xslt.com</I></DT>
      <DD>http://www.xslt.com</DD>
      <DT><I>XML Times</I></DT>
      <DD>http://www.xmltimes.com/</DD>
      <DT><I>The XML Cover Pages</I></DT>
      <DD>http://www.oasis-open.org/cover</DD>
      <DT><I>IBM's Alphaworks (including XML Viewer, XSL Edirot, XML Tree Diff and TeXML)</I></DT>
      <DD>http://alphaworks.ibm.com</DD>
    </DL>
  </BODY>
</HTML>"""


expected_3="""\
<HTML xmlns:doc="http://docbook.org/docbook/xml/4.0/namespace">
  <HEAD>
    <META HTTP-EQUIV='Content-Type' CONTENT='text/html; charset=ISO-8859-1'>
    <TITLE>An Overview of IBM DB2 Universal Database 7.1 for Linux</TITLE>
    <META CONTENT='text/html' charset='UTF-8' HTTP-EQUIV='content-type'>
    <META NAME='author' CONTENT='Uche Ogbuji'>
  </HEAD>
  <BODY>
    <H1>An Overview of IBM DB2 Universal Database 7.1 for Linux</H1>
    <H3></H3>
    <P>
      IBM has become legendary in the Linux community with its repeated announcments and re-announcements of Linux support.  It seems every six months at some Linux show ro even general PC show IBM pledges across the board Linux support.  All very odd because since Big Blue's first altar conversion a couple of years ago, it has done a great deal for the Linux community (despite purported resistance fro the AIX group), but by constantly re-proclaiming its allegiance, it gives the impression that it never followed through on prior pledges.  The truth is that IBM's many contributions to Linux have been typical big blue: very practical and thus very boring.  Jikes, IBM JDK, Apache patches and a Linux port to IBM 370 Mainframes (someone was <I>very</I> bored) are not exactly the sorts of goodies that have a Linux pundit hopping up and down, but they provide real, solid bases for businesses looking at Linux for critical tasks.  Not that IBM is incapable of splashy software: its remarkable Alphaworks project has constributed rather nifty stuff to the Java and XML communities (pretty much all of which runs on Linux).  See my recent article on XML and Linux for more details.
    </P>
    <P>
      The second side of the coin, besides contributing to free Linux software has ben supporting Linux with its popular and well-respected ("nobody ever got fired for buying IBM") commercial offerings.  IBM has made moves in this direction from the hardware end such as Thinkpads to the software end such as the subject of this article: DB2.  IBM first ported its Universal Database to Linux in version 6.0, in the great 1998/99 wave commercial database ports which also featured Oracle, Informix, Borland and Sybase.  In fact, DB2 for Linux was originally to be available at no charge and only became payware after IBM noticed high demand from corporate customers.  Big Blue has followed through with Linux versions of each subsequent release.  Promising the full panolpy of enterprise database features from a robust ANSI SQL 92 core to Object Database (if not yet SQL-99) extensions to administration, network, performance tuning, and replication tools, to extenders for geospacial systems, XML, hard-core financial number-crunching, et cetera, et cetera, et cetera.
    </P>
    <P>
      I downloaded IBM DB2 personal edition from the source (see Resources).  There was an option to order a CD, but the last time I ordered a DB2 CD from IBM (UDB 6.2), it took over two months, and I wanted to have a look this year.  Besides, linuxpecmn.tar was a pretty modest-sized download (relative to its peers) at 75 MB.  You might be wondering why IBM doesn't gzip it as well, but it turns out that most of the archive contents are RPMs, which already compress their contents.
    </P>
    <H3>Installation</H3>
    <P>
      My review machine is a Pentium II 500 with 256MB RAM and 4GB of disk space available for DB2.  The operating system is the KRUD distribution July 2000 release, based on Red Hat 6.2 (see my last Oracle article --linked in Resources-- for more on KRUD).
    </P>
    <P>
      If you caught my Oracle article you'll remember how harshly I criticized the 8.1.5 Linux release for installation and database creation difficulties ("tortures" would be more accurate, if too colorful).  In that article I might have mentioned that Oracle's terrible installation process on Linux was probably no worse than that of IBM DB2 Universal Database for Linux 6.1, which I actually gave up on trying to install and set-up.
    </P>
    <P>
      Part of the problem was the infamous confusion Red Hat introduced through its botched handling of the migration to Glibc 6.0 in Red Hat 6.1.  But even after dodging the bullets this sent at the DB2 user in either of two ways: by trying an install under Red hat 6.0 or by following detailed, unofficial instructions for install under Red Hat 6.1, there were many remaining problems with the installer and in the DB2 tools.  Judging from my experience and the size of the resulting DB2 6.1 fixpaks, it was pretty much of beta quality.  And so I sat down to install DB2 7.1 with some trepidation.  Was I in for more of the IBM DB2 6.1 and Oracle 8.1.5 treatment?  (See the side-bar for a brief update on whether Oracle 8.1.6 is any more lenient on the mortal user).
    </P>
    <P>
      The fact that I was able to get Oracle 8.1.5 installed and not DB2 6.1 was probably not because Oracle demanded less indulgence but because in addition to Dejanews and Technet there were the excellent third-party HOWTOs by people such as Jesus Salvo.  DB2 had rather few such resources that I could find until recently.
    </P>
    <P>
This time there is a HOWTO put together by Daniel Scott of IBM and
available from the Linux Documentation Project (see Resources).  Knowing
IBM's culture of brilliant individuals within a stultifying bureaucracy,
Mr. Scott probably got tired of DB2/Linux frustrations and took the
initative to put together the HOWTO, but regardless, it's an excellent
resource.  As a bonus, it covers a wide range of distributions, including
Caldera OpenLinux, Debian, Red Hat, SuSE and Turbo Linux.
</P>
    <P>
Armed with this, I dove into the install, starting with the installation
of the pdksh RPM from the KRUD CD.
</P>
    <PRE>
[root@euro /root]# rpm -i /mnt/cdrom/RedHat/RPMS/pdksh-5.2.14-2.i386.rpm 
</PRE>

    <P>
      Then I ran db2setup from the untarred DB2 Personal Edition root directory
    </P>
    <PRE>
[root@euro s000510.personal]# ./db2setup &amp;
</PRE>

    <P>
      This brought up the text-mode installer (see figure 1).  This of course is less flashy than the Java-based installers Oracle and Sybase have moved to, but it's far more readable and less idiosyncratic for all that.
    </P>
    <IMG SRC='db2-install.tiff' ALT='Figure 1: The DB2 Installer'>

    <P>
I selected the "Administration Client", then "Customize", and enabled
"Control Center".  I selected "DB2 Personal Edition", then "Customize", 
and enabled all options except for the "Local Control Warehouse
Database" and Asian code page options.  I then selected "DB2 Application
Development Client", then "Customize", and selected "Create Links for DB2
Libraries".  The next screen allowed automatic creation of a database
instance, which I opted for using the default user names for the
administration.  I also opted to add sample data to the created
instance.  I opted to set up distributed join on the database instance,
which allows SQL statements to involve multiple database instances.  I
also opted to "Create the Administration Server", with all default
options.
</P>
    <P>
Finally, after a stern "are you sure?" warning, the installation went
merrilly off, displaying a single-line status message witht he current
installing component.  It left a comprehensive log of its actions at
/tmp/db2setup.log.
</P>
    <P>
      So far, so good.  None of the problems I ran into with DB2 6.1: freezes and screen-scrawling.  With considerable relief, I found I had what appeared to be a working DB2 install and database instance with little or no fuss.
    </P>
    <P>
One final and often neglected aspect of installation is "de-installation".  It's nice to know
that if you ever cease to need a package or decide against using it after
installation, that you can remove it cleanly from your system.  Windows
users have the capable InstallShield for this, but Linux packagers often have to
each find do their own thing.  Luckily, since the DB2 is RPM-based,
uninstallation is simple enough, and accomplished by running the
db2_deinstall script from the package, CD, or installed location.  Oracle also 
provided uninstallation support, but through a custom interface.
</P>
    <H3>Getting Started</H3>
    <P>
DB2 comes with many nice GUI utilities, all using Java for display (which
seems to be the standard modus operandi of Linux database companies).  To
use it you must use IBM's JDK 1.1.8 for Linux, no other version, no
other vendor.  Write once, run anywhere on any JVM, right?  Ha.  At any
rate, IBM's JDK is the fastest available for Linux, and they hope to have
a 1.3 version soon (not that you'll be able to use it with DB2 UDB
7.1) See resources for the download link.
    </P>
    <P>
I downloaded the RPM and installed it:
</P>
    <PRE>
[root@euro V7.1]# rpm -i /root/packages/IBMJava118-SDK-1.1.8-4.0.i386.rpm 
</PRE>
    <P>Then I added the following lines environment entries to the various DB2
users:
</P>
    <PRE>
export JAVA_HOME=/usr/jdk118
export PATH=$PATH:$JAVA_HOME/bin
export CLASSPATH=$CLASSPATH:$JAVA_HOME/lib/classes.zip
</PRE>
    <P>
This should set up the environment for bash.  Note that if you're
using some other shell you might need a different format of commands to
set up the environment.
</P>
    <P>
Note that the DB2 installer places its environment set-up script in the
~/.bashrc script rather than ~/.bash_profile.
</P>
    <P>
After setting up the environment I logged in to the db2 administration
user and fired up the DB2 control center.
</P>
    <PRE>
[db2@euro db2]$ db2cc &amp;
</PRE>
    <P>
And I promptly ran into problems.  The DB2 splash window panel came up and
seemed to be hung until I noticed that there were the outlines of another
window behind it.  I wondered whether it was an error message of some
sort, but the splash screen obscured any controls for bringing it to the
front. and refused to get out of the way.  I was running the default
Enlightenment window manager under GNOME so I ended up switching it to
Sawfish (with which I'm more familiar) and I played with the config until I was able to force the error
message dialog to the front.
</P>
    <P>
So there is was in all its ignominy: "[IBM][JDBC Driver] CLI0602E  Memory allocation error on Server" (see figure 2).  Eh what?  Again this is a machine with 256MB RAM and though top did show that all RAM was soaked up (most of it hogged by the JRE, of course), there was 120MB of swap space free.  So I shrugged and closed the error window expecting to have to get out my medieval system
administration tools to get to the bottom of it, when to my surprise the
control center started up just fine despite the dire warning.
</P>
    <IMG SRC='jdbc-mem-error.tiff' ALT='Figure 2: Spurious JDBC Memory Error from DB2 Control Center'>
    <P>
But now the DB2 control center window was empty.  I was familiar with this
tool and knew that I should have seen entries representing my system and
the database instances set up therein, but there was nothing.  I closed
the control center and re-started, wondering whether the memory error was
the culprit.  On restarting I got the memory error again, but this time I
did get the entries I expected for my system and sample database
instance.  The bother didn't stop there, though.  On clicking on the
database instance icon I got a message that the database was not
started.  Odd, since I opted to have the database start on boot-up.
</P>
    <P>
So I went digging.  DB2 sets up an /etc/rc.db2, and adds an entry to the
/etc/inittab to start DB2 in runlevels 2, 3 and 4.  Of course, X Windows
on Red Hat (and most distros) operates in run level 5, and so DB2 wasn't
getting started.  I checked just to be positive, and surely enough, DB2 didn't
start after an explicit run level change (using telinit), nor after a reboot.
</P>
    <P>
But one thing the reboot did seem to cure was the JDBC memory error on control-center startup.  I
guess the installer must have siezed resources it refused to give up when
done.  Unless you want to spend time figuring out exactly what
rogue processes are involved, I'd suggest a reboot after DB2 install (what
a shame!)
</P>
    <P>
At any rate, although I expect not many people besides database reviewers
run datbases on machines with X Windows, for those that do, one can fix
DB2's auto-start by changing the /etc/inittab to entry from
</P>
    <PRE>
db:234:once:/etc/rc.db2 > /dev/console 2>&amp;1 # Autostart DB2 Services
</PRE>
    <P>to</P>
    <PRE>
db:2345:once:/etc/rc.db2 > /dev/console 2>&amp;1 # Autostart DB2 Services
</PRE>
    <P>Note the added "5".</P>
    <P>
At this point control center was content, and I as well because
control center is quite nice.  It's generally more responsive and
has more options than the very similar tool from Sybase, and it abstracts
all the  command-line and editing tasks that help make Oracle such a
pain.  There are still times that it takes ages to pop up windows and
refresh screens, but there was no clear pattern to this behavior.  See
figure 3 for a screen shot.
</P>
    <IMG SRC='db2cc.tiff' ALT='Figure 3: DB2 Control Center Screen Shot'>
    <P>
One of the tools in the Control Center is the Command Center, which is a
GUI-based SQL query tool.  It allows you enter individual commands and
scripts to DB2 instances, and presents the results in a nice
spreadhsheet-like display.  For instance, firing up the Command Center,
using the connect tool to connect to the SAMPLE database (or just entering
"connect to SAMPLE;" in the "Command" text box; then entering
</P>
    <P>
One of the tools in the Control Center is the Command Center, which is a
GUI-based query tool for Dynamic SQL, IBM's extended ANSI SQL command set.  It allows you enter individual commands and scripts to DB2 instances, and presents the results in a nice
spreadsheet-like display.  For instance, firing up the Command Center,
using the DB2 browser tool to connect to the SAMPLE database (or just entering
"connect to SAMPLE;" in the "Command" text box; then entering
</P>
    <PRE>
select * from staff;
</PRE>
    <P>
and then pressing CTRL-ENTER to execute the contents of the "Command" text box, resulted in the window in figure
4.  I must keep harping on how slow these Java tools are.  The Command
Center window was very sluggish displaying the result set.  I remember
using a very similar DB2 tool under OS/2 Presentation Manager years ago (and several cycles of Moore's Law ago) which
displayed results with considerable alacrity.  I guess that's the price of
cross-platform UI.
</P>
    <IMG SRC='cc-query-result.tiff' ALT='Figure 4: DB2 Command Center Query Result'>
    <P>
But most UNIX purists won't even bother because they'll be too busy enjoying the command line tools DB2 provides.  The main ingredient is the "db2" command, which can manage database commands across invocations, maintaining the session,
which provides great administrative power, especially when database
management and programming needs to be integrated into scripts.  A sample
session is very simple.  First the database connection is made:
</P>
    <P>

    </P>
    <PRE>
[db2@euro db2]$ db2 CONNECT TO SAMPLE

   Database Connection Information

 Database server        = DB2/LINUX 7.1.0
 SQL authorization ID   = DB2
 Local database alias   = SAMPLE

[db2@euro db2]$ 
</PRE>

    <P>
and then subsequent commands can be issued
</P>
    <PRE>
[db2@euro db2]$ db2 "select * from staff where id &lt; 100"

ID     NAME      DEPT   JOB   YEARS  SALARY    COMM     
------ --------- ------ ----- ------ --------- ---------
    10 Sanders       20 Mgr        7  18357.50         -
    20 Pernal        20 Sales      8  18171.25    612.45
    30 Marenghi      38 Mgr        5  17506.75         -
    40 O'Brien       38 Sales      6  18006.00    846.55
    50 Hanes         15 Mgr       10  20659.80         -
    60 Quigley       38 Sales      -  16808.30    650.25
    70 Rothman       15 Sales      7  16502.83   1152.00
    80 James         20 Clerk      -  13504.60    128.20
    90 Koonitz       42 Sales      6  18001.75   1386.70

  9 record(s) selected.

[db2@euro db2]$ 
</PRE>

    <P>
      At any time, you can jump into interactive mode:
    </P>
    <PRE>
[db2@euro db2]$ db2
(c) Copyright IBM Corporation 1993,2000
Command Line Processor for DB2 SDK 7.1.0

You can issue database manager commands and SQL statements from the
command 
prompt. For example:
    db2 => connect to sample
    db2 => bind sample.bnd

For general help, type: ?.
For command help, type: ? command, where command can be
the first few keywords of a database manager command. For example:
 ? CATALOG DATABASE for help on the CATALOG DATABASE command
 ? CATALOG          for help on all of the CATALOG commands.

To exit db2 interactive mode, type QUIT at the command prompt. Outside 
interactive mode, all commands must be prefixed with 'db2'.
To list the current command option settings, type LIST COMMAND OPTIONS.

For more detailed help, refer to the Online Reference Manual.

db2 => select * from staff where dept = 20

ID     NAME      DEPT   JOB   YEARS  SALARY    COMM     
------ --------- ------ ----- ------ --------- ---------
    10 Sanders       20 Mgr        7  18357.50         -
    20 Pernal        20 Sales      8  18171.25    612.45
    80 James         20 Clerk      -  13504.60    128.20
   190 Sneider       20 Clerk      8  14252.75    126.50

  4 record(s) selected.

db2 => quit
DB20000I  The QUIT command completed successfully.
[db2@euro db2]$ 
</PRE>

    <P>
      As you can see, just issue Dynamic SQL commands at the "db2 => " ptompt, or "quit" when you're done.  In either mode, to close the database connection, just use the "DISCONNECT" command:
    </P>
    <PRE>
[db2@euro db2]$ db2 disconnect SAMPLE
DB20000I  The SQL DISCONNECT command completed successfully.
[db2@euro db2]$ 
</PRE>

<H3>On-line Information</H3>
    <P>
DB2 combines system information and on-line documentation into the
Information Center tool, which you can invoke form the command line as
follows:
</P>
    <PRE>
[db2@euro db2]$ db2ic &amp;
</PRE>

    <P>
Which brings up a huge index.  The Information Center looks like a
Web/Java evolution of IBM's venerable Bookmanager documentation system, 
and sure enough, the DB2 information is very well organized, indexed and
associated in several views with each tree-view icon launching a chapter
in my Web browser.  The search function does not seem to come with
DB2 Personal Edition, reducing the utility of the information center
somewhat.
</P>
    <H3>Waaah!  No XML For Linux</H3>
    <P>
DB2 has not been left behind in the stampede to support XML.  Oracle, IBM,
Software AG and Informix have all announced major XML integration tools
and initiatives.  Oracle's XSQL, Intermedia and other facilities are
available for Linux already, but everyone else seems to have trouble
seeing past Windows XML users: Software AG might have been a Linux database pioneer
with Adabas, but their intriguing Tamino "Native XML" DBMS is NT and
Solaris only so far, and alas, IBM's DB2 XML Extender is Windows
only.  I had hoped to make the developer's section of this review
focus on XML, but this will have to wait until IBM is ready.  More on this
sad state of Linux/XML/DBMS affairs in another article.
</P>
    <H3>Conclusion</H3>
    <P>
IBM's DB2 is probably the most mature DBMS on the market, and it
shows in many respects.  It feels like a weird cross between the
old, unhip IBM and the new e-Business IBM (even though all my DB2 
experience has been using SQLC, using DB2 on Linux I almost feel as if I
should be firing up GNU COBOL for application programming).  I've reported
on several glitches I ran into during post-installation, but after this, and if one discounts the occasional
slow-downs in the management tools, DB2 proved solid and accessible during
management and programming.  IBM's pricing structure, which is uniform
across most platforms, is also very flexible, ranging from the $359
Personal Edition to the Developer's Edition, at $499 until December 13th,
to the grand Enterprise Extended Edition, and including revenue-sharing
options and other dot-com friendly packages.
</P>
    <P>
One nice thing about using IBM products is that IBM takes defect
management _very_ seriously.  You always have a clear idea of how to
proceed after troubleshooting.  You look for an APAR (Authorized Program
Analysis Report): IBM-ese for a "bug-report", which defines a very clear
path through remediation.  A couple of handy references which I link to
below are the Technical Library for DB2 and the DB2 downloads page where
you can find fixpaks and add-ons.  Also, if you use DB2 heavily, it might be a good idea to keep up with the International DB2 User's Group.
</P>
    <P>
There are a few third-party Linux DB2 tools such as J Enterprise Technologies' 
DataBrowser and DataManager 2.1, Java tools for browsing and managing a variety of databases including DB2 and MySQL.  Easysoft's SQLEngine allows queries and applications to work across heterogeneous databases including DB2 Postgres and MySQL.  I've already discussed OpenLink's ODBC drivers for Linux, which support DB2 as well as Oracle, Sybase and others.  All of these are commercial and listed in the Resources section.
</P>
    <P>
Nowadays the hardest choice for the prospective commercial Linux database user is deciding which product to use.  At the very high end it is a very close matter between Oracle and DB2, and though Oracle still has more of its enterprise add-ons ported to Linux so far, DB2 UDB 7.1 gives IBM the edge for Linux users by providing superior ease of use, stability and variety of tools.
</P>
    <H3>Resources</H3>
    <DL>
      <DT><I>Daniel Scott's DB2 HOWTO</I></DT>
      <DD>http://www.linuxdoc.org/HOWTO/DB2-HOWTO/index.html</DD>
      <DT><I>A practical guide to Oracle8i for Linux</I></DT>
      <DD>http://www.linuxworld.com/linuxworld/lw-2000-04/lw-04-oracle8i.html</DD>
      <DT><I>IBM JDK 1.1.8 for Linux</I></DT>
      <DD>http://www.ibm.com/java/jdk/118/linux/</DD>
      <DT><I>IBM Technical Library for DB2</I></DT>
      <DD>http://www-4.ibm.com/cgi-bin/db2www/data/db2/udb/winos2unix/support/techlib.d2w/report</DD>
      <DT><I>DB2 Downloads Page</I></DT>
      <DD>http://www-4.ibm.com/software/data/db2/udb/downloads.html</DD>
      <DT><I>International DB2 User's Group</I></DT>
      <DD>http://www.idug.org/</DD>
      <DT><I>DataBrowser/DataManager 2.1</I></DT>
      <DD>http://www.jetools.com/products/databrowser/</DD>
      <DT><I>Easysoft's SQLEngine</I></DT>
      <DD>http://www.easysoft.com/products/sql_engine/main.phtml</DD>
      <DT><I>OpenLink's Universal Data Access Driver Suite</I></DT>
      <DD>http://www.openlinksw.com/main/softdld.htm</DD>
      <DT><I>A bit of pro-DB2/Linux Propaganda</I></DT>
      <DD>http://www.vnunet.com/News/1104396</DD>
    </DL>
    <H3></H3>
    <P>
      XML is certainly an emerging and quick-changing technology.  One of the knocks against it has been the churn of standards and methodologies.  Certainly there is no greater evidence that XML is in flux than the fact that there is so much development and debate about how to validate XML documents, given that validation is one of the cornerstones of XML.
    </P>
    <P>
      This article introduces The Schematron, one of the currently available validation methodologies.  It will assume familiarity with XML, XML DTDs, and some familiarity with XPath and XSLT transforms.  For those who might need some grounding on one or more of those areas I've added some helpful links in the Resources section.
    </P>
    <H3>A Bit of Background</H3>
    <P>
      Although, as I pointed out in my last XML article on SunWorld (see Resources), XML doesn't introduce any notable innovation in data-processing, it has, through its popularity, introduced many useful disciplines inherited from SGML.  Perhaps the core discipline in this regard is in native support for validation.  One of XML's early promises in terms of easing information-management woes involved it's support for bundling the data schema with the data, and by providing for some standard schema discovery in cases where this bundling was not done.  Of course, the real-world has proven that this facility, while useful, is no panacea.  Even if one can a schema for machine-interpretation of a data set, how does one determine the semantics associated with that schema.  A further problem was the particular schema methodology that XML ended up being bundled with: Document-Type Definition (DTD).
    </P>
    <P>
DTDs are an odd mix of very generic and very specific expression.  For instance, simple tasks such as specifying that an element can have a number of particular child elements within a given range can be very cumbersome using DTDs.  Yet they are generic enough to allow such elegant design patterns as architectural forms (see Resources).  The expressive shortcomings of DTDs, along with arguments that XML validation should not require a separate computer language (DTDs of course differ in syntax from XML instances), encouraged the W3C, XML's major standards body, to develop a new schema language for XML, using XML syntax.  The resulting XML Schema specification is currently in "Candidate Recommendation" phase and presumably will soon hit version 1.0 (although based on experience with the DOM spec one should hardly rely on this).
</P>
    <P>
One of the key XML developments since XML 1.0 that has affected the schema story is XML Namespaces 1.0.  This recommendation provides a mechanism for disambiguating XML names, but does so in a way that is rather unfriendly to DTD users.  There are tricks for using namespaces with DTDs, but they are quite arcane.  Of course it must be noted that many of the SGML old school have argued that namespaces are a rather brittle solution, and furthermore they solve a rather narrow problem to justify such disruption in XML technologies.  The reality, however, is that with XML-related standards from XSLT to XLink relying heavily on namespaces, we shall have to develop solutions to the core problems that take namespaces into account.
</P>
    <P>
But back to validation.  The W3C Schema specification has been a long time in development, and along the way there began to be rumblings about the complexity of the emerging model.  XML Schemas did fill a very ambitious charter: covering document structure, data-typing worthy of databases, and even abstract data-modeling such as subclassing.
</P>
    <P>
And so because of the gap between the emergence of namespaces and the completion of XML Schemas, and because of fears that the coming specification was far too complex, the XML community, one with a remarkable history of practical problem-solving, went to work.
</P>
    <P>
One of the developments was Murata Makoto's Regular Language description for XML (RELAX) (see Resources).  Relax provides a system for developing grammars to describe XML documents.  It uses XML-like syntax and ofers similar featues to DTDs, adding some of the facilities offered by XML Schemas, such as schema annotation (basically, built-in documentation) and data-typing (for example specifying that an attribute value be an integer), and coming up with some exotic additions of its own such as "hedge grammars".  RELAX supports namespaces and provides a clean and inherently modular approach to validation and so has become rather popular, with its own mailing lists and contributed tools such as a DTD to RELAX translator (see Resources).
</P>
    <H3>A Different Approach: Harnessing the Power of XPath</H3>
    <P>
In the mean time XSLT emerged as a W3C standard, and immediately established itself as one of their most successful XML-related products.  Most people are familiar with XSLT as a tool to display XML content on "legacy" HTML-only browsers, but there is so much more to XSLT, largely because XPath, which it uses to express patterns in the XML source, is such a well-conceived tool.
</P>
    <P>
In fact, since XPath is such a comprehensive system for indicating and selecting from patterns in XML, there is no reason it could not express similar structural concepts as does DTD.  Take the following DTD, listing 1.
</P>
    <PRE>

&lt;!ELEMENT ADDRBOOK (ENTRY*)>
&lt;!ELEMENT ENTRY (NAME, ADDRESS, PHONENUM+, EMAIL)>
&lt;!ATTLIST ENTRY
    ID ID #REQUIRED
>
&lt;!ELEMENT NAME (#PCDATA)>
&lt;!ELEMENT ADDRESS (#PCDATA)>
&lt;!ELEMENT PHONENUM (#PCDATA)>
&lt;!ATTLIST PHONENUM
    DESC CDATA #REQUIRED
>
&lt;!ELEMENT EMAIL (#PCDATA)>

</PRE>

<P>
A sample document valid against this DTD is as follows, listing 2.
</P>
    <PRE>

&lt;?xml version = "1.0"?>
&lt;!DOCTYPE ADDRBOOK SYSTEM "addr_book.dtd">
&lt;ADDRBOOK>
        &lt;ENTRY ID="pa">
                &lt;NAME>Pieter Aaron&lt;/NAME>
                &lt;ADDRESS>404 Error Way&lt;/ADDRESS>
                &lt;PHONENUM DESC="Work">404-555-1234&lt;/PHONENUM>
                &lt;PHONENUM DESC="Fax">404-555-4321&lt;/PHONENUM>
                &lt;PHONENUM DESC="Pager">404-555-5555&lt;/PHONENUM>
                &lt;EMAIL>pieter.aaron@inter.net&lt;/EMAIL>
        &lt;/ENTRY>
        &lt;ENTRY ID="en">
                &lt;NAME>Emeka Ndubuisi&lt;/NAME>
                &lt;ADDRESS>42 Spam Blvd&lt;/ADDRESS>
                &lt;PHONENUM DESC="Work">767-555-7676&lt;/PHONENUM>
                &lt;PHONENUM DESC="Fax">767-555-7642&lt;/PHONENUM>
                &lt;PHONENUM DESC="Pager">800-SKY-PAGEx767676&lt;/PHONENUM>
                &lt;EMAIL>endubuisi@spamtron.com&lt;/EMAIL>
        &lt;/ENTRY>
&lt;/ADDRBOOK>

</PRE>

<P>
Examine the declaration of the ADDRBOOK element.  It basically says that such elements must have at least four child elements, a NAME, an ADDRESS, one or more PHONENUM and an EMAIL.  This can be expressed in XPath with a combination of the following three boolean expressions (using the ADDRBOOK element as the context):
</P>
    <PRE>
1. count(NAME) = 1 and count(ADDRESS) = 1 and count(EMAIL) = 1
2. NAME[following-sibling::ADDRESS] and ADDRESS[following-sibling::PHONENUM] and PHONENUM[following-sibling::EMAIL]
3. count(NAME|ADDRESS|PHONENUM|EMAIL) = count(*)
</PRE>

<P>
The first is true if and only if (iff) there is exactly one each of NAME, ADDRESS, and EMAIL.  This establishes the occurrence rule for these children.  The second is true iff there is a NAME followed by an ADDRESS, an ADDRESS followed by a PHONENUM and a PHONENUM followed by an EMAIL.  This establishes the sequence rule for the children.  Note that the preceding-sibling axis could have been used just as well.  The third expression is true iff there are no other elements besides the NAME ADDRESS PHONENUM EMAIL.  This establishes the (implied) DTD rule that elements are not permitted except where specified in the content model by name or with the ANY symbol.
</P>
    <P>
You first reaction might be that the XPath expressions are so much more verbose than the equivalent DTD specification.  This is so in this case, though one can easily come up with situations where the DTD equivalent would be more verbose than the equivalent XPath expressions.  However, this is entirely beside the point.  The DTD version is more concise because it is carefully designed to model such occurrence and sequence patterns.  XPath has far more general purpose and we are actually building the DTD equivalent through a series of primitives each of which operate at a more granular conceptual level than the DTD equivalent.  So it may be more wordy, but it has far greater expressive power.  Let's say we wanted to specify that there can be multiple ADDRESS and EMAIL children, but that they must be of the same number.  This task, which seems a simple enough extension of the previous content-midel, is pretty much beyond the abilities of DTD.  Not so XPath.  Since XPath gives a primitive but complete model of the document, it's an easy enough addition.
</P>
    <PRE>
1. count(NAME) = 1 and count(ADDRESS) = count(EMAIL)
2. NAME[following-sibling::ADDRESS] and ADDRESS[following-sibling::PHONENUM] and PHONENUM[following-sibling::EMAIL]
3. count(NAME|ADDRESS|PHONENUM|EMAIL) = count(*)
</PRE>

<P>
The only change is in expression 1, and should be self-explanatory.  This small foray beyond the scope of DTD illustrates the additional power offered by XPath.  Of course XPath can handle the attribute declarations as well.  For example, the attribute declaration for PHONENUM in the DTD can be expressed as follows (again using the ADDRBOOK element as context):
</P>
    <PRE>
PHONENUM/@DESC
</PRE>

<P>
All these XPath expressions are very well in the abstract, but how would one actually use them for validation?  The most convenient way is to write an XSLT transform that uses them to determine validity.  Here's an example, listing 3, which represents a sub-set of the address book DTD.
</P>
    <PRE>

&lt;?xml version="1.0"?>
&lt;xsl:transform xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">

  &lt;xsl:template match="/">
    &lt;xsl:if test='not(ADDRBOOK)'>
      Validation error: there must be an ADDRBOOK element at the root of the document.
    &lt;/xsl:if>
    &lt;xsl:apply-templates select='*'/>
  &lt;/xsl:template>

  &lt;xsl:template match="ENTRY">
    &lt;xsl:if test='not(count(NAME) = 1)'>
      Validation error: ENTRY element missing a NAME child.
    &lt;/xsl:if>
    &lt;xsl:if test='not(count(ADDRESS) = 1)'>
      Validation error: ENTRY element missing an ADDRESS child.
    &lt;/xsl:if>
    &lt;xsl:if test='not(count(EMAIL) = 1)'>
      Validation error: ENTRY element missing an EMAIL child.
    &lt;/xsl:if>
    &lt;xsl:if test='not(NAME[following-sibling::ADDRESS] and ADDRESS[following-sibling::PHONENUM] and PHONENUM[following-sibling::EMAIL])'>
      Validation error: ENTRY must have a NAME, ADDRESS, one or more PHONENUM, and an EMAIL in sequence
    &lt;/xsl:if>
    &lt;xsl:if test='not(count(NAME|ADDRESS|PHONENUM|EMAIL) = count(*))'>
      Validation error: there is an extraneous element child of ENTRY
    &lt;/xsl:if>
    &lt;xsl:apply-templates select='*'/>
  &lt;/xsl:template>

  &lt;xsl:template match="PHONENUM">
    &lt;xsl:if test='not(@DESC)'>
      Validation error: PHONENUM must have a DESC attribute
    &lt;/xsl:if>
    &lt;xsl:apply-templates select='*'/>
  &lt;/xsl:template>

  &lt;xsl:template match="*">
    &lt;xsl:apply-templates select='*'/>
  &lt;/xsl:template>

&lt;/xsl:transform>

</PRE>

<P>
When run with a valid document, such as the example above, this stylesheet would produce no output.  When run, however, with an invalid document such as the following, listing 4, however, it's a different story.
</P>
    <PRE>

&lt;?xml version = "1.0"?>
&lt;ADDRBOOK>
        &lt;ENTRY ID="pa">
                &lt;NAME>Pieter Aaron&lt;/NAME>
                &lt;PHONENUM DESC="Work">404-555-1234&lt;/PHONENUM>
                &lt;PHONENUM DESC="Fax">404-555-4321&lt;/PHONENUM>
                &lt;PHONENUM DESC="Pager">404-555-5555&lt;/PHONENUM>
                &lt;EMAIL>pieter.aaron@inter.net&lt;/EMAIL>
        &lt;/ENTRY>
        &lt;ENTRY ID="en">
                &lt;NAME>Emeka Ndubuisi&lt;/NAME>
                &lt;PHONENUM DESC="Work">767-555-7676&lt;/PHONENUM>
                &lt;PHONENUM DESC="Fax">767-555-7642&lt;/PHONENUM>
                &lt;PHONENUM DESC="Pager">800-SKY-PAGEx767676&lt;/PHONENUM>
                &lt;EMAIL>endubuisi@spamtron.com&lt;/EMAIL>
                &lt;ADDRESS>42 Spam Blvd&lt;/ADDRESS>
                &lt;SPAM>Make money fast&lt;/SPAM>
        &lt;/ENTRY>
        &lt;EXTRA/>
&lt;/ADDRBOOK>

</PRE>

<P>
Note that all the XPath expressions we came up with are placed in if statements and negated.  This is because they represent conditions such that we want a message put out if they are <I>not</I> met.  Running this source against the validation transform using an XSLT processor results in the following output:
</P>
    <PRE>

      Validation error: ENTRY element missing an ADDRESS child.
    
      Validation error: ENTRY must have a NAME, ADDRESS, one or more PHONENUM, and an EMAIL in sequence
    
      Validation error: ENTRY must have a NAME, ADDRESS, one or more PHONENUM, and an EMAIL in sequence
    
      Validation error: there must be an ENTRY element at the root of the document.
    

</PRE>

<P>
And so we have our validation result.  Note that it's pretty much a report of the document, such as we set it up to be.  One nice thing about this is that you can see all the validation errors at once.  Using most XML parsers you only get one error at a time.  But the real power of this XSLT-based validation report is that it's just that: a report.  We happened to use it for DTD-based XML validation, but it's not hard to see how this could be extended to more sophisticated data-management needs.  For instance, suppose we wanted to examine address-book documents for e-mail addresses in the .gov domain.  This is pretty much entirely beyond the realm of validation, but it is an example, as database programmers will immediately recognize, of reporting.
</P>
    <P>
While it might be argued one way or another whether validation and reporting are cut from the same conceptual cloth, it is pretty clear that in practice, XML document validation can be treated as a subset of XML document reporting, and furthermore that XPath and XSLT provide a powerful toolkit for document validation.
</P>
    <H3>Introducing the Schematron</H3>
    <P>
This re-casting of validation as a reporting problem is a core insight of the Schematron (see Resources).  The Schematron is a validation and reporting methodology and toolkit developed by Rick Jeliffe who, interestingly enough, is a member of the W3C Schema working group.  Without denigrating the efforts of his group, Mr. Jeliffe has pointed out that XML Schemas may be too complex for many users, and approaches validation from the same old approach as DTD.  He developed the Schematron as a simple tool to harness the power of XPath, attacking the schema problem from a new angle.  As he put it on his site, "The Schematron differs in basic concept from other schema languages in that it not based on grammars but on finding tree patterns in the parsed document. This approach allows many kinds of structures to be represented which are inconvenient and difficult in grammar-based schema languages."
</P>
    <P>
The Schematron is really no more than an XML vocabulary that can be used as an instruction set for generating stylesheets such as the one presented above.  For instance, the following, listing 5, is how our XPath-based validation might look like in The Schematron.
</P>
    <PRE>

&lt;schema xmlns='http://www.ascc.net/xml/schematron'>
        &lt;pattern name="Structural Validation">
                &lt;!-- Use a hack to set the root context.  Necessary because of
                     a bug in the schematron 1.3 meta-transforms. -->
                &lt;rule context="/*">
                        &lt;assert test="../addr:ADDRBOOK">Validation error: there must be an ADDRBOOK element at the root of the document.&lt;/assert>
                &lt;/rule>
                &lt;rule context="ENTRY">
                        &lt;assert test="count(NAME) = 1">Validation error: &lt;name/> element missing a NAME child.&lt;/assert>
                        &lt;assert test="count(ADDRESS) = 1">Validation error: &lt;name/> element missing an ADDRESS child.&lt;/assert>
                        &lt;assert test="count(EMAIL) = 1">Validation error: &lt;name/> element missing an EMAIL child.&lt;/assert>
                        &lt;assert test="NAME[following-sibling::ADDRESS] and ADDRESS[following-sibling::PHONENUM] and PHONENUM[following-sibling::EMAIL]">Validation error: &lt;name/> must have a NAME, ADDRESS, one or more PHONENUM, and an EMAIL in sequence&lt;/assert>
                        &lt;assert test="count(NAME|ADDRESS|PHONENUM|EMAIL) = count(*)">Validation error: there is an extraneous element child of ENTRY&lt;/assert>
                &lt;/rule>
                &lt;rule context="PHONENUM">
                        &lt;assert test="@DESC">Validation error: &lt;name/> must have a DESC attribute&lt;/assert>
                &lt;/rule>
        &lt;/pattern>
&lt;/schema>

</PRE>

<P>
The root element in schematron is the schema element in the appropriate namespace.  It contains one or more patterns, each of which represents a conceptual grouping of declarations.  Patterns contain one or more rules, each of which sets a context for a series of declarations.  This is not only a conceptual context, but also the context that is used for the XPath expressions in declarations within each rule.
</P>
    <P>
Each rule contains a collection of asserts, reports and keys.  You can see asserts at work in our example.  Asserts are similar to asserts in C.  They represent a declaration that a condition is true, and if it is not true, a signal is made to such effect.  In the Schematron, assert elements specify that if the condition in their test attribute is not true, the content of the assert elements will be copied to the result.  You'll note that the assert messages contain empty <PRE>name</PRE> elements.  This is a convenient short-hand for the name of the current context node, given by the parent rule element.  This makes it easy to reuse asserts from context to context.  Reports are similar to asserts, except that they output their contents when the condition in their test attribute is true rather than false.  They also allow the use of the empty name element.  Reports, as their name implies, tend to make sense for structural reporting tasks.  For instance, to implement our eariler example of reporting e-mail addresses in the .gov domain we might add the following rule to our Schematron:
</P>

<PRE>

                &lt;rule context="EMAIL">
                        &lt;report test="contains(., '.gov') and not(substring-after(., '.gov'))">This address book contains government contacts.&lt;/report>
                &lt;/rule>

</PRE>

<P>
Of course I already mentioned that namespaces are an important reason to seek a different validation methodology than DTDs.  Schematron supports namespaces through XPath's support for namespaces.  For instance, if we wanted to validate that all child elements of ENTRY in our address book document were in a particular namespace, we could do so so by adding an assert which checks the count of elements in a particular namespace.  Assume that the prefix "addr" is bound to the target namespace in the following example:
</P>
    <PRE>
count(addr:*) = count(*)
</PRE>

<P>
Maybe that's too draconian for your practical needs and you want to also allow elements in a particular namespace reserved for extansions.
</P>
    <PRE>
count(addr:*) + count(ext:*) = count(*)
</PRE>

<P>
Maybe rather than permitting a single particular extension namespace, you want to instead allow any elements with namespaces whose URI contains the string "extension":
</P>
    <PRE>
count(addr:*) + count(*[contains(namespace(.), 'extension')]) = count(*)
</PRE>

<P>
With this latter addition and the addition of a report for e-mail addresses in the .gov address our schematron looks as follows, listing 6.
</P>
    <PRE>

&lt;schema xmlns='http://www.ascc.net/xml/schematron'>

        &lt;ns prefix='addr' uri='http://addressbookns.com'/>

        &lt;pattern name="Structural Validation">
                &lt;!-- Use a hack to set the root context.  Necessary because of
                     a bug in the schematron 1.3 meta-transforms. -->
                &lt;rule context="/*">
                        &lt;assert test="../addr:ADDRBOOK">Validation error: there must be an ADDRBOOK element at the root of the document.&lt;/assert>
                &lt;/rule>
                &lt;rule context="addr:ENTRY">
                        &lt;assert test="count(addr:*) + count(*[contains(namespace-uri(.), 'extension')]) = count(*)">
Validation error: all children of &lt;name/> must either be in the namespace 'http://addressbookns.com' or in a namespace containing the substring 'extension'.
                        &lt;/assert>
                        &lt;assert test="count(addr:NAME) = 1">
Validation error: &lt;name/> element missing a NAME child.
                        &lt;/assert>
                        &lt;assert test="count(addr:ADDRESS) = 1">
Validation error: &lt;name/> element missing an ADDRESS child.
                        &lt;/assert>
                        &lt;assert test="count(addr:EMAIL) = 1">
Validation error: &lt;name/> element missing an EMAIL child.
                        &lt;/assert>
                        &lt;assert test="addr:NAME[following-sibling::addr:ADDRESS] and addr:ADDRESS[following-sibling::addr:PHONENUM] and addr:PHONENUM[following-sibling::addr:EMAIL]">
Validation error: &lt;name/> must have a NAME, ADDRESS, one or more PHONENUM, and an EMAIL in sequence
                        &lt;/assert>
                        &lt;assert test="count(addr:NAME|addr:ADDRESS|addr:PHONENUM|addr:EMAIL) = count(*)">
Validation error: there is an extraneous element child of ENTRY
                        &lt;/assert>
                &lt;/rule>
                &lt;rule context="addr:PHONENUM">
                        &lt;assert test="@DESC">
Validation error: &lt;name/> must have a DESC attribute
                        &lt;/assert>
                &lt;/rule>
        &lt;/pattern>
        &lt;pattern name="Government Contact Report">
                &lt;rule context="addr:EMAIL">
                        &lt;report test="contains(., '.gov') and not(substring-after(., '.gov'))">
This address book contains government contacts.
                        &lt;/report>
                &lt;/rule>
        &lt;/pattern>
&lt;/schema>

</PRE>

<P>
Note the new top-level element, ns.  We use this to declare the namespace that we'll be incorporating into the schematron rules.  If you have multiple such namespaces to declare, use one ns element for each.  Note that there are some advanced uses of schematron namespace declarations about which you can read on theSchematron site.
</P>
    <P>
This was a pretty quick whirl through The Schematron.  This shouldn't be much of a problem since it is so simple.  However, for a bit more instruction, there is the tidy tutorial put together by Dr Miloslav Nic (see Resouces.  Note that the good Doctor has tutorials on many other XML-related topics at his page).  There are also a few examples linked from the Schematron home page.
</P>
    <H3>Putting The Schematron to Work</H3>
    <P>
So how do we use The Schematron?  Rememeber that a Schematron document could be thought of as a instructions for generating special validation and report transforms such as we introduced earlier.  This is in fact the most common way of using The Schematron in practice.  Conveniently enough, XSLT has all the power to convert Schematron specifications to XSLT-based validators.  There is a meta-transform available at the Schematron Web site which, when run against a schematron specification, will generate a specialized validator/reporter transform which can be then run against target source documents.  For instance, suppose I have the above schematron specification as "addrbook.schematron".  I can turn it into a validator/reporter transform as follows:
</P>
    <PRE>
[uogbuji@borgia code]$ 4xslt.py listing6.schematron ~/devel/Ft/Xslt/test_suite/borrowed/schematron-skel-ns.xslt > addrbook.validator.xslt
</PRE>

<P>
Here and for all other examples in this article, I am using the 4XSLT processor.  4XSLT (see Resources) is an XSLT 1.0-compliant processor written in Python and distributed as open source by my company, Fourthought, Inc.  I ran the above from Linux and the first argument to 4xslt.py is the XML source document: in this case the schematron specification in listing 6.  The second argument is the transform to be used, in this case the Schematron namespace-aware meta-transform.  I then redirect the standard output to the file addrbook.validator.xslt, which thus becomes my validator/reporter transform.  I can then run the validator transform against the following source document, listing 7.
</P>
    <PRE>

&lt;?xml version = "1.0"?>
&lt;ADDRBOOK xmlns='http://addressbookns.com'>
        &lt;ENTRY ID="pa">
                &lt;NAME xmlns='http://bogus.com'>Pieter Aaron&lt;/NAME>
                &lt;ADDRESS>404 Error Way&lt;/ADDRESS>
                &lt;PHONENUM DESC="Work">404-555-1234&lt;/PHONENUM>
                &lt;PHONENUM DESC="Fax">404-555-4321&lt;/PHONENUM>
                &lt;PHONENUM DESC="Pager">404-555-5555&lt;/PHONENUM>
                &lt;EMAIL>pieter.aaron@inter.net&lt;/EMAIL>
        &lt;/ENTRY>
        &lt;ENTRY ID="en">
                &lt;NAME xmlns='http://bogus.com'>Emeka Ndubuisi&lt;/NAME>
                &lt;ADDRESS>42 Spam Blvd&lt;/ADDRESS>
                &lt;PHONENUM DESC="Work">767-555-7676&lt;/PHONENUM>
                &lt;PHONENUM DESC="Fax">767-555-7642&lt;/PHONENUM>
                &lt;PHONENUM DESC="Pager">800-SKY-PAGEx767676&lt;/PHONENUM>
                &lt;EMAIL>endubuisi@spamtron.com&lt;/EMAIL>
        &lt;/ENTRY>
&lt;/ADDRBOOK>

</PRE>

<P>
Yielding the following output:
</P>
    <PRE>
[uogbuji@borgia code]$ 4xslt.py listing7.xml addrbook.validator.xslt 
Validation error: all children of ENTRY must either be in the namespace 'http://addressbookns.com' or in a namespace containing the substring 'extension'.Validation error: ENTRY element missing a NAME child.Validation error: ENTRY must have a NAME, ADDRESS, one or more PHONENUM, and an EMAIL in sequenceValidation error: there is an extraneous element child of ENTRYValidation error: all children of ENTRY must either be in the namespace 'http://addressbookns.com' or in a namespace containing the substring 'extension'.Validation error: ENTRY element missing a NAME child.Validation error: ENTRY must have a NAME, ADDRESS, one or more PHONENUM, and an EMAIL in sequenceValidation error: there is an extraneous element child of ENTRY
</PRE>

<P>
Hmm.  Rather a mess, what?  Looks as if there were quite a few messages combined without clear separation.  There were actually two sets of messages, one for each ENTRY in the source document, since we caused the same cascade of validation errors in both by messing with the namespace of the NAME element.  The reason the two messages run together so is that we used the skeleton Schematron meta-transform.  The skeleton comes with only basic output support, and in particular, it normalizes space in all output, running the results together.
</P>
    <P>
There's a good chance this is not what you want, and luckily Schematron is designed to be quite extensible.  There are several schematron meta-transforms on the Schematron home page that build on the skeleton by importing it.  They range from basic, clearer text messages to HTML for browser-integration.  Using the sch-basic meta-transform rather than the skeleton yields:
</P>
    <PRE>
[uogbuji@borgia code]$ 4xslt.py listing6.schematron ~/devel/Ft/Xslt/test_suite/borrowed/sch-basic.xslt > addrbook.validator.xslt
[uogbuji@borgia code]$ 4xslt.py listing7.xml addrbook.validator.xslt 
In pattern Structural Validation:
   Validation error: all children of ENTRY must either be in the namespace 'http://addressbookns.com' or in a namespace containing the substring 'extension'.
In pattern Structural Validation:
   Validation error: ENTRY element missing a NAME child.
In pattern Structural Validation:
   Validation error: ENTRY must have a NAME, ADDRESS, one or more PHONENUM, and an EMAIL in sequence
In pattern Structural Validation:
   Validation error: there is an extraneous element child of ENTRY
In pattern Structural Validation:
   Validation error: all children of ENTRY must either be in the namespace 'http://addressbookns.com' or in a namespace containing the substring 'extension'.
In pattern Structural Validation:
   Validation error: ENTRY element missing a NAME child.
In pattern Structural Validation:
   Validation error: ENTRY must have a NAME, ADDRESS, one or more PHONENUM, and an EMAIL in sequence
In pattern Structural Validation:
   Validation error: there is an extraneous element child of ENTRY

</PRE>

<P>
To round things up, here is an example, listing 8, of a source document that validates cleanly against our sample schematron.
</P>
    <PRE>

&lt;?xml version = "1.0"?>
&lt;ADDRBOOK xmlns='http://addressbookns.com'>
        &lt;ENTRY ID="pa">
                &lt;NAME>Pieter Aaron&lt;/NAME>
                &lt;ADDRESS>404 Error Way&lt;/ADDRESS>
                &lt;PHONENUM DESC="Work">404-555-1234&lt;/PHONENUM>
                &lt;PHONENUM DESC="Fax">404-555-4321&lt;/PHONENUM>
                &lt;PHONENUM DESC="Pager">404-555-5555&lt;/PHONENUM>
                &lt;EMAIL>pieter.aaron@inter.net&lt;/EMAIL>
        &lt;/ENTRY>
        &lt;ENTRY ID="en">
                &lt;NAME>Manfredo Manfredi&lt;/NAME>
                &lt;ADDRESS>4414 Palazzo Terrace&lt;/ADDRESS>
                &lt;PHONENUM DESC="Work">888-555-7676&lt;/PHONENUM>
                &lt;PHONENUM DESC="Fax">888-555-7677&lt;/PHONENUM>
                &lt;EMAIL>mpm@scudetto.dom.gov&lt;/EMAIL>
        &lt;/ENTRY>
&lt;/ADDRBOOK>

</PRE>

<P>
Which we test as follows.
</P>
    <PRE>
[uogbuji@borgia code]$ 4xslt.py listing8.xml addrbook.validator.xslt 
In pattern Government Contact Report:
   This address book contains government contacts.

</PRE>

<P>
Now everything is in the correct namespace so we get no validation errors.  However, notice that we did get the report from the e-mail address in the .gov domain.
</P>
    <P>
This is all very well, but no doubt you're wondering whether XSLT is fast enought to suit your real-world validation needs.  This will of course depend on your needs.  In my experience, it is very rarely necessary to validate a document every time it is processed.  If you have attributes with default value, or you have no control at all over the sources of your data throughout your processing applications then you may have no choice.  In this case, validation by an XML 1.0-compliant validating parser such as xmlproc (see Resources) is almost certainly faster than XSLT-based Schematron.  But then again, there is no hard requirement that a Schematron processor use XSLT.  It would not be terribly difficult, given an efficient XPath library, to write a specialized Schematron application that doesn't need translation from meta-transforms.
</P>
    <P>
But just to give a quick comparison, I parsed a 170K address book example similar to the above but with more entries.  Using xmlproc and DTD validation it took 7.25 seconds.  Parsing this document without validation and then applying the schematron transform took 10.61 seconds.  Hardly so great a penalty.
</P>
    <P>
Of course there are several things that DTDs provide that Schematron cannot.  The most notable are entity and notation definitions and fixed or default attribute values.  RELAX does not provide any of these facilities either, but XML Schemas do provide all of them as it must since it is positioned as a DTD replacement.  RELAX makes no such claim and indeed the RELAX documentation has a section on using RELAX in concert with DTD.  We have already discussed that Schematron, far from claiming to be a DTD replacement, is positioned as an entirely fresh approach to validation.  Nevertheless, attribute-value defaulting can be a useful way to reduce the clutter of XML documents for human readability so we shall examine one way to provide default attributes in association with Schematron.
</P>
    <P>
Remember that you're always free to combine DTD with Schematron to get the best of both worlds, but if you want to to leave DTD entirely behind, you can still get attribute-defaulting at the cost of one more pass through the document when the values are to be substituted.  This can easily be done by a transform that turns a source document to a result that is identical except that all default attribute values are given.
</P>
    <P>
There are other features of Schematron for those interested in further exploration.  For instance it supports keys: a mechanism similar to DTD's ID and IDREF.  There are some hooks for embedding and control through external applications.  Certainly a more formal introduction to Schematron is available in the Schematron specification (see Resources).
</P>
    <H3>Conclusion</H3>
    <P>
We at Fourthought pretty much stopped using DTD about a year ago when we started using namespaces in earnest.  We soon seized on Schematron and have used it in deployed work product for our clients and internally.  Since we already do a lot of work with XSLT it's a very comfortable system and the training required for XPath isn't much of an issue.  To match most of the basic features of DTD, not much more knowledge should be required than path expressions, predicates, unions, the sibling and attribute axes, and a handful of functions such as count.  Performance has not been an issue because we typically have strong control over XML data in our systems and hardly ever use defaulted attributes.  This allows us to validate only when a new XML datum is input, or an existing datum modified our systems, reducing performance concerns.
</P>
    <P>
Schematron is a clean, well-considered approache to the problems of validation and simple reporting.  XML Schemas are a significant development, but it is debatable whether such an entirely new and complex system is required for such a straightforward task as validation.  RELAX and The Schematron both present simpler approaches coming from different angles and they might be a better fit for quick integration into XML systems.  In any case, Schematron once again demonstrates the extraordinary reach of XSLT and the flexibility of XML in general as a data-management technology.
</P>
    <H3>Resources</H3>
    <DL>
      <DT><I>RELAX XML Schema System</I></DT>
      <DD>http://www.xml.gr.jp/relax/</DD>
      <DT><I>W3C XML Schemas: Primer</I></DT>
      <DD>http://www.w3.org/TR/xmlschema-0/</DD>
      <DT><I>W3C XML Schemas Part 1: Structures</I></DT>
      <DD>http://www.w3.org/TR/xmlschema-1/</DD>
      <DT><I>W3C XML Schemas Part 2: Datatypes</I></DT>
      <DD>http://www.w3.org/TR/xmlschema-2/</DD>
      <DT><I>DTD2RELAX</I></DT>
      <DD>http://www.horobi.com/Projects/RELAX/Archive/DTD2RELAX.html</DD>
      <DT><I>The Schematron home page</I></DT>
      <DD>http://www.ascc.net/xml/resource/schematron/schematron.html</DD>
      <DT><I>Rick Jelliffe's Comparison of Various Schema Methods</I></DT>
      <DD>http://www.ascc.net/%7ericko/XMLSchemaInContext.html</DD>
      <DT><I>4XSLT</I></DT>
      <DD>http://www.fourthought.com/4XSLT</DD>
      <DT><I>4Suite</I></DT>
      <DD>http://www.fourthought.com/4Suite</DD>
      <DT><I>Schematron Tutorial</I></DT>
      <DD>http://www.zvon.org/HTMLonly/SchematronTutorial/General/contents.html</DD>
      <DT><I>Other ZVON Tutorials for XML-related topics</I></DT>
      <DD>http://www.zvon.org/</DD>
      <DT><I>The Schematron Specification</I></DT>
      <DD>http://www.ascc.net/xml/resource/schematron/Schematron2000.html</DD>
      <DT><I>General news, product info, etc. concerning XSLT</I></DT>
      <DD>http://www.xslt.com</DD>
      <DT><I>General news, product info, etc. concerning XML</I></DT>
      <DD>http://www.xmlhack.com</DD>
      <DT><I>Slides from an XSLT introduction by the author</I></DT>
      <DD>http://fourthought.com/Presentations/xmlforum-xslt-20000830</DD>
      <DT><I>The XSLT FAQ</I></DT>
      <DD>http://www.dpawson.freeserve.co.uk/xsl/xslfaq.html</DD>
      <DT><I>Zvon XSLT Reference</I></DT>
      <DD>http://www.zvon.org/xxl/XSLTreference/Output/index.html</DD>
      <DT><I>Zvon DTD tutorial</I></DT>
      <DD>http://www.zvon.org/xxl/DTDTutorial/General/book.html</DD>
      <DT><I>Zvon namespace tutorial</I></DT>
      <DD>http://www.zvon.org/xxl/NamespaceTutorial/Output/index.html</DD>
      <DT><I>Zvon XML tutorial</I></DT>
      <DD>http://www.zvon.org/xxl/XMLTutorial/General/book_en.html</DD>
      <DT><I>Zvon XPath tutorial</I></DT>
      <DD>http://www.zvon.org/xxl/XPathTutorial/General/examples.html</DD>
      <DT><I>Zvon XSLT tutorial</I></DT>
      <DD>http://www.zvon.org/xxl/XSLTutorial/Books/Book1/index.html</DD>
      <DT><I>Links related to architectural forms</I></DT>
      <DD>http://www.xml.com/pub/Guide/Architectural_Forms</DD>
    </DL>
    <H3></H3>
    <P>
On re-reading my first two XML articles, just over a year ago in this journal and in its sister, Sunworld, I'm struck by how much they represented a justification of XML as the great tin opener of closed data formats.  In under a year, it looks as if all the light-bulbs went on at once.  XML is in the computer news every day, every company seems to be scrambling to ink XML into their brochures, and XML standards organizations such as the World-Wide Web consortium (W3C) practically have to turn people away.  At this point I hardly think any more justification of XML for open data exchange is required.  It's pretty much a fact of information technology.  The remaining questions are how to use XML to solve real problems better than with any other means.
</P>
    <P>
As I mentioned in my most recent article, the W3C and other standards organizations are working very quickly to complete specifications for technologies complementary to XML.  I mentioned namespaces, which are a key facility for managing global names and are now used in almost every XML technology.  I also mentioned DOM and XSLT.  Since then, XLink, XPointer, XML Schemas, SVG and other specs are almost complete.  I shall discuss these later in the series as well as RDF, Schematron and other beasts in the XML menagerie.  The XML community has also matured greatly, and as one example, there are many new, high-quality information and news sites, some of which I list in Resources section.  If you are highly interested in XML, I highly recommend regular visits to xmlhack, in particular.
</P>
    <H3>The Triumph of Open Standards</H3>
    <P>
The most amazing thing about XML's incredible rise, in my opinion sharper than that of the PC, Java, or even the Web, is the fact that it has remained as open as when it started.  Even though XML in its early days was positioned as a tool for encouraging data interchange by providing both human and machine readibility, odds always were that a powerful company, or group of companies would foul the waters.  Many vertical industries such as the automobile inustry (which recently surprised analysts by announcing a huge, XML-driven on-line exchange), health-care and chemicals have been moving to XML as data-exchange format.  If the likes of Microsoft (early and on-going XML champion) and Oracle, could co-opt standards for XML processing, they could gain even more domination than they currently had in such industries, all under the guise of openness.  The perfect monopolistic trojan horse.
</P>
    <P>
And this was never just an idle menace.  Last year, Microsoft nearly suceeded in derailing XSLT by bundling a mutation of XSLT into its Internet Explorer 5 browser which was different from the emerging standards, and laden with Microsoft extensions.  Many Linux advocates cried loudly over Microsoft's "embrace-extend-extinguish" move on Kerberos, but this was a weak jab compared to the MS-XSL ploy.  Since Internet Explorer is by far the most popular browser, Microsoft ensured that most of the world's experience of XSLT came through their own proprietary version, and nearly made this proprietary version the de-facto standard.  There was many a flame-war on the xsl-list mailing list (see Resources) when IE users arrived in droves asking questions about what they perceived to be proper XSLT.
</P>
    <P>
But then something surprising happened.  Microsoft started to hear loudly and clearly from its customers that they didn't want an MS flavor of XSLT.  They wanted the standard.  The first signs of this were that Microsoft slowly started migrating to the standard in Internet Explorer updates.  Then MS developers announced publicly that their design goal was now full compliance with the XSLT standard.  Finally, after some prodding on xsl-list, several of Microsoft's developers admitted that they had been receiving numerous e-mail messages asking them to get in line.
</P>
    <P>
Now I know Linux users aren't used to expecting such sophistication and independent thought from large numbers of MS users, and I'm no exception to that (possibly bigoted) attitude.  I credit this remarkable episode to the power of the promise of openness in XML.  Of course, this doesn't prevent Microsoft from amusing gaffes such as claiming to have invented XML (as reported by The Washington Post in May), but such things are far less dangerous than standards pollution..
</P>
    <P>
Similar stories are repeated over and over throughout XML's brief history.  In fact, Microsoft, not having learned all its lessons from the XSLT fiasco, is currently being bludgeoned into abandoning its proprietary XML schema format, XML-Data, in favor of XML Schemas, which has come almost all the way through the W3C standards track.  The battle hit fever pitch with Microsoft's loud announcement of BizTalk, an ambitious repository and toolkit for XML schemas.  But day by day, it looks more as if the open standard will win out.
</P>
    <P>
But enough about the wide, wild world.  Let's have a look at what's happening at home.  Another striking change from my first XML article in these Web pages is that I pretty much had to apologize for the lack of XML tools for Linux.  This problem has been corrected to an astonishing degree.
</P>
    <P>
This article briefly introduces a selection of XML tools for Linux in a few basic categories: parsers, web servers, application servers, GUIs and bare-bones tools.  Most users' introduction to XML will be for purposes of better managing Web pages, from which they may choose to migrate to complete, all-inclusive appication servers or construct custom systems from the various XML toolkits available and the usual UNIX duct tape and wire ties.  In all cases there is usually some content to manage, and though you may see no reason to leave the world of Emacs or vi to churn out documents, since content-managers are often non-technical, it's a very good thing that there is a good selection of GUI XML editors for all tastes.
</P>
    <H3>Just the Parsers, Ma'am</H3>
    <P>
XML processing starts with the parser, and Linux has many to choose from.  Basically all you have to do is pick a language.  C, C++, Java, Python, PHP, Perl, TCL, or even Javascript (and this is hardly an exhaustive list).  The next thing to choose is whether and how to validate your XML documents.  Validation is the process of ensuring that all the elements and attributes in an XML document conform to a schema.  The traditional XML validation method is the Document-Type Definition (DTD).  The W3C, as I mentioned, has almost completed XML Schemas, which have the advantages of XML format (DTDs are in a different format) and "modern" data-typing, with the disadvantage of complexity and immaturity.
</P>
    <P>
C users are well served by the old standby from James Clark, Expat, which is a barebones parser and arguably the fastest in existence, but provides no validation.  Significantly, almost every language under the sun, from Python to Eiffel, provides a front-end to Expat.  But even Expat is facing some tough "coopetition" from entries such as the capable libxml project, led by Daniel Viellard of the W3C.  This library, most prominently used in GNOME, offers many options for fine-tuning parsing, and supports DTD validation.  There is also Richard Tobin's RXP, which supports DTD.  C++ users have Xerces-C++, which is based on XML4C code IBM donated to the Apache/XML project.  Xerces-C++ supports both DTD and Schemas.  In fact, if you want to start using XML Schemas in Linux, Xerces is probably your best bet.  Individual efforts include Michael Fink's xmlpp, which is quite new and doesn't support validation.
</P>
    <P>
There is a Java version of Xerces with similar pedigree.  Java users are pretty much drowned in choice.  The media has made much of the "marriage" between Java and XML, but the most likely explanation for the huge number of XML tools for Java is that XML emerged right as Java was cresting as a programming language.  Besides Xerces-J, there are Java parsers from Oracle, Sun, DataChannel, and others.  Individual efforts include Thomas Weidenfeller's XMLtp (Tiny XML Parser), which is designed for embedding into other Java apps (as was the pioneering but now moribund Aelfred from Microstar).  Mr. Weidenfeller also provides one of the neatest summaries of OSS license I've seen: "Do what you like with the software, but don't sue me".  Then there is The Wilson Partnership's MinML, designed to be even smaller, for use in embedded systems.
</P>
    <P>
Python still has the growing and evolving PyXML package as well as my own company's 4Suite.  XML considerations are helping shape many grand trends of Python such as unicode support and improved memory-management.  The perl community has definitely taken to XML.  The main parser is, appropriately, XML::Parser, but you can pretty much take any XML buzzword, prepend "XML::", and find a corresponding perl package.
</P>
    <H3>Serving up XML Pages</H3>
    <P>
XML's early promise to the media was as a way to tame the Web.  Structured documents, separation of content from presentation, and more manageable searching and autonomous Web agents.  Some of this has been drowned out by all the recent interest in XML for database integration and message-based middleware, but XML is still an excellent way to manage structured content on the Web.  And Linux is a pretty good operating system on which to host the content. 
</P>
    <P>
The big dog among the XML Web servers is also the well known big dog of Web servers, period.  Apache is absolutely swarming with XML activity lately.  I've already mentioned Xerces, the XML parser from the Apache/XML project.  There is also an XSLT processor, Xalan, with roots in IBM/Lotus's LotusXSL.  There is also Formatting-Object Processor (FOP), a tool for converting XML documents to the popular PDF document, by way of XSL formatting objects, a special XML vocabulary for presentation.  Apache has added support for the Simple Object Access Protocol (SOAP), an XML messaging protocol that can be used to make HTTP-based queries to a server in an XML format.  As a side note, SOAP, and open protocol, is heavily contributed to and championed by Microsoft, in one of the many positive contributions that company has made to XML while not trying to embrace and extend.
</P>
    <P>
These bits and pieces are combined into an Apache-based XML Web publishing solution called Cocoon.  Cocoon allows XML documents to be developed, and then published on the Web, for wireless applications through Wireless Application Protocol (WAP), and to print-ready PDF format through FOP.
</P>
    <P>
Perl hackers already have the proliferation of "XML::*" packages I've already mentioned, but Matt Sergeant has also put together a comprehensive toolkit for XML processing: Axkit.  Axkit is specialized for use with Apache and mod_perl, and provides XSLT transformation as well as other non-standard transform approaches such as "XPathScript".
</P>
    <H3>Full-blown application servers</H3>
    <P>
Enterprises that want an end-to-end solution for developing and deploying applications using XML data have several options under Linux.  Application servers build on basic Web servers such as described above by adding database integration, version control, distributed transactions and other such facilities.
</P>
    <P>
The grey and respectable Hewelett Packard found an open-source, Web-hip side with its e-speak project, a tool for distributed XML applications with Java, Python and C APIs for development and extension.
</P>
    <P>
A smaller company that has found the advantages of open-source for promoting its XML services is Lutris, Inc., developers of Enhydra.  Enhydra, about which I've reported in a previous LinuxWorld article, is a Java application server for XML processing.  It has some neat innovations such as XMLC, a way to "compile" XML into an intermediate binary form for efficient processing.  It is also one of the first open-source implementations of Java 2's Enterprise Edition services, including Enterprise JavaBeans.
</P>
    <P>
XML Blaster is a messaging-oriented middleware (MOM) suite for XML applications.  It uses an XML transport in a publish/subscribe system for exchanging text and binary data.  It uses CORBA for network and inter-process communication and supports components written in Java, Perl, Python and TCL.
</P>
    <P>
Conglomerate, developed by Styx, is a somewhat less ambitious but interesting project for an XML application server more attuned for document management.  It includes a nifty GUI editor and provides a proprietary transformation language that can generate HTML, TeX and other formats.
</P>
    <H3>Oo-wee!  GUI!</H3>
    <P>
One area in which I lamented Linux's lag in XML tools last year was in the area of GUI browsers and editors.  While I personally use a 4XSLT script and XEmacs for these respective tasks, I frequently work with clients who want to use more friendly GUIs for XML editing and ask whether my preferred Linux platform has anything available.  Fortunately, there are more choices than ever on our favorite OS.  Again much of the succour comes in the form of Java's cross-platform GUI support.
</P>
    <P>
GEXml is a Java XML editor which allows programmers use pluggable Java modules for editing their own special tag sets.  It uses a pretty standard layout for XML editors: a multi-pane window with a section for the tree-view, and sections for attributes and a section for CDATA.
</P>
    <P>
Merlot, by Channelpoint, Inc., is another Java-based XML editor that emphasizes modeling XML documents around their DTDs, abstracting the actual XML file from the user.  It supports pluggable extension modules for custom DTDs.
</P>
    <P>
Lunatech's Morphon is yet another DTD-based XML editor and modeling tool.  Hopefully all these DTD-based tools will expand to accommodate XML schemas and other validation methods as well in order to make life easier for those of us who use XML namespaces.  Morphon is similar to the other editors described here with a couple of nice twists: it allows you to specify cascading stylesheets for the editor appearance and document preview, and it mixes the ubiquitous tree view with a friendly view of the XML document being edited.  Morphon, however, is not open-source, though available for Linux.
</P>
    <P>
IBM's Alphaworks keeps on churning out free (beer) XML tools, one of which, XML Viewer, allows users to view XML documents using (once again) the tree-view and specialized panes for element and attribute data.  XML Viewer is written in Java.  It also allows linking the XML source and DTD to allow viewing such items as element and attribute definitions.  There is also XSL Editor, a specialized java-based XML editor for XSLT stylesheets.  It also incorporates advanced features such as syntax highlighting and an XSLT debugger.
</P>
    <P>
TreeNotes is an XML text editor that uses a series of widgets to open up XML's tree structure, elements and attributes, and of course character data, to editing.
</P>
    <P>
DocZilla is an interesting project: an extension of the Mozilla project for Web-based XML document applications.  It promises XML browsing support on par with Internet Explorer's including an extension and plug-in framework.  DocZilla started out very strongly, but now seems to have lagged a bit.  Part of the reason might be that Mozilla is increasing its XML focus.  Mozilla has always supported XML+Cascading Style-Sheets (CSS), but now, with Transformiix (an XSLT processor for Mozilla) and other such projects, it is making its own bid to replace Explorer as king of XML browsers.
</P>
    <P>
There is also KXMLViewer, a KDE XML viewer written in Python, but I'll cover this in more detail when I discuss GNOME and KDE XML support in a coming article in this series.
</P>
    <H3>In the Hacker Spirit</H3>
    <P>
So we've looked at lumbering app servers and pretty GUI tools.  All very nice for easing into XML, but we all know that Linux (and UNIX) users typically prefer sterner stuff.  Small, manageable, versatile, no-nonsense packages that can be strung together to get a larger job done.  Luckily for the desperate hacker, the nuts-and-bolts toolkit is growing just as quickly as the rest of XML space.
</P>
    <P>
A key and quite mature entry is LT XML, developed by the Edinburgh Language Technology Group.  LT XML is a set of stand-along tools and libraries for C programmers using XML.  It supports both tree-based and stream-oriented processing, covering a wide variety of application types.  The LT XML repertoire would be quite familiar and pleasant to those who love nothing more than to string together GNU textutils to produce some neat text transformation.  There is the mandatory XML-aware grep, sggrep (the "sg" for SGML), as well as sgsort, sgcount, sgtoken, etc, which should be self-explanatory.  Python bindings for LT XML should be available by the time you read this.
</P>
    <P>
Speaking of grep, there is also fxgrep, a powerful XML querying tool written in Standard ML, a well-regarded functional programming language from Bell Labs (XML provides a rather fitting problem space for functional languages).  fxgrep uses the XML parser fxp, also written in SML.  fxgrep supports specialized XML searching and query using its own pattern syntax.
</P>
    <P>
Paul Tchistopolskii makes clear there is no mistake as to his target user-base for Ux: "Ux is UNIX, revisited with XML".  Ux is a set of small XML components written in Java (OK, we're leaking some UNIX heritage right there).  The components are designed to be piped together for database storage and extraction, XSLT transformation, query, etc.
</P>
    <P>
Pyxie is an XML parsing and processing toolkit in Python by Sean McGrath and highlighted in his book, <I>XML Processing with Python</I>.  Pyxie's main distiction is that it builds on earlier work by James Clark by focusing on a line-based view of XML rather than the "natural" tokens that emerge from the spec.  This can provide a useful optimization if occasional complications.
</P>
    <P>
For those looking askance at XML in a TeX environment, IBM's Alphaworks might have a useful introduction.  TeXML is a tool that allows you to define an XSLT transform for converting XML files to a specialized vocabulary, the results of which are converted to TeX.  Also, thanks to Alphaworks, there is an XML diff as well as a grep.  XML Tree Diff shows the differences between documents based on their DOM tree representation.  It's more of a collection of Javabeans for performing diffs than a stand-alone application, but it's relatively straightforward to use.
</P>
    <P>
And there is my own company's 4Suite, a set of libraries for Python users to construct their own XML applications using DOM, XPath and XSLT, among other tools.  I covered 4XSLT in my last XML article (though the spec and 4XSLT have changed since then), and 4Suite libraries are now standard components in the Python XML distribution.
</P>
    <H3>Conclusion</H3>
    <P>
Hopefully this tour will help find XML resources for Linux users of all levels.  In upcoming articles (hopefully not as delayed as this one), I shall cover XML and Databases, XML and KDE/GNOME, and mnore topics on how to put XML to work in a Linux environment.
</P>
    <P>
By the way this very article is available in XML form (using the DocBook standard).  I've also put up a simplified DocBook XSLT stylesheet that can be used to render this article to HTML (see Resources for both).  Note that I use the "doc" file extension for DocBook files.  I encourage you to use DocBook (O'Reilly and Associates publishes an excellent book on the topic by Norman Walsh) and the ".doc" extension, chopping at the hegemony of the proprietary Microsoft Word format.  Just another small way XML can open up data to the world.
</P>
    <H3>Resources</H3>
    <H4>Parsers</H4>
    <DL>
      <DT><I>Expat</I></DT>
      <DD>http://www.jclark.com/xml/expat.html</DD>
      <DT><I>Xerces C++</I></DT>
      <DD>http://xml.apache.org/xerces-c/index.html</DD>
      <DT><I>Xerces-Java</I></DT>
      <DD>http://xml.apache.org/xerces-j/index.html</DD>
      <DT><I>xmlpp</I></DT>
      <DD>http://www.vividos.de/xmlpp/</DD>
      <DT><I>libxml</I></DT>
      <DD>http://www.xmlsoft.org/</DD>
      <DT><I>RXP</I></DT>
      <DD>http://www.cogsci.ed.ac.uk/~richard/rxp.html</DD>
      <DT><I>XMLtp</I></DT>
      <DD>http://mitglied.tripod.de/xmltp/</DD>
      <DT><I>MinML</I></DT>
      <DD>http://www.wilson.co.uk/xml/minml.htm</DD>
    </DL>
    <H4>Web Servers</H4>
    <DL>
      <DT><I>Axkit</I></DT>
      <DD>http://axkit.org/</DD>
      <DT><I>XML/Apache</I></DT>
      <DD>http://xml.apache.org</DD>
    </DL>
    <H4>App Servers</H4>
    <DL>
      <DT><I>Conglomerate</I></DT>
      <DD>http://www.conglomerate.org/</DD>
      <DT><I>e-speak</I></DT>
      <DD>http://www.e-speak.net/</DD>
      <DT><I>Enhydra</I></DT>
      <DD>http://www.enhydra.org/</DD>
      <DT><I>XML Blaster</I></DT>
      <DD>http://www.xmlBlaster.org/</DD>
    </DL>
    <H4>Low-Level Tools</H4>
    <DL>
      <DT><I>LT XML</I></DT>
      <DD>http://www.ltg.ed.ac.uk/software/xml/index.html</DD>
      <DT><I>fxgrep</I></DT>
      <DD>http://www.informatik.uni-trier.de/~neumann/Fxgrep/</DD>
      <DT><I>Ux</I></DT>
      <DD>http://www.pault.com/Ux/</DD>
      <DT><I>Pyxie</I></DT>
      <DD>http://www.digitome.com/pyxie.html</DD>
    </DL>
    <H4>GUIs</H4>
    <DL>
      <DT><I>TreeNotes</I></DT>
      <DD>http://pikosoft.dragontiger.com/en/treenotes/</DD>
      <DT><I>DocZilla</I></DT>
      <DD>http://www.doczilla.com/</DD>
      <DT><I>GEXml</I></DT>
      <DD>http://gexml.cx/</DD>
      <DT><I>Merlot</I></DT>
      <DD>http://www.merlotxml.org/</DD>
      <DT><I>Morphon</I></DT>
      <DD>http://www.morphon.com/</DD>
    </DL>
    <H4>Et Cetera</H4>
    <DL>
      <DT><I>There is more to XML than roll-your-own HTML</I></DT>
      <DD>http://www.linuxworld.com/linuxworld/lw-1999-03/lw-03-xml.html</DD>
      <DT><I>Practical XML with Linux, Part 1</I></DT>
      <DD>http://www.linuxworld.com/linuxworld/lw-1999-09/lw-09-xml2.html</DD>
      <DT><I>The xsl-list mailing list</I></DT>
      <DD>http://www.mulberrytech.com/xsl/xsl-list</DD>
      <DT><I>DocBook and stylesheet for this article</I></DT>
      <DD>http://www.Fourthought.com/Publications/lw-xml2</DD>
      <DT><I>The Apache/XML Project</I></DT>
      <DD>http://xml.apache.org/</DD>
      <DT><I>SOAP</I></DT>
      <DD>http://www.w3.org/TR/SOAP/</DD>
      <DT><I>xmlhack</I></DT>
      <DD>http://www.xmlhack.com</DD>
      <DT><I>XML Pit Stop</I></DT>
      <DD>http://www.xmlpitstop.com/</DD>
      <DT><I>xslt.com</I></DT>
      <DD>http://www.xslt.com</DD>
      <DT><I>XML Times</I></DT>
      <DD>http://www.xmltimes.com/</DD>
      <DT><I>The XML Cover Pages</I></DT>
      <DD>http://www.oasis-open.org/cover</DD>
      <DT><I>IBM's Alphaworks (including XML Viewer, XSL Edirot, XML Tree Diff and TeXML)</I></DT>
      <DD>http://alphaworks.ibm.com</DD>
    </DL>
  </BODY>
</HTML>"""

#"

def Test(tester):
    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1,
                          title='test 1')

    source = test_harness.FileInfo(string=source_2)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_2,
                          title='test 2')

    source = test_harness.FileInfo(string=source_3)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_3,
                          title='test 3')
    return
