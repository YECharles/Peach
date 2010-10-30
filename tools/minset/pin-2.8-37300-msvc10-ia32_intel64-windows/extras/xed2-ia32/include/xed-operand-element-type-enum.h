/*BEGIN_LEGAL 
Intel Open Source License 

Copyright (c) 2002-2010 Intel Corporation. All rights reserved.
 
Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

Redistributions of source code must retain the above copyright notice,
this list of conditions and the following disclaimer.  Redistributions
in binary form must reproduce the above copyright notice, this list of
conditions and the following disclaimer in the documentation and/or
other materials provided with the distribution.  Neither the name of
the Intel Corporation nor the names of its contributors may be used to
endorse or promote products derived from this software without
specific prior written permission.
 
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE INTEL OR
ITS CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
END_LEGAL */
/// @file xed-operand-element-type-enum.h

// This file was automatically generated.
// Do not edit this file.

#if !defined(_XED_OPERAND_ELEMENT_TYPE_ENUM_H_)
# define _XED_OPERAND_ELEMENT_TYPE_ENUM_H_
#include "xed-common-hdrs.h"
typedef enum {
  XED_OPERAND_ELEMENT_TYPE_INVALID,
  XED_OPERAND_ELEMENT_TYPE_UINT, ///< Unsigned integer
  XED_OPERAND_ELEMENT_TYPE_INT, ///< Signed integer
  XED_OPERAND_ELEMENT_TYPE_SINGLE, ///< 32b FP single precision
  XED_OPERAND_ELEMENT_TYPE_DOUBLE, ///< 64b FP double precision
  XED_OPERAND_ELEMENT_TYPE_LONGDOUBLE, ///< 80b FP x87
  XED_OPERAND_ELEMENT_TYPE_LONGBCD, ///< 80b decimal BCD
  XED_OPERAND_ELEMENT_TYPE_STRUCT, ///< a structure of various fields
  XED_OPERAND_ELEMENT_TYPE_VARIABLE, ///< depends on other fields in the instruction
  XED_OPERAND_ELEMENT_TYPE_LAST
} xed_operand_element_type_enum_t;

XED_DLL_EXPORT xed_operand_element_type_enum_t str2xed_operand_element_type_enum_t(const char* s);
XED_DLL_EXPORT const char* xed_operand_element_type_enum_t2str(const xed_operand_element_type_enum_t p);

XED_DLL_EXPORT xed_operand_element_type_enum_t xed_operand_element_type_enum_t_last(void);
       
#endif
