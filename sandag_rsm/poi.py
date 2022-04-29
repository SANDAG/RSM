import pandas as pd
import pyproj
import shapely.geometry.point

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
    gdf,
    skims_omx,
    names,
    poi=None,
):
    if poi is None:
        poi = poi_taz_mgra(gdf)
    if isinstance(names, str):
        names = [names]
    zone_nums = skims_omx.root.lookup.zone_number
    cols = {}
    for k in poi:
        ktaz = poi[k]["taz"]
        for name in names:
            cols[f"{k}_{name}"] = pd.Series(
                skims_omx.root.data[name][ktaz - 1],
                index=zone_nums[:],
            )
    add_to_gdf = {}
    for c in cols:
        add_to_gdf[c] = gdf["taz"].map(cols[c])
    return gdf.assign(**add_to_gdf)
