Macro "ExportSandagData"

    shared path_study, path, inputDir, outputDir

    RunMacro("close all")
    RunMacro("TCB Init")
    

    inputDir = path+"\\input"
    outputDir = path+"\\output"
    reportDir = path+"\\report"

    network_file = outputDir+"\\hwy.dbd"    
    
    output_network_file = reportDir + "\\hwy_tcad"
    output_transit_onoff_file = reportDir + "\\transit_onoff"
    output_transit_flow_file = reportDir + "\\transit_flow"
    output_transit_aggflow_file = reportDir + "\\transit_aggflow"
    input_route_file = inputDir + "\\trrt"
    output_route_file = reportDir + "\\trrt"
    input_stop_file = inputDir + "\\trstop"
    output_stop_file = reportDir + "\\trstop"
   
    input_hwyload_file = RunMacro("FormPath",{outputDir,"hwyload_"})    
    output_hwyload_file = RunMacro("FormPath",{reportDir,"hwyload_"})

    external_zones = {"1","2","3","4","5","6","7","8","9","10","11","12"}

    RunMacro("ExportNetworkToCsv",network_file,output_network_file)   
    RunMacro("ExportHwyloadtoCSV",input_hwyload_file,output_hwyload_file)    
    RunMacro("ExportBintoCSV",input_route_file, output_route_file) 
    RunMacro("ExportBintoCSV",input_stop_file, output_stop_file) 
    RunMacro("ExportTransitTablesToCsv",outputDir,RunMacro("BuildOnOffOptions"),output_transit_onoff_file)
    RunMacro("ExportTransitTablesToCsv",outputDir,RunMacro("BuildTransitFlowOptions"),output_transit_flow_file)
    RunMacro("ExportTransitTablesToCsv",outputDir,RunMacro("BuildAggFlowOptions"),output_transit_aggflow_file)
  
    RunMacro("G30 File Close All")
    return(1)   

EndMacro
