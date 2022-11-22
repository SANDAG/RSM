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
import openmatrix as omx
from sandag_rsm.translate import (
    translate_demand, 
    copy_transit_demand,
)

rsm_main_dir = os.path.join(sys.argv[1])
rsm_input_dir = os.path.join(sys.argv[1], "input")
org_model_input_dir = os.path.join(sys.argv[2], "input")
agg_zone_mapping = os.path.join(rsm_main_dir, sys.argv[3])

rsm_output_dir = os.path.join(sys.argv[1], "output")
org_model_output_dir = os.path.join(sys.argv[2], "output")


matrix_names = ['trip_EA.omx', 'trip_AM.omx', 'trip_MD.omx', 'trip_PM.omx', 'trip_EV.omx']
translate_demand(
    matrix_names,
    agg_zone_mapping,
    org_model_input_dir,
    rsm_input_dir
)

#Aggregating the trips based on new zone structure
matrix_names = ['autoAirportTrips.CBX_AM_high.omx', 'autoAirportTrips.CBX_AM_med.omx', 'autoAirportTrips.CBX_AM_low.omx',
                'autoAirportTrips.CBX_MD_high.omx', 'autoAirportTrips.CBX_MD_med.omx', 'autoAirportTrips.CBX_MD_low.omx',
                'autoAirportTrips.CBX_PM_high.omx', 'autoAirportTrips.CBX_PM_med.omx', 'autoAirportTrips.CBX_PM_low.omx',
                'autoAirportTrips.CBX_EA_high.omx', 'autoAirportTrips.CBX_EA_med.omx', 'autoAirportTrips.CBX_EA_low.omx',
                'autoAirportTrips.CBX_EV_high.omx', 'autoAirportTrips.CBX_EV_med.omx', 'autoAirportTrips.CBX_EV_low.omx',

                'autoAirportTrips.SAN_AM_high.omx', 'autoAirportTrips.SAN_AM_med.omx', 'autoAirportTrips.SAN_AM_low.omx',
                'autoAirportTrips.SAN_MD_high.omx', 'autoAirportTrips.SAN_MD_med.omx', 'autoAirportTrips.SAN_MD_low.omx',
                'autoAirportTrips.SAN_PM_high.omx', 'autoAirportTrips.SAN_PM_med.omx', 'autoAirportTrips.SAN_PM_low.omx',
                'autoAirportTrips.SAN_EA_high.omx', 'autoAirportTrips.SAN_EA_med.omx', 'autoAirportTrips.SAN_EA_low.omx',
                'autoAirportTrips.SAN_EV_high.omx', 'autoAirportTrips.SAN_EV_med.omx', 'autoAirportTrips.SAN_EV_low.omx',

                'autoCrossBorderTrips_AM_high.omx', 'autoCrossBorderTrips_AM_med.omx', 'autoCrossBorderTrips_AM_low.omx',
                'autoCrossBorderTrips_MD_high.omx', 'autoCrossBorderTrips_MD_med.omx', 'autoCrossBorderTrips_MD_low.omx',
                'autoCrossBorderTrips_PM_high.omx', 'autoCrossBorderTrips_PM_med.omx', 'autoCrossBorderTrips_PM_low.omx',
                'autoCrossBorderTrips_EA_high.omx', 'autoCrossBorderTrips_EA_med.omx', 'autoCrossBorderTrips_EA_low.omx',
                'autoCrossBorderTrips_EV_high.omx', 'autoCrossBorderTrips_EV_med.omx', 'autoCrossBorderTrips_EV_low.omx',

                'autoInternalExternalTrips_AM_high.omx', 'autoInternalExternalTrips_AM_med.omx', 'autoInternalExternalTrips_AM_low.omx',
                'autoInternalExternalTrips_MD_high.omx', 'autoInternalExternalTrips_MD_med.omx', 'autoInternalExternalTrips_MD_low.omx',
                'autoInternalExternalTrips_PM_high.omx', 'autoInternalExternalTrips_PM_med.omx', 'autoInternalExternalTrips_PM_low.omx',
                'autoInternalExternalTrips_EA_high.omx', 'autoInternalExternalTrips_EA_med.omx', 'autoInternalExternalTrips_EA_low.omx',
                'autoInternalExternalTrips_EV_high.omx', 'autoInternalExternalTrips_EV_med.omx', 'autoInternalExternalTrips_EV_low.omx',

                'autoVisitorTrips_AM_high.omx', 'autoVisitorTrips_AM_med.omx', 'autoVisitorTrips_AM_low.omx',
                'autoVisitorTrips_MD_high.omx', 'autoVisitorTrips_MD_med.omx', 'autoVisitorTrips_MD_low.omx',
                'autoVisitorTrips_PM_high.omx', 'autoVisitorTrips_PM_med.omx', 'autoVisitorTrips_PM_low.omx',
                'autoVisitorTrips_EA_high.omx', 'autoVisitorTrips_EA_med.omx', 'autoVisitorTrips_EA_low.omx',
                'autoVisitorTrips_EV_high.omx', 'autoVisitorTrips_EV_med.omx', 'autoVisitorTrips_EV_low.omx',

                'nmotAirportTrips.CBX_AM.omx', 'nmotAirportTrips.CBX_MD.omx', 'nmotAirportTrips.CBX_PM.omx', 'nmotAirportTrips.CBX_EA.omx', 'nmotAirportTrips.CBX_EV.omx',
                'nmotAirportTrips.SAN_AM.omx', 'nmotAirportTrips.SAN_MD.omx', 'nmotAirportTrips.SAN_PM.omx', 'nmotAirportTrips.SAN_EA.omx', 'nmotAirportTrips.SAN_EV.omx',
                'nmotCrossBorderTrips_AM.omx', 'nmotCrossBorderTrips_MD.omx', 'nmotCrossBorderTrips_PM.omx', 'nmotCrossBorderTrips_EA.omx', 'nmotCrossBorderTrips_EV.omx',
                'nmotInternalExternalTrips_AM.omx', 'nmotInternalExternalTrips_MD.omx', 'nmotInternalExternalTrips_PM.omx', 'nmotInternalExternalTrips_EA.omx', 'nmotInternalExternalTrips_EV.omx',
                'nmotVisitorTrips_AM.omx', 'nmotVisitorTrips_MD.omx', 'nmotVisitorTrips_PM.omx', 'nmotVisitorTrips_EA.omx', 'nmotVisitorTrips_EV.omx',

                'othrAirportTrips.CBX_AM.omx', 'othrAirportTrips.CBX_MD.omx', 'othrAirportTrips.CBX_PM.omx', 'othrAirportTrips.CBX_EA.omx', 'othrAirportTrips.CBX_EV.omx',
                'othrAirportTrips.SAN_AM.omx', 'othrAirportTrips.SAN_MD.omx', 'othrAirportTrips.SAN_PM.omx', 'othrAirportTrips.SAN_EA.omx', 'othrAirportTrips.SAN_EV.omx',
                'othrCrossBorderTrips_AM.omx', 'othrCrossBorderTrips_MD.omx', 'othrCrossBorderTrips_PM.omx', 'othrCrossBorderTrips_EA.omx', 'othrCrossBorderTrips_EV.omx',
                'othrInternalExternalTrips_AM.omx', 'othrInternalExternalTrips_MD.omx', 'othrInternalExternalTrips_PM.omx', 'othrInternalExternalTrips_EA.omx', 'othrInternalExternalTrips_EV.omx',
                'othrVisitorTrips_AM.omx', 'othrVisitorTrips_MD.omx', 'othrVisitorTrips_PM.omx', 'othrVisitorTrips_EA.omx', 'othrVisitorTrips_EV.omx',

                'TNCVehicleTrips_AM.omx', 'TNCVehicleTrips_MD.omx', 'TNCVehicleTrips_PM.omx', 'TNCVehicleTrips_EA.omx', 'TNCVehicleTrips_EV.omx',

                ]



#translate_demand(
#    matrix_names,
#    agg_zone_mapping,
#    org_model_output_dir,
#    rsm_output_dir
#)

matrix_names = ['tranAirportTrips.SAN_AM.omx', 'tranAirportTrips.SAN_MD.omx', 'tranAirportTrips.SAN_PM.omx', 'tranAirportTrips.SAN_EA.omx', 'tranAirportTrips.SAN_EV.omx',
                'tranCrossBorderTrips_AM.omx', 'tranCrossBorderTrips_MD.omx', 'tranCrossBorderTrips_PM.omx', 'tranCrossBorderTrips_EA.omx', 'tranCrossBorderTrips_EV.omx', 
                'tranInternalExternalTrips_AM.omx', 'tranInternalExternalTrips_MD.omx', 'tranInternalExternalTrips_PM.omx', 'tranInternalExternalTrips_EA.omx', 'tranInternalExternalTrips_EV.omx',
                'tranTrips_AM.omx', 'tranTrips_MD.omx', 'tranTrips_PM.omx', 'tranTrips_EA.omx', 'tranTrips_EV.omx',
                'tranVisitorTrips_AM.omx', 'tranVisitorTrips_MD.omx', 'tranVisitorTrips_PM.omx', 'tranVisitorTrips_EA.omx', 'tranVisitorTrips_EV.omx',
                ]

copy_transit_demand(
    matrix_names,
    org_model_output_dir,
    rsm_output_dir
)