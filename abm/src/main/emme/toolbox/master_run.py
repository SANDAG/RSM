# //////////////////////////////////////////////////////////////////////////////
# ////                                                                       ///
# //// Copyright INRO, 2016-2017.                                            ///
# //// Rights to use and modify are granted to the                           ///
# //// San Diego Association of Governments and partner agencies.            ///
# //// This copyright notice must be preserved.                              ///
# ////                                                                       ///
# //// model/master_run.py                                                   ///
# ////                                                                       ///
# ////                                                                       ///
# ////                                                                       ///
# ////                                                                       ///
# //////////////////////////////////////////////////////////////////////////////
#
# The Master run tool is the primary method to operate the SANDAG
# travel demand model. It operates all the model components.
#
#   main_directory: Main ABM directory: directory which contains all of the
#       ABM scenario data, including this project. The default is the parent
#       directory of the current Emme project.
#   scenario_id: Scenario ID for the base imported network data. The result
#       scenarios are indexed in the next five scenarios by time period.
#    scenario_title: title to use for the scenario.
#    emmebank_title: title to use for the Emmebank (Emme database)
#    num_processors: the number of processors to use for traffic and transit
#       assignments and skims, aggregate demand models (where required) and
#       other parallelized procedures in Emme. Default is Max available - 1.
#    Properties loaded from conf/sandag_abm.properties:
#       When using the tool UI, the sandag_abm.properties file is read
#       and the values cached and the inputs below are pre-set. When the tool
#       is started button is clicked this file is written out with the
#       values specified.
#           Sample rate by iteration: three values for the sample rates for each iteration
#           Start from iteration: iteration from which to start the model run
#           Skip steps: optional checkboxes to skip model steps.
#               Note that most steps are dependent upon the results of the previous steps.
#   Select link: add select link analyses for traffic.
#       See the Select link analysis section under the Traffic assignment tool.
#
#   Also reads and processes the per-scenario
#    vehicle_class_availability.csv (optional): 0 or 1 indicators by vehicle class and specified facilities to indicate availability
#
# Script example:
"""
import inro.modeller as _m
import os
modeller = _m.Modeller()
desktop = modeller.desktop

master_run = modeller.tool("sandag.master_run")
main_directory = os.path.dirname(os.path.dirname(desktop.project_path()))
scenario_id = 100
scenario_title = "Base 2015 scenario"
emmebank_title = "Base 2015 with updated landuse"
num_processors = "MAX-1"
master_run(main_directory, scenario_id, scenario_title, emmebank_title, num_processors)
"""

TOOLBOX_ORDER = 1
VIRUTALENV_PATH = "C:\\python_virtualenv\\abm14_2_0"

import inro.modeller as _m
import inro.emme.database.emmebank as _eb

import traceback as _traceback
import glob as _glob
import subprocess as _subprocess
import ctypes as _ctypes
import json as _json
import shutil as _shutil
import tempfile as _tempfile
from copy import deepcopy as _copy
from collections import defaultdict as _defaultdict
import time as _time
import socket as _socket
import sys
import os

import pandas as pd
import numpy as np
import csv
import datetime
import pyodbc
import win32com.client as win32

import pandas as pd
from scipy.spatial import distance

_join = os.path.join
_dir = os.path.dirname
_norm = os.path.normpath

gen_utils = _m.Modeller().module("sandag.utilities.general")
dem_utils = _m.Modeller().module("sandag.utilities.demand")
props_utils = _m.Modeller().module("sandag.utilities.properties")


class MasterRun(props_utils.PropertiesSetter, _m.Tool(), gen_utils.Snapshot):
    main_directory = _m.Attribute(unicode)
    scenario_id = _m.Attribute(int)
    scenario_title = _m.Attribute(unicode)
    emmebank_title = _m.Attribute(unicode)
    num_processors = _m.Attribute(str)
    select_link = _m.Attribute(unicode)
    username = _m.Attribute(unicode)
    password = _m.Attribute(unicode)

    properties_path = _m.Attribute(unicode)

    tool_run_msg = ""

    def __init__(self):
        super(MasterRun, self).__init__()
        project_dir = _dir(_m.Modeller().desktop.project.path)
        self.main_directory = _dir(project_dir)
        self.properties_path = _join(_dir(project_dir), "conf", "sandag_abm.properties")
        self.scenario_id = 100
        self.scenario_title = ""
        self.emmebank_title = ""
        self.num_processors = "MAX-1"
        self.select_link = '[]'
        self.username = os.environ.get("USERNAME")
        self.attributes = [
            "main_directory", "scenario_id", "scenario_title", "emmebank_title",
            "num_processors", "select_link"
        ]
        self._log_level = "ENABLED"
        self.LOCAL_ROOT = "C:\\abm_runs"

    def page(self):
        self.load_properties()
        pb = _m.ToolPageBuilder(self)
        pb.title = "Master run ABM"
        pb.description = """Runs the SANDAG ABM, assignments, and other demand model tools."""
        pb.branding_text = "- SANDAG - Model"
        tool_proxy_tag = pb.tool_proxy_tag

        if self.tool_run_msg != "":
            pb.tool_run_status(self.tool_run_msg_status)

        pb.add_select_file('main_directory', 'directory',
                           title='Select main ABM directory', note='')
        pb.add_text_box('scenario_id', title="Scenario ID:")
        pb.add_text_box('scenario_title', title="Scenario title:", size=80)
        pb.add_text_box('emmebank_title', title="Emmebank title:", size=60)
        dem_utils.add_select_processors("num_processors", pb, self)

        # username and password input for distributed assignment
        # username also used in the folder name for the local drive operation
        pb.add_html('''
<div class="t_element">
    <div class="t_local_title">Credentials for remote run</div>
    <div>
        <strong>Username:</strong>
        <input type="text" id="username" size="20" class="-inro-modeller"
                data-ref="parent.%(tool_proxy_tag)s.username"></input>
        <strong>Password:</strong>
        <input type="password" size="20" id="password" class="-inro-modeller"
                data-ref="parent.%(tool_proxy_tag)s.password"></input>
    </div>
    <div class="t_after_widget">
    Note: required for running distributed traffic assignments using PsExec.
    <br>
    Distributed / single node modes are configured in "config/server-config.csv".
    <br> The username is also used for the folder name when running on the local drive.
    </div>
</div>''' % {"tool_proxy_tag": tool_proxy_tag})

        # defined in properties utilities
        self.add_properties_interface(pb, disclosure=True)
        # redirect properties file after browse of main_directory
        pb.add_html("""
<script>
    $(document).ready( function ()
    {
        var tool = new inro.modeller.util.Proxy(%(tool_proxy_tag)s) ;
        $("#main_directory").bind('change', function()    {
            var path = $(this).val();
            tool.properties_path = path + "/conf/sandag_abm.properties";
            tool.load_properties();
            $("input:checkbox").each(function() {
                $(this).prop('checked', tool.get_value($(this).prop('id')) );
            });
            $("#startFromIteration").prop('value', tool.startFromIteration);
            $("#sample_rates").prop('value', tool.sample_rates);
        });
   });
</script>""" % {"tool_proxy_tag": tool_proxy_tag})

        traffic_assign = _m.Modeller().tool("sandag.assignment.traffic_assignment")
        traffic_assign._add_select_link_interface(pb)

        return pb.render()

    def run(self):
        self.tool_run_msg = ""
        try:
            self.save_properties()
            self(self.main_directory, self.scenario_id, self.scenario_title, self.emmebank_title,
                 self.num_processors, self.select_link, username=self.username, password=self.password)
            run_msg = "Model run complete"
            self.tool_run_msg = _m.PageBuilder.format_info(run_msg, escape=False)
        except Exception as error:
            self.tool_run_msg = _m.PageBuilder.format_exception(error, _traceback.format_exc())

            raise

    @_m.method(return_type=_m.UnicodeType)
    def tool_run_msg_status(self):
        return self.tool_run_msg

    @_m.logbook_trace("Master run model", save_arguments=True)
    def __call__(self, main_directory, scenario_id, scenario_title, emmebank_title, num_processors,
                 select_link=None, periods=["EA", "AM", "MD", "PM", "EV"], username=None, password=None):
        attributes = {
            "main_directory": main_directory,
            "scenario_id": scenario_id,
            "scenario_title": scenario_title,
            "emmebank_title": emmebank_title,
            "num_processors": num_processors,
            "select_link": select_link,
            "periods": periods,
            "username": username,
        }
        gen_utils.log_snapshot("Master run model", str(self), attributes)

        modeller = _m.Modeller()
        # Checking that the virtualenv path is set and the folder is installed
        if not os.path.exists(VIRUTALENV_PATH):
            raise Exception("Python virtual environment not installed at expected location %s" % VIRUTALENV_PATH)
        venv_path = os.environ.get("PYTHON_VIRTUALENV")
        rsm_venv_path = os.environ.get("RSM_PYTHON_VIRTUALENV")
        rsm_script_path = os.environ.get("RSM_SCRIPT_DIR")
        rsm_python2_venv_path = os.environ.get("RSM_PYTHON2_VIRTUALENV")
        if not venv_path:
            raise Exception("Environment variable PYTHON_VIRTUALENV not set, start Emme from 'start_emme_with_virtualenv.bat'")
        if not venv_path == VIRUTALENV_PATH:
            raise Exception("PYTHON_VIRTUALENV is not the expected value (%s instead of %s)" % (venv_path, VIRUTALENV_PATH))
        venv_path_found = False
        for path in sys.path:
            if VIRUTALENV_PATH in path:
                venv_path_found = True
                break
        if not venv_path_found:
            raise Exception("Python virtual environment not found in system path %s" % VIRUTALENV_PATH)
        copy_scenario = modeller.tool("inro.emme.data.scenario.copy_scenario")
        run4Ds = modeller.tool("sandag.import.run4Ds")
        import_network = modeller.tool("sandag.import.import_network")
        input_checker = modeller.tool("sandag.import.input_checker")
        init_transit_db = modeller.tool("sandag.initialize.initialize_transit_database")
        init_matrices = modeller.tool("sandag.initialize.initialize_matrices")
        import_demand = modeller.tool("sandag.import.import_seed_demand")
        build_transit_scen = modeller.tool("sandag.assignment.build_transit_scenario")
        transit_assign = modeller.tool("sandag.assignment.transit_assignment")
        run_truck = modeller.tool("sandag.model.truck.run_truck_model")
        external_internal = modeller.tool("sandag.model.external_internal")
        external_external = modeller.tool("sandag.model.external_external")
        import_auto_demand = modeller.tool("sandag.import.import_auto_demand")
        import_transit_demand = modeller.tool("sandag.import.import_transit_demand")
        export_transit_skims = modeller.tool("sandag.export.export_transit_skims")
        export_for_transponder = modeller.tool("sandag.export.export_for_transponder")
        export_network_data = modeller.tool("sandag.export.export_data_loader_network")
        export_matrix_data = modeller.tool("sandag.export.export_data_loader_matrices")
        export_tap_adjacent_lines = modeller.tool("sandag.export.export_tap_adjacent_lines")
        export_for_commercial_vehicle = modeller.tool("sandag.export.export_for_commercial_vehicle")
        validation = modeller.tool("sandag.validation.validation")
        file_manager = modeller.tool("sandag.utilities.file_manager")
        utils = modeller.module('sandag.utilities.demand')
        load_properties = modeller.tool('sandag.utilities.properties')
        run_summary = modeller.tool("sandag.utilities.run_summary")
        emmebank_aggregator = modeller.tool("sandag.utilities.databank_aggregator")

        self.username = username
        self.password = password

        props = load_properties(_join(main_directory, "conf", "sandag_abm.properties"))
        props.set_year_specific_properties(_join(main_directory, "input", "parametersByYears.csv"))
        props.set_year_specific_properties(_join(main_directory, "input", "filesByYears.csv"))
        props.save()
        # Log current state of props file for debugging of UI / file sync issues
        attributes = dict((name, props["RunModel." + name]) for name in self._run_model_names)
        _m.logbook_write("SANDAG properties file", attributes=attributes)
        if self._properties:  # Tool has been called via the UI
            # Compare UI values and file values to make sure they are the same
            error_text = ("Different value found in sandag_abm.properties than specified in UI for '%s'. "
                          "Close sandag_abm.properties if open in any text editor, check UI and re-run.")
            for name in self._run_model_names:
                if getattr(self, name) != props["RunModel." + name]:
                    raise Exception(error_text % name)

        scenarioYear = str(props["scenarioYear"])
        startFromIteration = props["RunModel.startFromIteration"]
        precision = props["RunModel.MatrixPrecision"]
        minSpaceOnC = props["RunModel.minSpaceOnC"]
        sample_rate = props["sample_rates"]
        end_iteration = len(sample_rate)
        scale_factor = props["cvm.scale_factor"]
        visualizer_reference_path = props["visualizer.reference.path"]
        visualizer_output_file = props["visualizer.output"]
        visualizer_reference_label = props["visualizer.reference.label"]
        visualizer_build_label = props["visualizer.build.label"]
        mgraInputFile = props["mgra.socec.file"]

        period_ids = list(enumerate(periods, start=int(scenario_id) + 1))

        useLocalDrive = props["RunModel.useLocalDrive"]

        skip4Ds = props["RunModel.skip4Ds"]
        skipInputChecker = props["RunModel.skipInputChecker"]
        skipInitialization = props["RunModel.skipInitialization"]
        deleteAllMatrices = props["RunModel.deleteAllMatrices"]
        skipCopyWarmupTripTables = props["RunModel.skipCopyWarmupTripTables"]
        skipCopyBikeLogsum = props["RunModel.skipCopyBikeLogsum"]
        skipCopyWalkImpedance = props["RunModel.skipCopyWalkImpedance"]
        skipWalkLogsums = props["RunModel.skipWalkLogsums"]
        skipBikeLogsums = props["RunModel.skipBikeLogsums"]
        skipBuildNetwork = props["RunModel.skipBuildNetwork"]
        skipHighwayAssignment = props["RunModel.skipHighwayAssignment"]
        skipTransitSkimming = props["RunModel.skipTransitSkimming"]
        skipTransponderExport = props["RunModel.skipTransponderExport"]
        skipCoreABM = props["RunModel.skipCoreABM"]
        skipOtherSimulateModel = props["RunModel.skipOtherSimulateModel"]
        skipMAASModel = props["RunModel.skipMAASModel"]
        skipCTM = props["RunModel.skipCTM"]
        skipEI = props["RunModel.skipEI"]
        skipExternal = props["RunModel.skipExternalExternal"]
        skipTruck = props["RunModel.skipTruck"]
        skipTripTableCreation = props["RunModel.skipTripTableCreation"]
        skipFinalHighwayAssignment = props["RunModel.skipFinalHighwayAssignment"]
        skipFinalHighwayAssignmentStochastic = props["RunModel.skipFinalHighwayAssignmentStochastic"]
        if skipFinalHighwayAssignmentStochastic == True:
        	makeFinalHighwayAssignmentStochastic = False
        else:
        	makeFinalHighwayAssignmentStochastic = True
        skipFinalTransitAssignment = props["RunModel.skipFinalTransitAssignment"]
        skipVisualizer = props["RunModel.skipVisualizer"]
        skipDataExport = props["RunModel.skipDataExport"]
        skipDataLoadRequest = props["RunModel.skipDataLoadRequest"]
        skipDeleteIntermediateFiles = props["RunModel.skipDeleteIntermediateFiles"]
        skipTransitShed = props["RunModel.skipTransitShed"]
        transitShedThreshold = props["transitShed.threshold"]
        transitShedTOD = props["transitShed.TOD"]
        
        #RSM Settings
        run_rsm_setup = int(props["run.rsm.setup"])
        run_rsm = int(props["run.rsm"])
        run_zone_aggregator = int(props["run.rsm.zone.aggregator"])
        num_rsm_zones = props["rsm.zones"]
        num_external_zones = props["external.zones"]
        rsm_cc_start_id = props["rsm.centroid.connector.start.id"]
        orig_full_model_dir = props["full.modelrun.dir"]
        rsm_baseline_run_dir = props["rsm.baseline.run.dir"]
        taz_crosswalk_file = props["taz.to.cluster.crosswalk.file"]
        mgra_crosswalk_file = props["mgra.to.cluster.crosswalk.file"]
        cluster_zone_file = props["cluster.zone.centroid.file"]
        
        run_rsm_sampler = int(props["run.rsm.sampling"])
        run_rsm_assembler = int(props["run.rsm.assembler"])
        rsm_default_sample_rate = props["rsm.default.sampling.rate"]

        #check if visualizer.reference.path is valid in filesbyyears.csv
        if not os.path.exists(visualizer_reference_path):
            raise Exception("Visualizer reference %s does not exist. Check filesbyyears.csv." %(visualizer_reference_path)) 
            
        if useLocalDrive:
            folder_name = os.path.basename(main_directory)
            if not os.path.exists(_join(self.LOCAL_ROOT, username, folder_name, "report")): # check free space only if it is a new run
                self.check_free_space(minSpaceOnC)
            # if initialization copy ALL files from remote
            # else check file meta data and copy those that have changed
            initialize = (skipInitialization == False and startFromIteration == 1)
            local_directory = file_manager(
                "DOWNLOAD", main_directory, username, scenario_id, initialize=initialize)
            self._path = local_directory
        else:
            self._path = main_directory

        drive, path_no_drive = os.path.splitdrive(self._path)
        path_forward_slash = path_no_drive.replace("\\", "/")
        input_dir = _join(self._path, "input")
        input_truck_dir = _join(self._path, "input_truck")
        output_dir = _join(self._path, "output")
        validation_dir = _join(self._path, "analysis/validation")
        main_emmebank = _eb.Emmebank(_join(self._path, "emme_project", "Database", "emmebank"))
        if emmebank_title:
            main_emmebank.title = emmebank_title
        external_zones = "1-12"

        travel_modes = ["auto", "tran", "nmot", "othr"]
        core_abm_files = ["Trips*.omx"] #, "InternalExternalTrips*.omx"]
        core_abm_files = [mode + name for name in core_abm_files for mode in travel_modes]
        smm_abm_files = ["AirportTrips*.omx", "CrossBorderTrips*.omx", "VisitorTrips*.omx"]
        smm_abm_files = [mode + name for name in smm_abm_files for mode in travel_modes]
        maas_abm_files = ["EmptyAVTrips.omx", "TNCVehicleTrips*.omx"]

        relative_gap = props["convergence"]
        max_assign_iterations = 1000
        mgra_lu_input_file = props["mgra.socec.file"]

        with _m.logbook_trace("Setup and initialization"):
            self.set_global_logbook_level(props)

            # Swap Server Configurations
            self.run_proc("serverswap.bat", [drive, path_no_drive, path_forward_slash], "Run ServerSwap")
            self.check_for_fatal(_join(self._path, "logFiles", "serverswap.log"),
                                 "ServerSwap failed! Open logFiles/serverswap.log for details.")
            self.run_proc("checkAtTransitNetworkConsistency.cmd", [drive, path_forward_slash],
                          "Checking if AT and Transit Networks are consistent")
            self.check_for_fatal(_join(self._path, "logFiles", "AtTransitCheck_event.log"),
                                 "AT and Transit network consistency checking failed! Open AtTransitCheck_event.log for details.")
            
            # check few rsm setup properties to validate that the
            # user specified properties for the RSM are acceptable
            if run_rsm == 1:
                # if sampler is on then assembler can not be off
                if run_rsm_sampler == 1 and run_rsm_assembler == 0:
                    raise Exception("If Sampler is turned on then Assembler cannot be turned off. run.rsm.sampling = 1 and run.rsm.assembler = 0 is not allowed option")
                
                # if assembler is off then scale factor (1/default_sample_rate) should be integer
                if run_rsm_assembler == 0:
                    scale_factor = 1.0/rsm_default_sample_rate
                    if not scale_factor.is_integer():
                        raise Exception("If Assembler is turned off, default sample rate should be such that 1/(sample rate) is integer value")
            
            if run_rsm_setup == 1: 
            
                if run_zone_aggregator == 1:
                    self.run_proc(
                        "runRSMZoneAggregator.cmd", 
                        [main_directory, rsm_venv_path, rsm_script_path, orig_full_model_dir, num_rsm_zones, num_external_zones],
                        "Zone Aggregator")
                else:
                    _shutil.copy(_join(rsm_baseline_run_dir, mgra_lu_input_file), _join(main_directory, mgra_lu_input_file))
                    _shutil.copy(_join(rsm_baseline_run_dir, taz_crosswalk_file), _join(main_directory, taz_crosswalk_file))
                    _shutil.copy(_join(rsm_baseline_run_dir, mgra_crosswalk_file), _join(main_directory, mgra_crosswalk_file))
                    _shutil.copy(_join(rsm_baseline_run_dir, cluster_zone_file), _join(main_directory, cluster_zone_file))

                self.run_proc(
                "runRSMInputAggregator.cmd", 
                [main_directory, rsm_venv_path, rsm_script_path, orig_full_model_dir, num_rsm_zones, num_external_zones], 
                "Input Files Aggregator")
                
                self.run_proc(
                "runRSMTripMatrixAggregator.cmd", 
                [main_directory, rsm_python2_venv_path, orig_full_model_dir, rsm_script_path, taz_crosswalk_file], 
                "Input Trip Matrix files Aggregator")


            if startFromIteration == 1:  # only run the setup / init steps if starting from iteration 1
                if not skipWalkLogsums:
                    self.run_proc("runSandagWalkLogsums.cmd", [drive, path_forward_slash],
                                  "Walk - create AT logsums and impedances")
                if not skipCopyWalkImpedance:
                    self.copy_files(["walkMgraEquivMinutes.csv", "walkMgraTapEquivMinutes.csv", "microMgraEquivMinutes.csv", "microMgraTapEquivMinutes.csv"],
                                    input_dir, output_dir)

                if not skip4Ds:
                    run4Ds(path=self._path, int_radius=0.65, ref_path=visualizer_reference_path)


                mgraFile = 'mgra13_based_input' + str(scenarioYear) + '.csv'
                self.complete_work(scenarioYear, input_dir, output_dir, mgraFile, "walkMgraEquivMinutes.csv")
                
                
                if not skipBuildNetwork:
                    base_scenario = import_network(
                        source=input_dir,
                        merged_scenario_id=scenario_id,
                        title=scenario_title,
                        data_table_name=scenarioYear,
                        overwrite=True,
                        emmebank=main_emmebank)

                    if "modify_network.py" in os.listdir(os.getcwd()):
                        try:
                            with _m.logbook_trace("Modify network script"):
                                import modify_network
                                reload(modify_network)
                                modify_network.run(base_scenario)
                        except ImportError as e:
                            pass
                    
                    #########################################  added on 0629
                    
                    #TODO-AK: move this to a separate function
                    
                    taz_crosswalk = pd.read_csv(os.path.join(main_directory, taz_crosswalk_file), index_col = 0)
                    taz_crosswalk = taz_crosswalk['cluster_id'].to_dict()

                    emmebank = _m.Modeller().emmebank
                    scenario = emmebank.scenario(base_scenario)
                    hwy_network = scenario.get_network()


                    centroid_nodes = []
                    exclude_nodes = []

                    for node in range(1,13,1):
                        exclude_nodes.append(hwy_network.node(node))

                    for node in hwy_network.centroids():
                        if not node in exclude_nodes:
                            centroid_nodes.append(node)

                    i_nodes = []
                    j_nodes = []
                    data1 = []
                    length = []
                    links = []

                    for link in hwy_network.links():
                        if link.i_node in centroid_nodes:
                            links.append(link)
                            i_nodes.append(int(link.i_node))
                            j_nodes.append(int(link.j_node))
                            data1.append(link.data1)
                            length.append(link.length)

                    df = pd.DataFrame({'links' : links, 'i_nodes' : i_nodes, 'j_nodes': j_nodes, 'ul1_org': data1, 'length_org':length})
                    df['i_nodes_new'] = df['i_nodes'].map(taz_crosswalk)
                    
                    #get XY of existing centroids
                    j_nodes_list = df['j_nodes'].unique()
                    j_nodes_list = [hwy_network.node(x) for x in j_nodes_list]

                    j_nodes = []
                    j_x = []
                    j_y = []
                    for nodes in hwy_network.nodes():
                        if nodes in j_nodes_list:
                            j_nodes.append(nodes)
                            j_x.append(nodes.x)
                            j_y.append(nodes.y)

                    j_nodes_XY = pd.DataFrame({'j_nodes' : j_nodes, 'j_x' : j_x, 'j_y': j_y})
                    j_nodes_XY['j_nodes'] = [int(x) for x in j_nodes_XY['j_nodes']]
                    df = pd.merge(df, j_nodes_XY, on = 'j_nodes', how = 'left')

                    agg_node_coords = pd.read_csv(os.path.join(main_directory, cluster_zone_file))
                    df = pd.merge(df, agg_node_coords, left_on = 'i_nodes_new', right_on = 'cluster_id', how = 'left')
                    df = df.drop(columns = 'cluster_id')
                    df = df.rename(columns = {'centroid_x' : 'i_new_x', 'centroid_y' : 'i_new_y'})

                    i_coords = zip(df['j_x'], df['j_y'])
                    j_coords = zip(df['i_new_x'], df['i_new_y'])

                    df['length'] = [distance.euclidean(i, j)/5280.0 for i,j in zip(i_coords, j_coords)]

                    #delete all the existing centroid nodes
                    for index,row in df.iterrows():
                        if hwy_network.node(row['i_nodes']):
                            hwy_network.delete_node(row['i_nodes'], True)  

                    # create new nodes (centroids of clusters)
                    for index,row in agg_node_coords.iterrows():
                        new_node = hwy_network.create_node(row['cluster_id'], is_centroid = True)
                        new_node.x = int(row['centroid_x'])
                        new_node.y = int(row['centroid_y'])

                    df['type'] = 10
                    df['num_lanes'] = 1
                    df['vdf'] = 11
                    df['ul3'] = 999999

                    final_df = df[["i_nodes_new", "j_nodes", "length", "type", "num_lanes", "vdf", "ul3"]]
                    final_df = final_df.drop_duplicates()
                    final_df = final_df.reset_index(drop=True)
                    final_df['type'] = final_df['type'].astype("int") 
                    
                    cc_id = rsm_cc_start_id

                    # create new links
                    for index,row in final_df.iterrows():
                        
                        link_ij = hwy_network.create_link(row['i_nodes_new'], row['j_nodes'], 
                                            modes = ["d", "h", "H", "i","I","s", "S", "v", "V", "m", "M", "t", "T"])
                        link_ij.length = row['length']
                        link_ij.type = row['type'].astype("int")
                        link_ij.num_lanes = row['num_lanes'].astype("int")
                        link_ij.volume_delay_func = row['vdf'].astype("int")
                        link_ij.data3 = row['ul3'].astype("int")
                        link_ij['@lane_ea'] = 1 # had to do this as they are being replaced in highway assignment by the values in these columns
                        link_ij['@lane_am'] = 1
                        link_ij['@lane_md'] = 1
                        link_ij['@lane_pm'] = 1
                        link_ij['@lane_ev'] = 1
                        
                        link_ij['@capacity_link_ea'] = 999999 
                        link_ij['@capacity_link_am'] = 999999 
                        link_ij['@capacity_link_md'] = 999999 
                        link_ij['@capacity_link_pm'] = 999999 
                        link_ij['@capacity_link_ev'] = 999999 
                        
                        link_ij['@capacity_inter_ea'] = 999999 
                        link_ij['@capacity_inter_am'] = 999999 
                        link_ij['@capacity_inter_md'] = 999999 
                        link_ij['@capacity_inter_pm'] = 999999 
                        link_ij['@capacity_inter_ev'] = 999999
                        
                        link_ij['@tcov_id'] = cc_id
                        
                        if(row['length'] > 0.85):
                            link_ij['@time_link_ea'] = row['length'] * 60 / 20
                            link_ij['@time_link_am'] = row['length'] * 60 / 20 
                            link_ij['@time_link_md'] = row['length'] * 60 / 20
                            link_ij['@time_link_pm'] = row['length'] * 60 / 20
                            link_ij['@time_link_ev'] = row['length'] * 60 / 20 
                        else:
                            link_ij['@time_link_ea'] = row['length'] * 60 / 45
                            link_ij['@time_link_am'] = row['length'] * 60 / 45 
                            link_ij['@time_link_md'] = row['length'] * 60 / 45 
                            link_ij['@time_link_pm'] = row['length'] * 60 / 45 
                            link_ij['@time_link_ev'] = row['length'] * 60 / 45

                       
                        link_ji = hwy_network.create_link(row['j_nodes'], row['i_nodes_new'], 
                                            modes = ["d", "h", "H", "i","I","s", "S", "v", "V", "m", "M", "t", "T"])
                        link_ji.length = row['length']
                        link_ji.type = row['type'].astype("int")
                        link_ji.num_lanes = row['num_lanes'].astype("int")
                        link_ji.volume_delay_func = row['vdf'].astype("int")
                        link_ji.data3 = row['ul3'].astype("int")
                        link_ji['@lane_ea'] = 1 # had to do this as they are being replaced in highway assignment by the values in these columns
                        link_ji['@lane_am'] = 1
                        link_ji['@lane_md'] = 1
                        link_ji['@lane_pm'] = 1
                        link_ji['@lane_ev'] = 1
                        
                        link_ji['@capacity_link_ea'] = 999999  
                        link_ji['@capacity_link_am'] = 999999 
                        link_ji['@capacity_link_md'] = 999999 
                        link_ji['@capacity_link_pm'] = 999999 
                        link_ji['@capacity_link_ev'] = 999999 
                        
                        link_ji['@capacity_inter_ea'] = 999999 
                        link_ji['@capacity_inter_am'] = 999999 
                        link_ji['@capacity_inter_md'] = 999999 
                        link_ji['@capacity_inter_pm'] = 999999 
                        link_ji['@capacity_inter_ev'] = 999999
                        
                        link_ji['@tcov_id'] = cc_id + 1
                        
                        if(row['length'] > 0.85):
                            link_ji['@time_link_ea'] = row['length'] * 60 / 20
                            link_ji['@time_link_am'] = row['length'] * 60 / 20 
                            link_ji['@time_link_md'] = row['length'] * 60 / 20
                            link_ji['@time_link_pm'] = row['length'] * 60 / 20
                            link_ji['@time_link_ev'] = row['length'] * 60 / 20 
                        else:
                            link_ji['@time_link_ea'] = row['length'] * 60 / 45
                            link_ji['@time_link_am'] = row['length'] * 60 / 45 
                            link_ji['@time_link_md'] = row['length'] * 60 / 45 
                            link_ji['@time_link_pm'] = row['length'] * 60 / 45 
                            link_ji['@time_link_ev'] = row['length'] * 60 / 45
                            
                        cc_id = cc_id + 2
                        
                    scenario.publish_network(hwy_network)

                    #############################################

                    if not skipInputChecker:
                        input_checker(path=self._path)

                    export_tap_adjacent_lines(_join(output_dir, "tapLines.csv"), base_scenario)
                    # parse vehicle availablility file by time-of-day
                    availability_file = "vehicle_class_availability.csv"
                    availabilities = self.parse_availability_file(_join(input_dir, availability_file), periods)
                    # initialize per time-period scenarios
                    for number, period in period_ids:
                        title = "%s - %s assign" % (base_scenario.title, period)
                        # copy_scenario(base_scenario, number, title, overwrite=True)
                        _m.logbook_write(
                            name="Copy scenario %s to %s" % (base_scenario.number, number),
                            attributes={
                                'from_scenario': base_scenario.number,
                                'scenario_id': number,
                                'overwrite': True,
                                'scenario_title': title
                            }
                        )
                        if main_emmebank.scenario(number):
                            main_emmebank.delete_scenario(number)
                        scenario = main_emmebank.copy_scenario(base_scenario.number, number)
                        scenario.title = title
                        # Apply availabilities by facility and vehicle class to this time period
                        self.apply_availabilities(period, scenario, availabilities)
                else:
                    base_scenario = main_emmebank.scenario(scenario_id)

                if not skipInitialization:
                    # initialize traffic demand, skims, truck, CV, EI, EE matrices
                    traffic_components = [
                        "traffic_skims",
                        "truck_model",
                        "external_internal_model", "external_external_model"]
                    if not skipCopyWarmupTripTables:
                        traffic_components.append("traffic_demand")
                    init_matrices(traffic_components, periods, base_scenario, deleteAllMatrices)

                    transit_scenario = init_transit_db(base_scenario, add_database=not useLocalDrive)
                    transit_emmebank = transit_scenario.emmebank
                    transit_components = ["transit_skims"]
                    if not skipCopyWarmupTripTables:
                        transit_components.append("transit_demand")
                    init_matrices(transit_components, periods, transit_scenario, deleteAllMatrices)
                else:
                    transit_emmebank = _eb.Emmebank(_join(self._path, "emme_project", "Database_transit", "emmebank"))
                    transit_scenario = transit_emmebank.scenario(base_scenario.number)

                if not skipCopyWarmupTripTables:
                    # import seed auto demand and seed truck demand
                    for period in periods:
                        omx_file = _join(input_dir, "trip_%s.omx" % period)
                        import_demand(omx_file, "AUTO", period, base_scenario)
                        import_demand(omx_file, "TRUCK", period, base_scenario)

                if not skipBikeLogsums:
                    self.run_proc("runSandagBikeLogsums.cmd", [drive, path_forward_slash],
                                  "Bike - create AT logsums and impedances")
                if not skipCopyBikeLogsum:
                    self.copy_files(["bikeMgraLogsum.csv", "bikeTazLogsum.csv"], input_dir, output_dir)

            else:
                base_scenario = main_emmebank.scenario(scenario_id)
                transit_emmebank = _eb.Emmebank(_join(self._path, "emme_project", "Database_transit", "emmebank"))
                transit_scenario = transit_emmebank.scenario(base_scenario.number)

            # Check that setup files were generated
            self.run_proc("CheckOutput.bat", [drive + path_no_drive, 'Setup'], "Check for outputs")
            
            if run_rsm_setup == 1:
                # this is to aggregate the EE, EI and Truck matrices from emme databank
                emmebank_aggregator(main_directory, orig_full_model_dir, taz_crosswalk_file)

        # Note: iteration indexes from 0, msa_iteration indexes from 1
        for iteration in range(startFromIteration - 1, end_iteration):
            msa_iteration = iteration + 1
            with _m.logbook_trace("Iteration %s" % msa_iteration):
            
             
                if not skipCoreABM[iteration] or not skipOtherSimulateModel[iteration] or not skipMAASModel[iteration]:
                    self.run_proc("runMtxMgr.cmd", [drive, drive + path_no_drive], "Start matrix manager")
                    self.run_proc("runHhMgr.cmd", [drive, drive + path_no_drive], "Start Hh manager")

                if not skipHighwayAssignment[iteration]:
                    # run traffic assignment
                    # export traffic skims
                    with _m.logbook_trace("Traffic assignment and skims"):
                        self.run_traffic_assignments(
                            base_scenario, period_ids, msa_iteration, relative_gap,
                            max_assign_iterations, num_processors)
                    self.run_proc("CreateD2TAccessFile.bat", [drive, path_forward_slash],
                                  "Create drive to transit access file", capture_output=True)

                if not skipTransitSkimming[iteration]:
                    # run transit assignment
                    # export transit skims
                    with _m.logbook_trace("Transit assignments and skims"):
                        for number, period in period_ids:
                            src_period_scenario = main_emmebank.scenario(number)
                            transit_assign_scen = build_transit_scen(
                                period=period, base_scenario=src_period_scenario,
                                transit_emmebank=transit_emmebank,
                                scenario_id=src_period_scenario.id,
                                scenario_title="%s %s transit assign" % (base_scenario.title, period),
                                data_table_name=scenarioYear, overwrite=True)
                            transit_assign(period, transit_assign_scen, data_table_name=scenarioYear,
                                           skims_only=True, num_processors=num_processors)

                        omx_file = _join(output_dir, "transit_skims.omx")
                        export_transit_skims(omx_file, periods, transit_scenario)

                if not skipTransponderExport[iteration]:
                    am_scenario = main_emmebank.scenario(base_scenario.number + 2)
                    export_for_transponder(output_dir, num_processors, am_scenario)

                # For each step move trip matrices so run will stop if ctramp model
                # doesn't produced csv/omx files for assignment
                # also needed as CT-RAMP does not overwrite existing files
                if not skipCoreABM[iteration]:
                    self.remove_prev_iter_files(core_abm_files, output_dir, iteration)
                    
                    if run_rsm == 1:
                        #set rsm specific properties
                        self.run_proc(
                        "runRSMSetupUpdate.cmd", 
                        [main_directory, rsm_venv_path, rsm_script_path, msa_iteration], 
                        "Update Properties", capture_output=True)                  
                        
                        #run accessibility (stand-alone) outside of the ABM call
                        self.run_proc(
                        "runRSMAccessibility.cmd",
                        [drive, drive + path_forward_slash, sample_rate[iteration], msa_iteration],
                        "Create Accessibility", capture_output=True)
                        
                        #run RSM Sampler 
                        self.run_proc(
                        "runRSMSampler.cmd", 
                        [main_directory, rsm_venv_path, rsm_script_path, msa_iteration], 
                        "RSM Sampler", capture_output=True)
                        
                        self.run_proc(
                        "runRSMSetProperty.cmd", 
                        [main_directory, rsm_venv_path, rsm_script_path, 'acc.read.input.file', 'true'],
                        "Set Property", capture_output=True)     

                        #run CT-RAMP
                        self.run_proc(
                        "runRSMSandagAbm.cmd",
                        [drive, drive + path_forward_slash, sample_rate[iteration], msa_iteration],
                        "ABM CT-RAMP", capture_output=True)
                        
                        #run RSM Assembler
                        self.run_proc(
                        "runRSMAssembler.cmd", 
                        [main_directory, rsm_venv_path,  rsm_script_path, orig_full_model_dir, msa_iteration], 
                        "RSM Assembler", capture_output=True)
                        
                        #run build trip tables
                        self.run_proc(
                        "runRSMSandagAbmTripTables.cmd",
                        [drive, drive + path_forward_slash, sample_rate[iteration], msa_iteration],
                        "Build Trip Tables", capture_output=True)
                        
                    else:
                    
                        self.run_proc(
                        "runSandagAbm_SDRM.cmd",
                        [drive, drive + path_forward_slash, sample_rate[iteration], msa_iteration],
                        "Java-Run CT-RAMP", capture_output=True)

                if not skipOtherSimulateModel[iteration]:
                    self.remove_prev_iter_files(smm_abm_files, output_dir, iteration)
                    self.run_proc(
                        "runSandagAbm_SMM.cmd",
                        [drive, drive + path_forward_slash, sample_rate[iteration], msa_iteration],
                        "Java-Run airport model, visitor model, cross-border model", capture_output=True)

                if not skipMAASModel[iteration]:
                    self.remove_prev_iter_files(maas_abm_files, output_dir, iteration)
                    self.run_proc(
                        "runSandagAbm_MAAS.cmd",
                        [drive, drive + path_forward_slash, sample_rate[iteration], msa_iteration],
                        "Java-Run AV allocation model and TNC routing model", capture_output=True)

                if not skipCTM[iteration]:
                    export_for_commercial_vehicle(output_dir, base_scenario)
                    self.run_proc(
                        "cvm.bat",
                        [drive, path_no_drive, path_forward_slash, scale_factor, mgra_lu_input_file,
                         "tazcentroids_cvm.csv"],
                        "Commercial vehicle model", capture_output=True)
                if msa_iteration == startFromIteration:
                    external_zones = "1-12"
                    if not skipTruck[iteration]:
                        # run truck model (generate truck trips)
                        run_truck(True, input_dir, input_truck_dir, num_processors, base_scenario)
                    # run EI model "US to SD External Trip Model"
                    if not skipEI[iteration]:
                        external_internal(input_dir, base_scenario)
                    # run EE model
                    if not skipExternal[iteration]:
                        external_external(input_dir, external_zones, base_scenario)

                # import demand from all sub-market models from CT-RAMP and
                #       add CV trips to auto demand
                #       add EE and EI trips to auto demand
                if not skipTripTableCreation[iteration]:
                    import_auto_demand(output_dir, external_zones, num_processors, base_scenario)

        if not skipFinalHighwayAssignment:
            with _m.logbook_trace("Final traffic assignments"):
                # Final iteration is assignment only, no skims
                final_iteration = 4
                self.run_traffic_assignments(
                    base_scenario, period_ids, final_iteration, relative_gap, max_assign_iterations,
                    num_processors, select_link, makeFinalHighwayAssignmentStochastic, input_dir)

        if not skipFinalTransitAssignment:
            import_transit_demand(output_dir, transit_scenario)
            with _m.logbook_trace("Final transit assignments"):
                # Final iteration includes the transit skims per ABM-1072
                for number, period in period_ids:
                    src_period_scenario = main_emmebank.scenario(number)
                    transit_assign_scen = build_transit_scen(
                        period=period, base_scenario=src_period_scenario,
                        transit_emmebank=transit_emmebank, scenario_id=src_period_scenario.id,
                        scenario_title="%s - %s transit assign" % (base_scenario.title, period),
                        data_table_name=scenarioYear, overwrite=True)
                    transit_assign(period, transit_assign_scen, data_table_name=scenarioYear,
                                   num_processors=num_processors)
                omx_file = _join(output_dir, "transit_skims.omx")
                export_transit_skims(omx_file, periods, transit_scenario, big_to_zero=True)

        if not skipTransitShed:
            # write walk and drive transit sheds
            self.run_proc("runtransitreporter.cmd", [drive, path_forward_slash, transitShedThreshold, transitShedTOD],
                          "Create walk and drive transit sheds",
                          capture_output=True)

        if not skipVisualizer:
            self.run_proc("RunViz.bat",
                          [drive, path_no_drive, visualizer_reference_path, visualizer_output_file, "NO", visualizer_reference_label, visualizer_build_label, mgraInputFile],
                          "HTML Visualizer", capture_output=True)

        if not skipDataExport:
            # export network and matrix results from Emme directly to T if using local drive
            output_directory = _join(self._path, "output")
            export_network_data(self._path, scenario_id, main_emmebank, transit_emmebank, num_processors)
            export_matrix_data(output_directory, base_scenario, transit_scenario)
            # export core ABM data
            # Note: uses relative project structure, so cannot redirect to T drive
            self.run_proc("DataExporter.bat", [drive, path_no_drive], "Export core ABM data",capture_output=True)

        #Validation for 2016 scenario
        if scenarioYear == "2016":
            validation(self._path, main_emmebank, base_scenario) # to create source_EMME.xlsx
            
            # #Create Worksheet for ABM Validation using PowerBI Visualization #JY: can be uncommented if deciding to incorporate PowerBI vis in ABM workflow
            # self.run_proc("VisPowerBI.bat",  # forced to update excel links
            #                 [drive, path_no_drive, scenarioYear, 0],
            #                 "VisPowerBI",
            #                 capture_output=True)

            ### CL: Below step is temporarily used to update validation output files. When Gregor complete Upload procedure, below step should be removed. 05/31/20
            # self.run_proc("ExcelUpdate.bat",  # forced to update excel links
                            # [drive, path_no_drive, scenarioYear, 0],
                            # "ExcelUpdate",
                            # capture_output=True)

            ### ES: Commented out until this segment is updated to reference new database. 9/10/20 ###
            # add segments below for auto-reporting, YMA, 1/23/2019
            # add this loop to find the sceanro_id in the [dimension].[scenario] table

            #database_scenario_id = 0
            #int_hour = 0
            #while int_hour <= 96:

            #    database_scenario_id = self.sql_select_scenario(scenarioYear, end_iteration,
            #                                                    sample_rate[end_iteration - 1], path_no_drive,
            #                                                    start_db_time)
            #    if database_scenario_id > 0:
            #        break

            #    int_hour = int_hour + 1
            #    _time.sleep(900)  # wait for 15 mins

            # if load failed, then send notification email
            #if database_scenario_id == 0 and int_hour > 96:
            #    str_request_check_result = self.sql_check_load_request(scenarioYear, path_no_drive, username,
            #                                                           start_db_time)
            #    print(str_request_check_result)
            #    sys.exit(0)
                # self.send_notification(str_request_check_result,username) #not working in server
            #else:
            #    print(database_scenario_id)
            #    self.run_proc("DataSummary.bat",  # get summary from database, added for auto-reporting
            #                  [drive, path_no_drive, scenarioYear, database_scenario_id],
            #                  "Data Summary")

            #    self.run_proc("ExcelUpdate.bat",  # forced to update excel links
            #                  [drive, path_no_drive, scenarioYear, database_scenario_id],
            #                  "Excel Update",
            #                  capture_output=True)

        # terminate all java processes
        _subprocess.call("taskkill /F /IM java.exe")

        # close all DOS windows
        _subprocess.call("taskkill /F /IM cmd.exe")

        # UPLOAD DATA AND SWITCH PATHS
        if useLocalDrive:
            file_manager("UPLOAD", main_directory, username, scenario_id,
                         delete_local_files=not skipDeleteIntermediateFiles)
            self._path = main_directory
            drive, path_no_drive = os.path.splitdrive(self._path)
            # self._path = main_directory
            # drive, path_no_drive = os.path.splitdrive(self._path)
            init_transit_db.add_database(
                _eb.Emmebank(_join(main_directory, "emme_project", "Database_transit", "emmebank")))

        if not skipDataLoadRequest:
            start_db_time = datetime.datetime.now()  # record the time to search for request id in the load request table, YMA, 1/23/2019
            # start_db_time = start_db_time + datetime.timedelta(minutes=0)
            self.run_proc("DataLoadRequest.bat",
                          [drive + path_no_drive, end_iteration, scenarioYear, sample_rate[end_iteration - 1]],
                          "Data load request")

        # delete trip table files in iteration sub folder if model finishes without errors
        if not useLocalDrive and not skipDeleteIntermediateFiles:
            for msa_iteration in range(startFromIteration, end_iteration + 1):
                self.delete_files(
                    ["auto*Trips*.omx", "tran*Trips*.omx", "nmot*.omx", "othr*.omx", "trip*.omx"],
                    _join(output_dir, "iter%s" % (msa_iteration)))
					
        # record run time
        run_summary(path=self._path)

    def set_global_logbook_level(self, props):
        self._log_level = props.get("RunModel.LogbookLevel", "ENABLED")
        log_all = _m.LogbookLevel.ATTRIBUTE | _m.LogbookLevel.VALUE | _m.LogbookLevel.COOKIE | _m.LogbookLevel.TRACE | _m.LogbookLevel.LOG
        log_states = {
            "ENABLED": log_all,
            "DISABLE_ON_ERROR": log_all,
            "NO_EXTERNAL_REPORTS": log_all,
            "NO_REPORTS": _m.LogbookLevel.ATTRIBUTE | _m.LogbookLevel.COOKIE | _m.LogbookLevel.TRACE | _m.LogbookLevel.LOG,
            "TITLES_ONLY": _m.LogbookLevel.TRACE | _m.LogbookLevel.LOG,
            "DISABLED": _m.LogbookLevel.NONE,
        }
        _m.logbook_write("Setting logbook level to %s" % self._log_level)
        try:
            _m.logbook_level(log_states[self._log_level])
        except KeyError:
            raise Exception("properties.RunModel.LogLevel: value must be one of %s" % ",".join(log_states.keys()))

    def run_traffic_assignments(self, base_scenario, period_ids, msa_iteration, relative_gap,
                                max_assign_iterations, num_processors, select_link=None, 
                                makeFinalHighwayAssignmentStochastic=False, input_dir=None):
        modeller = _m.Modeller()
        traffic_assign = modeller.tool("sandag.assignment.traffic_assignment")
        export_traffic_skims = modeller.tool("sandag.export.export_traffic_skims")
        output_dir = _join(self._path, "output")
        main_emmebank = base_scenario.emmebank

        machine_name = _socket.gethostname().lower()
        with open(_join(self._path, "conf", "server-config.csv")) as f:
            columns = f.next().split(",")
            for line in f:
                values = dict(zip(columns, line.split(",")))
                name = values["ServerName"].lower()
                if name == machine_name:
                    server_config = values
                    break
            else:
                _m.logbook_write("Warning: current machine name not found in "
                                 "conf\\server-config.csv ServerName column")
                server_config = {"SNODE": "yes"}
        distributed = server_config["SNODE"] == "no"
        if distributed and not makeFinalHighwayAssignmentStochastic:
            scen_map = dict((p, main_emmebank.scenario(n)) for n, p in period_ids)
            input_args = {
                "msa_iteration": msa_iteration,
                "relative_gap": relative_gap,
                "max_assign_iterations": max_assign_iterations,
                "select_link": select_link
            }

            periods_node1 = ["PM", "MD"]
            input_args["num_processors"] = server_config["THREADN1"],
            database_path1, skim_names1 = self.setup_remote_database(
                [scen_map[p] for p in periods_node1], periods_node1, 1, msa_iteration)
            self.start_assignments(
                server_config["NODE1"], database_path1, periods_node1, scen_map, input_args)

            periods_node2 = ["AM"]
            input_args["num_processors"] = server_config["THREADN2"]
            database_path2, skim_names2 = self.setup_remote_database(
                [scen_map[p] for p in periods_node2], periods_node2, 2, msa_iteration)
            self.start_assignments(
                server_config["NODE2"], database_path2, periods_node2, scen_map, input_args)

            try:
                # run assignments locally
                periods_local = ["EA", "EV"]
                for period in periods_local:
                    local_scenario = scen_map[period]
                    traffic_assign(period, msa_iteration, relative_gap, max_assign_iterations,
                                   num_processors, local_scenario, select_link)
                    omx_file = _join(output_dir, "traffic_skims_%s.omx" % period)
                    if msa_iteration <= 4:
                        export_traffic_skims(period, omx_file, base_scenario)
                scenarios = {
                    database_path1: [scen_map[p] for p in periods_node1],
                    database_path2: [scen_map[p] for p in periods_node2]
                }
                skim_names = {
                    database_path1: skim_names1, database_path2: skim_names2
                }
                self.wait_and_copy([database_path1, database_path2], scenarios, skim_names)
            except:
                # Note: this will kill ALL python processes - not suitable if servers are being
                # used for other tasks
                _subprocess.call("taskkill /F /T /S \\\\%s /IM python.exe" % server_config["NODE1"])
                _subprocess.call("taskkill /F /T /S \\\\%s /IM python.exe" % server_config["NODE2"])
                raise
        else:
            for number, period in period_ids:
                period_scenario = main_emmebank.scenario(number)
                traffic_assign(period, msa_iteration, relative_gap, max_assign_iterations,
                               num_processors, period_scenario, select_link, stochastic=makeFinalHighwayAssignmentStochastic, input_directory=input_dir)
                omx_file = _join(output_dir, "traffic_skims_%s.omx" % period)
                if msa_iteration <= 4:
                    export_traffic_skims(period, omx_file, base_scenario)

    def run_proc(self, name, arguments, log_message, capture_output=False):
        path = _join(self._path, "bin", name)
        if not os.path.exists(path):
            raise Exception("No command / batch file '%s'" % path)
        command = path + " " + " ".join([str(x) for x in arguments])
        attrs = {"command": command, "name": name, "arguments": arguments}
        with _m.logbook_trace(log_message, attributes=attrs):
            if capture_output and self._log_level != "NO_EXTERNAL_REPORTS":
                report = _m.PageBuilder(title="Process run %s" % name)
                report.add_html('Command:<br><br><div class="preformat">%s</div><br>' % command)
                # temporary file to capture output error messages generated by Java
                err_file_ref, err_file_path = _tempfile.mkstemp(suffix='.log')
                err_file = os.fdopen(err_file_ref, "w")
                try:
                    output = _subprocess.check_output(command, stderr=err_file, cwd=self._path, shell=True)
                    report.add_html('Output:<br><br><div class="preformat">%s</div>' % output)
                except _subprocess.CalledProcessError as error:
                    report.add_html('Output:<br><br><div class="preformat">%s</div>' % error.output)
                    raise
                finally:
                    err_file.close()
                    with open(err_file_path, 'r') as f:
                        error_msg = f.read()
                    os.remove(err_file_path)
                    if error_msg:
                        report.add_html('Error message(s):<br><br><div class="preformat">%s</div>' % error_msg)
                    try:
                        # No raise on writing report error
                        # due to observed issue with runs generating reports which cause
                        # errors when logged
                        _m.logbook_write("Process run %s report" % name, report.render())
                    except Exception as error:
                        print _time.strftime("%Y-%M-%d %H:%m:%S")
                        print "Error writing report '%s' to logbook" % name
                        print error
                        print _traceback.format_exc(error)
                        if self._log_level == "DISABLE_ON_ERROR":
                            _m.logbook_level(_m.LogbookLevel.NONE)
            else:
                _subprocess.check_call(command, cwd=self._path, shell=True)

    @_m.logbook_trace("Check free space on C")
    def check_free_space(self, min_space):
        path = "c:\\"
        temp, total, free = _ctypes.c_ulonglong(), _ctypes.c_ulonglong(), _ctypes.c_ulonglong()
        if sys.version_info >= (3,) or isinstance(path, unicode):
            fun = _ctypes.windll.kernel32.GetDiskFreeSpaceExW
        else:
            fun = _ctypes.windll.kernel32.GetDiskFreeSpaceExA
        ret = fun(path, _ctypes.byref(temp), _ctypes.byref(total), _ctypes.byref(free))
        if ret == 0:
            raise _ctypes.WinError()
        total = total.value / (1024.0 ** 3)
        free = free.value / (1024.0 ** 3)
        if free < min_space:
            raise Exception("Free space on C drive %s is less than %s" % (free, min_space))

    def remove_prev_iter_files(self, file_names, output_dir, iteration):
        if iteration == 0:
            self.delete_files(file_names, output_dir)
        else:
            self.move_files(file_names, output_dir, _join(output_dir, "iter%s" % (iteration)))

    def copy_files(self, file_names, from_dir, to_dir):
        with _m.logbook_trace("Copy files %s" % ", ".join(file_names)):
            for file_name in file_names:
                from_file = _join(from_dir, file_name)
                _shutil.copy(from_file, to_dir)

    def complete_work(self, scenarioYear, input_dir, output_dir, input_file, output_file):

        fullList = np.array(pd.read_csv(_join(input_dir, input_file))['mgra'])
        workList = np.array(pd.read_csv(_join(output_dir, output_file))['i'])

        list_set = set(workList)
        unique_list = (list(list_set))
        notMatch = [x for x in fullList if x not in unique_list]

        if notMatch:
            out_file = _join(output_dir, output_file)
            with open(out_file, 'ab') as csvfile:
                spamwriter = csv.writer(csvfile)
                # spamwriter.writerow([])
                for item in notMatch:
                    # pdb.set_trace()
                    spamwriter.writerow([item, item, '30', '30', '30'])

    def move_files(self, file_names, from_dir, to_dir):
        with _m.logbook_trace("Move files %s" % ", ".join(file_names)):
            if not os.path.exists(to_dir):
                os.mkdir(to_dir)
            for file_name in file_names:
                all_files = _glob.glob(_join(from_dir, file_name))
                for path in all_files:
                    try:
                        dst_file = _join(to_dir, os.path.basename(path))
                        if os.path.exists(dst_file):
                            os.remove(dst_file)
                        _shutil.move(path, to_dir)
                    except Exception as error:
                        _m.logbook_write(
                            "Error moving file %s" % path, {"error": _traceback.format_exc(error)})

    def delete_files(self, file_names, directory):
        with _m.logbook_trace("Delete files %s" % ", ".join(file_names)):
            for file_name in file_names:
                all_files = _glob.glob(_join(directory, file_name))
                for path in all_files:
                    os.remove(path)

    def check_for_fatal(self, file_name, error_msg):
        with open(file_name, 'a+') as f:
            for line in f:
                if "FATAL" in line:
                    raise Exception(error_msg)

    def set_active(self, emmebank):
        modeller = _m.Modeller()
        desktop = modeller.desktop
        data_explorer = desktop.data_explorer()
        for db in data_explorer.databases():
            if _norm(db.path) == _norm(unicode(emmebank)):
                db.open()
                return db
        return None

    def parse_availability_file(self, file_path, periods):
        if os.path.exists(file_path):
            availabilities = _defaultdict(lambda: _defaultdict(lambda: dict()))
            # NOTE: CSV Reader sets the field names to UPPERCASE for consistency
            with gen_utils.CSVReader(file_path) as r:
                for row in r:
                    name = row.pop("FACILITY_NAME")
                    class_name = row.pop("VEHICLE_CLASS")
                    for period in periods:
                        is_avail = int(row[period + "_AVAIL"])
                        if is_avail not in [1, 0]:
                            msg = "Error processing file '%s': value for period %s class %s facility %s is not 1 or 0"
                            raise Exception(msg % (file_path, period, class_name, name))
                        availabilities[period][name][class_name] = is_avail
        else:
            availabilities = None
        return availabilities

    def apply_availabilities(self, period, scenario, availabilities):
        if availabilities is None:
            return

        network = scenario.get_network()
        hov2 = network.mode("h")
        hov2_trnpdr = network.mode("H")
        hov3 = network.mode("i")
        hov3_trnpdr = network.mode("I")
        sov = network.mode("s")
        sov_trnpdr = network.mode("S")
        heavy_trk = network.mode("v")
        heavy_trk_trnpdr = network.mode("V")
        medium_trk = network.mode("m")
        medium_trk_trnpdr = network.mode("M")
        light_trk = network.mode("t")
        light_trk_trnpdr = network.mode("T")

        class_mode_map = {
            "DA":    set([sov_trnpdr, sov]),
            "S2":    set([hov2_trnpdr, hov2]),
            "S3":    set([hov3_trnpdr, hov3]),
            "TRK_L": set([light_trk_trnpdr, light_trk]),
            "TRK_M": set([medium_trk_trnpdr, medium_trk]),
            "TRK_H": set([heavy_trk_trnpdr, heavy_trk]),
        }
        report = ["<div style='margin-left:5px'>Link mode changes</div>"]
        for name, class_availabilities in availabilities[period].iteritems():
            report.append("<div style='margin-left:10px'>%s</div>" % name)
            changes = _defaultdict(lambda: 0)
            for link in network.links():
                if name in link["#name"]:
                    for class_name, is_avail in class_availabilities.iteritems():
                        modes = class_mode_map[class_name]
                        if is_avail == 1 and not modes.issubset(link.modes):
                            link.modes |= modes
                            changes["added %s to" % class_name] += 1
                        elif is_avail == 0 and modes.issubset(link.modes):
                            link.modes -= modes
                            changes["removed %s from" % class_name] += 1
            report.append("<div style='margin-left:20px'><ul>")
            for x in changes.iteritems():
                report.append("<li>%s %s links</li>" % x)
            report.append("</div></ul>")
        scenario.publish_network(network)

        title = "Apply global class availabilities by faclity name for period %s" % period
        log_report = _m.PageBuilder(title=title)
        for item in report:
            log_report.add_html(item)
        _m.logbook_write(title, log_report.render())

    def setup_remote_database(self, src_scenarios, periods, remote_num, msa_iteration):
        with _m.logbook_trace("Set up remote database #%s for %s" % (remote_num, ", ".join(periods))):
            init_matrices = _m.Modeller().tool("sandag.initialize.initialize_matrices")
            create_function = _m.Modeller().tool("inro.emme.data.function.create_function")
            src_emmebank = src_scenarios[0].emmebank
            remote_db_dir = _join(self._path, "emme_project", "Database_remote" + str(remote_num))
            if msa_iteration == 1:
                # Create and initialize database at first iteration, overwrite existing
                if os.path.exists(remote_db_dir):
                    _shutil.rmtree(remote_db_dir)
                    _time.sleep(1)
                os.mkdir(remote_db_dir)
                dimensions = src_emmebank.dimensions
                dimensions["scenarios"] = len(src_scenarios)
                remote_emmebank = _eb.create(_join(remote_db_dir, "emmebank"), dimensions)
                try:
                    remote_emmebank.title = src_emmebank.title
                    remote_emmebank.coord_unit_length = src_emmebank.coord_unit_length
                    remote_emmebank.unit_of_length = src_emmebank.unit_of_length
                    remote_emmebank.unit_of_cost = src_emmebank.unit_of_cost
                    remote_emmebank.unit_of_energy = src_emmebank.unit_of_energy
                    remote_emmebank.use_engineering_notation = src_emmebank.use_engineering_notation
                    remote_emmebank.node_number_digits = src_emmebank.node_number_digits

                    for src_scen in src_scenarios:
                        remote_scen = remote_emmebank.create_scenario(src_scen.id)
                        remote_scen.title = src_scen.title
                        for attr in sorted(src_scen.extra_attributes(), key=lambda x: x._id):
                            dst_attr = remote_scen.create_extra_attribute(
                                attr.type, attr.name, attr.default_value)
                            dst_attr.description = attr.description
                        for field in src_scen.network_fields():
                            remote_scen.create_network_field(
                                field.type, field.name, field.atype, field.description)
                        remote_scen.has_traffic_results = src_scen.has_traffic_results
                        remote_scen.has_transit_results = src_scen.has_transit_results
                        remote_scen.publish_network(src_scen.get_network())
                    for function in src_emmebank.functions():
                        create_function(function.id, function.expression, remote_emmebank)
                    init_matrices(["traffic_skims", "traffic_demand"], periods, remote_scen)
                finally:
                    remote_emmebank.dispose()

            src_scen = src_scenarios[0]
            with _m.logbook_trace("Copy demand matrices to remote database"):
                with _eb.Emmebank(_join(remote_db_dir, "emmebank")) as remote_emmebank:
                    demand_matrices = init_matrices.get_matrix_names("traffic_demand", periods, src_scen)
                    for matrix_name in demand_matrices:
                        matrix = remote_emmebank.matrix(matrix_name)
                        src_matrix = src_emmebank.matrix(matrix_name)
                        if matrix.type == "SCALAR":
                            matrix.data = src_matrix.data
                        else:
                            matrix.set_data(src_matrix.get_data(src_scen.id), src_scen.id)
            skim_matrices = init_matrices.get_matrix_names("traffic_skims", periods, src_scen)
            return remote_db_dir, skim_matrices

    def start_assignments(self, machine, database_path, periods, scenarios, assign_args):
        with _m.logbook_trace("Start remote process for traffic assignments %s" % (", ".join(periods))):
            assign_args["database_path"] = database_path
            end_path = _join(database_path, "finish")
            if os.path.exists(end_path):
                os.remove(end_path)
            for period in periods:
                assign_args["period_scenario"] = scenarios[period].id
                assign_args["period"] = period
                with open(_join(database_path, "start_%s.args" % period), 'w') as f:
                    _json.dump(assign_args, f, indent=4)
            script_dir = _join(self._path, "python")
            bin_dir = _join(self._path, "bin")
            args = [
                'start %s\\PsExec.exe' % bin_dir,
                '-c',
                '-f',
                '\\\\%s' % machine,
                '-u \%s' % self.username,
                '-p %s' % self.password,
                "-d",
                '%s\\emme_python.bat' % bin_dir,
                "T:",
                self._path,
                '%s\\remote_run_traffic.py' % script_dir,
                database_path,
            ]
            command = " ".join(args)
            p = _subprocess.Popen(command, shell=True)

    @_m.logbook_trace("Wait for remote assignments to complete and copy results")
    def wait_and_copy(self, database_dirs, scenarios, matrices):
        database_dirs = database_dirs[:]
        wait = True
        while wait:
            _time.sleep(5)
            for path in database_dirs:
                end_path = _join(path, "finish")
                if os.path.exists(end_path):
                    database_dirs.remove(path)
                    _time.sleep(2)
                    self.check_for_fatal(
                        end_path, "error during remote run of traffic assignment. "
                                  "Check logFiles/traffic_assign_database_remote*.log")
                    self.copy_results(path, scenarios[path], matrices[path])
            if not database_dirs:
                wait = False

    @_m.logbook_trace("Copy skim results from remote database", save_arguments=True)
    def copy_results(self, database_path, scenarios, matrices):
        with _eb.Emmebank(_join(database_path, "emmebank")) as remote_emmebank:
            for dst_scen in scenarios:
                remote_scen = remote_emmebank.scenario(dst_scen.id)
                # Create extra attributes and network fields which do not exist
                for attr in sorted(remote_scen.extra_attributes(), key=lambda x: x._id):
                    if not dst_scen.extra_attribute(attr.name):
                        dst_attr = dst_scen.create_extra_attribute(
                            attr.type, attr.name, attr.default_value)
                        dst_attr.description = attr.description
                for field in remote_scen.network_fields():
                    if not dst_scen.network_field(field.type, field.name):
                        dst_scen.create_network_field(
                            field.type, field.name, field.atype, field.description)
                dst_scen.has_traffic_results = remote_scen.has_traffic_results
                dst_scen.has_transit_results = remote_scen.has_transit_results

                dst_scen.publish_network(remote_scen.get_network())

            dst_emmebank = dst_scen.emmebank
            scen_id = dst_scen.id
            for matrix_id in matrices:
                src_matrix = remote_emmebank.matrix(matrix_id)
                dst_matrix = dst_emmebank.matrix(matrix_id)
                dst_matrix.set_data(src_matrix.get_data(scen_id), scen_id)

    @_m.method(return_type=unicode)
    def get_link_attributes(self):
        export_utils = _m.Modeller().module("inro.emme.utility.export_utilities")
        return export_utils.get_link_attributes(_m.Modeller().scenario)

    def sql_select_scenario(self, year, iteration, sample, path, dbtime):  # YMA, 1/24/2019
        """Return scenario_id from [dimension].[scenario] given path"""

        import datetime

        sql_con = pyodbc.connect(driver='{SQL Server}',
                                 server='sql2014a8',
                                 database='abm_2',
                                 trusted_connection='yes')

        # dbtime = dbtime + datetime.timedelta(days=0)

        df = pd.read_sql_query(
            sql=("SELECT [scenario_id] "
                 "FROM [dimension].[scenario]"
                 "WHERE [year] = ? AND [iteration] = ? AND [sample_rate]= ? AND [path] Like ('%' + ? + '%') AND [date_loaded] > ? "),
            con=sql_con,
            params=[year, iteration, sample, path, dbtime]
        )

        if len(df) > 0:
            return (df.iloc[len(df) - 1]['scenario_id'])
        else:
            return 0

    def sql_check_load_request(self, year, path, user, ldtime):  # YMA, 1/24/2019
        """Return information from [data_load].[load_request] given path,username,and requested time"""

        import datetime

        t0 = ldtime + datetime.timedelta(minutes=-1)
        t1 = t0 + datetime.timedelta(minutes=30)

        sql_con = pyodbc.connect(driver='{SQL Server}',
                                 server='sql2014a8',
                                 database='abm_2',
                                 trusted_connection='yes')

        df = pd.read_sql_query(
            sql=(
                "SELECT [load_request_id],[year],[name],[path],[iteration],[sample_rate],[abm_version],[user_name],[date_requested],[loading],[loading_failed],[scenario_id] "
                "FROM [data_load].[load_request] "
                "WHERE [year] = ?  AND [path] LIKE ('%' + ? + '%') AND [user_name] LIKE ('%' + ? + '%') AND [date_requested] >= ? AND [date_requested] <= ?  "),
            con=sql_con,
            params=[year, path, user, t0, t1]
        )

        if len(df) > 0:
            return "You have successfully made the loading request, but the loading to the database failed. \r\nThe information is below. \r\n\r\n" + df.to_string()
        else:
            return "The data load request was not successfully made, please double check the [data_load].[load_request] table to confirm."


'''
    def send_notification(self,str_message,user):      # YMA, 1/24/2019, not working on server
        """automate to send email notification if load request or loading failed"""

        import win32com.client as win32

        outlook = win32.Dispatch('outlook.application')
        Msg = outlook.CreateItem(0)
        Msg.To = user + '@sandag.org'
        Msg.CC = 'yma@sandag.org'
        Msg.Subject = 'Loading Scenario to Database Failed'
        Msg.body = str_message + '\r\n' + '\r\n' + 'This email alert is auto generated.\r\n' +  'Please do not respond.\r\n'
        Msg.send'''
