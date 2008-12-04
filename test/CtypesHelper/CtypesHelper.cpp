// CtypesHelper.cpp : Defines the exported functions for the DLL application.
//

#include "stdafx.h"
#include "CtypesHelper.h"

CTYPESHELPER_API int TestCase1(struct TestCase1 value)
{
	if(value.Val1 == 0xffe && value.Val2 == 0xfffffe)
	{
		return 1;
	}

	return 0;
}

CTYPESHELPER_API int TestCase1_1(struct TestCase1* value)
{
	if(value->Val1 == 0xffe && value->Val2 == 0xfffffe)
	{
		return 1;
	}

	return 0;
}

CTYPESHELPER_API int TestCase2(struct TestCase2 value)
{
	if(value.byte1 == 0xfe)
	{
		return 1;
	}

	return 0;
}

CTYPESHELPER_API int TestCase3(struct TestCase3 value)
{
	if(value.byte1 == 0xfe && value.byte2 == 0xef && value.byte3 == 0 && 
		value.case1.Val1 == 0xffe && value.case1.Val2 == 0xfffffe)
	{
		return 1;
	}

	return 0;
}

CTYPESHELPER_API int TestCase4(struct TestCase4 value)
{
	if(value.byte1 == 0xfe && value.byte2 == 0xef && 
		value.case1->Val1 == 0xffe && value.case1->Val2 == 0xfffffe)
	{
		return 1;
	}

	return 0;
}

// end
