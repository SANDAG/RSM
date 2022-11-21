#
# On the host machine, on linux or macOS terminal run:
#
# ```shell
# docker run -v $(pwd):/home/mambauser/sandag_rsm -w /home/mambauser/sandag_rsm sandag_rsm python RSM_pregame.py
# ```
#
# or in `cwd` on Windows, run:
#
# ```shell
# docker run -v %cd%:/home/mambauser/sandag_rsm -v "C:\VY-Projects\Github\RSM\notebooks\data-dl":/data -w /home/mambauser/sandag_rsm sandag_rsm python RSM_pregame.py
# ```
#

import os
import sys
import pandas as pd
import numpy as np
from sandag_rsm.logging import logging_start
from sandag_rsm.assembler import rsm_assemble

#
#   CONFIG HERE
#   All these files should be relative to and within in the current working dir
#

logging_start()

rsm_dir = sys.argv[1]
org_model_dir = sys.argv[2]
iteration = sys.argv[3]


#input files
ORG_INDIV_TRIPS = os.path.join(org_model_dir, "output", "indivTripData_3.csv")
ORG_JOINT_TRIPS = os.path.join(org_model_dir, "output", "jointTripData_3.csv")
RSM_INDIV_TRIPS = os.path.join(rsm_dir, "output", "indivTripData_" + str(iteration) + ".csv")
RSM_JOINT_TRIPS = os.path.join(rsm_dir, "output", "jointTripData" + str(iteration) + ".csv")
HOUSEHOLDS = os.path.join(rsm_dir, "input", "households.csv")


final_trips_rsm, combined_trips_by_zone = rsm_assemble(
    ORG_INDIV_TRIPS,
    ORG_JOINT_TRIPS,
    RSM_INDIV_TRIPS,
    RSM_JOINT_TRIPS,
    HOUSEHOLDS
)












