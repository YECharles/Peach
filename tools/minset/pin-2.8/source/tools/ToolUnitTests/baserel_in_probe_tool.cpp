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
/*
  This tool validates ability to set probe if base relocation is present in probed bytes.
  Such probe is not allowed in relocated image where fixups are not yet resolved.
  The test application first loads a DLL at preferred base address and then its copy
  which is certainly relocated by system loader, so rebase condition is guaranteed.
  The tool limits validation of Pin functionality only to case where fixups are not yet resolved.
  To detect unresolved fixups the tool checks reference to known address.
*/

#include <stdio.h>
#include <string>

#include "pin.H"


/*
 * Return TRUE if baseName matches tail of imageName. Comparison is case-insensitive.
 * @param[in]  imageName  image file name in either form with extension
 * @param[in]  baseName   image base name with extension (e.g. kernel32.dll)
 */
static BOOL CmpBaseImageName(const string & imageName, const string & baseName)
{
    if (imageName.size() >= baseName.size())
    {
        return _stricmp(imageName.c_str() + imageName.size() - baseName.size(), baseName.c_str()) == 0;
    }
    return FALSE;
}


static VOID on_module_loading(IMG img, VOID *data)
{
    RTN routine = RTN_FindByName(img, "baserel_in_probe");
    if (!RTN_Valid(routine))
    {
        routine = RTN_FindByName(img, "_baserel_in_probe");
    }

    // This same function is exported by the main executable and by 2 loaded DLLs.
    // Main executable is built with base address 0, so it will be relocated.
    // DLLs are exact copies, differ only by file name.
    // The first DLL is loaded at its preferred base address origDLLbase and the second is relocated.
    const ADDRINT origDLLbase = 0x10000000;
    if (RTN_Valid(routine))
    {
        // Fixup is located at offset 3 from function entry point.
        ADDRINT * fixup_addr = reinterpret_cast<ADDRINT *>(RTN_Address(routine) + 3);
        // Value of the fixup is address of the function entry point.
        if (*fixup_addr == RTN_Address(routine))
        {
            // Fixups were already resolved. Check that probe is allowed.
            if (RTN_IsSafeForProbedInsertion(routine) && RTN_IsSafeForProbedReplacement(routine))
            {
                // Fixup in probed bytes of relocated main exe should unconditionally invalidate probe!
                if (! IMG_IsMainExecutable(img))
                {
                    printf("fixup is handled properly, probe enabled\n");
                }
                else
                {
                    printf("ERROR: probe was enabled for relocated main exe\n");
                }
            }
            else if (IMG_IsMainExecutable(img) || (IMG_LowAddress(img) != origDLLbase))
            {
                // Fixups were applied but Pin considers probe unsafe.
                // This is OK if the image is main exe or it was dynamically loaded and relocated.
                printf("fixup is handled properly, probe refused\n");
            }
            else
            {
                printf("ERROR: probe was refused for non-relocated DLL\n");
            }
        }
        else
        {
            // Fixups were not yet resolved. Check that probe is not allowed due to unresolved fixup.
            if (!RTN_IsSafeForProbedInsertion(routine) && !RTN_IsSafeForProbedReplacement(routine))
            {
                printf("fixup is handled properly, probe refused\n");
            }
            else
            {
                printf("ERROR: probe was enabled while fixups were not yet applied in relocated image\n");
            }
        }
    }

    if (CmpBaseImageName(IMG_Name(img), "kernel32.dll"))
    {
        routine = RTN_FindByName(img, "DuplicateHandle");
        if (RTN_Valid(routine))
        {
            // DuplicateHandle in kernel32.dll contains base relocation in first 5 bytes of code.
            // Anyway Pin should allow probe since kernel32.dll is statically loaded
            // and thus it is assumed base relocation were already applied by OS
            // prior to invocation of this callback.
            // Fixups were already resolved. Check that probe is allowed.
            if (RTN_IsSafeForProbedInsertion(routine) && RTN_IsSafeForProbedReplacement(routine))
            {
                printf("fixup is handled properly, probe enabled\n");
            }
            else
            {
                printf("ERROR: probe of DuplicateHandle was refused\n");
            }
        }
    }
    // The tool is expected to print the message 4 times.
}


int main(int argc, char** argv)
{
    PIN_InitSymbols();

    if (!PIN_Init(argc, argv))
    {
        IMG_AddInstrumentFunction(on_module_loading,  0);        

        PIN_StartProbedProgram();
    }

    exit(1);
}
