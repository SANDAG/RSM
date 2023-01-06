rem ##### RSM Sampler #####

set MAIN_DIR=%1
set PYTHON_DIR=%2
set RSM_SCRIPT_DIR=%3
set ITERATION=%4

rem #### creates sampled_household.csv and sampled_person.csv file
"%PYTHON_DIR%/python.exe" "%RSM_SCRIPT_DIR%/rsm_sampler.py" %MAIN_DIR% %ITERATION%


