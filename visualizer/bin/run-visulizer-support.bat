@echo on

SET VISUALIZER_PATH=%1
SET CONFIG=%2

:: activate the conda environment (created in run-pipeline.bat call)
CALL conda activate sandag-rsm-visualizer

:: run the support script. 
cd /d %VISUALIZER_PATH%
python visualizer_support.py %CONFIG%
