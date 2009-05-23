<?xml version="1.0" ?>
<!-- Preprocessor for the Schematron XML Schema Language.
	http://www.ascc.net/xml/resource/schematron/schematron.html
    Copyright (C) 1999 Rick Jelliffe and Academia Sinica Computing Centre
    Permission to use granted under GPL or MPL.
-->

<!-- Skeleton: namespace enabled version -->

<xsl:stylesheet
   version="1.0"
   xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
   xmlns:axsl="http://www.w3.org/1999/XSL/TransformAlias"
   xmlns:sch="http://www.ascc.net/xml/schematron">
   <!-- Note that this namespace is not version specific.
	This program implements schematron 1.2 with some
	of the extensions for schematron 1.3: namespaces, keys -->

<xsl:namespace-alias stylesheet-prefix="axsl" result-prefix="xsl"/>

<!-- Category: top-level-element -->
<xsl:output
   method="xml" 
   omit-xml-declaration="no"
   standalone="yes" 
   indent="yes" />

<xsl:template match="sch:schema">
   <axsl:stylesheet version="1.0">
      <xsl:for-each select="sch:ns">
         <xsl:attribute name="{concat(@prefix,':dummy-for-xmlns')}"
                        namespace="{@uri}"/>
      </xsl:for-each>
      <xsl:call-template name="process-prolog"/>
      <xsl:apply-templates mode="do-keys" />
      <axsl:template match='/'>
         <xsl:call-template name="process-root">
            <xsl:with-param name="fpi" select="@fpi" />
            <xsl:with-param name="title" select="sch:title" />
            <xsl:with-param name="contents">
               <xsl:apply-templates mode="do-all-patterns" />
            </xsl:with-param>
         </xsl:call-template>
      </axsl:template>
      <xsl:apply-templates />
      <axsl:template match="text()" priority="-1">
         <!-- strip characters -->
      </axsl:template>
   </axsl:stylesheet>
</xsl:template>

<xsl:template match="sch:pattern" mode="do-all-patterns" >
   <xsl:call-template name="process-pattern">
      <xsl:with-param name="name" select="@name" />
      <xsl:with-param name="id"   select="@id" />
      <xsl:with-param name="see"  select="@see" />
      <xsl:with-param name="fpi"  select="@fpi" />
   </xsl:call-template>
   <axsl:apply-templates mode='M{count(preceding-sibling::*)}' />
</xsl:template>

<xsl:template match="sch:pattern">
   <xsl:apply-templates />
   <axsl:template match="text()" priority="-1" 
                  mode="M{count(preceding-sibling::*)}">
      <!-- strip characters -->
   </axsl:template>
</xsl:template>

<xsl:template match="sch:rule">
   <axsl:template match='{@context}' 
                  priority='{4000 - count(preceding-sibling::*)}' 
                  mode='M{count(../preceding-sibling::*)}'>
      <xsl:apply-templates />
    <axsl:apply-templates mode='M{count(../preceding-sibling::*)}'/>
   </axsl:template>
</xsl:template>

<xsl:template match="sch:name" mode="text">
   <axsl:text xml:space="preserve"> </axsl:text>
   <xsl:choose>
      <xsl:when test='@path' >
         <xsl:call-template name="process-name">
            <xsl:with-param name="name" select="'name({@path})'" />
         </xsl:call-template>
      </xsl:when>		
      <xsl:otherwise>
         <xsl:call-template name="process-name">
            <xsl:with-param name="name" select="'name(.)'" />
         </xsl:call-template>
      </xsl:otherwise>
   </xsl:choose>
   <axsl:text xml:space="preserve"> </axsl:text>
</xsl:template>

<xsl:template match="sch:assert">
   <axsl:choose> 
      <axsl:when test='{@test}'/>
      <axsl:otherwise>
         <xsl:call-template name="process-assert">
            <xsl:with-param name="pattern" 
                            select="ancestor::sch:pattern/@name" />
            <xsl:with-param name="role"
                            select="@role" />
         </xsl:call-template>
      </axsl:otherwise>
   </axsl:choose> 
</xsl:template>


<xsl:template match="sch:report">
   <axsl:if test='{@test}'>
      <xsl:call-template name="process-report">
         <xsl:with-param name="pattern" 
                         select="ancestor::sch:pattern/@name" />
         <xsl:with-param name="role" select="@role" />
      </xsl:call-template>
   </axsl:if> 
</xsl:template>

<xsl:template match="sch:rule/sch:key" mode="do-keys">
	<axsl:key match="{../@context}" name="{@name}" use="{@path}" />
</xsl:template>

<xsl:template match="text()" priority="-1" mode="do-keys" >
   <!-- strip characters -->
</xsl:template>

<xsl:template match="text()" priority="-1" mode="do-all-patterns">
   <!-- strip characters -->
</xsl:template>

<xsl:template match="text()" priority="-1">
   <!-- strip characters -->
</xsl:template>

<xsl:template match="text()" mode="text">
   <xsl:value-of select="normalize-space(.)" />
</xsl:template>

<!-- ============================================================== -->

<!-- report schema errors -->

<xsl:template match="sch:title|sch:ns|sch:key">
   <xsl:if test="count(*)">
      <xsl:message>
         <xsl:text>Warning: </xsl:text>
         <xsl:value-of select="name(.)" />
         <xsl:text> must not contain any child elements</xsl:text>
      </xsl:message>
   </xsl:if>
</xsl:template>

<xsl:template match="*">
   <xsl:message>
      <xsl:text>Warning: unrecognized element </xsl:text>
      <xsl:value-of select="name(.)" />
   </xsl:message>
</xsl:template>

<xsl:template match="*" mode="text">
   <xsl:message>
      <xsl:text>Warning: unrecognized element </xsl:text>
      <xsl:value-of select="name(.)" />
   </xsl:message>
</xsl:template>


<!-- ============================================================== -->

<!-- Default templates -->

<xsl:template name="process-prolog" />
<!-- no params -->

<xsl:template name="process-root">
   <xsl:param name="contents" />
   <xsl:copy-of select="$contents" />
<!-- additional params: fpi, title -->
</xsl:template>

<xsl:template name="process-pattern" />
<!-- params: name, id, see, fpi -->

<xsl:template name="process-name">
   <xsl:param name="name" />
   <axsl:value-of select="{$name}" />
</xsl:template>

<xsl:template name="process-assert">
   <xsl:param name="pattern" />
   <xsl:param name="role" />
   <xsl:call-template name="process-message">
      <xsl:with-param name="pattern" select="$pattern" />
      <xsl:with-param name="role" select="$role" />
   </xsl:call-template>
</xsl:template>

<xsl:template name="process-report">
   <xsl:param name="pattern" />
   <xsl:param name="role" />
   <xsl:call-template name="process-message">
      <xsl:with-param name="pattern" select="$pattern" />
      <xsl:with-param name="role" select="$role" />
   </xsl:call-template>
</xsl:template>

<xsl:template name="process-message">
<!-- params: pattern, role -->
   <xsl:apply-templates mode="text" />
</xsl:template>


</xsl:stylesheet>
