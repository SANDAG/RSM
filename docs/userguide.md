## RSM Setup
Below are the steps to setup an RSM scenario run:

1.  Set up an ABM run on the server's C drive* by using the ABM2+ release 14.2.2 scenario creation GUI located at T:\ABM\release\ABM\version_14_2_2\dist\createStudyAndScenario.exe.

    *running the model on the T drive and setting it to run on the local drive causes an error. An issue has been created on GitHub

2. Open Anaconda Prompt and type the following command:

    *python T:\projects\RSM\setup\setup_rsm.py [MODEL_RUN_DIRECTORY]*

    Specifying the model run directory in the command line is optional. If it is not specified a dialog box will open asking the user to specify the model run.

3. Change the inputs and properties as needed. Be sure to check the following:
    1. If running a new network, make sure the network files are correct
    2. Check that the RSM properties were appended to the property file and make sure the RSM properties are correct
    3. Check that the updated Tour Mode Choice UEC was copied over

4. After opening Emme using start_emme_with_virtual_env.bat and opening the SANDAG toolbox in Modeller as usual, set the steps to skip all of the special market models and to run only 2 iterations. Most of these should be set automatically, though you may need to set it to skip the EE model manually.

    Figure 1: Steps to run in SANDAG model GUI for RSM run

    ![](images\user_guide\figure_1.PNG)

## Debugging
For crashes encountered in CT-RAMP, review the event log as usual. However, if it occurs during an RSM step, a new logfile called rsm-logging.log is created in the LogFiles folder.

## RSM Specific Changes
#### Application
- sandag_abm.jar
    * New CT-RAMP jar file with few required Java code updates. 

#### Bin
- runRSMAccessibility.cmd
    - Runs CT-RAMP to compute the accessibility of each zone
- runRSMAssembler.cmd
    - Runs the intelligent assembler
- runRSMEmmebankMatrixAggregator.cmd
    - Opens the Emmebank of the donor model and aggregates the truck and external trip tables
- runRSMInputAggregator.cmd
    - Aggregates various model inputs into the aggregated zone system creating 
- runRSMSampler.cmd
    - Runs the intelligent sampler that combines the donor model trip diaries with the travel behavior of the resampled households
- runRSMSandagABM.cmd
    - Runs CT-RAMP on the sampled households
- runRSMSandagABMTripTables.cmd
    - Builds trip tables from assembled trip data
- runRSMSetProperty.cmd
    - Updates property file to read the accessibility file instead of building it
- runRSMSetupUpdate.cmd
    - Updates several properties
- runRSMTripMatrixAggregator.cm
    - Aggregates trip tables stored in OMX files from donor model
- runRSMZoneAggregator.cmd
    - Runs the zone aggregator

#### Emme_project
- start_emme_with_virtualenv.bat
    - New lines to call Python environments used in RSM scripts
- scripts\sandag_toolbox.mtbx
    - Updated toolbox with a master run script to call RSM steps

#### Input
- MGRASHAPE.zip
    - Zipped shapefile of the MGRAs (used in zone aggregator)

#### Python\emme\toolbox
- master_run.py
    - Changed to include new model steps
- import\import_auto_demand.py
    - Changes to how the trip tables are read into the Emmebank
- utilities\databank_aggregator.py
    - Aggregates matrices stored in the Emmebank

#### New Properties
- run.rsm.setup
    * Set to 1 if running the RSM setup steps and 0 otherwise
        + Zone aggregator
        + Input aggregator
        + Matrix aggregator
        + Emmebank aggregator
- run.rsm
    * Set to 1 if running the RSM and 0 otherwise
- run.rsm.zone.aggregator
    * If set to 1, the zone aggregator will be run. If set to 0, the zone system from a run specified in rsm.baseline.run.dir will be used.
- rsm.baseline.run.dir
    * Baseline run to read in zone system from if not running zone aggregator
- rsm.zones
    * Number of zones to use
- External.zones
    * Number of external zones
- Run.rsm.sampling
    * 1 if running the intelligent sampler and 0 if not. If set to 0, every zone will have the default sampling rate
- Rsm.default.sampling.rate
    * Default sampling rate to use when running the intelligent sampler
- Rsm.centroid.connector.start.id
    * Starting value of tcovid for new zonal connectors to aggregated zones
- Full.modelrun.dir
    * Filepath of donor model
- Taz.to.cluster.crosswalk.file
    * Maps TAZs to aggregated zones
- Mgra.to.cluster.crosswalk.file
    * Maps MGRAs to aggregated zones
- Cluster.zone.centroid.file
    * Latitude and longitude coordinates of aggregated zone centroids

#### New Files
1. study_area.csv:

    This optional file specifies an explicit definition of how to aggregate certain zones, and consequentially, which zones to not aggregate. This is useful for project-level analysis as a modeler may want higher resolution close to a project but not be need the resolution further away. The file has two columns, taz and group. The taz column is the zone ID in the ABM zone system, and the group column indicates what RSM zone the ABM zone will be a part of. This will be the MGRA ID, and the TAZ ID being the MGRA ID added to the number of external zones. If a user doesn't want to aggregate any zones within the study area, the group ID should be distinct for all of them. Presently, all RSM zones defined in the study area are sampled at 100%, and the remaining zones are sampled at the sampling rate set in the property file. 

    Any zones not within the study area will be aggregated using the standard RSM zone aggregating algorithm.

    An example of how the study area file works is shown below (assuming 12 external zones):

    Figure 2: ABM Zones
    ![](images\user_guide\figure_2.PNG)

    Table 1: study_area.csv

    | taz  | group |
    | ---- | ----- |
    | 1    | 1     |
    | 2    | 2     |
    | 3    | 3     |
    | 4    | 4     |
    | 5    | 5     |
    | 6    | 6     |

    Figure 3: Resulting RSM Zones
    ![](images\user_guide\figure_3.PNG)

    For a practical example, see Figure 4, where a study area was defined as every zone within a half mile of a project. Note that within the study area, no zones were aggregated (as it was defined), but outside of the study area, aggregation occurred.

    Figure 4: Example Study Area
    ![](images\user_guide\figure_4.PNG)
