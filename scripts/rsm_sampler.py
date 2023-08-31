#
# Creates sampled household and person file
# This file is being called in bin/runRSMSampler.cmd
#
#
# inputs:
#   rsm_dir: RSM main  directory
#   iteration: iteraton number
# outputs:
#   sampled_households.csv
#   sampled_persons.csv
#

import logging
import os
import sys
main_path = os.path.dirname(os.path.realpath(__file__)) + "/../"
sys.path.append(main_path)
from rsm.logging import logging_start
from rsm.sampler import rsm_household_sampler
from rsm.utility import *

rsm_dir = sys.argv[1]
iteration = int(sys.argv[2])

# input files
FULL_ABM_SYNTH_HOUSHOLDS = os.path.join(rsm_dir, "input", "households.csv")
FULL_ABM_SYNTH_PERSONS = os.path.join(rsm_dir, "input", "persons.csv")
OUTPUT_MGRA_CROSSWALK = os.path.join(rsm_dir, "input", "mgra_crosswalk.csv")
OUTPUT_TAZ_CROSSWALK = os.path.join(rsm_dir, "input", "taz_crosswalk.csv")
ABM_PROPERTIES_FOLDER = os.path.join(rsm_dir, "conf")
ABM_PROPERTIES = os.path.join(ABM_PROPERTIES_FOLDER, "sandag_abm.properties")
INPUT_RSM_DIR = os.path.join(rsm_dir, "input")
EXPILICT_AGG_TAZ = os.path.join(rsm_dir, "input", "study_area.csv")

# output files
OUTPUT_RSM_DIR = os.path.join(rsm_dir, "output")
OUTPUT_RSM_SAMPLED_HOUSHOLDS = os.path.join(rsm_dir, "input", "sampled_households.csv")
OUTPUT_RSM_SAMPLED_PERSONS = os.path.join(rsm_dir, "input", "sampled_person.csv")

logging_start(
    filename=os.path.join(rsm_dir, "logFiles", "rsm-logging.log"), level=logging.INFO
)
logging.info(f"start logging rsm_sampler for iteration {iteration}")

run_rsm_sampling = int(get_property(ABM_PROPERTIES, "run.rsm.sampling"))
sampling_rate = float(get_property(ABM_PROPERTIES, "rsm.default.sampling.rate"))
min_sampling_rate = float(get_property(ABM_PROPERTIES, "rsm.min.sampling.rate"))
baseline_run_dir = get_property(ABM_PROPERTIES, "rsm.baseline.run.dir")
use_differential_sampling = int(get_property(ABM_PROPERTIES, "use.differential.sampling"))

if run_rsm_sampling == 1:
    CURR_ITER_ACCESS = os.path.join(
        rsm_dir, "input", "accessibilities_" + str(iteration) + ".csv"
    )

    if iteration == 1:
        # use accessibilities from baseline RSM run
        PREV_ITER_ACCESS = os.path.join(
            baseline_run_dir, "input", "accessibilities.csv"
        )
    else:
        # use accessibilities from previous iteration of this same RSM run
        PREV_ITER_ACCESS = os.path.join(
            rsm_dir, "input", "accessibilities_" + str(iteration - 1) + ".csv"
        )
else: 
    PREV_ITER_ACCESS = None
    CURR_ITER_ACCESS = None

logging.info(f"Current Iteration Accessibility File: {CURR_ITER_ACCESS}")
logging.info(f"Previous Iteration Accessibility File: {PREV_ITER_ACCESS}")

if use_differential_sampling & os.path.exists(EXPILICT_AGG_TAZ):
    logging.info(f"Study Area file: {EXPILICT_AGG_TAZ}")
    study_area_taz = find_rsm_zone_of_study_area(EXPILICT_AGG_TAZ, OUTPUT_TAZ_CROSSWALK)
    if study_area_taz is not None:
        # Process the result
        sa_taz = study_area_taz
        logger.info(f"RSM Zone identified for the Study area are : {sa_taz}", )
    else:
        # Handle the error
        logger.info("Please check the study area file. 'taz' column is expected in the file to find the corresponding RSM zone.")
        sa_taz = None

else:
    logger.info("All RSM zones will be sampled at the deafult sampling rate")
    sa_taz = None


rsm_household_sampler(
    input_dir=rsm_dir,
    output_dir=rsm_dir,
    prev_iter_access=PREV_ITER_ACCESS,
    curr_iter_access=CURR_ITER_ACCESS,
    study_area=sa_taz,
    input_household=FULL_ABM_SYNTH_HOUSHOLDS,
    input_person=FULL_ABM_SYNTH_PERSONS,
    taz_crosswalk=OUTPUT_TAZ_CROSSWALK,
    mgra_crosswalk=OUTPUT_MGRA_CROSSWALK,
    default_sampling_rate=sampling_rate,
    lower_bound_sampling_rate=min_sampling_rate,
    output_household=OUTPUT_RSM_SAMPLED_HOUSHOLDS,
    output_person=OUTPUT_RSM_SAMPLED_PERSONS,
)

logging.info(f"finished logging rsm_sampler for iteration {iteration}")