rem ##### Zone Aggregator #####

set INPUT_DIR=%1
set PYTHON_DIR=%2
set RSM_SCRIPT_DIR=%3
set ORG_FULL_MODEL_DIR=%4
set AGGREGATED_ZONES=%5
set EXT_ZONES=%6

::cd RSM_SCRIPT_DIR
"%PYTHON_DIR%/python.exe" "%RSM_SCRIPT_DIR%/rsm_zone_aggregator.py" %INPUT_DIR% %ORG_FULL_MODEL_DIR% %AGGREGATED_ZONES% %EXT_ZONES%
::docker run -v %cd%:/home/mambauser/sandag_rsm -w /home/mambauser/sandag_rsm sandag_rsm python rsm_zone_aggregator.py INPUT_DIR

