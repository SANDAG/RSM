import logging

import networkx as nx
import numpy as np
import pandas as pd
import pyproj
from statistics import mode
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
    explicit_agg=(),  # TODO
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


    if not explicit_agg:
        mgra_gdf = mgra_gdf.copy()
        n_zones_upd = n_zones

    else:
        mgra_gdf = mgra_gdf.loc[~mgra_gdf['mgra'].isin(explicit_agg)]
        mgra_gdf_explicit = mgra_gdf.loc[mgra_gdf['mgra'].isin(explicit_agg)]
        n_zones_upd = n_zones - len(mgra_gdf_explicit)


    if use_xy:
        geometry = mgra_gdf.centroid
        X = list(geometry.apply(lambda p: p.x))
        Y = list(geometry.apply(lambda p: p.y))
        factors = [X, Y]
    else:
        factors = []
    for cf, cf_wgt in cluster_factors.items():
        factors.append(cf_wgt * mgra_gdf[cf].values.astype(np.float32))
    if cluster_factors_onehot:
        for cf, cf_wgt in cluster_factors_onehot.items():
            factors.append(cf_wgt * OneHotEncoder().fit_transform(mgra_gdf[[cf]]))
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
        kmeans = KMeans(n_clusters=n_zones_upd, random_state=random_state)
        kmeans.fit(data)
        cluster_id = kmeans.labels_
    elif method == "agglom":
        agglom = AgglomerativeClustering(
            n_clusters=n_zones_upd, affinity="euclidean", linkage="ward"
        )
        agglom.fit_predict(data)
        cluster_id = agglom.labels_
    elif method == "agglom_adj":
        from libpysal.weights import Rook

        w_rook = Rook.from_dataframe(mgra_gdf)
        adj_mat = nx.adjacency_matrix(w_rook.to_networkx())
        agglom = AgglomerativeClustering(
            n_clusters=n_zones_upd,
            affinity="euclidean",
            linkage="ward",
            connectivity=adj_mat,
        )
        agglom.fit_predict(data)
        cluster_id = agglom.labels_
    else:
        raise NotImplementedError(method)
    mgra_gdf["cluster_id"] = cluster_id
    if agg_instruction is None:
        # TODO: fill out the aggregation data system
        # Define a lambda function to compute the weighted mean:
        
        wgt_avg_hh = lambda x: np.average(x, weights=mgra_gdf.loc[x.index, 'hh']) if mgra_gdf.loc[x.index, 'hh'].sum()> 0 else 0
        wgt_avg_hpc = lambda x: np.average(x, weights=mgra_gdf.loc[x.index, 'hstallssam']) if mgra_gdf.loc[x.index,'hstallssam'].sum()>0 else 0
        wgt_avg_dpc = lambda x: np.average(x, weights=mgra_gdf.loc[x.index,'dstallssam']) if mgra_gdf.loc[x.index,'dstallssam'].sum()>0 else 0
        wgt_avg_mpc = lambda x: np.average(x, weights=mgra_gdf.loc[x.index, 'mstallssam']) if mgra_gdf.loc[x.index,'mstallssam'].sum()>0 else 0
        wgt_avg_mtc = lambda x: np.average(x, weights=mgra_gdf.loc[x.index, 'pop']) if mgra_gdf.loc[x.index, 'pop'].sum()>0 else 0
        wgt_avg_mat = lambda x: np.average(x, weights=mgra_gdf.loc[x.index, 'pop']) if mgra_gdf.loc[x.index, 'pop'].sum()>0 else 0
        wgt_avg_dud = lambda x: np.average(x, weights=mgra_gdf.loc[x.index, 'hh']) if mgra_gdf.loc[x.index, 'hh'].sum()>0 else 0
        wgt_avg_empden = lambda x: np.average(x, weights=mgra_gdf.loc[x.index, 'emp_total']) if mgra_gdf.loc[x.index, 'emp_total'].sum()>0 else 0
        wgt_avg_rtempden = lambda x: np.average(x, weights=mgra_gdf.loc[x.index, 'emp_total']) if mgra_gdf.loc[x.index, 'emp_retail'].sum()>0 else 0
        wgt_avg_peden = lambda x: np.average(x, weights=(mgra_gdf.loc[x.index, 'emp_total'] + mgra_gdf.loc[x.index, 'pop'])) if (mgra_gdf.loc[x.index, 'emp_total'].sum()+mgra_gdf.loc[x.index, 'pop'].sum())>0 else 0
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
            "hhs": wgt_avg_hh,
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
            #"luz_id": "sum",
            "truckregiontype": "sum",
            #"district27": "sum",
            "milestocoast": wgt_avg_mtc,
            #"acres": "sum",
            #"effective_acres": "sum",
            #"land_acres": "sum",
            "MicroAccessTime": wgt_avg_mat,
            "remoteAVParking": "max",
            "refueling_stations": "sum",
            "totint": "sum",
            "duden": wgt_avg_dud,
            "empden": wgt_avg_empden,
            #"popden": "sum",
            "retempden": wgt_avg_rtempden,
            #"totintbin": "sum", #bins in original data 0, 80, 130 
            #"empdenbin": "sum", #bins in original data 0, 10, 30
            #"dudenbin": "sum", #bins in original data  0, 5, 10
            "PopEmpDenPerMi": wgt_avg_peden
        }
    dissolved = mgra_gdf[["cluster_id", "geometry"]].dissolve(by="cluster_id")
    dissolved = dissolved.join(mgra_gdf.groupby("cluster_id").agg(agg_instruction))

    #adding bins
    dissolved['totintbin'] = 1
    dissolved.loc[(dissolved['totintbin'] >= 80) & (dissolved['totintbin'] < 130), 'totintbin'] = 2
    dissolved.loc[(dissolved['totintbin'] >= 130), 'totintbin'] = 3

    dissolved['empdenbin'] = 1
    dissolved.loc[(dissolved['empdenbin'] >= 10) & (dissolved['empdenbin'] < 30), 'empdenbin'] = 2
    dissolved.loc[(dissolved['empdenbin'] >= 30), 'empdenbin'] = 3

    dissolved['dudenbin'] = 1
    dissolved.loc[(dissolved['dudenbin'] >=5 ) & (dissolved['dudenbin'] < 10), 'dudenbin'] = 2
    dissolved.loc[(dissolved['dudenbin'] >= 10), 'dudebin'] = 3

    
    dissolved["cluster_id"] = list(range(n_zones_upd, n_zones, 1))
    dissolved = pd.concat([dissolved, mgra_gdf_explicit], ignore_index = False)
    dissolved = dissolved.reset_index(drop=True)

    return dissolved


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
