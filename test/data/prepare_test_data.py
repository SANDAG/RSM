# SANDAG Test Data Generator
#   This script create the minimal test data for the SANDAG RSM, from
#   an original full-scale data source.

import gzip
import os
import shutil
from pathlib import Path

import numpy as np
import openmatrix as omx
import pandas as pd

from sandag_rsm.data_load.zones import simplify_shapefile

this_dir = Path(os.path.dirname(__file__))


def mgra_geopackage(shapefilename="MGRASHAPE.zip"):
    simplify_shapefile(
        shapefilename=shapefilename,
        simplify_tolerance=10,
        prequantize=False,
        layername="MGRA",
        topo=True,
        output_filename=this_dir / "MGRASHAPE_simplified_10.gpkg",
    )


def mini_skim(full_skim="Data/traffic_skims_AM.omx", tablename="AM_SOV_TR_M_TIME"):
    output_filename = this_dir / "traffic_skims_AM_mini.omx"
    f = omx.open_file(full_skim, mode="r")
    out = omx.open_file(str(output_filename), mode="w")
    out[tablename] = f[tablename][:].astype(np.float32)
    out.create_array(
        "/lookup",
        "zone_number",
        f.root["lookup"]["zone_number"][:],
    )
    out.flush()
    out.close()
    f.close()


def gz_copy(in_file, out_file="mgra13_based_input2016.csv.gz"):
    with open(in_file, "rb") as f_in:
        with gzip.open(out_file, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)


def sample_trips(in_file="indivTripData_3.csv.gz", out_file="trips_sample.pq"):
    trips = pd.read_csv(in_file)
    trips = trips.iloc[::25]
    trips.to_parquet(out_file)


if __name__ == "__main__":
    mgra_geopackage(shapefilename="Data/MGRASHAPE.zip")
    mini_skim("Data/traffic_skims_AM.omx", "AM_SOV_TR_M_TIME")
    gz_copy("Data/mgra13_based_input2016.csv")
    sample_trips("Data/indivTripData_3.csv.gz")
