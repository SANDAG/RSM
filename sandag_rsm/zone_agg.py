import logging

import networkx as nx
import numpy as np
import pyproj
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
    mgra_gdf = mgra_gdf.copy()
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
        kmeans = KMeans(n_clusters=n_zones, random_state=random_state)
        kmeans.fit(data)
        cluster_id = kmeans.labels_
    elif method == "agglom":
        agglom = AgglomerativeClustering(
            n_clusters=n_zones, affinity="euclidean", linkage="ward"
        )
        agglom.fit_predict(data)
        cluster_id = agglom.labels_
    elif method == "agglom_adj":
        from libpysal.weights import Rook

        w_rook = Rook.from_dataframe(mgra_gdf)
        adj_mat = nx.adjacency_matrix(w_rook.to_networkx())
        agglom = AgglomerativeClustering(
            n_clusters=n_zones,
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
        wgt_avg = lambda x: np.average(x, weights=mgra_gdf.loc[x.index].area)
        agg_instruction = {
            "pop": "sum",
            "popden": wgt_avg,
        }
    dissolved = mgra_gdf[["cluster_id", "geometry"]].dissolve(by="cluster_id")
    dissolved = dissolved.join(mgra_gdf.groupby("cluster_id").agg(agg_instruction))
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
