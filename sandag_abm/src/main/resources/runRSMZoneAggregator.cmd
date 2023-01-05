rem ##### RSM Zone Aggregator #####

set INPUT_DIR=%1
set PYTHON_DIR=%2
set RSM_SCRIPT_DIR=%3
set ORG_FULL_MODEL_DIR=%4
set AGGREGATED_ZONES=%5
set EXT_ZONES=%6

rem #### create RSM zones and TAZ/MGRA to RSM zone crosswalks
"%PYTHON_DIR%/python.exe" "%RSM_SCRIPT_DIR%/rsm_zone_aggregator.py" %INPUT_DIR% %ORG_FULL_MODEL_DIR% %AGGREGATED_ZONES% %EXT_ZONES%


