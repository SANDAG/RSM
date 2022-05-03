import logging
from functools import partial
from numbers import Number
from statistics import mode

import networkx as nx
import numpy as np
import pandas as pd
import pyproj
from scipy.optimize import minimize_scalar
from sklearn.cluster import AgglomerativeClustering, KMeans
from sklearn.preprocessing import OneHotEncoder

logger = logging.getLogger(__name__)


def aggregate_zones(
    mgra_gdf,
    method="kmeans",
    n_zones=2000,
    random_state=0,
    cluster_factors=None,
    cluster_factors_onehot=None,
    use_xy=True,
    explicit_agg=(),
    agg_instruction=None,
):
    """
    Aggregate zones.

    Parameters
    ----------
    mgra_gdf : GeoDataFrame
        Geometry and attibutes of MGRAs
    method : {'kmeans', 'agglom', 'agglom_adj'}
    n_zones : int
    random_state : RandomState or int
    cluster_factors : dict
    cluster_factors_onehot : dict
    use_xy : bool
        Use X and Y coordinates as a cluster factor
    explicit_agg : list[int or list]
        A list containing integers (individual MGRAs that should not be aggregated)
        or lists of integers (groups of MGRAs that should be aggregated exactly as
        given, with no less and no more)
    agg_instruction : dict
        Dictionary passed to pandas `agg` that says how to aggregate data columns.

    Returns
    -------
    GeoDataFrame
    """

    if cluster_factors is None:
        cluster_factors = {}

    n = 1
    if explicit_agg:
        explicit_agg_ids = {}
        for i in explicit_agg:
            if isinstance(i, Number):
                explicit_agg_ids[i] = n
            else:
                for j in i:
                    explicit_agg_ids[j] = n
            n += 1
        in_explicit = mgra_gdf["mgra"].isin(explicit_agg_ids)
        mgra_gdf_algo = mgra_gdf.loc[~in_explicit].copy()
        mgra_gdf_explicit = mgra_gdf.loc[in_explicit].copy()
        mgra_gdf_explicit["cluster_id"] = mgra_gdf_explicit["mgra"].map(
            explicit_agg_ids
        )
        n_zones_algorithm = n_zones - len(
            mgra_gdf_explicit["cluster_id"].value_counts()
        )
    else:
        mgra_gdf_algo = mgra_gdf.copy()
        mgra_gdf_explicit = None
        n_zones_algorithm = n_zones

    if use_xy:
        geometry = mgra_gdf_algo.centroid
        X = list(geometry.apply(lambda p: p.x))
        Y = list(geometry.apply(lambda p: p.y))
        factors = [np.asarray(X) * use_xy, np.asarray(Y) * use_xy]
    else:
        factors = []
    for cf, cf_wgt in cluster_factors.items():
        factors.append(cf_wgt * mgra_gdf_algo[cf].values.astype(np.float32))
    if cluster_factors_onehot:
        for cf, cf_wgt in cluster_factors_onehot.items():
            factors.append(cf_wgt * OneHotEncoder().fit_transform(mgra_gdf_algo[[cf]]))
        from scipy.sparse import hstack

        factors2d = []
        for j in factors:
            if j.ndim < 2:
                factors2d.append(np.expand_dims(j, -1))
            else:
                factors2d.append(j)
        data = hstack(factors2d).toarray()
    else:
        data = np.array(factors).T

    if method == "kmeans":
        kmeans = KMeans(n_clusters=n_zones_algorithm, random_state=random_state)
        kmeans.fit(data)
        cluster_id = kmeans.labels_
    elif method == "agglom":
        agglom = AgglomerativeClustering(
            n_clusters=n_zones_algorithm, affinity="euclidean", linkage="ward"
        )
        agglom.fit_predict(data)
        cluster_id = agglom.labels_
    elif method == "agglom_adj":
        from libpysal.weights import Rook

        w_rook = Rook.from_dataframe(mgra_gdf_algo)
        adj_mat = nx.adjacency_matrix(w_rook.to_networkx())
        agglom = AgglomerativeClustering(
            n_clusters=n_zones_algorithm,
            affinity="euclidean",
            linkage="ward",
            connectivity=adj_mat,
        )
        agglom.fit_predict(data)
        cluster_id = agglom.labels_
    else:
        raise NotImplementedError(method)
    mgra_gdf_algo["cluster_id"] = cluster_id
    if agg_instruction is None:
        # TODO: fill out the aggregation data system
        # Define a lambda function to compute the weighted mean:
        wgt_avg_by_hh = (
            lambda x: np.average(x, weights=mgra_gdf.loc[x.index, "hh"])
            if mgra_gdf.loc[x.index, "hh"].sum() > 0
            else 0
        )
        wgt_avg_hpc = (
            lambda x: np.average(x, weights=mgra_gdf.loc[x.index, "hstallssam"])
            if mgra_gdf.loc[x.index, "hstallssam"].sum() > 0
            else 0
        )
        wgt_avg_dpc = (
            lambda x: np.average(x, weights=mgra_gdf.loc[x.index, "dstallssam"])
            if mgra_gdf.loc[x.index, "dstallssam"].sum() > 0
            else 0
        )
        wgt_avg_mpc = (
            lambda x: np.average(x, weights=mgra_gdf.loc[x.index, "mstallssam"])
            if mgra_gdf.loc[x.index, "mstallssam"].sum() > 0
            else 0
        )
        wgt_avg_by_pop = (
            lambda x: np.average(x, weights=mgra_gdf.loc[x.index, "pop"])
            if mgra_gdf.loc[x.index, "pop"].sum() > 0
            else 0
        )
        wgt_avg_empden = (
            lambda x: np.average(x, weights=mgra_gdf.loc[x.index, "emp_total"])
            if mgra_gdf.loc[x.index, "emp_total"].sum() > 0
            else 0
        )
        wgt_avg_rtempden = (
            lambda x: np.average(x, weights=mgra_gdf.loc[x.index, "emp_retail"])
            if mgra_gdf.loc[x.index, "emp_retail"].sum() > 0
            else 0
        )
        wgt_avg_peden = (
            lambda x: np.average(
                x,
                weights=(
                    mgra_gdf.loc[x.index, "emp_total"] + mgra_gdf.loc[x.index, "pop"]
                ),
            )
            if (
                mgra_gdf.loc[x.index, "emp_total"].sum()
                + mgra_gdf.loc[x.index, "pop"].sum()
            )
            > 0
            else 0
        )
        get_mode = lambda x: mode(x)
        agg_instruction = {
            "hs": "sum",
            "hs_sf": "sum",
            "hs_mf": "sum",
            "hs_mh": "sum",
            "hh": "sum",
            "hh_sf": "sum",
            "hh_mf": "sum",
            "hh_mh": "sum",
            "gq_civ": "sum",
            "gq_mil": "sum",
            "i1": "sum",
            "i2": "sum",
            "i3": "sum",
            "i4": "sum",
            "i5": "sum",
            "i6": "sum",
            "i7": "sum",
            "i8": "sum",
            "i9": "sum",
            "i10": "sum",
            "hhs": wgt_avg_by_hh,
            "pop": "sum",
            "hhp": "sum",
            "emp_ag": "sum",
            "emp_const_non_bldg_prod": "sum",
            "emp_const_non_bldg_office": "sum",
            "emp_utilities_prod": "sum",
            "emp_utilities_office": "sum",
            "emp_const_bldg_prod": "sum",
            "emp_const_bldg_office": "sum",
            "emp_mfg_prod": "sum",
            "emp_mfg_office": "sum",
            "emp_whsle_whs": "sum",
            "emp_trans": "sum",
            "emp_retail": "sum",
            "emp_prof_bus_svcs": "sum",
            "emp_prof_bus_svcs_bldg_maint": "sum",
            "emp_pvt_ed_k12": "sum",
            "emp_pvt_ed_post_k12_oth": "sum",
            "emp_health": "sum",
            "emp_personal_svcs_office": "sum",
            "emp_amusement": "sum",
            "emp_hotel": "sum",
            "emp_restaurant_bar": "sum",
            "emp_personal_svcs_retail": "sum",
            "emp_religious": "sum",
            "emp_pvt_hh": "sum",
            "emp_state_local_gov_ent": "sum",
            "emp_fed_non_mil": "sum",
            "emp_fed_mil": "sum",
            "emp_state_local_gov_blue": "sum",
            "emp_state_local_gov_white": "sum",
            "emp_public_ed": "sum",
            "emp_own_occ_dwell_mgmt": "sum",
            "emp_fed_gov_accts": "sum",
            "emp_st_lcl_gov_accts": "sum",
            "emp_cap_accts": "sum",
            "emp_total": "sum",
            "enrollgradekto8": "sum",
            "enrollgrade9to12": "sum",
            "collegeenroll": "sum",
            "othercollegeenroll": "sum",
            "adultschenrl": "sum",
            "ech_dist": get_mode,
            "hch_dist": get_mode,
            "parkarea": "max",
            "hstallsoth": "sum",
            "hstallssam": "sum",
            "hparkcost": wgt_avg_hpc,
            "numfreehrs": wgt_avg_hpc,
            "dstallsoth": "sum",
            "dstallssam": "sum",
            "dparkcost": wgt_avg_dpc,
            "mstallsoth": "sum",
            "mstallssam": "sum",
            "mparkcost": wgt_avg_mpc,
            "parkactive": "sum",
            "openspaceparkpreserve": "sum",
            "beachactive": "sum",
            "budgetroom": "sum",
            "economyroom": "sum",
            "luxuryroom": "sum",
            "midpriceroom": "sum",
            "upscaleroom": "sum",
            "hotelroomtotal": "sum",
            # "luz_id": "sum",
            "truckregiontype": "sum",
            # "district27": "sum",
            "milestocoast": wgt_avg_by_pop,
            # "acres": "sum",
            # "effective_acres": "sum",
            # "land_acres": "sum",
            "MicroAccessTime": wgt_avg_by_pop,
            "remoteAVParking": "max",
            "refueling_stations": "sum",
            "totint": "sum",
            "duden": wgt_avg_by_hh,
            "empden": wgt_avg_empden,
            # "popden": "sum",
            "retempden": wgt_avg_rtempden,
            # "totintbin": "sum", #bins in original data 0, 80, 130
            # "empdenbin": "sum", #bins in original data 0, 10, 30
            # "dudenbin": "sum", #bins in original data  0, 5, 10
            "PopEmpDenPerMi": wgt_avg_peden,
        }

    pending = []
    for df in [mgra_gdf_algo, mgra_gdf_explicit]:

        dissolved = df[["cluster_id", "geometry"]].dissolve(by="cluster_id")
        dissolved = dissolved.join(
            mgra_gdf_algo.groupby("cluster_id").agg(agg_instruction)
        )

        # adding bins
        dissolved["totintbin"] = 1
        dissolved.loc[
            (dissolved["totintbin"] >= 80) & (dissolved["totintbin"] < 130), "totintbin"
        ] = 2
        dissolved.loc[(dissolved["totintbin"] >= 130), "totintbin"] = 3

        dissolved["empdenbin"] = 1
        dissolved.loc[
            (dissolved["empdenbin"] >= 10) & (dissolved["empdenbin"] < 30), "empdenbin"
        ] = 2
        dissolved.loc[(dissolved["empdenbin"] >= 30), "empdenbin"] = 3

        dissolved["dudenbin"] = 1
        dissolved.loc[
            (dissolved["dudenbin"] >= 5) & (dissolved["dudenbin"] < 10), "dudenbin"
        ] = 2
        dissolved.loc[(dissolved["dudenbin"] >= 10), "dudenbin"] = 3

        pending.append(dissolved)

    pending[0]["cluster_id"] = list(range(n, n + n_zones_algorithm))
    pending[0] = pending[0][[c for c in pending[1].columns if c in pending[0].columns]]
    pending[1] = pending[1][[c for c in pending[0].columns if c in pending[1].columns]]
    combined = pd.concat(pending, ignore_index=False)
    combined = combined.reset_index(drop=True)

    return combined


def _scale_zones(x, zones_by_district, district_focus):
    x = np.abs(x)
    agg_by_district = pd.Series(zones_by_district) * x
    for i, j in district_focus.items():
        agg_by_district[i] *= j
    agg_by_district = np.minimum(agg_by_district, zones_by_district)
    agg_by_district = np.maximum(agg_by_district, 1)
    return agg_by_district


def _rescale_zones(x, n_z, zones_by_district, district_focus):
    return (_scale_zones(x, zones_by_district, district_focus).sum() - n_z) ** 2


def aggregate_zones_within_districts(
    mgra_gdf,
    method="kmeans",
    n_zones=2000,
    random_state=0,
    cluster_factors=None,
    cluster_factors_onehot=None,
    use_xy=True,
    explicit_agg=(),
    agg_instruction=None,
    district_col="district27",
    district_focus=None,
):
    logger.info("aggregate_zones_within_districts...")
    if district_focus is None:
        district_focus = {}
    zones_by_district = mgra_gdf[district_col].value_counts()
    rescale_zones = partial(
        _rescale_zones,
        n_z=n_zones,
        zones_by_district=zones_by_district,
        district_focus=district_focus,
    )
    zone_factor = minimize_scalar(rescale_zones).x
    agg_by_district = (
        _scale_zones(zone_factor, zones_by_district, district_focus).round().astype(int)
    )
    out = []
    for district_n, district_z in agg_by_district.items():
        logger.info(f"combining district {district_n} into {district_z} zones")
        out.append(
            aggregate_zones(
                mgra_gdf[mgra_gdf[district_col] == district_n],
                method=method,
                n_zones=district_z,
                random_state=random_state + district_n,
                cluster_factors=cluster_factors,
                cluster_factors_onehot=cluster_factors_onehot,
                use_xy=use_xy,
                explicit_agg=explicit_agg,
                agg_instruction=agg_instruction,
            )
        )
    return pd.concat(out).reset_index(drop=True)


def viewer(
    gdf,
    *,
    simplify_tolerance=None,
    color=None,
    transparent=False,
    **kwargs,
):
    import plotly.express as px

    gdf = gdf.copy()
    if simplify_tolerance is not None:
        gdf.geometry = gdf.geometry.simplify(tolerance=simplify_tolerance)
    gdf = gdf.to_crs(pyproj.CRS.from_epsg(4326))
    kwargs1 = {}
    if color is not None:
        kwargs1["color"] = color
    fig = px.choropleth(
        gdf,
        geojson=gdf.geometry,
        locations=gdf.index,
        **kwargs1,
    )
    fig.update_shapes()
    fig.update_geos(
        visible=False,
        fitbounds="locations",
    )
    fig.update_layout(height=300, margin={"r": 0, "t": 0, "l": 0, "b": 0})
    if kwargs:
        fig.update_traces(**kwargs)
    if transparent:
        fig.update_traces(
            colorscale=((0.0, "rgba(0, 0, 0, 0.0)"), (1.0, "rgba(0, 0, 0, 0.0)"))
        )
    return fig


def viewer2(
    edges,
    colors,
    color_col,
):
    coloring_map = viewer(colors, color=color_col, marker_line_width=0)
    edge_map = viewer(edges, transparent=True, marker_line_color="white")
    coloring_map.add_trace(edge_map.data[0])
    return coloring_map
