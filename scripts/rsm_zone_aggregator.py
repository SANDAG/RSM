#
# Aggregates the donor model zones to RSM zones
# This python file is being called in bin\runRSMZoneAggregator.cmd
#
# inputs:
#   rsm_main_dir: RSM main directory
#   full_model_dir: Donor model directory
#   num_rsm_zones: Number of RSM zones
#   num_ext_zones: Number of external zones
# outputs:
#   mgra_crosswalk.csv
#   taz_crosswalk.csv
#   cluster_centroids.csv
#   mgra13_based_input2016.csv

import os
import sys
import pandas as pd
import logging
#sys.path.append('T:/ABM/WSP_Space/RSM/')
main_path = os.path.dirname(os.path.realpath(__file__)) + "/../"
sys.path.append(main_path)
from rsm.poi import attach_poi_taz_skims, poi_taz_mgra
from rsm.data_load.zones import load_mgra_data
from rsm.data_load.triplist import load_trip_list, trip_mode_shares_by_mgra, trip_mode_shares_by_taz
from rsm.logging import logging_start
from rsm.poi import attach_poi_taz_skims, poi_taz_mgra
from rsm.sampler import rsm_household_sampler
from rsm.zone_agg import (
    aggregate_zones,
    make_crosswalk,
    mark_centroids,
    merge_zone_data,
)
from rsm.utility import *

rsm_main_dir = sys.argv[1]
full_model_dir = sys.argv[2]
NUM_RSM_ZONES = int(sys.argv[3])
NUM_EXT_ZONES = int(sys.argv[4])

#input files
FULL_ABM_PROPERTIES = os.path.join(full_model_dir, "conf", "sandag_abm.properties")
FULL_ABM_MGRA_FILE = os.path.join(full_model_dir, get_property(FULL_ABM_PROPERTIES, "mgra.socec.file"))
FULL_ABM_MGRA_SHAPEFILE = os.path.join(rsm_main_dir, "input", "MGRASHAPE.zip")
FULL_ABM_AM_HIGHWAY_SKIM = os.path.join(full_model_dir, "output", "traffic_skims_AM.omx")
FULL_ABM_TRIP_DIR = os.path.join(full_model_dir, "output")
FULL_ABM_SYNTH_HOUSHOLDS = os.path.join(full_model_dir, "input", "households.csv")
FULL_ABM_SYNTH_PERSONS = os.path.join(full_model_dir, "input", "persons.csv")
EXPLICIT_ZONE_AGG = []

#output files
RSM_ABM_PROPERTIES = os.path.join(rsm_main_dir, "conf", "sandag_abm.properties")
OUTPUT_MGRA_CROSSWALK = os.path.join(rsm_main_dir, get_property(RSM_ABM_PROPERTIES, "mgra.to.cluster.crosswalk.file"))
OUTPUT_TAZ_CROSSWALK = os.path.join(rsm_main_dir, get_property(RSM_ABM_PROPERTIES, "taz.to.cluster.crosswalk.file"))
OUTPUT_CLUSTER_CENTROIDS = os.path.join(rsm_main_dir, get_property(RSM_ABM_PROPERTIES, "cluster.zone.centroid.file"))
OUTPUT_RSM_ZONE_FILE = os.path.join(rsm_main_dir, get_property(RSM_ABM_PROPERTIES, "mgra.socec.file"))

logging_start(
    filename=os.path.join(rsm_main_dir, "logFiles", "rsm-logging.log"), level=logging.INFO
)
logging.info("start logging rsm_zone_aggregator")

#
#   Zone Aggregation
#

logging.info("loading mgra data")
mgra = load_mgra_data(
    shapefilename=FULL_ABM_MGRA_SHAPEFILE,
    supplemental_features=FULL_ABM_MGRA_FILE,
    simplify_tolerance=10,
    topo=True,
)

logging.info("loading trip file")
trips = load_trip_list(trips_filename = "indivTripData_3.csv", data_dir = FULL_ABM_TRIP_DIR)

# in the original model, these variables are computed in the 4Ds module
mgra = add_intersection_count(rsm_main_dir, mgra)
mgra = add_density_variables(full_model_dir, mgra)

tazs = merge_zone_data(mgra, cluster_id="taz")

logging.info("getting mode shares")
trip_mode_shares = trip_mode_shares_by_taz(trips, tazs=tazs.index, mgra_gdf=mgra)
tazs = tazs.join(trip_mode_shares.add_prefix("modeshare_"), on='taz')

logging.info("adding poi")
poi = poi_taz_mgra(mgra)

cluster_factors = {"popden": 1, "empden": 1, "modeshare_NM": 100, "modeshare_WT": 100}

logging.info("attaching skims to poi taz")
tazs, cluster_factors = attach_poi_taz_skims(
    tazs,
    FULL_ABM_AM_HIGHWAY_SKIM,
    names="AM_SOV_TR_M_TIME",
    poi=poi,
    cluster_factors=cluster_factors,
)

logging.info("aggregating zones")
agglom3full = aggregate_zones(
    tazs,
    cluster_factors=cluster_factors,
    n_zones=NUM_RSM_ZONES,
    method="agglom_adj",
    use_xy=1e-4,
    explicit_agg=EXPLICIT_ZONE_AGG,
    explicit_col="taz",
)

logging.info("printing outputs")
taz_crosswalk = make_crosswalk(agglom3full, tazs, old_index="taz").sort_values("taz")
mgra_crosswalk = make_crosswalk(agglom3full, mgra, old_index="MGRA").sort_values("MGRA")
agglom3full = mark_centroids(agglom3full)

cluster_centroids = agglom3full[["cluster_id", "centroid_x", "centroid_y"]]

agglom3full = agglom3full.drop(columns = ["geometry", "centroid_x", "centroid_y"])
agglom3full = agglom3full.rename(columns = {"cluster_id" : "taz"})
agglom3full['mgra'] = range(1, len(agglom3full)+1)
agglom3full.insert(0, 'mgra', agglom3full.pop('mgra'))
agglom3full.insert(1, 'taz', agglom3full.pop('taz'))

#for school enrollments and high school enrollments - checks

agglom3full = fix_zero_enrollment(agglom3full)

ext_zones_df = pd.DataFrame({'taz':range(1,NUM_EXT_ZONES+1), 'cluster_id': range(1,NUM_EXT_ZONES+1)})

taz_crosswalk = pd.concat([taz_crosswalk, ext_zones_df])
taz_crosswalk = taz_crosswalk.sort_values('taz')

mgra_crosswalk['cluster_id'] = mgra_crosswalk['cluster_id'] - NUM_EXT_ZONES

mgra_crosswalk.to_csv(OUTPUT_MGRA_CROSSWALK, index=False)
taz_crosswalk.to_csv(OUTPUT_TAZ_CROSSWALK, index=False)
cluster_centroids.to_csv(OUTPUT_CLUSTER_CENTROIDS, index=False)
# agglom3full.to_csv(OUTPUT_RSM_ZONE_FILE, index=False)

logging.info("Finished logging rsm_zone_aggregator")
