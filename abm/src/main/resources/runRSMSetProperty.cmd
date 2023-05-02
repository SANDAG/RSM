rem ##### Set property values in sandag abm properties file #####

set MAIN_DIR=%1
set PYTHON_DIR=%2
set RSM_SCRIPT_DIR=%3
set PROPERTY_NAME=%4
set PROPERTY_VALUE=%5

set PROPERTIES_FILE=%MAIN_DIR%/conf/sandag_abm.properties

"%PYTHON_DIR%/python.exe" "%RSM_SCRIPT_DIR%/rsm_set_property.py" %PROPERTIES_FILE% %PROPERTY_NAME% %PROPERTY_VALUE%