import logging
import os
import warnings

import geopandas as gpd
import pandas as pd
import pyproj
from shapely.ops import orient  # version >=1.7a2

logger = logging.getLogger(__name__)


def geometry_cleanup(gdf):
    gdf.geometry = gdf.geometry.apply(orient, args=(-1,))
    gdf.geometry = gdf.geometry.buffer(0)
    return gdf


def simplify_shapefile(
    shapefilename="MGRASHAPE.zip",
    simplify_tolerance=1,
    prequantize=False,
    layername="MGRA",
    topo=True,
    output_filename=None,
):
    if output_filename is not None:
        gpkg_filename = output_filename
    else:
        gpkg_filename = (
            os.path.splitext(shapefilename)[0]
            + f"_simplified_{simplify_tolerance}.gpkg"
        )
    if os.path.exists(gpkg_filename):
        gdf = gpd.read_file(gpkg_filename)
        return geometry_cleanup(gdf)
    gdf = gpd.read_file(shapefilename)
    if topo:
        try:
            import topojson as tp
        except ImportError:
            warnings.warn("topojson is not installed")
            gdf.geometry = gdf.geometry.simplify(simplify_tolerance)
            return geometry_cleanup(gdf)
        else:
            logger.info("converting to epsg:3857")
            gdf = gdf.to_crs(pyproj.CRS.from_epsg(3857))
            logger.info("creating topology")
            topo = tp.Topology(gdf, prequantize=prequantize)
            logger.info("simplifying topology")
            topo = topo.toposimplify(simplify_tolerance)
            logger.info("converting to gdf")
            gdf = topo.to_gdf()
            gdf.crs = pyproj.CRS.from_epsg(3857)
            logger.info("checking orientation")
            gdf.geometry = gdf.geometry.apply(orient, args=(-1,))
            logger.info("completed")
            gdf.to_file(gpkg_filename, layer=layername, driver="GPKG")
            return geometry_cleanup(gdf)
    else:
        if simplify_tolerance is not None:
            gdf.geometry = gdf.geometry.simplify(simplify_tolerance)
        return geometry_cleanup(gdf)


def load_mgra_data(
    shapefilename="MGRASHAPE.zip",
    supplemental_features="mgra13_based_input2016.csv.gz",
    data_dir=None,
    simplify_tolerance=1,
    prequantize=False,
    topo=True,
):
    if data_dir is not None:
        data_dir = os.path.expanduser(data_dir)
        cwd = os.getcwd()
        os.chdir(data_dir)
    else:
        cwd = None

    try:
        gdf = simplify_shapefile(
            shapefilename=shapefilename,
            simplify_tolerance=simplify_tolerance,
            layername="MGRA",
            prequantize=prequantize,
            topo=topo,
        )
        sdf = pd.read_csv(supplemental_features)
        mgra = gdf.merge(sdf, left_on="MGRA", right_on="mgra")
        return mgra

    finally:
        # change back to original cwd
        os.chdir(cwd)
