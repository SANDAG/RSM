rem ##### Settings for CT-RAMP Accessibility run #####

set MAIN_DIR=%1
set PYTHON_DIR=%2
set RSM_SCRIPT_DIR=%3
set VALUE=%4

::cd RSM_SCRIPT_DIR
"%PYTHON_DIR%/python.exe" "%RSM_SCRIPT_DIR%/rsm_set_accessibility.py" %MAIN_DIR% %VALUE%
::docker run -v %cd%:/home/mambauser/sandag_rsm -w /home/mambauser/sandag_rsm sandag_rsm python rsm_zone_aggregator.py INPUT_DIR

