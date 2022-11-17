@echo on

:: set paths
SET DATA_PIPELINE_PATH=D:\Models\RSM\visualizer\Data-Pipeline-Tool
SET SIMWRAPPER_PATH=D:\Models\RSM\visualizer\SimWrapper

:: change the directory to data-pipeline-tool folder
cd /d %DATA_PIPELINE_PATH%

:: create conda environment using the environment.yml
CALL conda env create -f environment.yml

:: activate the conda environment
CALL conda activate sandag-rsm-visualizer

:: run the script for data pipeline tool 
python run.py

:: install simwrapper package
::CALL conda install -c conda-forge simwrapper
CALL pip install simwrapper

:: change the directory to simwrapper folder
cd /d %SIMWRAPPER_PATH%

:: use this to start simwrapper
:: and then type "http://localhost:8050/live" in a browser
::simwrapper here

:: this starts the simwrapper and then opens the browser too. 
simwrapper open asim


