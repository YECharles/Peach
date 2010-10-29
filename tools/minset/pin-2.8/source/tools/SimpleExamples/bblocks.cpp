#include <stdio.h>
#include "pin.H"

FILE* trace;

// This function is called before every instruction is executed
VOID docount(VOID *ip, BOOL isBranch, AADRINT branchAddress)
{
    if(isBranch)
        fprintf(trace, "%p\n", branchAddress);
}
    
// Pin calls this function every time a new instruction is encountered
VOID Instruction(TRACE ins, VOID *v)
{
    // Insert a call to docount before every instruction, no arguments are passed
    TRACE_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)docount, IARG_INST_PTR, IARG_BRANCH_TAKEN, IARG_BRANCH_TARGET_ADDR, IARG_END);
} // IPOINT_TAKEN_BRANCH 

KNOB<string> KnobOutputFile(KNOB_MODE_WRITEONCE, "pintool",
    "o", "inscount.out", "specify output file name");

// This function is called when the application exits
VOID Fini(INT32 code, VOID *v)
{
    fclose(trace);
}

/* ===================================================================== */
/* Print Help Message                                                    */
/* ===================================================================== */

INT32 Usage()
{
    PIN_ERROR("This tool counts the number of dynamic instructions executed\n" + 
        KNOB_BASE::StringKnobSummary() + "\n");
    return -1;
}

/* ===================================================================== */
/* Main                                                                  */
/* ===================================================================== */
/*   argc, argv are the entire command line: pin -t <toolname> -- ...    */
/* ===================================================================== */

int main(int argc, char * argv[])
{
    trace = fopen("bblocks.out", "w");
    
    // Initialize pin
    if (PIN_Init(argc, argv)) return Usage();

    // Register Instruction to be called to instrument instructions
    TRACE_AddInstrumentFunction(Instruction, 0);

    // Register Fini to be called when the application exits
    PIN_AddFiniFunction(Fini, 0);
    
    // Start the program, never returns
    PIN_StartProgram();
    
    return 0;
}
