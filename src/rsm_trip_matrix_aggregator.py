#
# Aggregates demand files to RSM zone structure
# Uses specific version of python -
# This python file is being called in bin\runInputTripMatrixAggregator.cmd
#
# Inputs:
#   rsm_main_dir: RSM main directory
#   org_model_dir: Donor model main directory
#   agg_zone_mapping: TAZ to RSM zone crosswalk
#
# Outputs:
#   Aggregated OMX files based on new zone structure
#
# Please note that logging couldn't be included in the module because of the different python environments
#

import os
import sys
import openmatrix as omx
main_path = os.path.dirname(os.path.realpath(__file__)) + "/../"
sys.path.append(main_path)
from rsm.translate import (
    translate_demand, 
    copy_transit_demand,
)


rsm_main_dir = os.path.join(sys.argv[1])
rsm_input_dir = os.path.join(sys.argv[1], "input")
org_model_input_dir = os.path.join(sys.argv[2], "input")
agg_zone_mapping = os.path.join(rsm_main_dir, sys.argv[3])

rsm_output_dir = os.path.join(sys.argv[1], "output")
org_model_output_dir = os.path.join(sys.argv[2], "output")

periods = ["_EA", "_AM", "_MD", "_PM", "_EV"]
vot_bins = ["_low", "_med", "_high"]
file_ext = '.omx'

mat_names = []
for period in periods:
    mat_names.append('trip'+period+file_ext)

translate_demand(
    mat_names,
    agg_zone_mapping,
    org_model_input_dir,
    rsm_input_dir
)


agg_mats = []

for period in periods:
    for vot in vot_bins: 
        agg_mats.append('autoAirportTrips.CBX'+period+vot+file_ext)
        agg_mats.append('autoAirportTrips.SAN'+period+vot+file_ext)
        agg_mats.append('autoCrossBorderTrips'+period+vot+file_ext)
        agg_mats.append('autoInternalExternalTrips'+period+vot+file_ext)
        agg_mats.append('autoVisitorTrips'+period+vot+file_ext)


for period in periods:
    agg_mats.append('nmotAirportTrips.CBX'+period+file_ext)
    agg_mats.append('nmotAirportTrips.SAN'+period+file_ext)
    agg_mats.append('nmotCrossBorderTrips'+period+file_ext)
    agg_mats.append('nmotInternalExternalTrips'+period+file_ext)
    agg_mats.append('nmotVisitorTrips'+period+file_ext)

    agg_mats.append('othrAirportTrips.CBX'+period+file_ext)
    agg_mats.append('othrAirportTrips.SAN'+period+file_ext)
    agg_mats.append('othrCrossBorderTrips'+period+file_ext)
    agg_mats.append('othrInternalExternalTrips'+period+file_ext)
    agg_mats.append('othrVisitorTrips'+period+file_ext)

    agg_mats.append('TNCVehicleTrips'+period+file_ext)

agg_mats.append('EmptyAVTrips'+file_ext)

#Aggregating the trips based on new zone structure
translate_demand(
    agg_mats,
    agg_zone_mapping,
    org_model_output_dir,
    rsm_output_dir
)

#copying transit demand matrices 
copy_mats = []
for period in periods:
    copy_mats.append('tranAirportTrips.SAN'+period+file_ext)
    copy_mats.append('tranCrossBorderTrips'+period+file_ext)
    copy_mats.append('tranInternalExternalTrips'+period+file_ext)
    #copy_mats.append('tranTrips'+period+file_ext)
    copy_mats.append('tranVisitorTrips'+period+file_ext)

copy_transit_demand(
    copy_mats,
    org_model_output_dir,
    rsm_output_dir
)

