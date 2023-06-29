#
# Assembles trips from RSM ABM and FULL SANDAG ABM to build final trip tables
# This python file is being called in bin/runRSMAssembler.cmd
#
# inputs:
#   rsm_dir: RSM main directory
#   org_model_dir: Donor model directory
#   iteration: Iteration number of the model run
#

import os
import sys
import logging
import shutil
main_path = os.path.dirname(os.path.realpath(__file__)) + "/../"
sys.path.append(main_path)
from rsm.logging import logging_start
from rsm.assembler import rsm_assemble
from rsm.utility import *

rsm_dir = sys.argv[1]
org_model_dir = sys.argv[2]
iteration = sys.argv[3]

logging_start(
    filename=os.path.join(rsm_dir, "logFiles", "rsm-logging.log"), level=logging.INFO
)
logging.info("start logging rsm_assembler")

#input files
ORG_INDIV_TRIPS = os.path.join(org_model_dir, "output", "indivTripData_3.csv")
ORG_JOINT_TRIPS = os.path.join(org_model_dir, "output", "jointTripData_3.csv")
RSM_INDIV_TRIPS = os.path.join(rsm_dir, "output", "indivTripData_" + str(iteration) + ".csv")
RSM_JOINT_TRIPS = os.path.join(rsm_dir, "output", "jointTripData_" + str(iteration) + ".csv")

HOUSEHOLDS = os.path.join(org_model_dir, "input", "households.csv")
MGRA_CROSSWALK = os.path.join(rsm_dir, "input", "mgra_crosswalk.csv")

#creating copy of individual and joint trips file
shutil.copy(RSM_INDIV_TRIPS, os.path.join(rsm_dir, "output", "indivTripData_abm_"+ str(iteration) + ".csv"))
shutil.copy(RSM_JOINT_TRIPS, os.path.join(rsm_dir, "output", "jointTripData_abm_"+ str(iteration) + ".csv"))

ABM_PROPERTIES_FOLDER = os.path.join(rsm_dir, "conf")
ABM_PROPERTIES = os.path.join(ABM_PROPERTIES_FOLDER, "sandag_abm.properties")
RUN_ASSEMBLER = int(get_property(ABM_PROPERTIES, "run.rsm.assembler"))
SAMPLE_RATE = float(get_property(ABM_PROPERTIES, "rsm.default.sampling.rate"))

#RSM Assembler
final_ind_trips, final_jnt_trips = rsm_assemble(
    ORG_INDIV_TRIPS,
    ORG_JOINT_TRIPS,
    RSM_INDIV_TRIPS,
    RSM_JOINT_TRIPS,
    HOUSEHOLDS,
    MGRA_CROSSWALK,
    SAMPLE_RATE,
    RUN_ASSEMBLER
)

#save as csv files
final_ind_trips.to_csv(os.path.join(rsm_dir, "output", "indivTripData_" + str(iteration) + ".csv"), index = False)
final_jnt_trips.to_csv(os.path.join(rsm_dir, "output", "jointTripData_" + str(iteration) + ".csv"), index = False)

logging.info("finished logging rsm_assembler")