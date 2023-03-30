# RSM Visualizer
Model Results Visualizer using SimWrapper for Rapid Strategic Model (RSM)

## How to Setup
- Download the data for 'donor_model' and 'rsm_base' scenarios from the shared folder (contact Joe from SANDAG or Arash from WSP) and place it in the 'visualizer\simwrapper\data\external' folder. 

- The visualizer is set up to compare three scenarios - Donor (full) Model, RSM Baseline and RSM Scenario. Each scenario folder in the external directory should have 'input' and 'report' as sub-folders. 

- For each of the scenario folder, 'report' folder has the files that are generated as part of the data exporter step in the model and 'input' folder only needs to have mgra_crosswalk.csv and households.csv file for RSM scenarios. 

## Configuration
- 'config/scenarios.yaml' file specifies the user configuration for the three scenarios. This file does not need to be modified unless config changes are desired by the user. 

## How to Run
- Open Anaconda prompt and change the directory to visualizer folder in your local RSM repository. 

- Run the process scenario script by typing command below and then press enter.

  `python process_scenarios.py`

- Processing the scenario using pipeline will take some time. 

- Next, open this link in the web browser
  https://simwrapper.github.io/site/

- Click on 'Enter Site' button, then click on 'add local folder' and add simwrapper directory (visualizer\simwrapper) to run the SimWrapper Visualizer for RSM. 

