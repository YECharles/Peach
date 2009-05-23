#Dave Carlile's greeting card to XSLT

from Xml.Xslt import test_harness

sheet_1 = """\
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
        version="1.0"><xsl:output method="text"/><xsl:variable name="x"
        select="'y*xxz13fr9hd*z19o19Fe14wfnsk/#S741a%d1#q*9F/214od*zk'"/> <xsl:template match="/"><xsl:value-of select="translate($x, 'Fw*y/x#z134kfq7%9','hwaH pXy BT!iPLnt')"/></xsl:template> </xsl:stylesheet> 
"""

source_1 = "<dummy/>"

expected_1 = 'Happy Birthday to the Twins! XSLT and XPath 2 Today!'


def Test(tester):
    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1,
                          title='wacky translate')
    return
