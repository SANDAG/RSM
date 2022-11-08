Macro "Run SANDAG ABM"

   RunMacro("TCB Init")

   shared path, inputDir, outputDir, inputTruckDir, mxzone, mxtap, mxext,mxlink,mxrte,scenarioYear,version


   sample_rate = { 0.2, 0.5, 1.0 }
   max_iterations=sample_rate.length    //number of feedback loops
   skimByVOT = "true"
   assignByVOT = "true"

   path = "${workpath}"

   RunMacro("HwycadLog",{"sandag_abm_master.rsc:","*********Model Run Starting************"})

   path_parts = SplitPath(path)
   path_no_drive = path_parts[2]+path_parts[3]
   drive=path_parts[1]
   path_forward_slash =  Substitute(path_no_drive, "\\", "/", )

   inputDir = path+"\\input"
   outputDir = path+"\\output"
   inputTruckDir = path+"\\input_truck"

   SetLogFileName(path+"\\logFiles\\tclog.xml")
   SetReportFileName(path+"\\logFiles\\tcreport.xml")

   RunMacro("parameters")

   // read properties from sandag_abm.properties in /conf folder
   properties = "\\conf\\sandag_abm.properties"
   sample_rate = RunMacro("read properties array",properties,"sample_rates", "S")
   max_iterations=sample_rate.length    //number of feedback loops
   scenarioYear = RunMacro("read properties",properties,"scenarioYear", "S")
   skipCopyWarmupTripTables = RunMacro("read properties",properties,"RunModel.skipCopyWarmupTripTables", "S")
   skipCopyBikeLogsum = RunMacro("read properties",properties,"RunModel.skipCopyBikeLogsum", "S")
   skipCopyWalkImpedance= RunMacro("read properties",properties,"RunModel.skipCopyWalkImpedance", "S")
   skipWalkLogsums= RunMacro("read properties",properties,"RunModel.skipWalkLogsums", "S")
   skipBikeLogsums= RunMacro("read properties",properties,"RunModel.skipBikeLogsums", "S")
   skipBuildHwyNetwork = RunMacro("read properties",properties,"RunModel.skipBuildHwyNetwork", "S")
   skipBuildTransitNetwork= RunMacro("read properties",properties,"RunModel.skipBuildTransitNetwork", "S")
   startFromIteration = s2i(RunMacro("read properties",properties,"RunModel.startFromIteration", "S"))
   skipHighwayAssignment = RunMacro("read properties array",properties,"RunModel.skipHighwayAssignment", "S")
   skipHighwaySkimming = RunMacro("read properties array",properties,"RunModel.skipHighwaySkimming", "S")
   skipTransitSkimming = RunMacro("read properties array",properties,"RunModel.skipTransitSkimming", "S")
   skipCoreABM = RunMacro("read properties array",properties,"RunModel.skipCoreABM", "S")
   skipOtherSimulateModel = RunMacro("read properties array",properties,"RunModel.skipOtherSimulateModel", "S")
   skipSpecialEventModel = RunMacro("read properties array",properties,"RunModel.skipSpecialEventModel", "S")
   skipCTM = RunMacro("read properties array",properties,"RunModel.skipCTM", "S")
   skipEI = RunMacro("read properties array",properties,"RunModel.skipEI", "S")
   skipTruck = RunMacro("read properties array",properties,"RunModel.skipTruck", "S")
   skipTripTableCreation = RunMacro("read properties array",properties,"RunModel.skipTripTableCreation", "S")
   skipFinalHighwayAssignment = RunMacro("read properties",properties,"RunModel.skipFinalHighwayAssignment", "S")
   skipFinalTransitAssignment = RunMacro("read properties",properties,"RunModel.skipFinalTransitAssignment", "S")
   skipFinalHighwaySkimming = RunMacro("read properties",properties,"RunModel.skipFinalHighwaySkimming", "S")
   skipFinalTransitSkimming = RunMacro("read properties",properties,"RunModel.skipFinalTransitSkimming", "S")
   skipLUZSkimCreation = RunMacro("read properties",properties,"RunModel.skipLUZSkimCreation", "S")
   skipDataExport = RunMacro("read properties",properties,"RunModel.skipDataExport", "S")
   skipDataLoadRequest = RunMacro("read properties",properties,"RunModel.skipDataLoadRequest", "S")
   skipDeleteIntermediateFiles = RunMacro("read properties",properties,"RunModel.skipDeleteIntermediateFiles", "S")
   precision = RunMacro("read properties",properties,"RunModel.MatrixPrecision", "S")
   minSpaceOnC=RunMacro("read properties",properties,"RunModel.minSpaceOnC", "S")

  // Swap Server Configurations
   runString = path+"\\bin\\serverswap.bat "+drive+" "+path_no_drive+" "+path_forward_slash
   RunMacro("HwycadLog",{"sandag_abm_master.rsc:","Server Config Swap: "+" "+runString})
   ok = RunMacro("TCB Run Command", 1, "Run ServerSwap", runString)
   if !ok then goto quit
   ok=RunMacro("find String","\\logFiles\\serverswap.log","FATAL")
   if !ok then  do
     RunMacro("HwycadLog",{"sandag_abm_master.rsc:","ServerSwap failed! Open logFiles/serverswap.log for details."})
     goto quit
   end

   //Update year specific properties
   runString = path+"\\bin\\updateYearSpecificProps.bat "+drive+" "+path_no_drive+" "+path_forward_slash
   RunMacro("HwycadLog",{"sandag_abm_master.rsc:","Update year specific properties: "+" "+runString})
   ok = RunMacro("TCB Run Command", 1, "Update Year Specific Properties", runString)
   if !ok then goto quit


   //check free space on C drive
   runString = path+"\\bin\\checkFreeSpaceOnC.bat "+minSpaceOnC
   RunMacro("HwycadLog",{"sandag_abm_master.rsc:","Checking if there is enough space on C drive: "+" "+runString})
   ok = RunMacro("TCB Run Command", 1, "Check space on C drive", runString)

   //check AT and Transit networks consistency
   runString = path+"\\bin\\checkAtTransitNetworkConsistency.cmd "+drive+" "+path_forward_slash
   RunMacro("HwycadLog",{"sandag_abm_master.rsc:","Checking if AT and Transit Networks are consistent: "+" "+runString})
   RunProgram(runString, )
   ok=RunMacro("find String","\\logFiles\\AtTransitCheck_event.log","FATAL")
   if !ok then  do
   	RunMacro("HwycadLog",{"sandag_abm_master.rsc:","AT and Transit network consistency chekcing failed! Open AtTransitCheck_event.log for details."})
	goto quit
   end

   // copy bike logsums from input to output folder
   if skipCopyBikeLogsum = "false" then do
	   CopyFile(inputDir+"\\bikeMgraLogsum.csv", outputDir+"\\bikeMgraLogsum.csv")
	   CopyFile(inputDir+"\\bikeTazLogsum.csv", outputDir+"\\bikeTazLogsum.csv")
   end
   if skipBikeLogsums = "false" then do
   	  runString = path+"\\bin\\runSandagBikeLogsums.cmd "+drive+" "+path_forward_slash
	  RunMacro("HwycadLog",{"sandag_abm_master.rsc:","Java-Run create AT logsums and walk impedances"+" "+runString})
	  ok = RunMacro("TCB Run Command", 1, "Run AT-Logsums", runString)
	  if !ok then goto quit
   end

   // copy walk impedance from input to output folder
   if skipCopyWalkImpedance = "false" then do
	   CopyFile(inputDir+"\\walkMgraEquivMinutes.csv", outputDir+"\\walkMgraEquivMinutes.csv")
	   CopyFile(inputDir+"\\walkMgraTapEquivMinutes.csv", outputDir+"\\walkMgraTapEquivMinutes.csv")
   end
   if skipWalkLogsums = "false" then do
	  runString = path+"\\bin\\runSandagWalkLogsums.cmd "+drive+" "+path_forward_slash
	  RunMacro("HwycadLog",{"sandag_abm_master.rsc:","Java-Run create AT logsums and walk impedances"+" "+runString})
	  ok = RunMacro("TCB Run Command", 1, "Run AT-Logsums", runString)
	  if !ok then goto quit
   end

   // copy initial trip tables from input to output folder
   if skipCopyWarmupTripTables = "false" then do
	   CopyFile(inputDir+"\\Trip_EA_VOT.mtx", outputDir+"\\Trip_EA_VOT.mtx")
	   CopyFile(inputDir+"\\Trip_AM_VOT.mtx", outputDir+"\\Trip_AM_VOT.mtx")
	   CopyFile(inputDir+"\\Trip_MD_VOT.mtx", outputDir+"\\Trip_MD_VOT.mtx")
	   CopyFile(inputDir+"\\Trip_PM_VOT.mtx", outputDir+"\\Trip_PM_VOT.mtx")
	   CopyFile(inputDir+"\\Trip_EV_VOT.mtx", outputDir+"\\Trip_EV_VOT.mtx")
   end

  // Build highway network
   if skipBuildHwyNetwork = "false" then do
	   RunMacro("HwycadLog",{"sandag_abm_master.rsc:","Macro - run create hwy"})
	   ok = RunMacro("TCB Run Macro", 1, "run create hwy",{})
	   if !ok then goto quit
   end

   // Create transit routes
   if skipBuildTransitNetwork = "false" then do
	   RunMacro("HwycadLog",{"sandag_abm_master.rsc:","Macro - run create all transit"})
	   ok = RunMacro("TCB Run Macro", 1, "Create all transit",{})
	   if !ok then goto quit
   end

   //Looping
   for iteration = startFromIteration to max_iterations do

      if skipCoreABM[iteration] = "false" or skipOtherSimulateModel[iteration] = "false" or skipSpecialEventModel[iteration] = "false" then do  //Wu modified to add special event model 5/19/2017
	      // Start matrix manager locally
	      runString = path+"\\bin\\runMtxMgr.cmd "+drive+" "+path_no_drive
	      ok = RunMacro("TCB Run Command", 1, "Start matrix manager", runString)
	      if !ok then goto quit

	      // Start  JPPF driver
	      runString = path+"\\bin\\runDriver.cmd "+drive+" "+path_no_drive
	      ok = RunMacro("TCB Run Command", 1, "Start JPPF Driver", runString)
	      if !ok then goto quit

	      // Start HH Manager, and worker nodes
	      runString = path+"\\bin\\StartHHAndNodes.cmd "+drive+" "+path_no_drive
	      ok = RunMacro("TCB Run Command", 1, "Start HH Manager, JPPF Driver, and nodes", runString)
	      if !ok then goto quit
      end

      // Run highway assignment
      if skipHighwayAssignment[iteration] = "false" then do
        RunMacro("HwycadLog",{"sandag_abm_master.rsc:","Macro - hwy assignment"})
	      ok = RunMacro("TCB Run Macro", 1, "hwy assignment",{iteration, assignByVOT})
	      if !ok then goto quit
      end

      // Skim highway network
      if skipHighwaySkimming[iteration] = "false" then do
	      RunMacro("HwycadLog",{"sandag_abm_master.rsc:","Macro - Hwy skim all"})
	      ok = RunMacro("TCB Run Macro", 1, "Hwy skim all",{skimByVOT})
	      if !ok then goto quit

      // Create drive to transit access file
      runString = path+"\\bin\\CreateD2TAccessFile.bat "+drive+" "+path_forward_slash

	    RunMacro("HwycadLog",{"sandag_abm_master.rsc:","Java - Creating drive to transit access file"})
      ok = RunMacro("TCB Run Command", 1, "Creating drive to transit access file", runString)
      if !ok then goto quit
     end

	     // Skim transit network
      if skipTransitSkimming[iteration] = "false" then do
	      RunMacro("HwycadLog",{"sandag_abm_master.rsc:","Macro - Build transit skims"})
	      ok = RunMacro("TCB Run Macro", 1, "Build transit skims",{})
	      if !ok then goto quit
      end

      // First move some trip matrices so model will crash if ctramp model doesn't produced csv/mtx files for assignment
      if (iteration > startFromIteration) then do
         fromDir = outputDir
         toDir = outputDir+"\\iter"+String(iteration-1)
         //check for directory of output
         if GetDirectoryInfo(toDir, "Directory")=null then do
                CreateDirectory( toDir)
         end
         status = RunProgram("cmd.exe /c copy "+fromDir+"\\auto*.mtx "+toDir+"\\auto*.mtx",)
         status = RunProgram("cmd.exe /c copy "+fromDir+"\\tran*.mtx "+toDir+"\\tran*.mtx",)
         status = RunProgram("cmd.exe /c copy "+fromDir+"\\nmot*.mtx "+toDir+"\\nmot*.mtx",)
         status = RunProgram("cmd.exe /c copy "+fromDir+"\\othr*.mtx "+toDir+"\\othr*.mtx",)
         status = RunProgram("cmd.exe /c copy "+fromDir+"\\trip*.mtx "+toDir+"\\trip*.mtx",)
         status = RunProgram("cmd.exe /c copy "+fromDir+"\\internalExternalTrips.csv "+toDir+"\\internalExternalTrips.csv",)
         status = RunProgram("cmd.exe /c copy "+fromDir+"\\airport_out.csv "+toDir+"\\airport_out.csv",)
         status = RunProgram("cmd.exe /c copy "+fromDir+"\\crossBorderTrips.csv "+toDir+"\\crossBorderTrips.csv",)
         status = RunProgram("cmd.exe /c copy "+fromDir+"\\visitorTrips.csv "+toDir+"\\visitorTrips.csv",)

//         status = RunProgram("cmd.exe /c copy "+fromDir+"\\daily*.mtx "+toDir+"\\daily*.mtx",)
//         status = RunProgram("cmd.exe /c copy "+fromDir+"\\comm*.mtx "+toDir+"\\comm*.mtx",)

         status = RunProgram("cmd.exe /c del "+fromDir+"\\auto*.mtx",)
         status = RunProgram("cmd.exe /c del "+fromDir+"\\tran*.mtx",)
         status = RunProgram("cmd.exe /c del "+fromDir+"\\nmot*.mtx",)
         status = RunProgram("cmd.exe /c del "+fromDir+"\\othr*.mtx",)
         status = RunProgram("cmd.exe /c del "+fromDir+"\\trip*.mtx",)
         status = RunProgram("cmd.exe /c del "+fromDir+"\\internalExternalTrips.csv",)
         status = RunProgram("cmd.exe /c del "+fromDir+"\\airport_out.csv",)
         status = RunProgram("cmd.exe /c del "+fromDir+"\\crossBorderTrips.csv",)
         status = RunProgram("cmd.exe /c del "+fromDir+"\\visitorTrips.csv",)

//		 status = RunProgram("cmd.exe /c del "+fromDir+"\\daily*.mtx",)
//		 status = RunProgram("cmd.exe /c del "+fromDir+"\\comm*.mtx",)

      end


      // Run CT-RAMP model
      if skipCoreABM[iteration] = "false" then do
	      runString = path+"\\bin\\runSandagAbm_SDRM.cmd "+drive+" "+path_forward_slash +" "+sample_rate[iteration]+" "+i2s(iteration)
	      RunMacro("HwycadLog",{"sandag_abm_master.rsc:","Java-Run CT-RAMP"+" "+runString})
	      ok = RunMacro("TCB Run Command", 1, "Run CT-RAMP", runString)
	      if !ok then goto quit
      end


       // Run airport model, visitor model, cross-border model, internal-external model
      if skipOtherSimulateModel[iteration] = "false" then do
	      runString = path+"\\bin\\runSandagAbm_SMM.cmd "+drive+" "+path_forward_slash +" "+sample_rate[iteration]+" "+i2s(iteration)
	      RunMacro("HwycadLog",{"sandag_abm_master.rsc:","Java-Run airport model, visitor model, cross-border model"+" "+runString})
	      ok = RunMacro("TCB Run Command", 1, "Run CT-RAMP", runString)
	      if !ok then goto quit
      end

      // Run special event model
      if skipSpecialEventModel[iteration] = "false" then do
	      runString = path+"\\bin\\runSandagAbm_SEM.cmd "+drive+" "+path_forward_slash +" "+sample_rate[iteration]+" "+i2s(iteration)
	      RunMacro("HwycadLog",{"sandag_abm_master.rsc:","Java-Run special event model"+" "+runString})
	      ok = RunMacro("TCB Run Command", 1, "Run CT-RAMP", runString)
	      if !ok then goto quit
      end


      if skipCTM[iteration] = "false" then do
	     //Commercial vehicle trip generation
	      RunMacro("HwycadLog",{"sandag_abm_master.rsc:","Macro - run commercial vehicle generation"})
	      ok = RunMacro("TCB Run Macro", 1, "Commercial Vehicle Generation",{})
	      if !ok then goto quit

	      //Commercial vehicle trip distribution
	      RunMacro("HwycadLog",{"sandag_abm_master.rsc:","Macro - run commercial vehicle distribution"})
	      ok = RunMacro("TCB Run Macro", 1, "Commercial Vehicle Distribution",{})
	      if !ok then goto quit

	      //Commercial vehicle time-of-day
	      RunMacro("HwycadLog",{"sandag_abm_master.rsc:","Macro - run commercial vehicle Time Of Day"})
	      ok = RunMacro("TCB Run Macro", 1, "Commercial Vehicle Time Of Day",{})
	      if !ok then goto quit

	      //Commercial vehicle toll diversion model
	      RunMacro("HwycadLog",{"sandag_abm_master.rsc:","Macro - run commercial vehicle Toll Diversion"})
	      ok = RunMacro("TCB Run Macro", 1, "cv toll diversion model",{})
	      if !ok then goto quit

    	      // reduce commerical travel matrix precisions
    	      RunMacro("HwycadLog",{"sandag_abm_master.rsc","reduce matrix precision for commVehTODTrips.mtx"})
    	      RunMacro("reduce matrix precision",outputDir,"commVehTODTrips.mtx", precision)
      end

      /*
      @WSU 2-23-2017
      Run EI and truck models only in the starting iteration (not necessarily the 1st iteration)
      Purpose:
      	  Reduce number of iterations to cut model run time by 2-2.5 hrs
      Notes:
	      1) Combined EI and truck trips are less than 2.5% of total trips;
	      2) Trip generations are not sensitive to skims, total EI and truck demands are not affected;
	      3) Skims only affect EI and truck destination choices
      */
      if iteration = startFromIteration then do
	      //Run External(U.S.)-Internal Model
	      if skipEI[iteration] = "false" then do
		      RunMacro("HwycadLog",{"sandag_abm_master.rsc:","Macro - US to SD External Trip Model"})
		      ok = RunMacro("TCB Run Macro", 1, "US to SD External Trip Model",{})
		      if !ok then goto quit

	    	     // reduce EI matrix precisions

	    	     m={"usSdWrk_EA.mtx","usSdWrk_AM.mtx","usSdWrk_MD.mtx","usSdWrk_PM.mtx","usSdWrk_EV.mtx","usSdNon_EA.mtx","usSdNon_AM.mtx","usSdNon_MD.mtx","usSdNon_PM.mtx","usSdNon_EV.mtx"}
	    	     for i = 1 to m.length do
	    		RunMacro("HwycadLog",{"sandag_abm_master.rsc","reduce precision for:"+m[i]})
	    		RunMacro("reduce matrix precision",outputDir,m[i], precision)
	    	     end
	      end

	      //Run Truck Model
	      if skipTruck[iteration] = "false" then do
		      RunMacro("HwycadLog",{"sandag_abm_master.rsc:","Macro - truck model"})
		      ok = RunMacro("truck model",properties, iteration)
		      if !ok then goto quit

	    	     // reduce truck matrix precisions
	    	     m={"dailyDistributionMatricesTruckEA.mtx","dailyDistributionMatricesTruckAM.mtx","dailyDistributionMatricesTruckMD.mtx","dailyDistributionMatricesTruckPM.mtx","dailyDistributionMatricesTruckEV.mtx"}
	    	     for i = 1 to m.length do
	    		RunMacro("HwycadLog",{"sandag_abm_master.rsc","reduce precision for:"+m[i]})
	    		RunMacro("reduce matrix precision",outputDir,m[i], precision)
	    	     end
	     end
     end

      //Construct trip tables
      if skipTripTableCreation[iteration] = "false" then do
	      RunMacro("HwycadLog",{"sandag_abm_master.rsc:","Macro - Create Auto Tables"})
	      ok = RunMacro("TCB Run Macro", 1, "Create Auto Tables",{})
	      if !ok then goto quit

    	      // reduce EE matrix precisions
    	      RunMacro("HwycadLog",{"sandag_abm_master.rsc","reduce matrix precision for externalExternalTrips.mtx"})
    	      RunMacro("reduce matrix precision",outputDir,"externalExternalTrips.mtx", precision)
      end

   end

  // Run final highway assignment
   if skipFinalHighwayAssignment = "false" then do
	   RunMacro("HwycadLog",{"sandag_abm_master.rsc:","Macro - hwy assignment"})
	   ok = RunMacro("TCB Run Macro", 1, "hwy assignment",{4,assignByVOT})
	   if !ok then goto quit
   end

   if skipFinalTransitAssignment = "false" then do
	   //Construct transit trip tables
	   RunMacro("HwycadLog",{"sandag_abm_master.rsc:","Macro - Create Transit Tables"})
	   ok = RunMacro("TCB Run Macro", 1, "Create Transit Tables",{})
	   if !ok then goto quit

	   //Run final and only transit assignment
	   RunMacro("HwycadLog",{"sandag_abm_master.rsc:","Macro - Assign Transit"})
	   ok = RunMacro("TCB Run Macro", 1, "Assign Transit",{4})
	   if !ok then goto quit
   end

   // Skim highway network based on final highway assignment
   if skipFinalHighwaySkimming = "false" then do
	   RunMacro("HwycadLog",{"sandag_abm_master.rsc:","Macro - Hwy skim all"})
	   ok = RunMacro("TCB Run Macro", 1, "Hwy skim all",{})
	   if !ok then goto quit
   end

   // Skim transit network based on final transit assignemnt
   if skipFinalTransitSkimming = "false" then do
	   RunMacro("HwycadLog",{"sandag_abm_master.rsc:","Macro - Build transit skims"})
	   ok = RunMacro("TCB Run Macro", 1, "Build transit skims",{})
	   if !ok then goto quit
   end

   //Create LUZ skims
   if skipLUZSkimCreation = "false" then do
	   RunMacro("HwycadLog",{"sandag_abm_master.rsc:","Macro - Create LUZ Skims"})
	   ok = RunMacro("TCB Run Macro", 1, "Create LUZ Skims",{})
	   if !ok then goto quit
   end

   //export TransCAD data (networks and trip tables)
   if skipDataExport = "false" then do
	   RunMacro("HwycadLog",{"sandag_abm_master.rsc:","Macro - Export TransCAD Data"})
	   ok = RunMacro("TCB Run Macro", 1, "ExportSandagData",{})
	   if !ok then goto quit

	   // export core ABM data
           runString = path+"\\bin\\DataExporter.bat "+drive+" "+path_no_drive
	   ok = RunMacro("TCB Run Command", 1, "Export core ABM data", runString)
	   if !ok then goto quit
   end

   //request data load after model run finish successfully
   if skipDataLoadRequest = "false" then do
	   runString = path+"\\bin\\DataLoadRequest.bat "+drive+path_no_drive+" "+String(max_iterations)+" "+scenarioYear+" "+sample_rate[max_iterations]
	   ok = RunMacro("TCB Run Command", 1, "Data load request", runString)
	   if !ok then goto quit
   end

   // delete trip table files in iteration sub folder if model finishes without crashing
   if skipDeleteIntermediateFiles = "false" then do
	   for iteration = startFromIteration to max_iterations-1 do
	      toDir = outputDir+"\\iter"+String(iteration-1)
	      status = RunProgram("cmd.exe /c del "+toDir+"\\auto*.mtx",)
	      status = RunProgram("cmd.exe /c del "+toDir+"\\tran*.mtx",)
	      status = RunProgram("cmd.exe /c del "+toDir+"\\nmot*.mtx",)
	      status = RunProgram("cmd.exe /c del "+toDir+"\\othr*.mtx",)
	      status = RunProgram("cmd.exe /c del "+toDir+"\\trip*.mtx",)
	   end
   end

   RunMacro("TCB Closing", ok, "False")
   return(1)
   quit:
      return(0)
EndMacro
