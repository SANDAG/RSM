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
# docker run -v %cd%:/home/mambauser/sandag_rsm -w /home/mambauser/sandag_rsm sandag_rsm python RSM_pregame.py
# ```
#

from sandag_rsm.data_load.zones import load_mgra_data
from sandag_rsm.logging import logging_start
from sandag_rsm.poi import attach_poi_taz_skims, poi_taz_mgra
from sandag_rsm.sampler import rsm_household_sampler
from sandag_rsm.zone_agg import (
    aggregate_zones,
    make_crosswalk,
    mark_centroids,
    merge_zone_data,
)

#
#   CONFIG HERE
#   All these files should be relative to and within in the current working dir
#

FULL_ABM_MGRA = r"notebooks/data-dl/mgra13_based_input2016.csv.gz"
FULL_ABM_MGRA_SHAPEFILE = r"notebooks/data-dl/MGRASHAPE.zip"
FULL_ABM_AM_HIGHWAY_SKIM = r"notebooks/data-dl/traffic_skims_AM_mini.omx"
FULL_ABM_TRIP_LIST = r"notebooks/data-dl/trips_sample.pq"
FULL_ABM_SYNTH_HOUSHOLDS = r"hh_test.csv.gz"
FULL_ABM_SYNTH_PERSONS = r"person_test.csv.gz"
EXPLICIT_ZONE_AGG = []

OUTPUT_MGRA_CROSSWALK = r"mgra_crosswalk.csv"
OUTPUT_TAZ_CROSSWALK = r"taz_crosswalk.csv"
OUTPUT_RSM_ZONE_FILE = "cluster_zones.csv"
OUTPUT_RSM_SAMPLED_HOUSHOLDS = "sampled_households_1.csv"
OUTPUT_RSM_SAMPLED_PERSONS = "sampled_person_1.csv"

logging_start()


#
#   Zone Aggregation
#

mgra = load_mgra_data(
    shapefilename=FULL_ABM_MGRA_SHAPEFILE,
    supplemental_features=FULL_ABM_MGRA,
    simplify_tolerance=10,
    topo=True,
)
tazs = merge_zone_data(mgra, cluster_id="taz")

poi = poi_taz_mgra(mgra)

cluster_factors = {"popden": 1, "empden": 1, "modeshare_NM": 100, "modeshare_WT": 100}
tazs, cluster_factors = attach_poi_taz_skims(
    tazs,
    FULL_ABM_AM_HIGHWAY_SKIM,
    names="AM_SOV_TR_M_TIME",
    poi=poi,
    cluster_factors=cluster_factors,
)


agglom3full = aggregate_zones(
    tazs,
    cluster_factors=cluster_factors,
    n_zones=2000,
    method="agglom_adj",
    use_xy=1e-4,
    explicit_agg=EXPLICIT_ZONE_AGG,
    explicit_col="taz",
)

taz_crosswalk = make_crosswalk(agglom3full, tazs, old_index="taz").sort_values("taz")
mgra_crosswalk = make_crosswalk(agglom3full, mgra, old_index="MGRA").sort_values("MGRA")
agglom3full = mark_centroids(agglom3full)
mgra_crosswalk.to_csv(OUTPUT_MGRA_CROSSWALK, index=False)
taz_crosswalk.to_csv(OUTPUT_TAZ_CROSSWALK, index=False)
agglom3full.to_csv(OUTPUT_RSM_ZONE_FILE, index=False)

rsm_household_sampler(
    # input_dir="./notebooks/data-dl",
    # output_dir=tempdir.name,
    input_household=FULL_ABM_SYNTH_HOUSHOLDS,
    input_person=FULL_ABM_SYNTH_PERSONS,
    taz_crosswalk=OUTPUT_TAZ_CROSSWALK,
    output_household=OUTPUT_RSM_SAMPLED_HOUSHOLDS,
    output_person=OUTPUT_RSM_SAMPLED_PERSONS,
)
