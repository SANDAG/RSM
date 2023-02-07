@echo on

:: set paths
SET DATA_PIPELINE_PATH=C:\projects\SimWrapper\RSM_main\visualizer\Pipeline
SET VISULAZER_PATH=C:\projects\SimWrapper\RSM_main\visualizer
:: change the directory to data-pipeline-tool folder
cd /d %DATA_PIPELINE_PATH%

:: create conda environment using the environment.yml
CALL conda env create -f environment.yml

:: activate the conda environment
CALL conda activate sandag-rsm-visualizer



:: run the support script. 
cd /d %VISULAZER_PATH%
python visualizer_support.py "config.yml"



