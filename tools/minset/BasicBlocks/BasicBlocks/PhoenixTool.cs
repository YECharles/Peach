//-----------------------------------------------------------------------------
//
// Description:
//
//    A standalone static analysis/instrumentation tool
//
// Usage:
//
//    BasicBlocks /in <image-name>
//
//-----------------------------------------------------------------------------

#region Using namespace declarations

using System;
using System.IO;
using System.Collections;

#endregion

using System.Collections.Generic;

namespace BasicBlocks
{
	//-------------------------------------------------------------------------
	//
	// Description:
	//
	//    Perform static analysis on the units in the binary.
	//
	//-------------------------------------------------------------------------

	public class StaticAnalysisPhase : Phx.Phases.Phase
	{
		public static List<uint> BasicBlockAddresses = new List<uint>();

#if (PHX_DEBUG_SUPPORT)
        private static Phx.Controls.ComponentControl StaticAnalysisPhaseCtrl;
#endif

		//---------------------------------------------------------------------
		//
		// Description:
		//
		//    Initialize the static analysis phase.
		//
		// Remarks:
		//
		//    Sets up a component control under debug builds, so that we
		//    can dump IR before/after the phase and so on. In other
		//    words, because we create this control, you can pass in
		//    options like -predumpmtrace that will dump the IR for each
		//    method before this phase runs.
		//
		//---------------------------------------------------------------------
		public static void Initialize()
		{
#if PHX_DEBUG_SUPPORT
            StaticAnalysisPhase.StaticAnalysisPhaseCtrl = 
                Phx.Controls.ComponentControl.New("root",
                "Perform Static Analysis", "BasicBlocks.cs");
#endif
		}

		//---------------------------------------------------------------------
		//
		// Description:
		//
		//    Creates a new StaticAnalysisPhase object
		//
		// Arguments:
		//
		//    config - The encapsulating object that simplifies handling of
		//    the phase list and pre and post phase events.
		//
		//---------------------------------------------------------------------
		public static StaticAnalysisPhase New(Phx.Phases.PhaseConfiguration config)
		{
			StaticAnalysisPhase staticAnalysisPhase =
				new StaticAnalysisPhase();

			staticAnalysisPhase.Initialize(config, "Static Analysis");

#if PHX_DEBUG_SUPPORT
            staticAnalysisPhase.PhaseControl = 
                StaticAnalysisPhase.StaticAnalysisPhaseCtrl;
#endif

			return staticAnalysisPhase;
		}

		//---------------------------------------------------------------------
		//
		// Description:
		//
		//    Executes the StaticAnalysisPhase phase.
		//
		// Arguments:
		//
		//    unit - The unit that this phase should operate on.
		//
		// Remarks:
		//
		//    You should add your static analysis code here.  Each unit of the
		//    program will pass through this function.
		//
		//---------------------------------------------------------------------
		protected override void Execute(Phx.Unit unit)
		{
			if (!unit.IsFunctionUnit)
			{
				return;
			}

			Phx.FunctionUnit functionUnit = unit.AsFunctionUnit;

			// TODO: Do your static analysis of this unit here
			functionUnit.BuildFlowGraph();
            int funcOffset = 0;
            uint i;

			foreach (Phx.Graphs.BasicBlock b in functionUnit.FlowGraph.BasicBlocks)
			{
                i = b.FirstInstruction.OriginalRva;
                if (i == 0)
				{
					continue;
				}

				// LABEL's are cuasing issues, so skip...
				switch (b.FirstInstruction.Opcode.Id)
				{
					case 101:	// LABEL
                        i = b.FirstInstruction.Next.OriginalRva;
						if (!BasicBlockAddresses.Contains(i))
							BasicBlockAddresses.Add(i);
						break;

					case 122:	// END
						continue;
					
					default:
						if (!BasicBlockAddresses.Contains(i))
							BasicBlockAddresses.Add(i);

						break;
				}
			}
		}
	}

	public class Driver
	{
		//---------------------------------------------------------------------
		//
		// Description:
		//
		//    Name of the executable file to process.
		//
		//---------------------------------------------------------------------
		public static Phx.Controls.StringControl input;

		//---------------------------------------------------------------------
		//
		// Description:
		//
		//    Name of the output binary.
		//
		//---------------------------------------------------------------------
		public static Phx.Controls.StringControl output;

		//---------------------------------------------------------------------
		//
		// Description:
		//
		//    Name of the output pdb.
		//
		//---------------------------------------------------------------------
		public static Phx.Controls.StringControl pdbout;

		//---------------------------------------------------------------------
		//
		// Description:
		//
		//    Does the static initialization of the Phoenix framework and the 
		//    program.
		//
		// Arguments:
		//
		//    arguments - Array of command line argument strings.
		//
		// Remarks:
		//
		//    StaticInitialize registers the available targets and processes in the 
		//    command-line options.
		//
		//---------------------------------------------------------------------
		public static void StaticInitialize(string[] arguments)
		{
			// Initialize the available targets.

			Driver.InitializeTargets();

			// Start initialization of the Phoenix framework.

			Phx.Initialize.BeginInitialization();

			// Initialize the command line string controls

			Driver.InitializeCommandLine();

			// Initialize the component control for the static analysis phase.
			// This is included so that standard Phoenix controls can be used 
			// on this too.

			StaticAnalysisPhase.Initialize();

			Phx.Initialize.EndInitialization("PHX|*|_PHX_", arguments);

			// Check the processed command line options against those required
			// by the tool for execution.  If they are not present, exit the 
			// app.

			if (!Driver.CheckCommandLine())
			{
				Driver.Usage();
				Phx.Term.All(Phx.Term.Mode.Fatal);
				Environment.Exit(1);
			}
		}

		//---------------------------------------------------------------------
		//
		// Description:
		//
		//    Usage string for this sample.
		//
		// Remarks:
		//
		//    Options can include any of the standard phoenix controls,
		//    eg -dumptypes.
		//
		//---------------------------------------------------------------------
		public static void Usage()
		{
			Phx.Output.WriteLine("BasicBlocks /in <image-name>");
		}

		//---------------------------------------------------------------------
		//
		// Description:
		//
		//    Checks the command line against the required options.
		//
		// Returns:
		//
		//    True if the command line has all the required options, false 
		//    otherwise.
		//
		//---------------------------------------------------------------------
		private static bool CheckCommandLine()
		{
			return !String.IsNullOrEmpty(Driver.input.GetValue(null));
		}

		//---------------------------------------------------------------------
		//
		// Description:
		//
		//    Registers string controls with Phoenix for command line option
		//    processing.
		//
		//---------------------------------------------------------------------
		private static void InitializeCommandLine()
		{
			// Initialize each command line option (string controls), so that
			// the framework knows about them.

			// C# doesn't have a __LINE__ macro, so instead we have chosen a 
			// hardcoded value, with some room to add other values in between
			Driver.input = Phx.Controls.StringControl.New("in",
				"input file",
				Phx.Controls.Control.MakeFileLineLocationString(
					"PhoenixTool.cs",
					100));
		}

		//---------------------------------------------------------------------
		//
		// Description:
		//
		//    Initialize the dependent architectures and runtimes.
		//
		// Remarks:
		//
		//    All runtimes and architectures available in the RDK are 
		//    registered.
		//
		//---------------------------------------------------------------------
		private static void InitializeTargets()
		{
			// Setup targets available in the RDK.

			Phx.Targets.Architectures.Architecture x86Arch =
				Phx.Targets.Architectures.X86.Architecture.New();
			Phx.Targets.Runtimes.Runtime win32x86Runtime =
				Phx.Targets.Runtimes.Vccrt.Win32.X86.Runtime.New(x86Arch);
			Phx.GlobalData.RegisterTargetArchitecture(x86Arch);
			Phx.GlobalData.RegisterTargetRuntime(win32x86Runtime);

			Phx.Targets.Architectures.Architecture msilArch =
				Phx.Targets.Architectures.Msil.Architecture.New();
			Phx.Targets.Runtimes.Runtime win32MSILRuntime =
				Phx.Targets.Runtimes.Vccrt.Win.Msil.Runtime.New(msilArch);
			Phx.GlobalData.RegisterTargetArchitecture(msilArch);
			Phx.GlobalData.RegisterTargetRuntime(win32MSILRuntime);
		}

		//---------------------------------------------------------------------
		//
		// Description:
		//
		//    Process the module.
		//
		// Remarks:
		//
		//    The launch point for the instrumentation/static analysis 
		//    functionality of the tool.  Process first opens the existing  
		//    binary and determines its target architecture and runtime.  Then, 
		//    it creates a PE module unit with the input binary and a phase  
		//    listing.  The phase listing is then executed on the PE module.
		//
		//---------------------------------------------------------------------
		public Phx.Term.Mode Process()
		{
			//Phx.Output.WriteLine("Processing " +
			//	Driver.input.GetValue(null) + " ...");

			// Lookup the architecture and runtime from the existing assembly.

			Phx.PEModuleUnit oldModuleUnit =
				Phx.PEModuleUnit.Open(Driver.input.GetValue(null));

			Phx.Targets.Architectures.Architecture architecture = oldModuleUnit.Architecture;
			Phx.Targets.Runtimes.Runtime runtime = oldModuleUnit.Runtime;

			oldModuleUnit.Close();
			oldModuleUnit.Delete();

			// Create an empty program unit

			Phx.Lifetime lifetime =
				Phx.Lifetime.New(Phx.LifetimeKind.Global, null);

			Phx.ProgramUnit programUnit = Phx.ProgramUnit.New(lifetime, null,
				Phx.GlobalData.TypeTable, architecture, runtime);

			// Make an empty moduleUnit

			Phx.PEModuleUnit moduleUnit = Phx.PEModuleUnit.New(lifetime,
				Phx.Name.New(lifetime, Driver.input.GetValue(null)),
				programUnit, Phx.GlobalData.TypeTable, architecture, runtime);

			// Create an overall phase list....

			Phx.Phases.PhaseConfiguration config = Phx.Phases.PhaseConfiguration.New(
				lifetime, "BasicBlocks Phases");

			// Add phases...

			config.PhaseList.AppendPhase(Phx.PE.ReaderPhase.New(config));

			// Create the per-function phase list....

			Phx.Phases.PhaseList unitList = Phx.PE.UnitListPhaseList.New(
				config, Phx.PE.UnitListWalkOrder.PrePass);

			unitList.AppendPhase(
				Phx.PE.RaiseIRPhase.New(config,
					Phx.FunctionUnit.LowLevelIRBeforeLayoutFunctionUnitState));

			unitList.AppendPhase(StaticAnalysisPhase.New(config));
			unitList.AppendPhase(Phx.PE.DiscardIRPhase.New(config));

			config.PhaseList.AppendPhase(unitList);


			// Add any plugins or target-specific phases.

			Phx.GlobalData.BuildPlugInPhases(config);

			// Run the phases.

			config.PhaseList.DoPhaseList(moduleUnit);

			return Phx.Term.Mode.Normal;
		}

		//---------------------------------------------------------------------
		//
		// Description:
		//
		//    Entry point for application
		//
		// Arguments:
		//
		//    argument - Command line argument strings.
		//
		//---------------------------------------------------------------------
		static int Main(string[] arguments)
		{
			// Do static initialization of the Phoenix framework.

			Driver.StaticInitialize(arguments);

			// Process the binary.

			Driver driver = new Driver();
			Phx.Term.Mode termMode = driver.Process();

			Phx.Term.All(termMode);

			//System.Console.WriteLine("All basic blocks");

            FileInfo f = new FileInfo("bblocks.txt");
            f.Delete();

            using (FileStream fout = new FileStream("bblocks.txt", FileMode.CreateNew, FileAccess.Write))
            {
                StreamWriter tout = new StreamWriter(fout);
                foreach (int addr in StaticAnalysisPhase.BasicBlockAddresses)
                {
                    //System.Console.WriteLine("bblock addr: " + addr);
                    tout.WriteLine(addr.ToString());
                }

                tout.Close();
                fout.Close();
            }

			return (termMode == Phx.Term.Mode.Normal ? 0 : 1);
		}
	}
}
