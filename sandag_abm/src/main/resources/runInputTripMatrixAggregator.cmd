rem ##### Input and UEC files Aggregator #####


set MAIN_DIR=%1
set PYTHON2_DIR=%2
set ORG_FULL_MODEL_DIR=%3
set RSM_SCRIPT_DIR=%4
set TAZ_CWK=%5


call "%PYTHON2_DIR%\Scripts\activate.bat" %PYTHON2_DIR%

python "%RSM_SCRIPT_DIR%/rsm_trip_matrix_aggregator.py" %MAIN_DIR% %ORG_FULL_MODEL_DIR% %TAZ_CWK%

call "%PYTHON2_DIR%\Scripts\deactivate.bat"


::"%PYTHON2_DIR%" "%RSM_SCRIPT_DIR%/rsm_trip_matrix_aggregator.py" %MAIN_DIR% %ORG_FULL_MODEL_DIR% %TAZ_CWK%
