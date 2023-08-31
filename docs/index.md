# SANDAG Rapid Strategic Model

Welcome to the SANDAG Rapid Strategic Model documentation site!


## Introduction
The travel demand model SANDAG used for the 2021 regional plan, referred to as ABM2+, is one of the most sophisticated modeling tools used anywhere in the world. Its activity-based approach to representing travel is behaviorally rich; the representations of land development and transportation infrastructure are represented in high fidelity spatial detail. An operational shortcoming of ABM2+ is it requires significant computational resources to carry out a simulation. A typical forecast year simulation of ABM2+ takes over 40 hours to complete on a high end workstation (e.g., 48 physical computing cores and 256 gigabytes of RAM). The components of this runtime include:

- Three iterations of the resident activity-based model, each about 6 hours
- Four iterations of roadway and transit assignment, with each iteration taking about 90 minutes

The computational time of ABM2+, and the likely computational time of the successor to ABM2+ (ABM3), hinders SANDAG's ability to carry out certain analyses in a timely manner. For example, if an analyst wants to explore 10 different roadway pricing schemes for a select corridor, a month of computation time would be required.

SANDAG requires a tool capable of quickly approximating the outcomes of ABM2+. Therefore, a tool was built for this purpose, referred to henceforth as the Rapid Strategic Model (RSM). The primary objective of the RSM was to enhance the speed of the resident passenger component within the broader modeling system and produce results that closely aligned with ABM2+ for policy planning requirements. 

## Use Cases and Key Limitations
Based on set of tests done as part of this project, RSM performs well for regional scale roadway projects (e.g., auto operating costs and mileage fee, TNC costs and wait times etc.) and regional scale transit projects (transit fare, headway changes etc.). RSM also performed well for land-use change policies. Lastly, RSM was also tested for local roadway changes (e.g., managed lanes conversion) and local transit changes (e.g., new BRT line), and the results indicate that those policies are reasonably represented by RSM as well. 

Here are some of the current limitations of RSM:

- The scope of the RSM is “passenger” travel. Policies and/or infrastructure that primarily impact commercial travel (e.g., truck lanes) will not be well represented.
- Minor re-calibration of the mode choice was necessary to match observed walk trips. Large changes to the number of zones will likely require recalibration.
- The spatial aggregation reduces the RSM’s ability to represent to simulate infrastructure and/or policies that act at small scales (e.g., pedestrian infrastructure).
- Policies related to the adoption of automated vehicles cannot be currently represented. RSM currently skips running the Household AV Allocation module.
- While the RSM has been tested, the testing has not been extensive. More extensive testing is likely to surface additional issues. Additional testing will be required to evaluate if RSM can be a viable tool for other policies that interests SANDAG.