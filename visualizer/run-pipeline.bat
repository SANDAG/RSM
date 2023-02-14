@echo on

SET arg1=%1
SET arg2=%2
:: set paths
SET DATA_PIPELINE_PATH=%arg2%
:: change the directory to data-pipeline-tool folder
cd /d %DATA_PIPELINE_PATH%

:: create conda environment using the environment.yml
CALL conda env create -f environment.yml

:: activate the conda environment
CALL conda activate sandag-rsm-visualizer

:: run the script for data pipeline tool 
python run.py %arg1%



