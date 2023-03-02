import pandas as pd
import numpy as np
import os
import yaml as yml
import sys
import subprocess

config_file = "scenario.yaml"
with open(os.path.join(config_file), 'r') as f:
    config = yml.safe_load(f)
f.close()

# set parameters
base_path = os.getcwd()
settings_file_rsm = "settings.yaml"
settings_file_base = "settings_donor_model.yaml"
pipeline_path = os.path.join(base_path, "pipeline")
visualizer_path = base_path


## run RSM scenarios
for scenario in config["rsm_scenarios"]:
    path_input = os.path.join(base_path + config["rsm_scenarios"][scenario]["input"])
    path_report = os.path.join(base_path + config["rsm_scenarios"][scenario]["report"])
    path_output = os.path.join(base_path + config["rsm_scenarios"][scenario]["output"])
    path_shapefile = os.path.join(base_path + config["shapefiles"])

    with open(os.path.join("pipeline\\config", settings_file_rsm), 'r') as f:
        settings = yml.safe_load(f)
    settings['extract'][0]['filepath'] = path_report
    settings['extract'][1]['filepath'] = path_input
    settings['load']['outdir'] = path_output
    f.close()

    with open(os.path.join("pipeline\\config", settings_file_rsm), "w") as f:
        yml.safe_dump(settings, f, sort_keys=False)

    if not os.path.exists(path_output):
        os.makedirs(path_output)

    print("Start Running Pipeline for " + scenario)
    r = subprocess.call(["run-pipeline.bat", "settings.yaml", pipeline_path])
    if (r==0):
        print("Pipeline successfully finished")
    else: 
        print("Pipeline not successfully finished for " + scenario)


## run Base scenarios
for scenario in config["base_scenarios"]:
    path_input = os.path.join(base_path + config["base_scenarios"][scenario]["input"])
    path_report = os.path.join(base_path + config["base_scenarios"][scenario]["report"])
    path_output = os.path.join(base_path + config["base_scenarios"][scenario]["output"])
    path_shapefile = os.path.join(base_path + config["shapefiles"])

    with open(os.path.join("pipeline\\config", settings_file_base), 'r') as f:
        settings = yml.safe_load(f)
    settings['extract'][0]['filepath'] = path_report
    settings['extract'][1]['filepath'] = path_input
    settings['load']['outdir'] = path_output
    f.close()

    with open(os.path.join("pipeline\\config", settings_file_base), "w") as f:
        yml.safe_dump(settings, f, sort_keys=False)

    if not os.path.exists(path_output):
        os.makedirs(path_output)

    print("Start Running Pipeline for " + scenario)
    r = subprocess.call(["run-pipeline.bat", "settings_donor_model.yaml", pipeline_path])
    if (r==0):
        print("Pipeline successfully finished")
    else: 
        print("Pipeline not successfully finished for " + scenario)

## Run visualizer support script
rsm_scenarios = list()
base_scenarios = list()
for scenario in config["rsm_scenarios"]:
    rsm_scenarios.append(scenario) 
base_scenarios = list()
for scenario in config["base_scenarios"]:
    base_scenarios.append(scenario)    

with open("config_visualizer_support.yml", 'r') as f:
    config_visulizer_support = yml.safe_load(f)
config_visulizer_support["parameters"]["rsm_scenario_list"] = rsm_scenarios
config_visulizer_support["parameters"]["base_scenario_list"] = base_scenarios
f.close()

with open("config_visualizer_support.yml", "w") as f:
    yml.safe_dump(config_visulizer_support, f, sort_keys=False)

print("Visualizer Support Script")
r = subprocess.call(["run-visulizer-support.bat", pipeline_path, visualizer_path])
if (r==0):
    print("Script successfully finished")
else: 
    print("Script not successfully finished" )    





