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

from sandag_rsm.logging import logging_start
from sandag_rsm.sampler import rsm_household_sampler
from sandag_rsm.utility import (
    copy_file,
    get_shadow_pricing_files,
    modify_sandag_properties_for_shadowpricing,
    get_user_input,
)

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

# output files
OUTPUT_RSM_DIR = os.path.join(rsm_dir, "output")
OUTPUT_RSM_SAMPLED_HOUSHOLDS = os.path.join(rsm_dir, "input", "sampled_households.csv")
OUTPUT_RSM_SAMPLED_PERSONS = os.path.join(rsm_dir, "input", "sampled_person.csv")

logging_start(
    filename=os.path.join(rsm_dir, "logFiles", "rsm-logging.log"), level=logging.INFO
)
logging.info(f"start logging rsm_sampler for {iteration}")

run_rsm_sampling = get_user_input(ABM_PROPERTIES, "run.rsm.sampling")
user_defined_sample_rate = float(get_user_input(ABM_PROPERTIES, "rsm.sampling.rate"))


if run_rsm_sampling.lower() == 'true':
    # if rsm sampling set to True
    if iteration == 1:
        rsm_household_sampler(
            input_dir=rsm_dir,
            output_dir=rsm_dir,
            input_household=FULL_ABM_SYNTH_HOUSHOLDS,
            input_person=FULL_ABM_SYNTH_PERSONS,
            taz_crosswalk=OUTPUT_TAZ_CROSSWALK,
            mgra_crosswalk=OUTPUT_MGRA_CROSSWALK,
            default_sampling_rate=user_defined_sample_rate,
            output_household=OUTPUT_RSM_SAMPLED_HOUSHOLDS,
            output_person=OUTPUT_RSM_SAMPLED_PERSONS,
        )

    else:

        PREV_ITER_ACCESS = os.path.join(
            rsm_dir, "input", "accessibilities_" + str(iteration - 1) + ".csv"
        )
        CURR_ITER_ACCESS = os.path.join(
            rsm_dir, "input", "accessibilities_" + str(iteration) + ".csv"
        )

        # get the shadow pricing and school pricing file
        work_file, sch_file = get_shadow_pricing_files(OUTPUT_RSM_DIR)

        # create copy of sandag_abm.properties file
        copy_file(
            os.path.join(ABM_PROPERTIES_FOLDER, "sandag_abm.properties"),
            os.path.join(
                ABM_PROPERTIES_FOLDER, "sandag_abm_" + str(iteration) + ".properties"
            ),
        )

        copy_file(
            os.path.join(OUTPUT_RSM_DIR, work_file), os.path.join(INPUT_RSM_DIR, work_file)
        )
        copy_file(
            os.path.join(OUTPUT_RSM_DIR, sch_file), os.path.join(INPUT_RSM_DIR, sch_file)
        )

        # modifies the sandag_abm.properties file to reflect the names of shadow pricing files
        modify_sandag_properties_for_shadowpricing(
            ABM_PROPERTIES, work_file, sch_file, iteration
        )

        rsm_household_sampler(
            input_dir=rsm_dir,
            output_dir=rsm_dir,
            prev_iter_access=PREV_ITER_ACCESS,
            curr_iter_access=CURR_ITER_ACCESS,
            input_household=FULL_ABM_SYNTH_HOUSHOLDS,
            input_person=FULL_ABM_SYNTH_PERSONS,
            taz_crosswalk=OUTPUT_TAZ_CROSSWALK,
            mgra_crosswalk=OUTPUT_MGRA_CROSSWALK,
            output_household=OUTPUT_RSM_SAMPLED_HOUSHOLDS,
            output_person=OUTPUT_RSM_SAMPLED_PERSONS,
        )

else: 
    #if rsm sampling is set to False
    rsm_household_sampler(
            input_dir=rsm_dir,
            output_dir=rsm_dir,
            input_household=FULL_ABM_SYNTH_HOUSHOLDS,
            input_person=FULL_ABM_SYNTH_PERSONS,
            taz_crosswalk=OUTPUT_TAZ_CROSSWALK,
            mgra_crosswalk=OUTPUT_MGRA_CROSSWALK,
            default_sampling_rate=user_defined_sample_rate,
            output_household=OUTPUT_RSM_SAMPLED_HOUSHOLDS,
            output_person=OUTPUT_RSM_SAMPLED_PERSONS,
        )
    
    if iteration>1:
        PREV_ITER_ACCESS = os.path.join(
            rsm_dir, "input", "accessibilities_" + str(iteration - 1) + ".csv"
        )
        CURR_ITER_ACCESS = os.path.join(
            rsm_dir, "input", "accessibilities_" + str(iteration) + ".csv"
        )

        # get the shadow pricing and school pricing file
        work_file, sch_file = get_shadow_pricing_files(OUTPUT_RSM_DIR)

        # create copy of sandag_abm.properties file
        copy_file(
            os.path.join(ABM_PROPERTIES_FOLDER, "sandag_abm.properties"),
            os.path.join(
                ABM_PROPERTIES_FOLDER, "sandag_abm_" + str(iteration) + ".properties"
            ),
        )

        copy_file(
            os.path.join(OUTPUT_RSM_DIR, work_file), os.path.join(INPUT_RSM_DIR, work_file)
        )
        copy_file(
            os.path.join(OUTPUT_RSM_DIR, sch_file), os.path.join(INPUT_RSM_DIR, sch_file)
        )

        # modifies the sandag_abm.properties file to reflect the names of shadow pricing files
        modify_sandag_properties_for_shadowpricing(
            ABM_PROPERTIES, work_file, sch_file, iteration
        )


logging.info(f"finished logging rsm_sampler for {iteration}")