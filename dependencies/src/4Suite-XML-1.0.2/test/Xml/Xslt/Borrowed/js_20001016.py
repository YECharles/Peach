#"John E. Simpson" <simpson@polaris.net>

from Xml.Xslt import test_harness

sheet_1 = """<?xml version="1.0"?>
<!--  Including the HTML 4.0 namespace declaration, i.e.
      xmlns="http://www.w3.org/TR/REC-html40", makes the
      usd_equiv element empty. So it's not included below. :) -->
<xsl:stylesheet version="1.0"
   xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
   xmlns:exsl="http://exslt.org/common"
   exclude-result-prefixes="exsl"
>

<xsl:template match="/">
   <html>
     <head><title>Sorting an RTF</title></head>
     <body>
       <xsl:apply-templates/>
     </body>
   </html>
</xsl:template>

<!-- Template rule for root element <products> -->
<xsl:template match="products">
   <!-- This variable will hold the RTF, including the
        usd_equiv element for each product -->
   <xsl:variable name="prods_with_usd">
     <xsl:apply-templates select="product" mode="calc_usd" />
   </xsl:variable>
   <table border="1">
     <tr>
       <th>Name/Version</th>
       <th>Price / Curr</th>
       <th>Price (USD)</th>
     </tr>
     <!-- Note that the apply-templates doesn't select the
          <product> children, which would be "conventional," but
          the RTF (converted to node-set) created by the above
          variable. -->
     <xsl:apply-templates select="exsl:node-set($prods_with_usd)/*">
       <xsl:sort select="usd_equiv"/>
     </xsl:apply-templates>
   </table>
</xsl:template>

<!-- When the mode is "calc_usd" (as in apply-templates within
      the xsl:variable above which creates the prods_with_usd RTF),
      copy the product node and its attributes, and add a
      <usd_equiv> child for each <product> element -->
<xsl:template match="product" mode="calc_usd">
   <xsl:copy>
     <xsl:copy-of select="@*" />
     <xsl:copy-of select="*" />
     <!-- <xsl:element> can be replaced, if you want, with a simple
          literal result element, i.e. <usd_equiv>. In either case, the
          element so created isn't in the HTML namespace, which is
          apparently why adding the HTML 4.0 namespace declaration
          makes this <usd_equiv> element "disappear." -->
     <xsl:element name="usd_equiv">
       <xsl:choose>
         <xsl:when test="price/@curr='USD'">
           <xsl:value-of select="format-number(price, '#,##0.00')"/>
         </xsl:when>
         <xsl:when test="price/@curr='GBP'">
           <xsl:value-of select="format-number(price * 1.47275, '#,##0.00')"/>
         </xsl:when>
         <xsl:when test="price/@curr='EU'">
           <xsl:value-of select="format-number(price * 0.864379, '#,##0.00')"/>
         </xsl:when>
         <xsl:otherwise>Unknown Currency</xsl:otherwise>
       </xsl:choose>
     </xsl:element>
   </xsl:copy>
</xsl:template>

<!-- When the mode isn't specified, simply create a table row
      for the product in question. -->
<xsl:template match="product">
   <tr>
     <td valign="top"><xsl:value-of select="name"/></td>
     <td align="right">
       <xsl:value-of select="price"/> / <xsl:value-of select="price/@curr"/>
     </td>
     <td align="right"><xsl:value-of select="usd_equiv"/></td>
   </tr>
</xsl:template>

</xsl:stylesheet>"""

source_1 = """<products>
   <product prodID="A1234">
     <name>First prod</name>
     <price curr="USD">29.95</price>
   </product>
   <product prodID="A5678">
     <name>Second prod</name>
     <price curr="GBP">115.95</price>
   </product>
   <product prodID="A9012">
     <name>Third prod</name>
     <price curr="EU">29.95</price>
   </product>
   <product prodID="A9012">
     <name>Fourth prod</name>
     <price curr="USD">50.00</price>
   </product>
</products>"""

expected_1 = """<html>
  <head>
    <meta http-equiv='Content-Type' content='text/html; charset=iso-8859-1'>
    <title>Sorting an RTF</title>
  </head>
  <body>
    <table border='1'>
      <tr>
        <th>Name/Version</th>
        <th>Price / Curr</th>
        <th>Price (USD)</th>
      </tr>
      <tr>
        <td valign='top'>Second prod</td>
        <td align='right'>115.95 / GBP</td>
        <td align='right'>170.77</td>
      </tr>
      <tr>
        <td valign='top'>Third prod</td>
        <td align='right'>29.95 / EU</td>
        <td align='right'>25.89</td>
      </tr>
      <tr>
        <td valign='top'>First prod</td>
        <td align='right'>29.95 / USD</td>
        <td align='right'>29.95</td>
      </tr>
      <tr>
        <td valign='top'>Fourth prod</td>
        <td align='right'>50.00 / USD</td>
        <td align='right'>50.00</td>
      </tr>
    </table>
  </body>
</html>"""


def Test(tester):
    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1)
    return

