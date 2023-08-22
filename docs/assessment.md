# Assessment

## RSM Configuration

Different scenario runs with varying configurations were done during the RSM development to then select a final set of configuration parameters to move forward with the overall assessment of RSM. 

TODO: Include table with different configurations and corresponding run time. 



##Runtime Comparison 

For base year 2016 simulation, below is the runtime comparison of ABM2+ vs RSM. 

![](images\runtime_performance.PNG)



##Base Year Validation

With the model configuration (Rapid Zones, Global Iterations, Sample Rate, etc.) for RSM as identified above, tour and trip mode choice calibration was performed to match the RSM mode share to ABM2+ mode share, primarily to match the walk trips.

Note that a minor calibration will be required for RSM when number of rapid zones are changed. 

Here is the table of ABM2+ and RSM outcome comparison after the RSM calibration. The metrics used are some of the regional level key metrics. Volume comparison for the roadway segment on I-5 and I-8 were chosen at random. 

![](images\validation_performance.PNG)



After validating the RSM for base year with the chosen design configuration, RSM was used to carry out hypothetical planning studies related to some broader use-cases. Model results from both RSM and ABM2+ were compared for each of the sensitivity test to assess the performance of RSM and evaluate if RSM could be a viable tool for such policy planning. 

For each test, a few key metrics from ABM2+ No Action, ABM2+ Action, RSM No Action and RSM Action scenario runs were compared. The goal was to have RSM and ABM2+ show similar sensitivities for action vs no-action. 

## Regional Highway Changes

####Auto Operating Cost - 50% Increase

![](images\elasticity_aoc_plus_50%.PNG)



####Auto Operating Cost - 50% Decrease

![](images\elasticity_aoc_minus_50%.PNG)



#### Ride Hailing Cost - 50% decrease

![](images\elasticity_CMPR_RHC_minus_50%.PNG)



#### Automated Vehicles - 100% Adoption

In SANDAG model, the AV adoption is analyzed by capturing the zero occupancy vehicle movement as simulated in the Household AV Allocation module. For RSM, this AV allocation module is skipped, which is why RSM is not a viable tool for evaluating policies related to automated vehicles. 

![](images\elasticity_comparison_AV_100%.PNG)



## Land Use Changes

RSM and ABM2+ shows similar sensitivities for the two tested scenarios with land use change. 

#### Change in land use - Job Housing Balance

![](images\elasticity_comparison_JOB_HH.PNG)



####Change in land use - Mixed Land Use 

![](images\elasticity_comparison_Mixed_LU.PNG)



## Regional Transit Changes

#### Transit Fare



#### Transit Frequency







## Local Highway Changes

#### Managed Lane Conversion





## Local Transit Changes

#### Rapid 637 BRT

TODO: Add some text to explain how this test was performed using the study area parameter

TODO: Add outcome screenshot





## Use Cases and Key Limitations