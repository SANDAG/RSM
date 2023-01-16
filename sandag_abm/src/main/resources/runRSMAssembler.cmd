rem ##### RSM ASSEMBLER #####

set MAIN_DIR=%1
set PYTHON_DIR=%2
set RSM_SCRIPT_DIR=%3
set ORG_MODEL_DIR=%4
set ITERATION=%5

rem #### assemble trip tables from CT Ramp and Donor model
"%PYTHON_DIR%/python.exe" "%RSM_SCRIPT_DIR%/rsm_assembler.py" %MAIN_DIR% %ORG_MODEL_DIR% %ITERATION%

