rem ##### RSM ASSEMBLER #####

set MAIN_DIR=%1
set PYTHON_DIR=%2
set RSM_SCRIPT_DIR=%3
set ORG_MODEL_DIR=%4
set ITERATION=%5

::cd RSM_SCRIPT_DIR
"%PYTHON_DIR%/python.exe" "%RSM_SCRIPT_DIR%/rsm_assembler.py" %MAIN_DIR% %ORG_MODEL_DIR% %ITERATION%
::docker run -v %cd%:/home/mambauser/sandag_rsm -w /home/mambauser/sandag_rsm sandag_rsm python rsm_zone_aggregator.py INPUT_DIR

