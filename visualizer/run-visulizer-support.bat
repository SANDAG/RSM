@echo on

SET arg1=%1
SET arg2=%2
:: set paths
SET DATA_PIPELINE_PATH=%args1%
SET VISULAZER_PATH=%args2%
:: change the directory to data-pipeline-tool folder
cd /d %DATA_PIPELINE_PATH%

:: create conda environment using the environment.yml
CALL conda env create -f environment.yml

:: activate the conda environment
CALL conda activate sandag-rsm-visualizer



:: run the support script. 
cd /d %VISULAZER_PATH%
python visualizer_support.py "config_visualizer_support.yml"



