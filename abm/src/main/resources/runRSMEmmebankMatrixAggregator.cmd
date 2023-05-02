rem ##### Demand files aggregator #####

set SCENARIO=%1
set MAIN_DIR=%2
set ORG_FULL_MODEL_DIR=%3
set RSM_SCRIPT_DIR=%4
set TAZ_CWK=%5

rem #### Aggregate the emmebank matrices
"C:/Program Files/INRO/Emme/Emme 4/Emme-4.3.7/Python27/python.exe" "T:/ABM/WSP_Space/sandag_rsm/python/emme/toolbox/utilities/rsm_emmebank_aggregator.py" %SCENARIO% %MAIN_DIR% %ORG_FULL_MODEL_DIR% %TAZ_CWK%