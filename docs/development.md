
##  Needs
The time needed to configure, run, and summarize results from ABM2+ is too slow to support a nimble, challenging, and engagement-oriented planning process. SANDAG needs a tool that quickly approximates the outcomes of ABM2+. The rapid strategic model, or RSM, was built for this purpose.

ABM2+ Schematic is shown below
![](images\development\abm2plus_schematic.PNG)

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

## Integration Plan
A challenge in the RSM development is that the model is intended to approximate the outcomes of ABM3. The design plan therefore assumes that ABM3 outcomes will be used to inform an RSM model run. ABM3 is, however, also under development. We must therefore approach the RSM development carefully, designing around what we expect ABM3 to produce and testing with, initially, dummy files that represent ABM3 output.

For the MVP, the key outputs of interest from ABM3 are as follows:

* Disaggregate accessibilities
* MGRA and TAZ boundaries
* MGRA data
* Zone connectors (if a one-zone approach to transit skimming/assignment is used) - drive, walk access to transit, drive access to transit
* Trip list
* Non-resident passenger demand, e.g., commercial vehicle, cross border, airport access

Mechanically, the WSP team will request illustrative ABM3 files from SANDAG that can be used to build the RSM components. We will then conduct preliminary (i.e., those needed for development) tests of the procedures using these demonstration files. Formal testing of the procedures will come after an operational version of ABM3 is complete (see [Sample Test Procedure in Visualizer](visualizer.md#Sample-Test-Procedure)).

## User Experience
The RSM will repurpose the ABM3 Emme-based GUI. The options will be updated to reflect the RSM options, as will the input file locations and other parameters. The RSM user experience will, therefore, be nearly the same as the ABM3 user experience.

Because the RSM will be a standalone Python package, it can also be run from a Jupyter Notebook, if desired.

