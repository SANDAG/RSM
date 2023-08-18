
##  Needs
The time needed to configure, run, and summarize results from ABM2+ is too slow to support a nimble, challenging, and engagement-oriented planning process. SANDAG needs a tool that quickly approximates the outcomes of ABM2+. The rapid strategic model, or RSM, was built for this purpose.

ABM2+ Schematic is shown below
![](images\abm2plus_schematic.PNG)

## Design
### Reducing the number of zones reduces model runtime. 

* MGRAs are aggregated into Rapid Zones based on their proximity to each other and similarity in regards to mode choice decisions.

* Number of rapid zones can be quickly changed to assess trade-offs between runtime and how well the RSM results match the ABM2+ results.

* Initial testing revealed 2,000 rapid zones is approximately optimal and will be used in initial deployments. For reference, ABM2+ has ~23,000 MGRAs and ~5,000 TAZs.

### Reducing the number of model components reduces runtime.

* Most, but not all, of the policies of interest to SANDAG primarily impact resident passenger travel. 

### Reducing the number of global iterations reduces runtime.

## ABM2+ vs RSM 
### ABM2+ simulates population:
* First iteration: 25 percent
* Second iteration: 50 percent
* Third iteration: 100 percent

### RSM simulates population: 
* Higher rate in zones with large changes in accessibiility
* Lower rates in zones with small changes in accessibility
* This attempts to mitigate the impact of reducing the number of global iterations from 3 to 2.     
