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

import sys
from sandag_rsm.data_load.zones import load_mgra_data
from sandag_rsm.logging import logging_start
from sandag_rsm.sampler import rsm_household_sampler
from sandag_rsm.zone_agg import (
    aggregate_zones,
    make_crosswalk,
    mark_centroids,
    merge_zone_data,
)
from sandag_rsm.input_agg import agg_input_files
#
#   CONFIG HERE
#   All these files should be relative to and within in the current working dir
#

org_model_dir = sys.argv[2]
rsm_main_dir = sys.argv[2]

logging_start()


#
#   Zone Aggregation
#

agg_input_files(
    model_dir = org_model_dir, 
    rsm_dir = rsm_main_dir,
    taz_cwk_file = "taz_crosswalk.csv",
    mgra_cwk_file = "mgra_crosswalk.csv",
    mgra_zone_file = "mgra13_based_input2016.csv",
    input_files = ["microMgraEquivMinutes.csv", "microMgraTapEquivMinutes.csv", 
    "walkMgraTapEquivMinutes.csv", "walkMgraEquivMinutes.csv", "bikeTazLogsum.csv",
    "bikeMgraLogsum.csv", "zone.term", "zones.park", "tap.ptype", "accessam.csv",
    "ParkLocationAlts.csv", "CrossBorderDestinationChoiceSoaAlternatives.csv", 
    "households.csv", "ShadowPricingOutput_school_9.csv", "ShadowPricingOutput_work_9.csv"]
)