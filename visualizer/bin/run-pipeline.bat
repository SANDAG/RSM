@echo on

SET SETTINGS_FILE=%1
SET DATA_PIPELINE_PATH=%2

:: change the directory to data-pipeline-tool folder
cd /d %DATA_PIPELINE_PATH%

:: create conda environment using the environment.yml
CALL conda env create -f environment.yml

:: activate the conda environment
CALL conda activate sandag-rsm-visualizer

:: run the script for data pipeline tool 
python run.py %SETTINGS_FILE%
