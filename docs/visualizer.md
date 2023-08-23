## Introduction
The proposed MVP visualization tool is a SimWrapper dashboard. SimWrapper is an open-source simulation visualization software package that has recently been adapted for activity-based models and set up to work with ActivitySim software. The software works by creating a mini file server to host reduced data summaries of ActivitySim software. The dashboard is created via YAML files, which can be customized to automate interactive report summaries, such as charts and summary tables, while also enabling integration of the RSMAZ geographical component for an interactive map display. An example implementation of the YAML file setup is shown below.

![](images\visualizer\YAML_example.PNG)

The MVP visualization tool will consist of no fewer than ten visualization tabs presenting RSM output, as summarized in Table 1

Table 1. MVP Visualization Plan
![](images\visualizer\table_1.PNG)


## Key Limitations
1. The scope of the RSM is "passenger" travel.                                                                                                  
    - Policies and/or infrastructure that primarily impact commercial travel (e.g., truck lanes) will not be well represented.                     
                                                                                                                                             
2. Mode choice recalibration                                                                                                                    
    - Minor re-calibration of the mode choice to match observed walk trips.                                                                        
    - Changing the number of zones will likely require recalibration.                                                                              
                                                                                                                                             
3. Spatial aggregation                                                                                                                          
    - Reduces the RSM's ability to represent to simulate infrastructure and/or policies that act at small scales (e.g., pedestrian infrastructure).
        
## Sample Test Procedure
 
###Test Procedure for RSM_ST_1 

Copy **rsm_visualizer** from **T:\ABM\ETG_Space\visualizer\rsm_visualizer** folder into **RSM_ST_1** folder. The config files for ST1 are already set. 

Add the model data into external folder as we talked before. You should have four folders for model runs in the external folder and then add the report and input folder from model run folders in each of these folders. **[Don't delete the shapefile folder.]**

![](images\visualizer\image_1.PNG)

As the final step, you need to copy and rename couple of files:

1.	For both **build and base abm runs** Copy the following highlighted files (hwyLoad shapefiles) from **:\ABM\ETG_Space\RSM_ST_1\report** to **abm2p_base\report** and **ab2p_build\report** folders in the external data folder.

![](images\visualizer\image_2.PNG)

2.	For both **build and base abm runs**, from the {++output++} folder of the corresponding source abm run, copy **householdData_3.csv, personData_3.csv** and **jointTourData_3.csv** into **abm2p_base\report** and **ab2p_build\report** folders in the external data folder.

You can then follow the **README** file in the **rsm_visualizer** folder to run the process

###For other sensitivity tests:

Copy **rsm_visualizer** from **T:\ABM\ETG_Space\visualizer\rsm_visualizer** folder in the corresponding sensitivity test folder. Follow the same procedure as before to create four subfolders in the external folder. Follow the excel spreadsheet to find correct source directories for each four runs.

In the **rsm_visualizer** folder you copied, go to **config\scenarios.yml**. Search for **rsm_build_st_1** and replace them by the corresponding sensitivity test name you picked as the folder name in the external folder (e.g. **rsm_build_st_2**)

![](images\visualizer\image_3.PNG)

In the **rsm_visualizer** folder you copied, go to **simwrapper\dashboard-charts.yml**. Search for **rsm_build_st_1** and replace them by corresponding sensitivity test name (e.g. **rsm_build_st_2**)

![](images\visualizer\image_4.PNG)
![](images\visualizer\image_5.PNG)


As the final step, you need to copy and rename couple of files:

1. For both **build and base abm runs** Copy the following highlighted files (hwyLoad shapefiles) from **T:\ABM\ETG_Space\RSM_ST_1\report** to **abm2p_base\report** and **ab2p_build\report** folders in the external data folder.

![](images\visualizer\image_6.PNG)

2. For both **build and base abm runs**, from the output folder of the corresponding source abm runs, copy **householdData_3.csv** into **abm2p_base\report** and **ab2p_build\report** folders in the external data folder.

You can then follow the **README** file in the **rsm_visualizer** folder to run the process.