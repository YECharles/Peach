#G. Ken Holman's <gkholman@CraneSoftwrights.com>'s illustration of the fact that elements are the principal node type along the attribute axis

from Xml.Xslt import test_harness

sheet_and_source = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                 xmlns:dummy="dummy"
                 exclude-result-prefixes="dummy"
                 version="1.0">

<xsl:output method="text"/>

<dummy:data>
   <hello att1="att1-val" att2="att2-val" att3="att3-val"/>
</dummy:data>

<xsl:template match="/">                         <!--root rule-->
   <xsl:for-each select="document('')//hello">
     <xsl:text>Using self::</xsl:text>
     <!-- attributes are unordered, the sort is for comparision only -->
     <xsl:for-each select="@*[not(self::att2)]">
       <xsl:sort select="name()"/>
       <xsl:text>&#10;    </xsl:text>
       <xsl:value-of select="name(.)"/>-<xsl:value-of select="."/>
     </xsl:for-each>

     <xsl:text>&#xa;Using self::</xsl:text>
     <!-- attributes are unordered, the sort is for comparision only -->
     <xsl:for-each select="@*[name(.)!='att2']">
       <xsl:sort select="name()"/>
       <xsl:text>&#10;    </xsl:text>
       <xsl:value-of select="name(.)"/>-<xsl:value-of select="."/>
     </xsl:for-each>
   </xsl:for-each>
</xsl:template>

</xsl:stylesheet>"""

xt_output = """Using self::
    att1-att1-val
    att2-att2-val
    att3-att3-val
Using self::
    att1-att1-val
    att3-att3-val"""

     
expected_1 = """Using self::
    att1-att1-val
    att2-att2-val
    att3-att3-val
Using self::
    att1-att1-val
    att3-att3-val"""


def Test(tester):
    source = test_harness.FileInfo(string=sheet_and_source)
    sheet = test_harness.FileInfo(string=sheet_and_source)
    test_harness.XsltTest(tester, source, [sheet], expected_1)
    return
    
