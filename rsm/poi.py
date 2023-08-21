import itertools
from pathlib import Path

import pandas as pd
import pyproj
import shapely.geometry.point

from .data_load.skims import open_skims

# lat-lon of certain points
points_of_interest = dict(
    san_diego_city_hall=(32.71691, -117.16282),
    outside_pendleton_gate=(33.20722, -117.38973),
    escondido_city_hall=(33.122711, -117.08309),
    viejas_casino=(32.842097, -116.705582),
    san_ysidro_trolley=(32.544536, -117.02963),
)


def poi_taz_mgra(gdf):
    zones = {}
    mgra4326 = gdf.to_crs(pyproj.CRS.from_epsg(4326))
    for name, latlon in points_of_interest.items():
        pt = shapely.geometry.point.Point(*reversed(latlon))
        y = mgra4326.contains(pt)
        if y.sum() == 1:
            target = mgra4326[y].iloc[0]
            zones[name] = {"taz": target.taz, "mgra": target.mgra}
    return zones


def attach_poi_taz_skims(
    gdf, skims_omx, names, poi=None, data_dir=None, taz_col="taz", cluster_factors=None
):
    """
    Attach TAZ-based skim values to rows of a geodataframe.

    Parameters
    ----------
    gdf : gdf (GeoDataFrame)
        The skimmed values will be added as columns to this [geo]dataframe.
        If the POI's are given explicitly, this could be a regular pandas
        DataFrame, otherwise the geometry is used to find the TAZ's of the
        points of interest.
    skims_omx : skims_omx (path-like or openmatrix.File)
        Openmatrix.File of skimmed values.
    names : names (str or Mapping)
        Keys give the names of matrix tables to load out of the skims file.
        Values give the relative weight for each table (used later in
        clustering).
    poi : poi (Mapping)
        Maps named points of interest to the 'taz' id of each.  If not given,
        these will be computed based on the `gdf`.
    data_dir : data_dir (path-like, optional)
        Directory where the `skims_omx` file can be found, if not the current
        working directory.
    cluster_factors : cluster_factors (Mapping, optional)
        Existing cluster_factors, to which the new factors are added.

    Returns
    -------
    gdf : gdf (GeoDataFrame)
        [geo]dataframe to which the TAZ's of the points of interest were added.
    cluster_factors : cluster_factors (Mapping)
        Resulting cluster_factors.
    """
    if poi is None:
        poi = poi_taz_mgra(gdf)
    if isinstance(names, str):
        names = {names: 1.0}
    if isinstance(skims_omx, (str, Path)):
        skims_omx = open_skims(skims_omx, data_dir=data_dir)
    zone_nums = skims_omx.root.lookup.zone_number
    cols = {}
    for k in poi:
        ktaz = poi[k][taz_col]
        for name in names:
            cols[f"{k}_{name}"] = pd.Series(
                skims_omx.root.data[name][ktaz - 1],
                index=zone_nums[:],
            )
    add_to_gdf = {}
    if taz_col in gdf:
        gdf_taz_col = gdf[taz_col]
    elif gdf.index.name == taz_col:
        gdf_taz_col = pd.Series(data=gdf.index, index=gdf.index)
    else:
        raise KeyError(taz_col)
    for c in cols:
        add_to_gdf[c] = gdf_taz_col.map(cols[c])
    if cluster_factors is None:
        cluster_factors = {}
    new_cluster_factors = {
        f"{i}_{j}": names[j] for i, j in itertools.product(poi.keys(), names.keys())
    }
    return gdf.assign(**add_to_gdf), cluster_factors | new_cluster_factors
