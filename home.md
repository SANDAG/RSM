# SANDAG Rapid Strategic Model

Welcome to the SANDAG Rapid Strategic Model documentation site!
 
 
## Introduction
The travel demand model SANDAG used for the 2021 regional plan, referred to as ABM2+, is one of the most sophisticated modeling tools used anywhere in the world. Its activity-based approach to representing travel is behaviorally rich; the representations of land development and transportation infrastructure are represented in high fidelity spatial detail. An operational shortcoming of ABM2+ is it requires significant computational resources to carry out a simulation. A typical forecast year simulation of ABM2+ takes over 40 hours to complete on a high end workstation (e.g., 48 physical computing cores and 256 gigabytes of RAM). The components of this runtime include:
Three iterations of the resident activity-based model, each about 6 hours; and, Four iterations of roadway and transit assignment, with each iteration taking about 90 minutes.
The computational time of ABM2+, and the likely computational time of the successor to ABM2+ (ABM3), hinders SANDAG's ability to carry out certain analyses in a timely manner. For example, if an analyst wants to explore 10 different roadway pricing schemes for a select corridor, a month of computation time would be required.

SANDAG needs a tool that quickly approximates the outcomes of ABM2+. We will therefore build such a tool, which will be referred to henceforth as the Rapid Strategic Model, or RSM. In creating the tool, we will also be mindful of other limitations of ABM2+ and ABM3, including simulating policies that are currently tedious to represent in the models' framework. The primary purpose of the RSM is to improve the speed of the resident passenger component of the broader modeling system. However, we will be mindful of opportunities outside of the resident passenger component to improve SANDAG's analytical planning workflow during the RSM project.

