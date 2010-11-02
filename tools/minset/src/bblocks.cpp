
//
// PIN Tool to find all basic blocks a program hits.
//  This PIN Tool is intended for use with Peach.
//
//  Code based on examples from PIN documentation.
//
// Author:
//   Michael Eddington (mike@phed.org)
//

// TODO: Modify so we only hit each BBL once.

#include <pin.H>
#include <stdio.h>
#include <set>

using namespace std;

static FILE* trace;
static set<unsigned int> setKnownBlocks;
static pair<set<unsigned int>::iterator,bool> ret;

VOID PIN_FAST_ANALYSIS_CALL rememberBlock(ADDRINT bbl)
{
    ret = setKnownBlocks.insert(bbl);
    if(ret.second == true)
    {
        fprintf(trace, "%p\n", bbl);
        fflush(trace);
    }
}

VOID Trace(TRACE trace, VOID *v)
{
    for (BBL bbl = TRACE_BblHead(trace); BBL_Valid(bbl); bbl = BBL_Next(bbl))
    {
        BBL_InsertCall(bbl, IPOINT_ANYWHERE, AFUNPTR(rememberBlock), IARG_FAST_ANALYSIS_CALL, IARG_ADDRINT, BBL_Address(bbl), IARG_END);
    }
}

VOID Fini(INT32 code, VOID *v)
{
    /*
    set<unsigned int>::iterator i;
    for(i = setKnownBlocks.begin(); i != setKnownBlocks.end(); ++i)
    {
        fprintf(trace, "%p\n", *i);
    }
    */
    
    fclose(trace);
}

int main(int argc, char * argv[])
{
    trace = fopen("bblocks.out", "w");
    
    PIN_Init(argc, argv);
    TRACE_AddInstrumentFunction(Trace, 0);
    PIN_AddFiniFunction(Fini, 0);
    PIN_StartProgram();
    
    return 0;
}

// end
