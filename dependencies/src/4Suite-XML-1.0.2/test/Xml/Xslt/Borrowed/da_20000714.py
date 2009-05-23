# -*- coding: iso-8859-1 -*-
"""
Bug report from David Allouche (david@ansible.xlii.org)
Jul 14 2000

System: RedHat 6.2 and Debian 2.2
Python-1.5.2 4XSLT-0.9.1 4DOM-0.10.1 (from rpm or deb packages)

These are two bugs related to international caracters handling.  They
are related, since applying the "workaround" for the first "bug" cause
incorrect behaviour of the second "bug".

Actually, they may be Python bugs... Since I don't program with
Python, I can't tell.  In this case, please forward it...

Bug 1: Comments with international character can cause parse error
==================================================================

When the bug occurs:
--------------------
Input
^^^^^
cat > bug.xml << --
<?xml version="1.0"?>
<!-- � -->
<toto/>
--
4xslt.py bug.xml

Output
^^^^^^
Error Reading or Parsing XML source: unclosed token at :1:0

When the bug doesn't occur:
---------------------------
Input
^^^^^
cat > bug.xml << --
<?xml version="1.0"?>
<!-- �e -->
<toto/>
--
4xslt.py bug.xml

Output
^^^^^^
No stylesheets to process.

A workaround:
-------------
Input
^^^^^
cat > bug.xml << --
<?xml version="1.0" encoding="iso-8859-1"?>
<!-- � -->
<toto/>
--
4xslt.py bug.xml

Output
^^^^^^
No stylesheets to process.

Bug 2: International characters conversion has problems
=======================================================

When conversion is right:
-------------------------
Note that the accentuated letter must be followed by an ASCII letter
or parsing will fail.  Actually it might be wrong no to throw an error
since the encoding is not specified.

Input
^^^^^
cat > toto.xml << --
<?xml version="1.0"?>
<toto/>
--
cat > toto.xsl << --
<?xml version="1.0"?>
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:template match="toto">
�e
</xsl:template>
</xsl:stylesheet>
--
4xslt.py bug.xml bug.xsl

Output
^^^^^^
&#233;e

When the conversion is wrong:
-----------------------------
Input
^^^^^
cat > toto.xsl << --
<?xml version="1.0" encoding="iso-8859-1"?>
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:template match="toto">
�e
</xsl:template>
</xsl:stylesheet>
--
4xslt.py bug.xml bug.xsl

Output
^^^^^^
&#195;&#169;e
"""

from Ft.Xml.Xslt import Error
from Xml.Xslt import test_harness

# This is non-well-formed XML.
#In Python 1.52 plus XML-SIG, expat seems to deal with it by passing the data to us verbatim.
#In Python 2.0, expat seems to silently ignore the element content with unrecognizable text
sheet_1 = """<?xml version="1.0"?>
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:template match="toto">
�e
</xsl:template>
</xsl:stylesheet>"""

sheet_2 = """<?xml version="1.0" encoding="iso-8859-1"?>
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:template match="toto">
�e
</xsl:template>
</xsl:stylesheet>"""

source_1 = """<?xml version="1.0"?>
<toto/>
"""

expected_1 ="""<?xml version="1.0" encoding="UTF-8"?>

\351e
"""

expected_2 = """<?xml version="1.0" encoding="UTF-8"?>

\303\251e
"""
    

def Test(tester):

    # Test removed 9/12/2001 - unreliable exceptions when using runNode()
    # 2004-09-15: test updated to reflect proper exception raised
    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1,
                          exceptionCode=Error.STYLESHEET_PARSE_ERROR,
                          title='Default encoding (UTF-8)')

    source = test_harness.FileInfo(string=source_1)
    sheet= test_harness.FileInfo(string=sheet_2)
    test_harness.XsltTest(tester, source, [sheet], expected_2,
                          title='Declared ISO-8859-1 encoding')
    return
