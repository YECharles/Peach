/***********************************************************************
 * $Header: /var/local/cvsroot/4Suite/Ft/Xml/src/xmlstring.c,v 1.7.2.2 2006/09/25 17:03:08 jkloth Exp $
 ***********************************************************************/

static char module_doc[] = "\
Miscellaneous XML-specific string functions\n\
\n\
Copyright 2005 Fourthought, Inc. (USA).\n\
Detailed license and copyright information: http://4suite.org/COPYRIGHT\n\
Project home, documentation, distributions: http://4suite.org/\n\
";

#define PY_SSIZE_T_CLEAN
#include "Python.h"

#define XmlString_BUILDING_MODULE
#include "xmlstring.h"

/* header generated from gencharset.py */
#include "charset.h"

#include "common.h"

/** Private Routines **************************************************/

#define TEST_CHARSET(set, c) \
  (set[256 + (set[c >> 8] << 5) + ((c & 255) >> 3)] & (1 << (c & 7)))
#ifdef Py_UNICODE_WIDE
#define MATCH_CHARSET(set, c) ((c) < 65536 && TEST_CHARSET((set), (c)))
#else
#define MATCH_CHARSET(set, c) TEST_CHARSET((set), (c))
#endif
#define IS_NCNAMESTART(c) MATCH_CHARSET(charset_NCNameStart, c)
#define IS_NCNAMECHAR(c) MATCH_CHARSET(charset_NCNameChar, c)
#define IS_NAMESTART(c) MATCH_CHARSET(charset_NameStart, c)
#define IS_NAMECHAR(c) MATCH_CHARSET(charset_NameChar, c)
#define IS_XMLSPACE(c) (((c) == 0x09) || \
                        ((c) == 0x0A) || \
                        ((c) == 0x0D) || \
                        ((c) == 0x20))

static PyObject *XmlStrip(PyUnicodeObject *str, int left, int right)
{
  Py_UNICODE *p = PyUnicode_AS_UNICODE(str);
  int start = 0;
  int end = PyUnicode_GET_SIZE(str);

  if (left)
    while (start < end && IS_XMLSPACE(p[start]))
      start++;

  if (right)
    while (end > start && IS_XMLSPACE(p[end-1]))
      end--;

  if (start == 0 && end == PyUnicode_GET_SIZE(str)) {
    /* couldn't strip anything off, return original string */
    Py_INCREF(str);
    return (PyObject *) str;
  }
  return PySequence_GetSlice((PyObject *)str, (Py_ssize_t)start, (Py_ssize_t)end);
}

static PyObject *NormalizeSpace(PyObject *str)
{
  Py_UNICODE *start, *end, *p;
  PyObject *result;

  if (!PyUnicode_CheckExact(str)) {
    PyErr_SetString(PyExc_TypeError, "unicode object expected");
    return NULL;
  }

  start = PyUnicode_AS_UNICODE(str);
  end = start + PyUnicode_GET_SIZE(str);
  /* look for runs of contiguous whitespace */
  for (p = start; p < end; p++) {
    if (IS_XMLSPACE(p[0]) && IS_XMLSPACE(p[1])) break;
  }
  if (p == end && !IS_XMLSPACE(start[0]) && !IS_XMLSPACE(end[-1])) {
    /* no whitespace to remove; return original string */
    Py_INCREF(str);
    return str;
  }

  /* skip over leading whitespace */
  while (start < end && IS_XMLSPACE(start[0])) start++;
  /* skip over trailing whitespace */
  while (end > start && IS_XMLSPACE(end[-1])) end--;
  /* create the result string (it may be shrunk later) */
  result = PyUnicode_FromUnicode(start, (Py_ssize_t)(end - start));
  if (result) {
    start = PyUnicode_AS_UNICODE(result);
    end = start + PyUnicode_GET_SIZE(result);
    for (p = start; p < end; p++) {
      if (IS_XMLSPACE(*p)) {
        /* replace contiguous whitespace with a single space */
        *start++ = 0x20;
        p++;
        while (p < end && IS_XMLSPACE(*p)) p++;
      }
      *start++ = *p;
    }
    if (start != end) {
      Py_ssize_t newsize = (Py_ssize_t)(start - PyUnicode_AS_UNICODE(result));
      if (PyUnicode_Resize(&result, newsize) < 0) {
        Py_DECREF(result);
        return NULL;
      }
    }
  }
  return result;
}

static int IsSpace(PyObject *str)
{
  Py_UNICODE *p, *e;

  if (!PyUnicode_CheckExact(str))
    return -1;

  p = PyUnicode_AS_UNICODE(str);
  e = p + PyUnicode_GET_SIZE(str);
  while (p < e) {
    if (!IS_XMLSPACE(*p)) return 0;
    p++;
  }
  return 1;
}

static int IsName(PyObject *str)
{
  Py_UNICODE *p;

  if (!PyUnicode_CheckExact(str)) {
    PyErr_Format(PyExc_TypeError,
                 "argument must be unicode, %.80s found.",
                 str == Py_None ? "None" : str->ob_type->tp_name);
    return -1;
  }

  p = PyUnicode_AS_UNICODE(str);
  if (*p == 0) {
    return 0;
  }

  /* the first character must match NameStart */
  if (!IS_NAMESTART(*p)) {
    return 0;
  }

  /* the remaining characters must match NameChar */
  for (p++; *p; p++) {
    if (!IS_NAMECHAR(*p)) {
      return 0;
    }
  }

  return 1;
}

static int IsNames(PyObject *str)
{
  Py_UNICODE *p;

  if (!PyUnicode_CheckExact(str)) {
    PyErr_Format(PyExc_TypeError,
                 "argument must be unicode, %.80s found.",
                 str == Py_None ? "None" : str->ob_type->tp_name);
    return -1;
  }

  p = PyUnicode_AS_UNICODE(str);
  if (*p == 0) {
    return 0;
  }

  do {
    /* the first character must match NameStart */
    if (!IS_NAMESTART(*p)) {
      return 0;
    }

    /* the remaining characters must match NameChar */
    for (p++; *p && *p != 0x20; p++) {
      if (!IS_NAMECHAR(*p)) {
        return 0;
      }
    }
  } while (*p++);

  return 1;
}

static int IsNmtoken(PyObject *str)
{
  Py_UNICODE *p;

  if (!PyUnicode_CheckExact(str)) {
    PyErr_Format(PyExc_TypeError,
                 "argument must be unicode, %.80s found.",
                 str == Py_None ? "None" : str->ob_type->tp_name);
    return -1;
  }

  p = PyUnicode_AS_UNICODE(str);
  if (*p == 0) {
    return 0;
  }

  /* all characters must match NameChar */
  for (p++; *p; p++) {
    if (!IS_NAMECHAR(*p)) {
      return 0;
    }
  }

  return 1;
}

static int IsNmtokens(PyObject *str)
{
  Py_UNICODE *p;

  if (!PyUnicode_CheckExact(str)) {
    PyErr_Format(PyExc_TypeError,
                 "argument must be unicode, %.80s found.",
                 str == Py_None ? "None" : str->ob_type->tp_name);
    return -1;
  }

  p = PyUnicode_AS_UNICODE(str);
  if (*p == 0) {
    return 0;
  }

  do {
    /* all characters must match NameChar */
    for (p++; *p && *p != 0x20; p++) {
      if (!IS_NAMECHAR(*p)) {
        return 0;
      }
    }
  } while (*p++);

  return 1;
}

static int IsQName(PyObject *str)
{
  Py_UNICODE *p;

  if (!PyUnicode_CheckExact(str)) {
    PyErr_Format(PyExc_TypeError,
                 "argument must be unicode, %.80s found.",
                 str == Py_None ? "None" : str->ob_type->tp_name);
    return -1;
  }

  p = PyUnicode_AS_UNICODE(str);
  if (*p == 0) {
    return 0;
  }

  /* the first character must match NCNameStart */
  if (!IS_NCNAMESTART(*p)) {
    return 0;
  }

  /* the remaining characters must match NCNameChar (up to ':' or EOS) */
  for (p++; *p; p++) {
    if (!IS_NCNAMECHAR(*p)) {
      if (*p == ':') {
        /* skip over the ':' */
        p++;

        /* the next character must match NCNameStart */
        if (!IS_NCNAMESTART(*p)) {
          return 0;
        }

        /* the remaining characters must match NCName */
        for (p++; *p; p++) {
          if (!IS_NCNAMECHAR(*p)) {
            return 0;
          }
        }
        break;
      } else {
        return 0;
      }
    }
  }

  return 1;
}

static int IsNCName(PyObject *str)
{
  Py_UNICODE *p;

  if (!PyUnicode_CheckExact(str)) {
    PyErr_Format(PyExc_TypeError,
                 "argument must be unicode, %.80s found.",
                 str == Py_None ? "None" : str->ob_type->tp_name);
    return -1;
  }

  p = PyUnicode_AS_UNICODE(str);
  if (*p == 0) {
    return 0;
  }

  /* the first character must match NCNameStart */
  if (!IS_NCNAMESTART(*p)) {
    return 0;
  }

  /* the remaining characters must match NCNameChar */
  for (p++; *p; p++) {
    if (!IS_NCNAMECHAR(*p)) {
      return 0;
    }
  }

  return 1;
}

static int SplitQName(PyObject *qualifiedName, PyObject **prefix,
                      PyObject **localName)
{
  int i;
  Py_UNICODE colon = ':';
  Py_ssize_t len = PyUnicode_GET_SIZE(qualifiedName);
  const Py_UNICODE *p = PyUnicode_AS_UNICODE(qualifiedName);

  for (i = 0; i < len; i++) {
    if (p[i] == colon) {
      PyObject *u, *v;
      u = PyUnicode_FromUnicode(p, (Py_ssize_t)i);
      if (u == NULL) {
        return 0;
      }
      /* skip over the colon */
      i++;
      v = PyUnicode_FromUnicode((p + i), (Py_ssize_t)(len - i));
      if (v == NULL) {
        Py_DECREF(u);
        return 0;
      }
      *prefix = u;
      *localName = v;
      return 1;
    }
  }

  /* No prefix */
  *prefix = Py_None;
  Py_INCREF(Py_None);
  *localName = qualifiedName;
  Py_INCREF(qualifiedName);
  return 1;
}

/** Public Methods ****************************************************/

static char lstrip_doc[] =
"XmlStrLStrip(S) -> unicode\n\
\n\
Return a copy of the string S with leading whitespace removed.";

static PyObject *string_lstrip(PyObject *self, PyObject *args)
{
  PyObject *_argc0, *result;  /*Unicode objects*/
  PyUnicodeObject *unistr;

  if (!PyArg_ParseTuple(args,"O:XmlStrLStrip",&_argc0))
    return NULL;

  unistr = (PyUnicodeObject *)PyUnicode_FromObject(_argc0);
  if (!unistr) {
    if (PyErr_ExceptionMatches(PyExc_TypeError))
      PyErr_Format(PyExc_TypeError,
                   "argument must be unicode or string, %.80s found.",
                   _argc0->ob_type->tp_name);
    return NULL;
  }
  result = XmlStrip(unistr , 1, 0);

  /*PyUnicode_FromObject always adds one REF so do a DECREF on it*/
  Py_DECREF(unistr);

  /*Has a REF of one now so we don't need to INCREF it*/
  return result;
}


static char rstrip_doc[] =
"XmlStrRStrip(S) -> unicode\n\
\n\
Return a copy of the string S with trailing whitespace removed.";

static PyObject *string_rstrip(PyObject * self, PyObject *args)
{
  PyObject *_argc0, *result;  /*Unicode objects*/
  PyUnicodeObject *unistr;

  if (!PyArg_ParseTuple(args,"O:XmlStrRStrip",&_argc0))
    return NULL;

  unistr = (PyUnicodeObject *)PyUnicode_FromObject(_argc0);
  if (!unistr) {
    if (PyErr_ExceptionMatches(PyExc_TypeError))
      PyErr_Format(PyExc_TypeError,
                   "argument must be unicode or string, %.80s found.",
                   _argc0->ob_type->tp_name);
    return NULL;
  }
  result = XmlStrip(unistr, 0, 1);

  /*PyUnicode_FromObject always adds one REF so do a DECREF on it*/
  Py_DECREF(unistr);

  /*Has a REF of one now so we don't need to INCREF it*/
  return result;
}


static char strip_doc[] =
"XmlStrStrip(S) -> unicode\n\
\n\
Return a copy of the string S with leading and trailing whitespace removed.";

static PyObject *string_strip(PyObject * self, PyObject *args)
{
  PyObject *_argc0, *result;  /*Unicode objects*/
  PyUnicodeObject *unistr;

  if (!PyArg_ParseTuple(args,"O:XmlStrStrip",&_argc0))
    return NULL;

  unistr = (PyUnicodeObject *)PyUnicode_FromObject(_argc0);
  if (!unistr) {
    if (PyErr_ExceptionMatches(PyExc_TypeError))
      PyErr_Format(PyExc_TypeError,
                   "argument must be unicode or string, %.80s found.",
                   _argc0->ob_type->tp_name);
    return NULL;
  }

  result = XmlStrip(unistr, 1, 1);

  /*PyUnicode_FromObject always adds one REF so do a DECREF on it*/
  Py_DECREF(unistr);

  /*Has a REF of one now so we don't need to INCREF it*/
  return result;
}

static char isxml_doc[] =
"IsXml(S) -> bool\n\
\n\
Return True if the given bytes represent a (possibly) well-formed XML\n\
document. (see http://www.w3.org/TR/REC-xml/#sec-guessing).";

static PyObject *string_isxml(PyObject *self, PyObject *args)
{
  char *str, *encoding;
  Py_ssize_t len;
  PyObject *characters, *result;
  Py_UNICODE *p;

  if (!PyArg_ParseTuple(args,"s#:IsXml", &str, &len))
    return NULL;

  /* Determine the encoding of the XML bytes */
  if (len >= 4) {
    Py_UCS4 ch = (((unsigned char)str[0] << 24)
                  | ((unsigned char)str[1] << 16)
                  | ((unsigned char)str[2] << 8)
                  | (unsigned char)str[3]);
    switch (ch) {
    case 0x3C3F786D: /* '<?xm' */
    case 0x003C003F: /* '<?' UTF-16BE */
    case 0x3C003F00: /* '<?' UTF-16LE */
    case 0x4C6FA794: /* '<?xm' EBCDIC */
    case 0x0000003C: /* '<' UCS-4 (1234 order) [big-endian] */
    case 0x3C000000: /* '<' UCS-4 (4321 order) [little-endian] */
    case 0x00003C00: /* '<' UCS-4 (2143 order) [unusual] */
    case 0x003C0000: /* '<' UCS-4 (3412 order) [unusual] */
      Py_INCREF(Py_True);
      return Py_True;
    case 0x0000FEFF: /* BOM UCS-4 (1234 order) [big-endian] */
    case 0xFFFE0000: /* BOM UCS-4 (4321 order) [little-endian] */
    case 0x0000FFFE: /* BOM UCS-4 (2143 order) [unusual] */
    case 0xFEFF0000: /* BOM UCS-4 (3412 order) [unusual] */
      /* NOTE - this is not a valid Python codec (as of 2.4).  It is still
       * OK to use as failure to lookup here (and return a False result) is
       * the same as the parser not being able to handle it later.
       */
      encoding = "utf-32";
      break;
    default:
      /* check for UTF-8 BOM */
      if ((ch & 0xFFFFFF00) == 0xEFBBBF00) {
        /* Skip over the BOM as Python includes it in the result */
        encoding = "utf-8";
        str += 3;
        len -= 3;
      } else {
        switch (ch >> 16) {
        case 0xFEFF: /* BOM UTF-16BE */
        case 0xFFFE: /* BOM UTF-16LE */
          encoding = "utf-16";
          break;
        default: /* UTF-8 without encoding declaration */
          encoding = "utf-8";
        }
      }
    }
  } else {
    /* UTF-8 without encoding declaration */
    encoding = "utf-8";
  }

  characters = PyUnicode_Decode(str, len, encoding, NULL);
  if (characters == NULL) {
    /* The auto-detected encoding is not correct, must not be XML */
    PyErr_Clear();
    result = Py_False;
  } else {
    /* Find the first non-whitespace character */
    p = PyUnicode_AS_UNICODE(characters);
    while (IS_XMLSPACE(*p)) p++;

    /* The first non-whitespace character in a well-formed XML document must
     * be '<'.
     */
    result = *p == '<' ? Py_True : Py_False;
    Py_DECREF(characters);
  }

  Py_INCREF(result);
  return result;
}

static char isspace_doc[] =
"IsXmlSpace(S) -> bool\n\
\n\
Return True if there are only whitespace characters in S, False otherwise.";

static PyObject *string_isspace(PyObject *self, PyObject *args)
{
  PyObject *arg, *str;

  if (!PyArg_ParseTuple(args,"O:IsXmlSpace", &arg))
    return NULL;

  str = PyUnicode_FromObject(arg);
  if (!str) {
    if (PyErr_ExceptionMatches(PyExc_TypeError))
      PyErr_Format(PyExc_TypeError,
                   "argument must be unicode or string, %.80s found.",
                   arg->ob_type->tp_name);
    return NULL;
  }

  arg = IsSpace(str) ? Py_True : Py_False;
  Py_DECREF(str);

  Py_INCREF(arg);
  return arg;
}

static char isname_doc[] = "\
IsName(s) -> bool\n\
\n\
Returns True if the given string matches the Name production as defined\n\
by the W3C's XML 1.0 Recommendation.";

static PyObject *string_isname(PyObject *module, PyObject *args)
{
  PyObject *arg, *str;

  if (!PyArg_ParseTuple(args,"O:IsName", &arg))
    return NULL;

  str = PyUnicode_FromObject(arg);
  if (str == NULL) {
    if (PyErr_ExceptionMatches(PyExc_TypeError))
      PyErr_Format(PyExc_TypeError,
                   "argument must be unicode or string, %.80s found.",
                   arg->ob_type->tp_name);
    return NULL;
  }

  arg = IsName(str) ? Py_True : Py_False;
  Py_DECREF(str);

  Py_INCREF(arg);
  return arg;
}


static char isnmtoken_doc[] = "\
IsNmtoken(s) -> bool\n\
\n\
Returns True if the given string matches the Nmtoken production as defined\n\
by the W3C's XML 1.0 Recommendation.";

static PyObject *string_isnmtoken(PyObject *module, PyObject *args)
{
  PyObject *arg, *str;

  if (!PyArg_ParseTuple(args,"O:IsNmtoken", &arg))
    return NULL;

  str = PyUnicode_FromObject(arg);
  if (str == NULL) {
    if (PyErr_ExceptionMatches(PyExc_TypeError))
      PyErr_Format(PyExc_TypeError,
                   "argument must be unicode or string, %.80s found.",
                   arg->ob_type->tp_name);
    return NULL;
  }

  arg = IsNmtoken(str) ? Py_True : Py_False;
  Py_DECREF(str);

  Py_INCREF(arg);
  return arg;
}


static char isqname_doc[] = "\
IsQName(s) -> bool\n\
\n\
Returns True if the given string matches the QName production as defined\n\
by the W3C's Namespaces in XML Recommendation.";

static PyObject *string_isqname(PyObject *module, PyObject *args)
{
  PyObject *arg, *str;

  if (!PyArg_ParseTuple(args,"O:IsQName", &arg))
    return NULL;

  str = PyUnicode_FromObject(arg);
  if (str == NULL) {
    if (PyErr_ExceptionMatches(PyExc_TypeError))
      PyErr_Format(PyExc_TypeError,
                   "argument must be unicode or string, %.80s found.",
                   arg->ob_type->tp_name);
    return NULL;
  }

  arg = IsQName(str) ? Py_True : Py_False;
  Py_DECREF(str);

  Py_INCREF(arg);
  return arg;
}


static char isncname_doc[] = "\
IsNCName(s) -> bool\n\
\n\
Returns True if the given string matches the NCName production as defined\n\
by the W3C's Namespaces in XML Recommendation.";

static PyObject *string_isncname(PyObject *module, PyObject *args)
{
  PyObject *arg, *str;

  if (!PyArg_ParseTuple(args,"O:IsNCName", &arg))
    return NULL;

  str = PyUnicode_FromObject(arg);
  if (str == NULL) {
    if (PyErr_ExceptionMatches(PyExc_TypeError))
      PyErr_Format(PyExc_TypeError,
                   "argument must be unicode or string, %.80s found.",
                   arg->ob_type->tp_name);
    return NULL;
  }

  arg = IsNCName(str) ? Py_True : Py_False;
  Py_DECREF(str);

  Py_INCREF(arg);
  return arg;
}


static char splitqname_doc[] = "\
SplitQName(qualifiedName) -> (prefix, localName)\n\
\n\
where 'qualifiedName' is a QName according to XML Namespaces 1.0\n\
<http://www.w3.org/TR/REC-xml-names>.\n\
returns the name parts according to the spec.";

static PyObject *string_splitqname(PyObject *self, PyObject *args)
{
  PyObject *qualifiedName, *localName, *prefix, *result;

  if (!PyArg_ParseTuple(args, "O:SplitQName", &qualifiedName))
    return NULL;

  qualifiedName = PyUnicode_FromObject(qualifiedName);
  if (qualifiedName == NULL) return NULL;

  if (SplitQName(qualifiedName, &prefix, &localName) == 0) {
    Py_DECREF(qualifiedName);
    return NULL;
  }
  Py_DECREF(qualifiedName);

  result = PyTuple_New((Py_ssize_t)2);
  if (result == NULL) {
    Py_DECREF(prefix);
    Py_DECREF(localName);
    return NULL;
  }

  /* steals references */
  PyTuple_SET_ITEM(result, 0, prefix);
  PyTuple_SET_ITEM(result, 1, localName);
  return result;
}

/** Module Initialization *********************************************/

static PyMethodDef module_methods[] = {
  { "XmlStrLStrip", string_lstrip,     METH_VARARGS, lstrip_doc },
  { "XmlStrRStrip", string_rstrip,     METH_VARARGS, rstrip_doc },
  { "XmlStrStrip",  string_strip,      METH_VARARGS, strip_doc },
  { "IsXml",        string_isxml,      METH_VARARGS, isxml_doc },
  { "IsXmlSpace",   string_isspace,    METH_VARARGS, isspace_doc },
  { "IsName",       string_isname,     METH_VARARGS, isname_doc },
  { "IsNmtoken",    string_isnmtoken,  METH_VARARGS, isnmtoken_doc },
  { "IsQName",      string_isqname,    METH_VARARGS, isqname_doc },
  { "IsNCName",     string_isncname,   METH_VARARGS, isncname_doc },
  { "SplitQName",   string_splitqname, METH_VARARGS, splitqname_doc },
  { NULL, NULL }
};

static XmlString_APIObject XmlString_API = {
  IsSpace,
  IsName,
  IsNames,
  IsNmtoken,
  IsNmtokens,
  IsQName,
  IsNCName,
  SplitQName,
  NormalizeSpace,
};

DL_EXPORT(void) initXmlString(void)
{
  PyObject *module;
  PyObject *capi;

  module = Py_InitModule3("XmlString", module_methods, module_doc);
  if (module == NULL) return;

  /* Export C API */
  capi = PyCObject_FromVoidPtr((void *)&XmlString_API, NULL);
  if (capi) PyModule_AddObject(module, "CAPI", capi);

  return;
}
