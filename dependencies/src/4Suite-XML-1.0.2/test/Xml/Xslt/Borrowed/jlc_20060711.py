from Xml.Xslt import test_harness

SHEET = """<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:variable name="other" select="document('Xml/Xslt/Borrowed/jlc_20060711.xml',/)"/>
  <xsl:variable name="main" select="/"/>

  <xsl:template match="/">
    <hello>
    <xsl:apply-templates select="$other/*"/>
    </hello>
  </xsl:template>

  <xsl:template match="file">
    <xsl:variable name="foos" select="foo"/>
    <!--xsl:message>List of all `foo`s from 'other.xml'...</xsl:message-->
    <xsl:apply-templates select="foo" mode="debug"/>
    <!--xsl:message>List of all `foo`s from 'other.xml' (using a variable)...</xsl:message-->
    <xsl:apply-templates select="$foos" mode="debug"/>
    <!--xsl:message>List of all `thing`s from the main input document...</xsl:message-->
    <xsl:apply-templates select="$main/file/thing" mode="debug"/>
    <!--xsl:message>List of all `thing`s that do not correspond to some `foo` (using current())...</xsl:message-->
    <xsl:apply-templates select="
      $main/file/thing[not(. = current()/foo)]" mode="debug"/>
    <!--xsl:message>List of all `thing`s that do not correspond to some `foo` (using a variable)...</xsl:message-->
    <xsl:apply-templates select="
      $main/file/thing[not(. = $foos)]" mode="debug"/>
  </xsl:template>

  <xsl:template match="*" mode="debug">
    <xsl:value-of select="name()"/> := `<xsl:value-of select="."/>'
  </xsl:template>
</xsl:stylesheet>
"""

SOURCE = """<file>
  <thing>a</thing>
  <thing>b</thing>
  <thing>c</thing>
</file>
"""

EXPECTED = "<?xml version='1.0' encoding='UTF-8'?>\n<hello>foo := `b\'\n  foo := `c\'\n  foo := `b\'\n  foo := `c\'\n  thing := `a\'\n  thing := `b\'\n  thing := `c\'\n  thing := `a\'\n  thing := `a\'\n  </hello>"

def Test(tester):
    source = test_harness.FileInfo(string=SOURCE)
    sheet = test_harness.FileInfo(string=SHEET)
    test_harness.XsltTest(tester, source, [sheet], EXPECTED,
                          title='current() with node comparisons across documents')
    return
