#
# Aggregate donor model input files/uec/non-abm model outputs to new zone structure
# This python file is being called in bin\runRSMInputAggregator.cmd
#
# inputs:
#   rsm_main_dir: RSM main directory
#   org_model_dir: Donor model directory
#   num_rsm_zones: Number of RSM zones
#   num_ext_zones: Number of external zones
#
# outputs:
#   aggregated csv files

import sys
import os
import logging
import pandas as pd
main_path = os.path.dirname(os.path.realpath(__file__)) + "/../"
sys.path.append(main_path)
from rsm.data_load.zones import load_mgra_data
from rsm.logging import logging_start
from rsm.sampler import rsm_household_sampler
from rsm.zone_agg import (
    aggregate_zones,
    make_crosswalk,
    mark_centroids,
    merge_zone_data,
)
from rsm.input_agg import agg_input_files
from rsm.utility import *

rsm_main_dir = sys.argv[1]
org_model_dir = sys.argv[2]
num_rsm_zones = int(sys.argv[3])
num_ext_zones = int(sys.argv[4])

logging_start(
    filename=os.path.join(rsm_main_dir, "logFiles", "rsm-logging.log"), level=logging.INFO
)
logging.info("start logging rsm_input_aggregator")

RSM_ABM_PROPERTIES = os.path.join(rsm_main_dir, "conf", "sandag_abm.properties")
INPUT_RSM_ZONE_FILE = os.path.join(rsm_main_dir, get_property(RSM_ABM_PROPERTIES, "mgra.socec.file"))
INPUT_MGRA_CROSSWALK = os.path.join(rsm_main_dir, get_property(RSM_ABM_PROPERTIES, "mgra.to.cluster.crosswalk.file"))
OUTPUT_RSM_ZONE_FILE = os.path.join(rsm_main_dir, get_property(RSM_ABM_PROPERTIES, "mgra.socec.file"))

#merge crosswalks with input mgra file
mgra = pd.read_csv(INPUT_RSM_ZONE_FILE)
mgra = add_intersection_count(rsm_main_dir, mgra)
rsm_cwk = pd.read_csv(INPUT_MGRA_CROSSWALK)
rsm_cwk_dict = dict(zip(rsm_cwk['MGRA'], rsm_cwk['cluster_id']))
mgra['cluster_id'] = mgra['mgra'].map(rsm_cwk_dict)

mgra_agg  = merge_zone_data(mgra, cluster_id="cluster_id")
mgra_agg  = mgra_agg.reset_index()
mgra_agg  = mgra_agg.rename(columns = {"cluster_id" : "taz"})
mgra_agg['mgra'] = range(1, len(mgra_agg )+1)
mgra_agg.insert(0, 'mgra', mgra_agg.pop('mgra'))
mgra_agg.insert(1, 'taz', mgra_agg.pop('taz'))

#for school enrollments and high school enrollments - checks
mgra_agg  = fix_zero_enrollment(mgra_agg)
mgra_agg['taz'] = mgra_agg['taz'] + num_ext_zones
mgra_agg.to_csv(OUTPUT_RSM_ZONE_FILE, index=False)

# Input Aggregation
agg_input_files(
    model_dir = org_model_dir, 
    rsm_dir = rsm_main_dir,
    taz_cwk_file = "taz_crosswalk.csv",
    mgra_cwk_file = "mgra_crosswalk.csv",
    agg_zones = num_rsm_zones,
    ext_zones = num_ext_zones,
    input_files = ["microMgraEquivMinutes.csv", "microMgraTapEquivMinutes.csv", 
    "walkMgraTapEquivMinutes.csv", "walkMgraEquivMinutes.csv", "bikeTazLogsum.csv",
    "bikeMgraLogsum.csv", "zone.term", "zones.park", "tap.ptype", "accessam.csv",
    "ParkLocationAlts.csv", "CrossBorderDestinationChoiceSoaAlternatives.csv", 
    "TourDcSoaDistanceAlts.csv", "DestinationChoiceAlternatives.csv", "SoaTazDistAlts.csv",
    "TripMatrices.csv", "transponderModelAccessibilities.csv", "crossBorderTours.csv", 
    "internalExternalTrips.csv", "visitorTours.csv", "visitorTrips.csv", "householdAVTrips.csv", 
    "crossBorderTrips.csv", "TNCTrips.csv", "airport_out.SAN.csv", "airport_out.CBX.csv", 
    "TNCtrips.csv"]
	)

logging.info("finished logging rsm_input_aggregator")