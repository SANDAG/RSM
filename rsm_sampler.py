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
from sandag_rsm.logging import logging_start
from sandag_rsm.sampler import rsm_household_sampler

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

#output files
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











