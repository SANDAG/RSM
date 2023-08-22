
##  Needs
The time needed to configure, run, and summarize results from ABM2+ is too slow to support a nimble, challenging, and engagement-oriented planning process. SANDAG needed a tool that quickly approximates the outcomes of ABM2+. The rapid strategic model, or RSM, was built for this purpose.

ABM2+ Schematic is shown below
![](images\abm2plus_schematic.PNG)



## Design Considerations

Reducing the number of zones reduces model runtime.

* MGRAs are aggregated into Rapid Zones based on their proximity to each other and similarity in regards to mode choice decisions.

* RSM will have variable number of analysis zones and that can be quickly changed to assess trade-offs between runtime and how well the RSM results match the ABM2+ results.

* Initial testing revealed 2,000 rapid zones is approximately optimal and will be used in initial deployments. For reference, ABM2+ has ~23,000 MGRAs and ~5,000 TAZs.

Reducing the number of model components reduces runtime.

* Most, but not all, of the policies of interest to SANDAG primarily impact resident passenger travel. 
* Therefore, RSM will only run passenger travel component while maintaining the other demand components fixed. 

Reducing the number of global iterations reduces runtime.

- If the RSM results are in the same ballpark as ABM2+, reduce the number of global iterations from 3 to 2 for the model. 

Reducing sample rate reduces runtime.

- Runtime of the resident model will reduce if less population is simulated. 
- ABM2+ simulates population as 25 percent (first iteration), 50 percent (second iteration) and 100 percent (third iteration). 
- RSM will attempt to intelligently sample population and vary it by TAZ with higher sample rate in zones with large changes in accessibility and lower rates in zones with small changes in accessibility. 
- RSM could also have higher sampling in zones around the analysis project and lower elsewhere. 



## Architecture

The RSM is developed as a Python package and the required modules are launched when running the existing SANDAG travel model as Rapid Model. It takes as input a complete ABM2+ model run and has following modules: 

#### Zone Aggregator

#### Input Aggregator

#### Translate Demand

#### Intelligent Sampler

#### Intelligent Assembler



## User Experience

The RSM repurposes the ABM2+ Emme-based GUI. The options will be updated to reflect the
RSM options, as will the input file locations and other parameters. The RSM user experience will,
therefore, be nearly the same as the ABM2+ user experience.



## Calibration