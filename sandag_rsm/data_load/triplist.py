import os

import pandas as pd


def load_trip_list(
    trips_filename="indivTripData_3.parquet",
    data_dir=None,
):
    if data_dir is not None:
        data_dir = os.path.expanduser(data_dir)
        cwd = os.getcwd()
        os.chdir(data_dir)
    else:
        cwd = None

    try:
        if trips_filename.endswith(".pq") or trips_filename.endswith(".parquet"):
            trips = pd.read_parquet(trips_filename)
        else:
            trips = pd.read_csv(trips_filename)
        return trips

    finally:
        # change back to original cwd
        os.chdir(cwd)


def trip_mode_shares_by_mgra(
    trips,
    background_per_mgra=50,
    mgras=None,
):
    trip_modes = {
        1: "Au",  # Drive Alone
        2: "Au",  # Shared Ride 2
        3: "Au",  # Shared Ride 3
        4: "NM",  # Walk
        5: "NM",  # Bike
        6: "WT",  # Walk to Transit
        7: "DT",  # Park and Ride to Transit
        8: "DT",  # Kiss and Ride to Transit
        9: "Au",  # TNC to Transit
        10: "Au",  # Taxi
        11: "Au",  # TNC Single
        12: "Au",  # TNC Shared
        13: "Au",  # School Bus
    }
    trip_mode_cat = trips["trip_mode"].apply(trip_modes.get)
    tmo = trips.groupby([trips.orig_mgra, trip_mode_cat]).size().unstack().fillna(0)
    tmd = trips.groupby([trips.dest_mgra, trip_mode_cat]).size().unstack().fillna(0)
    tm = tmo + tmd
    tm_total = tm.sum()
    background = background_per_mgra * tm_total / tm_total.sum()
    if mgras is not None:
        tm = tm.reindex(mgras).fillna(0)
    tm = tm + background
    tripmodeshare = tm.div(tm.sum(axis=1), axis=0)
    return tripmodeshare


def trip_mode_shares_by_taz(
    trips,
    mgra_to_taz=None,
    background_per_taz=50,
    tazs=None,
    mgra_gdf=None,
):
    if mgra_gdf is not None and mgra_to_taz is None:
        mgra_to_taz = pd.Series(mgra_gdf.taz.values, index=mgra_gdf.MGRA)
    trip_modes = {
        1: "Au",  # Drive Alone
        2: "Au",  # Shared Ride 2
        3: "Au",  # Shared Ride 3
        4: "NM",  # Walk
        5: "NM",  # Bike
        6: "WT",  # Walk to Transit
        7: "DT",  # Park and Ride to Transit
        8: "DT",  # Kiss and Ride to Transit
        9: "Au",  # TNC to Transit
        10: "Au",  # Taxi
        11: "Au",  # TNC Single
        12: "Au",  # TNC Shared
        13: "Au",  # School Bus
    }
    trip_mode_cat = trips["trip_mode"].apply(trip_modes.get)
    tmo = (
        trips.groupby([trips.orig_mgra.map(mgra_to_taz), trip_mode_cat])
        .size()
        .unstack()
        .fillna(0)
    )
    tmd = (
        trips.groupby([trips.dest_mgra.map(mgra_to_taz), trip_mode_cat])
        .size()
        .unstack()
        .fillna(0)
    )
    tm = tmo + tmd
    tm_total = tm.sum()
    background = background_per_taz * tm_total / tm_total.sum()
    if tazs is not None:
        tm = tm.reindex(tazs).fillna(0)
    tm = tm + background
    tripmodeshare = tm.div(tm.sum(axis=1), axis=0)
    return tripmodeshare
