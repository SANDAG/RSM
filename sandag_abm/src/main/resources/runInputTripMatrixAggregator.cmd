rem ##### Demand files aggregator #####


set MAIN_DIR=%1
set PYTHON2_DIR=%2
set ORG_FULL_MODEL_DIR=%3
set RSM_SCRIPT_DIR=%4
set TAZ_CWK=%5

rem #### activate the python environment
call "%PYTHON2_DIR%\Scripts\activate.bat" %PYTHON2_DIR%

rem #### Aggregate the demand matrices
python "%RSM_SCRIPT_DIR%/rsm_trip_matrix_aggregator.py" %MAIN_DIR% %ORG_FULL_MODEL_DIR% %TAZ_CWK%

rem #### deactivate the python environment
call "%PYTHON2_DIR%\Scripts\deactivate.bat"


