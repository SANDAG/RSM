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
import re
import glob
from sandag_rsm.logging import logging_start
from sandag_rsm.sampler import rsm_household_sampler
from sandag_rsm.utility import *

#
#   CONFIG HERE
#   All these files should be relative to and within in the current working dir
#

rsm_dir = sys.argv[1]
iteration = int(sys.argv[2])


#input files
FULL_ABM_SYNTH_HOUSHOLDS = os.path.join(rsm_dir, "input", "households.csv")
FULL_ABM_SYNTH_PERSONS = os.path.join(rsm_dir, "input", "persons.csv")
OUTPUT_MGRA_CROSSWALK = os.path.join(rsm_dir, "input", "mgra_crosswalk.csv")
OUTPUT_TAZ_CROSSWALK = os.path.join(rsm_dir, "input", "taz_crosswalk.csv")
ABM_PROPERTIES_FOLDER = os.path.join(rsm_dir, "conf")
ABM_PROPERTIES = os.path.join(ABM_PROPERTIES_FOLDER, "sandag_abm.properties")
INPUT_RSM_DIR = os.path.join(rsm_dir, "input")
 

#output files
OUTPUT_RSM_DIR = os.path.join(rsm_dir, "output")
OUTPUT_RSM_SAMPLED_HOUSHOLDS = os.path.join(rsm_dir, "input" ,"sampled_households.csv")
OUTPUT_RSM_SAMPLED_PERSONS = os.path.join(rsm_dir, "input", "sampled_person.csv")

logging_start()

if iteration == 1:
    rsm_household_sampler(
        input_dir=rsm_dir,
        output_dir=rsm_dir,
        input_household=FULL_ABM_SYNTH_HOUSHOLDS,
        input_person=FULL_ABM_SYNTH_PERSONS,
        taz_crosswalk=OUTPUT_TAZ_CROSSWALK,
        mgra_crosswalk=OUTPUT_MGRA_CROSSWALK,
        output_household=OUTPUT_RSM_SAMPLED_HOUSHOLDS,
        output_person=OUTPUT_RSM_SAMPLED_PERSONS,
    )

else:

    PREV_ITER_ACCESS = os.path.join(rsm_dir, "input", "accessibilities_"+ str(iteration-1)+".csv")
    CURR_ITER_ACCESS = os.path.join(rsm_dir, "input", "accessibilities_" + str(iteration) + ".csv")

    # get the shadow pricing and school pricing file
    work_file, sch_file = get_shadow_pricing_files(OUTPUT_RSM_DIR)
    #print(work_file, sch_file)

    #create copy of sandag_abm.properties file 
    copy_file(os.path.join(ABM_PROPERTIES_FOLDER, "sandag_abm.properties"), os.path.join(ABM_PROPERTIES_FOLDER, "sandag_abm_"+str(iteration)+".properties"))

    copy_file(os.path.join(OUTPUT_RSM_DIR, work_file), os.path.join(INPUT_RSM_DIR, work_file))
    copy_file(os.path.join(OUTPUT_RSM_DIR, sch_file), os.path.join(INPUT_RSM_DIR, sch_file))

    # modifies the sandag_abm.properties file to reflect the names of shadow pricing files
    modify_sandag_properties_for_shadowpricing(ABM_PROPERTIES, work_file, sch_file, iteration)

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











