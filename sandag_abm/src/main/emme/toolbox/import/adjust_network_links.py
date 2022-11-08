#//////////////////////////////////////////////////////////////////////////////
#////                                                                       ///
#////                                                                       ///
#//// Rights to use and modify are granted to the                           ///
#//// San Diego Association of Governments and partner agencies.            ///
#//// This copyright notice must be preserved.                              ///
#////                                                                       ///
#//// import/adjust_network_links.py                                        ///
#////                                                                       ///
#////                                                                       ///
#////                                                                       ///
#////                                                                       ///
#//////////////////////////////////////////////////////////////////////////////
#
#
# deletes the existing centroid connectors and create new centroid connectors
# connecting the centroid of aggregated zones to the original end points (on network)
# of old centroid connectors
#
# Inputs:
#    source: path to the location of the input network files
#    base_scenario: scenario that has highway network only
#    emmebank: the Emme database in which to the new network is published
#    external_zone: string "1-12" that refernces to range of external zones
#    taz_cwk_file: input csv file created after zone aggregation. It has the crosswalk between existing TAZ to new zone structure
#    cluster_zone_file: input csv file created after zone aggregation. It has the centroid coordinates of the new zone structure
#
#

import os

import inro.modeller as _m
import pandas as pd
from scipy.spatial import distance


def adjust_network_links(source, base_scenario, emmebank, external_zone, taz_cwk_file, cluster_zone_file)

    taz_cwk = pd.read_csv(os.path.join(source, taz_cwk_file), index_col = 0)
    taz_cwk = taz_cwk['cluster_id'].to_dict()

    emmebank = _m.Modeller().emmebank
    scenario = emmebank.scenario(base_scenario)
    hwy_network = scenario.get_network()

    centroid_nodes = []
    exclude_nodes = []


    ext_zones = [int(s) for s in external_zone.split() if s.isdigit()]

    for node in range(ext_zones[0],ext_zones[1],1):
        exclude_nodes.append(hwy_network.node(node))

    for node in hwy_network.centroids():
        if not node in exclude_nodes:
            centroid_nodes.append(node)

    i_nodes = []
    j_nodes = []
    data1 = []
    length = []
    links = []

    for link in hwy_network.links():
        if link.i_node in centroid_nodes:
            links.append(link)
            i_nodes.append(int(link.i_node))
            j_nodes.append(int(link.j_node))
            data1.append(link.data1)
            length.append(link.length)

    df = pd.DataFrame({'links' : links, 'i_nodes' : i_nodes, 'j_nodes': j_nodes, 'ul1_org': data1, 'length_org':length})
    df['i_nodes_new'] = df['i_nodes'].map(taz_cwk)

    #get XY of existing centroids
    j_nodes_list = df['j_nodes'].unique()
    j_nodes_list = [hwy_network.node(x) for x in j_nodes_list]

    j_nodes = []
    j_x = []
    j_y = []
    for nodes in hwy_network.nodes():
        if nodes in j_nodes_list:
            j_nodes.append(nodes)
            j_x.append(nodes.x)
            j_y.append(nodes.y)

    j_nodes_XY = pd.DataFrame({'j_nodes' : j_nodes, 'j_x' : j_x, 'j_y': j_y})
    j_nodes_XY['j_nodes'] = [int(x) for x in j_nodes_XY['j_nodes']]
    df = pd.merge(df, j_nodes_XY, on = 'j_nodes', how = 'left')

    agg_node_coords = pd.read_csv(os.path.join(source, cluster_zone_file))
    df = pd.merge(df, agg_node_coords, left_on = 'i_nodes_new', right_on = 'cluster_id', how = 'left')
    df = df.drop(columns = 'cluster_id')
    df = df.rename(columns = {'centroid_x' : 'i_new_x', 'centroid_y' : 'i_new_y'})

    i_coords = zip(df['j_x'], df['j_y'])
    j_coords = zip(df['i_new_x'], df['i_new_y'])

    df['length'] = [distance.euclidean(i, j)/5280.0 for i,j in zip(i_coords, j_coords)]

    #delete all the existing centroid nodes
    for index,row in df.iterrows():
        if hwy_network.node(row['i_nodes']):
            hwy_network.delete_node(row['i_nodes'], True)

    # create new nodes (centroids of clusters)
    for index,row in agg_node_coords.iterrows():
        new_node = hwy_network.create_node(row['cluster_id'], is_centroid = True)
        new_node.x = int(row['centroid_x'])
        new_node.y = int(row['centroid_y'])

    df['type'] = 10
    df['num_lanes'] = 1
    df['vdf'] = 11
    df['ul3'] = 999999

    final_df = df[["i_nodes_new", "j_nodes", "length", "type", "num_lanes", "vdf", "ul3"]]
    final_df = final_df.drop_duplicates()
    final_df = final_df.reset_index(drop=True)
    final_df['type'] = final_df['type'].astype("int")

    # create new links
    for index,row in final_df.iterrows():

        link_ij = hwy_network.create_link(row['i_nodes_new'], row['j_nodes'],
                            modes = ["d", "h", "H", "i","I","s", "S", "v", "V", "m", "M", "t", "T"])
        link_ij.length = row['length']
        link_ij.type = row['type'].astype("int")
        link_ij.num_lanes = row['num_lanes'].astype("int")
        link_ij.volume_delay_func = row['vdf'].astype("int")
        link_ij.data3 = row['ul3'].astype("int")
        link_ij['@lane_ea'] = 1 # had to do this as they are being replaced in highway assignment by the values in these columns
        link_ij['@lane_am'] = 1
        link_ij['@lane_md'] = 1
        link_ij['@lane_pm'] = 1
        link_ij['@lane_ev'] = 1


        link_ji = hwy_network.create_link(row['j_nodes'], row['i_nodes_new'],
                            modes = ["d", "h", "H", "i","I","s", "S", "v", "V", "m", "M", "t", "T"])
        link_ji.length = row['length']
        link_ji.type = row['type'].astype("int")
        link_ji.num_lanes = row['num_lanes'].astype("int")
        link_ji.volume_delay_func = row['vdf'].astype("int")
        link_ji.data3 = row['ul3'].astype("int")
        link_ji['@lane_ea'] = 1 # had to do this as they are being replaced in highway assignment by the values in these columns
        link_ji['@lane_am'] = 1
        link_ji['@lane_md'] = 1
        link_ji['@lane_pm'] = 1
        link_ji['@lane_ev'] = 1

    return(hwy_network)
    #publish the highway network to the scenario
    #scenario.publish_network(hwy_network)
