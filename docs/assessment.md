# Assessment

##RSM Testing Strategy
Each of the methods in RSM will be tested to ensure that they are working as expected. These tests will leverage Python's capabilities, specifically the pytest package. Tests that do not depend on Emme will be executed when code is checked in using GitHub Actions, allowing for a continuous integration workflow. Tests that depend on Emme cannot be run on GitHub Actions due to Emme's licensing requirement. These tests will be run on a server with access to Emme prior to code being brought into the develop or main branch of the GitHub repository.

Table 1. RSM Testing Strategy
![](images\assessment\table_1.PNG)

##RSM Performance Assessment Results

###Runtime 
![](images\assessment\runtime_performance.PNG)

###Validation
![](images\assessment\validation_performance.PNG)

###Auto Operating Cost Elasticity - plus 50%
![](images\assessment\elasticity_aoc_plus_50%.PNG)

###Auto Operating Cost Elasticity - minus 50%
![](images\assessment\elasticity_aoc_minus_50%.PNG)

###Elasticity Comparison - AOC - plus 50% 
![](images\assessment\elasticity_CMPR_AOC_plus_50%.PNG)

###Elasticity Comparison - AOC - minus 50% 
![](images\assessment\elasticity_CMPR_AOC_minus_50%.PNG)

###Elasticity Comparison - Job HH Balance 
![](images\assessment\elasticity_comparison_JOB_HH.PNG)

###Elasticity Comparison - Mixed Land Use 
![](images\assessment\elasticity_comparison_Mixed_LU.PNG)

###Elasticity Comparison - 100% Automated Vehicle Adoption
![](images\assessment\elasticity_comparison_AV_100%.PNG)

###Elasticity Comparison - Ride Hailing Cost - minus 50% 
![](images\assessment\elasticity_CMPR_RHC_minus_50%.PNG)

###Boarding Comparison - Rapid 637 BRT  
![](images\assessment\Boarding_comparison_Rapid_637_BRT.PNG)
