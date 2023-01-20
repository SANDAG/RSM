rem ##### RSM Zone Aggregator #####

set MAIN_DIR=%1
set PYTHON_DIR=%2
set RSM_SCRIPT_DIR=%3
set ORG_FULL_MODEL_DIR=%4
set NUM_RSM_ZONES=%5
set NUM_EXT_ZONES=%6

rem #### create RSM zones and TAZ/MGRA to RSM zone crosswalks
"%PYTHON_DIR%/python.exe" "%RSM_SCRIPT_DIR%/rsm_zone_aggregator.py" %MAIN_DIR% %ORG_FULL_MODEL_DIR% %NUM_RSM_ZONES% %NUM_EXT_ZONES%


