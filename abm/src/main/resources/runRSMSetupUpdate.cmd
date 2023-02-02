rem ##### Set property values in sandag abm properties file #####

set MAIN_DIR=%1
set PYTHON_DIR=%2
set RSM_SCRIPT_DIR=%3
set ITERATION=%4

"%PYTHON_DIR%/python.exe" "%RSM_SCRIPT_DIR%/rsm_setup_update.py" %MAIN_DIR% %ITERATION%
