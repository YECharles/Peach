from Xml.Xslt import test_harness

sheet_str = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">
  <xsl:output method='html'/>
  <xsl:template match="/">
    <HTML>
    <HEAD><TITLE>Address Book</TITLE>
    </HEAD>
    <BODY>
    <TABLE><xsl:apply-templates/></TABLE>
    </BODY>
    </HTML>
  </xsl:template>

  <xsl:template match="ENTRY">
    <xsl:element name='TR'>
      <xsl:apply-templates select='NAME'/>
    </xsl:element>
  </xsl:template>

  <xsl:template match="NAME">
    <xsl:element name='TD'>
    <xsl:attribute name='ALIGN'>CENTER</xsl:attribute>
      <B><xsl:apply-templates/></B>
      <xsl:choose>
        <xsl:when test="text()='Pieter Aaron'">: Employee 1</xsl:when>
        <xsl:when test="text()='Emeka Ndubuisi'">: Employee 2</xsl:when>
        <xsl:otherwise>: Other Employee</xsl:otherwise>
      </xsl:choose>
    </xsl:element>
  </xsl:template>

</xsl:stylesheet>
"""

expected = """<HTML>
  <HEAD>
    <meta http-equiv='Content-Type' content='text/html; charset=iso-8859-1'>
    <TITLE>Address Book</TITLE>
  </HEAD>
  <BODY>
    <TABLE>
      <TR>
        <TD ALIGN='CENTER'><B>Pieter Aaron</B>: Employee 1</TD>
      </TR>
      <TR>
        <TD ALIGN='CENTER'><B>Emeka Ndubuisi</B>: Employee 2</TD>
      </TR>
      <TR>
        <TD ALIGN='CENTER'><B>Vasia Zhugenev</B>: Other Employee</TD>
      </TR>
    </TABLE>
  </BODY>
</HTML>"""

def Test(tester):
    source = test_harness.FileInfo(uri='Xml/Xslt/Core/addr_book1.xml')
    sheet = test_harness.FileInfo(string=sheet_str)
    test_harness.XsltTest(tester, source, [sheet], expected,
                          title='xsl:choose')
    return
