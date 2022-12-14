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
import os
from sandag_rsm.logging import logging_start
from sandag_rsm.utility import *

#
#   CONFIG HERE
#   All these files should be relative to and within in the current working dir
#

rsm_dir = sys.argv[1]
value = sys.argv[2]

ABM_PROPERTIES_FOLDER = os.path.join(rsm_dir, "conf")
ABM_PROPERTIES = os.path.join(ABM_PROPERTIES_FOLDER, "sandag_abm.properties")
    
# modifies the sandag_abm.properties file to reflect the names of shadow pricing files
modify_sandag_properties_for_accessibility(ABM_PROPERTIES, value)











