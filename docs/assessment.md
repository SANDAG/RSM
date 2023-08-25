## RSM Configuration

Different scenario runs with varying configurations were done during the RSM development to then select a final set of configuration parameters to move forward with the overall assessment of RSM. 

TODO: Include table with different configurations and corresponding run time. 

## Calibration
Aggregating the ABM zones to RSM zones, distorts the walk trips share coming out of the model. With the model configuration (Rapid Zones, Global Iterations, Sample Rate, etc.) for RSM as identified above, tour mode choice calibration was performed to match the RSM mode share to ABM2+ mode share, primarily to match the walk trips. A calibration constant was applied to the tour mode choice UEC to School, Maintenance, Discretionary tour purpose. The mode share for Work and University purpsoe were reasonable, therefore the calibration wasn't applied to those purposes. 

Note that a minor calibration will be required for RSM when number of rapid zones are changed.

Here is how the mode share and VMT compares before and after the calibration for RSM. Donor model in the charts below refers to the ABM2+ run. 

![](images\assessment\mode_share_calibrated.PNG)

![](images\assessment\vmt_by_class_calibrated.PNG)

![](images\assessment\total_vmt_calibrated.PNG)

## Base Year Validation
Here is the table of ABM2+ and RSM outcome comparison after the RSM calibration. The metrics used are some of the regional level key metrics. Volume comparison for the roadway segment on I-5 and I-8 were chosen at random. 

![](images\assessment\validation_performance.PNG)


## Runtime Comparison 
For base year 2016 simulation, below is the runtime comparison of ABM2+ vs RSM. 

![](images\assessment\runtime_performance.PNG)

## Sensitivity Testing
After validating the RSM for base year with the chosen design configuration, RSM was used to carry out hypothetical planning studies related to some broader use-cases. Model results from both RSM and ABM2+ were compared for each of the sensitivity test to assess the performance of RSM and evaluate if RSM could be a viable tool for such policy planning. 

For each test, a few key metrics from ABM2+ No Action, ABM2+ Action, RSM No Action and RSM Action scenario runs were compared. The goal was to have RSM and ABM2+ show similar sensitivities for action vs no-action. 

### Regional Highway Changes

####Auto Operating Cost - 50% Increase

![](images\assessment\elasticity_aoc_plus_50%.PNG)



####Auto Operating Cost - 50% Decrease

![](images\assessment\elasticity_aoc_minus_50%.PNG)



#### Ride Hailing Cost - 50% decrease

![](images\assessment\elasticity_CMPR_RHC_minus_50%.PNG)



#### Automated Vehicles - 100% Adoption

In SANDAG model, the AV adoption is analyzed by capturing the zero occupancy vehicle movement as simulated in the Household AV Allocation module. For RSM, this AV allocation module is skipped, which is why RSM is not a viable tool for evaluating policies related to automated vehicles. 

![](images\assessment\elasticity_comparison_AV_100%.PNG)



### Land Use Changes

RSM and ABM2+ shows similar sensitivities for the two tested scenarios with land use change. 

#### Change in land use - Job Housing Balance

![](images\assessment\elasticity_comparison_JOB_HH.PNG)



####Change in land use - Mixed Land Use 

![](images\assessment\elasticity_comparison_Mixed_LU.PNG)



### Regional Transit Changes

#### Transit Fare

TODO: Add some text to explain how this test was performed using the study area parameter
TODO: Add outcome screenshot

#### Transit Frequency

TODO: Add some text to explain how this test was performed using the study area parameter
TODO: Add outcome screenshot


### Local Highway Changes

#### Managed Lane Conversion

TODO: Add some text to explain how this test was performed using the study area parameter
TODO: Add outcome screenshot



### Local Transit Changes

#### Rapid 637 BRT

TODO: Add some text to explain how this test was performed using the study area parameter
TODO: Add outcome screenshot


## Use Cases and Key Limitations
Based on set of tests done as part of this project, RSM performs well for regional scale roadway projects (e.g., auto operating costs and mileage fee, TNC costs and wait times etc.) and regional scale transit projects (transit fare, headway changes etc.). RSM also performed well for land-use change policies. Lastly, RSM was also tested for local roadway changes (e.g., managed lanes conversion) and local transit changes (e.g., new BRT line), and the results indicate that those policies are reasonably represented by RSM as well. 

Here are some of the current limitations of RSM:

- The scope of the RSM is “passenger” travel. Policies and/or infrastructure that primarily impact commercial travel (e.g., truck lanes) will not be well represented.
- Minor re-calibration of the mode choice was necessary to match observed walk trips. Large changes to the number of zones will likely require recalibration.
- The spatial aggregation reduces the RSM’s ability to represent to simulate infrastructure and/or policies that act at small scales (e.g., pedestrian infrastructure).
- Policies related to the adoption of automated vehicles cannot be currently represented. RSM currently skips running the Household AV Allocation module.
- While the RSM has been tested, the testing has not been extensive. More extensive testing is likely to surface additional issues. Additional testing will be required to evaluate if RSM can be a viable tool for other policies that interests SANDAG.