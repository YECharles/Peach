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
//
// This tool prints a trace of image load and unload events
//

#include <stdio.h>
#include "pin.H"

#include <dlfcn.h>
#include <iostream>
#include <fstream>
#include <stdlib.h>


BOOL inMain = FALSE;

void MainBefore()
{
    inMain = TRUE;
}

VOID MainAfter()
{
    inMain = FALSE;
}

VOID ImageLoad(IMG img, VOID *v)
{
    if (inMain)
    {
        cout << "Loaded " << IMG_Name(img) << endl;
    }
    
    if (IMG_IsMainExecutable(img))
    {
        RTN mainRtn = RTN_FindByName(img, "_main");
        if (!RTN_Valid(mainRtn))
            mainRtn = RTN_FindByName(img, "main");

        if (!RTN_Valid(mainRtn))
        {
            cout << "Can't find the main routine in " << IMG_Name(img) << endl;
            exit(1);
        }
        RTN_Open(mainRtn);
        RTN_InsertCall(mainRtn, IPOINT_BEFORE, AFUNPTR(MainBefore), IARG_END);
        RTN_InsertCall(mainRtn, IPOINT_AFTER, AFUNPTR(MainAfter), IARG_END);
        RTN_Close(mainRtn);
    }
}

VOID ImageUnload(IMG img, VOID *v)
{
    if (inMain)
    {
        cout << "Unloaded " << IMG_Name(img) << endl;
    }
}


// argc, argv are the entire command line, including pin -t <toolname> -- ...
int main(int argc, char * argv[])
{
    PIN_InitSymbols();
    
    // Initialize pin
    PIN_Init(argc, argv);

    // Register ImageLoad to be called when an image is loaded
    IMG_AddInstrumentFunction(ImageLoad, 0);

    // Register ImageUnload to be called when an image is unloaded
    IMG_AddUnloadFunction(ImageUnload, 0);

    // Start the program, never returns
    PIN_StartProgram();
    
    return 0;
}
