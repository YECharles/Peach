from Xml.Xslt import test_harness
from Ft.Lib import Uri
from Ft.Xml.Xslt import Transform
from Ft.Xml.Lib import TreeCompare
import os
import cStringIO

SHEET2 = """<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  version="1.0"
  >
  <xsl:output method="html"/>

  <xsl:template match="/">
    <HTML>
    <HEAD><TITLE>Address Book</TITLE>
    </HEAD>
    <BODY>
    <H1><xsl:text>Tabulate just the Names</xsl:text></H1>
    <TABLE><xsl:apply-templates/></TABLE>
    </BODY>
    </HTML>
  </xsl:template>

  <xsl:template match="ENTRY">
        <TR>
        <xsl:apply-templates select='NAME|PHONENUM'/>
        </TR>
  </xsl:template>

  <xsl:template match="NAME">
    <TD ALIGN="CENTER">
      <B><xsl:apply-templates/></B>
    </TD>
  </xsl:template>

</xsl:stylesheet>
"""

SHEET3 = """<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  version="1.0"
  >

  <xsl:strip-space elements="*"/>

  <xsl:template match="/">
    <HTML>
    <HEAD><TITLE>Address Book</TITLE>
    </HEAD>
    <BODY>
    <H1><xsl:text>Tabulate just the Names</xsl:text></H1>
    <TABLE><xsl:apply-templates/></TABLE>
    </BODY>
    </HTML>
  </xsl:template>

  <xsl:template match="ADDRBOOK">
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="ENTRY">
    <TR>
      <xsl:apply-templates/>
    </TR>
  </xsl:template>

  <xsl:template match="NAME">
    <TD ALIGN="CENTER">
      <B><xsl:apply-templates/></B>
    </TD>
  </xsl:template>

  <xsl:template match="*"/>

</xsl:stylesheet>
"""

SHEET4 = """<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:A="http://spam.org"
  version="1.0"
  >

  <xsl:output method="html"/>

  <xsl:template match="/">
    <HTML>
    <HEAD><TITLE>Address Book</TITLE>
    </HEAD>
    <BODY>
    <H1><xsl:text>Tabulate just the Names</xsl:text></H1>
    <TABLE><xsl:apply-templates/></TABLE>
    </BODY>
    </HTML>
  </xsl:template>

  <xsl:template match="A:ENTRY">
        <TR>
        <xsl:apply-templates select='A:NAME|A:PHONENUM'/>
        </TR>
  </xsl:template>

  <xsl:template match="A:NAME">
    <TD ALIGN="CENTER">
      <B><xsl:apply-templates/></B>
    </TD>
  </xsl:template>

</xsl:stylesheet>
"""


SHEET5 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">

  <xsl:param name='override' select='"abc"'/>
  <xsl:param name='list' select='foo'/>

  <xsl:template match="/">
    <doc>
      <overridden><xsl:value-of select='$override'/></overridden>
      <list><xsl:apply-templates select="$list"/></list>
    </doc>
  </xsl:template>

  <xsl:template match="text()">
    <item><xsl:value-of select="."/></item>
  </xsl:template>

</xsl:stylesheet>
"""


SOURCE4 = """<?xml version = "1.0"?>
<?xml-stylesheet type="text/xml" href="Xml/Xslt/Core/addr_book1.xsl"?>
<!DOCTYPE ADDRBOOK [
  <!ELEMENT ADDRBOOK (ENTRY*)>
  <!ATTLIST ADDRBOOK
    xmlns CDATA #FIXED 'http://spam.org'
  >
  <!ELEMENT ENTRY (NAME, ADDRESS, PHONENUM*, EMAIL)>
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
]>
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
    <ENTRY ID="vz">
        <NAME>Vasia Zhugenev</NAME>
        <ADDRESS>2000 Disaster Plaza</ADDRESS>
        <PHONENUM DESC="Work">000-987-6543</PHONENUM>
        <PHONENUM DESC="Cell">000-000-0000</PHONENUM>
        <EMAIL>vxz@magog.ru</EMAIL>
    </ENTRY>
</ADDRBOOK>"""


SOURCE5 = """
<dummy/>
"""


EXPECTED1 = """<html>
  <head>
    <meta http-equiv='Content-Type' content='text/html; charset=iso-8859-1'>
    <title>Address Book</title>
  </head>
  <body>
    <h1>Tabulate Just Names and Phone Numbers</h1>
    <table>
      <tr>
        <td align='center'><b>Pieter Aaron</b></td>
        <td>(Work) 404-555-1234<br>(Fax) 404-555-4321<br>(Pager) 404-555-5555</td>
      </tr>
      <tr>
        <td align='center'><b>Emeka Ndubuisi</b></td>
        <td>(Work) 767-555-7676<br>(Fax) 767-555-7642<br>(Pager) 800-SKY-PAGEx767676</td>
      </tr>
      <tr>
        <td align='center'><b>Vasia Zhugenev</b></td>
        <td>(Work) 000-987-6543<br>(Cell) 000-000-0000</td>
      </tr>
    </table>
  </body>
</html>"""

EXPECTED2 = """<HTML>
  <HEAD>
    <meta http-equiv='Content-Type' content='text/html; charset=iso-8859-1'>
    <TITLE>Address Book</TITLE>
  </HEAD>
  <BODY>
    <H1>Tabulate just the Names</H1>
    <TABLE>
      <TR>
        <TD ALIGN='CENTER'><B>Pieter Aaron</B></TD>404-555-1234404-555-4321404-555-5555</TR>
      <TR>
        <TD ALIGN='CENTER'><B>Emeka Ndubuisi</B></TD>767-555-7676767-555-7642800-SKY-PAGEx767676</TR>
      <TR>
        <TD ALIGN='CENTER'><B>Vasia Zhugenev</B></TD>000-987-6543000-000-0000</TR>
    </TABLE>
  </BODY>
</HTML>"""

EXPECTED3 = """<HTML>
  <HEAD>
    <meta http-equiv='Content-Type' content='text/html; charset=iso-8859-1'>
    <TITLE>Address Book</TITLE>
  </HEAD>
  <BODY>
    <H1>Tabulate just the Names</H1>
    <TABLE>
      <TR>
        <TD ALIGN='CENTER'><B>Pieter Aaron</B></TD>
      </TR>
      <TR>
        <TD ALIGN='CENTER'><B>Emeka Ndubuisi</B></TD>
      </TR>
      <TR>
        <TD ALIGN='CENTER'><B>Vasia Zhugenev</B></TD>
      </TR>
    </TABLE>
  </BODY>
</HTML>"""

EXPECTED4 = """<HTML xmlns:A='http://spam.org'>
  <HEAD>
    <meta http-equiv='Content-Type' content='text/html; charset=iso-8859-1'>
    <TITLE>Address Book</TITLE>
  </HEAD>
  <BODY>
    <H1>Tabulate just the Names</H1>
    <TABLE>
      <TR>
        <TD ALIGN='CENTER'><B>Pieter Aaron</B></TD>404-555-1234404-555-4321404-555-5555</TR>
      <TR>
        <TD ALIGN='CENTER'><B>Emeka Ndubuisi</B></TD>767-555-7676767-555-7642800-SKY-PAGEx767676</TR>
      <TR>
        <TD ALIGN='CENTER'><B>Vasia Zhugenev</B></TD>000-987-6543000-000-0000</TR>
    </TABLE>
  </BODY>
</HTML>"""

EXPECTED5 = """<?xml version='1.0' encoding='UTF-8'?>
<doc><overridden>xyz</overridden><list><item>a</item><item>b</item><item>c</item></list></doc>"""


def Test(tester):
    source = test_harness.FileInfo(uri='Xml/Xslt/Core/addr_book1.xml')
    sheet = test_harness.FileInfo(uri='Xml/Xslt/Core/addr_book1.xsl')
    test_harness.XsltTest(tester, source, [sheet], EXPECTED1,
                          title='test 1')


    tester.startTest('test 1 using Ft.Xml.Xslt.Transform')
    result = Transform('Xml/Xslt/Core/addr_book1.xml', 'Xml/Xslt/Core/addr_book1.xsl')
    tester.compare(EXPECTED1, result, func=TreeCompare.HtmlTreeCompare)
    tester.testDone()


    source = test_harness.FileInfo(uri='Xml/Xslt/Core/addr_book1.xml')
    sheet = test_harness.FileInfo(string=SHEET2)
    test_harness.XsltTest(tester, source, [sheet], EXPECTED2,
                          title='test 2')


    source = test_harness.FileInfo(uri='Xml/Xslt/Core/addr_book1.xml')
    sheet = test_harness.FileInfo(string=SHEET3)
    test_harness.XsltTest(tester, source, [sheet], EXPECTED3,
                          title='test 3')


    source = test_harness.FileInfo(string=SOURCE4, validate=1)
    sheet = test_harness.FileInfo(string=SHEET4)
    test_harness.XsltTest(tester, source, [sheet], EXPECTED4,
                          title='test 4')


    tester.startTest('alternate stream output using Ft.Xml.Xslt.Transform')
    stream = cStringIO.StringIO()
    result = Transform('Xml/Xslt/Core/addr_book1.xml', 'Xml/Xslt/Core/addr_book1.xsl', output=stream)
    tester.compare(EXPECTED1, stream.getvalue(), func=TreeCompare.HtmlTreeCompare)
    tester.testDone()


    tester.startTest('top-level-param overide using Ft.Xml.Xslt.Transform')
    result = Transform(SOURCE5, SHEET5, params={'override' : 'xyz', 'list' : ['a', 'b', 'c']},)
    tester.compare(EXPECTED5, result, func=TreeCompare.XmlTreeCompare)
    tester.testDone()


    # Appending explicit stylesheet when xml-stylesheet PI already
    # specifies one results in both stylesheets being appended. If
    # it's the same stylesheet, it's an error.
    #
    #source = test_harness.FileInfo(uri='Xml/Xslt/Core/addr_book1.xml')
    #sheet = test_harness.FileInfo(uri='Xml/Xslt/Core/addr_book1.xsl')
    #    test_harness.XsltTest(tester, source, [sheet], EXPECTED1, ignorePis=0,
    #                          title='test 5')

    return
