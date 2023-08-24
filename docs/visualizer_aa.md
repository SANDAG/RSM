# RSM Visualizer
RSM Visualizer is a useful tool which enables user to visualize and compare numerous metrics from multiple RSM model runs in a short matter of time. It deploys SimWrapper platform, a powerful web-based data visualization tool for building disaggregate transportation simulations. User only needs to identify the path for different RSM scenarios and run a script which provides all the necessary summaries to feed SimWrapper. 
They don't need to code in any language to use SimWrapper -- you point it at your files, and use predefined (YAML) configuration files to tell SimWrapper what to do. For the full instruction on how to run the Visualizer please see [here][placeholder for guideline] 

## Overview
Visualizer aims to ease the process of comparing RSM scenarios. It has three tiers of data processing from getting model outputs to create visuals:

- [Pipeline](#Pipeline)
- [Post_Processing](#Post_Processing)
- [SimWrapper](#SimWrapper)

### Pipeline

SANDAG Data Pipeline Tool aims to aid in the process of building data pipelines that ingest, transform, and summarize data by taking advantage of the parameterization of data pipelines. Rather than coding from scratch, configure a few files and the tool will figure out the rest. Using pipeline helps to get the desired model summaries in a csv format. See [here](https://github.com/SANDAG/RSM/blob/visualizer/visualizer/pipeline/README.md) to learn how the tool works. Note that, for this version of visualizer certain number of summaries has been included in pipeline. If you wish to add more summaries you can do it by adding those to pipeline [settings](https://github.com/SANDAG/RSM/blob/visualizer/visualizer/pipeline/config/settings.yaml), [processor](https://github.com/SANDAG/RSM/blob/visualizer/visualizer/pipeline/config/processor.csv) and [expression](https://github.com/SANDAG/RSM/blob/visualizer/visualizer/pipeline/config/expressions.csv) files.

### Post_Processing

In addition to data pipeline , there is a support [script](https://github.com/SANDAG/RSM/blob/visualizer/visualizer/visualizer_support.py) to add necessary summaries and perform all the data manipulations which cannot be done in pipeline in order to get the data in a format SimWrapper requires. Similar to pipleine, you can also modify the support script to add any summaries in order to use them in Simwrapper. Once you point SimWrapper to your collection of files, some visualizations will be immediately available depending on what SimWrapper finds in your folder.


### SimWrapper

The final step is to use the summary files to generate visuals. SimWrapper is a web platform that can display either individual full-page data visualizations, or collections of visualizations in "dashboard" format. It expects your simulation outputs to just be regular files on your filesystem somewhere; there is no centralized database or cloud server that you need to upload your results to.
For visualizations, you'll create tiny configuration files (in YAML format) which tell SimWrapper what to load, how to lay out the dashboards, and which provide all the config details to get it started. These files can be collected in project folders and then will apply to all runs in a set of folders, if you want. See [here](https://simwrapper.github.io/docs/) to get more familiar with SimWrapper.

## How it works

All the abovementioned steps are being controlled through a [script](https://github.com/SANDAG/RSM/blob/visualizer/visualizer/process_scenarios.py) which navigates the process through the end.

* **Input**: you need to identify the directory of scenarios files you want to compare. There are two categories of scenarios in the scenario [file](https://github.com/SANDAG/RSM/blob/visualizer/visualizer/config/scenarios.yaml). RSM scenarios are any scenarios run for RSM and Donor model runs are original ABM model runs. You need to specify the directory of input and report folders of all the desired scenarios in this configuration file. You can add new scenarios by adding the same configurations to both RSM and Donor scenario categories. Those files will be used in the pipeline and data processing steps and will create summaries in the processed folder for SimWrapper.

* **Processor**: [process_scenarios.py](https://github.com/SANDAG/RSM/blob/visualizer/visualizer/process_scenarios.py) utilizes the scenarios files and creates all the required summaries and places them in processed folder for SimWrapper.

* **SimWrapper**: As mentioned above, SimWrapper uses configuration files (in YAML format) which tell SimWrapper what to load. For each visualization type there are certain specifications to use in the config file. You can find the current visualizer configuration files [here](https://github.com/SANDAG/RSM/blob/visualizer/visualizer/simwrapper)

## Visuals

Currently there are five default visualization summaries for user:

### Bar Charts:
These charts are for comparing VMT, mode shares, transit boardings and trip purpose by time-of-day distribution. Here is a snapshot of sample YAML configuration [file](https://github.com/SANDAG/RSM/blob/visualizer/visualizer/simwrapper/dashboard-charts.yaml) and how the visual looks on SimWrapper:

<img align="center" width="600" border=1 src="https://github.com/SANDAG/RSM/blob/update_docs/docs/images/visualizer/image_7.PNG">

you can add as many charts as you want to the layout. each chart should specify a csv file for the summaries and columns should match the csv file column name. There are also other specifications for the bar charts which you learn about more [here](https://simwrapper.github.io/docs/bar-area-line)


<img align="center" width="1100" border=1 src="https://github.com/SANDAG/RSM/blob/update_docs/docs/images/visualizer/image_8.PNG">


### Network Flows:

These charts are for comparing flow and VMT on the network. You can compare any two scenarios on one network. Here is a snapshot of the configuration [file](https://github.com/SANDAG/RSM/blob/visualizer/visualizer/simwrapper/dashboard-network.yaml) and how the visual looks on SimWrapper:

<img align="center" width="600" border=1 src="https://github.com/SANDAG/RSM/blob/update_docs/docs/images/visualizer/image_9.PNG">

For each network you need the csv files for two scenario summaries and an underlying network file which should be in geojson format. The supporting [script](https://github.com/SANDAG/RSM/blob/visualizer/visualizer/process_scenarios.py) creates the geojson files from the model outputs for the SimWrapper. On this network you can see the comparison of flows between RSM and Donor models. For more info on network visualization specification see [here](https://simwrapper.github.io/docs/link-vols)

<img align="center" width="1100" border=1 src="https://github.com/SANDAG/RSM/blob/update_docs/docs/images/visualizer/image_10.PNG">


### Sample Rate Map:

This visual is a map for showing the RSM sample rates for each zone. Here is a snapshot of the configuration [file](https://github.com/SANDAG/RSM/blob/visualizer/visualizer/simwrapper/dashboard-sample-rate-maps.yaml)  and how the map looks on SimWrapper.

<img align="center" width="600" border=1 src="https://github.com/SANDAG/RSM/blob/update_docs/docs/images/visualizer/image_11.PNG">

For each map you need a csv file of sample rates and the map of zones in .shp format. For more info on network visualization specification see [here](https://simwrapper.github.io/docs/shapefiles)

<img align="center" width="1100" border=1 src="https://github.com/SANDAG/RSM/blob/update_docs/docs/images/visualizer/image_12.PNG">



### Zero Car Map:
This visual is a map for showing the zero-car household distribution. Here is a snapshot of the configuration [file](https://github.com/SANDAG/RSM/blob/visualizer/visualizer/simwrapper/dashboard-zero-car-maps.yaml) and how it looks on SimWrapper.

<img align="center" width="600" border=1 src="https://github.com/SANDAG/RSM/blob/update_docs/docs/images/visualizer/image_13.PNG">

For each map you need a csv file of household rates and the map of zones in .shp format. For more info on network visualization specification see [here](https://simwrapper.github.io/docs/shapefiles)

<img align="center" width="1100" border=1 src="https://github.com/SANDAG/RSM/blob/update_docs/docs/images/visualizer/image_14.PNG">



### OD flows:

This chart is for showing OD trip flows. Here is a snapshot of the configuration [file](https://github.com/SANDAG/RSM/blob/visualizer/visualizer/simwrapper/viz-od-donor-model.yaml) and how it looks on SimWrapper.

<img align="center" width="600" border=1 src="https://github.com/SANDAG/RSM/blob/update_docs/docs/images/visualizer/image_15.PNG">

For each map you need a csv file of od trip flows and the map of zones in .shp format. For more info on network visualization specification see [here](https://simwrapper.github.io/docs/aggregate-od)

<img align="center" width="1100" border=1 src="https://github.com/SANDAG/RSM/blob/update_docs/docs/images/visualizer/image_16.PNG">




You can also modify the data and configuration of each visual on SimWrapper server. For each visual, there is a configuration button (see below), where you can add data, and modify all the map configurations. You can also export these configurations into a YAML file so you can use it in future.

<img align="center" width="600" border=1 src="https://github.com/SANDAG/RSM/blob/update_docs/docs/images/visualizer/image_17.PNG">



