import openmatrix as omx
import pandas as pd
import numpy as np
import os
import yaml
import itertools
import geopandas as gpd


def geo_post_processing(shapefile_name, shapefile_dir, mgra_json_file_name, hywload_shape_file_name, hywload_json_file_name, cpa_orig_shp_file_name, cpa_json_file_name, scenario, base ):

    scenario_dir = os.path.join("SimWrapper\\data\\external", scenario)  
    output_dir = os.path.join("SimWrapper\\data\\processed", scenario)
    # convert shapefiles to json for base
    if (base ==1):
         mgra_orig_shp = gpd.read_file(os.path.join(shapefile_dir, shapefile_name))

    else :
        mgra_orig_shp = gpd.read_file(os.path.join(scenario_dir, shapefile_name))

    mgra_orig_shp.to_file(os.path.join(output_dir, mgra_json_file_name), driver='GeoJSON')

    # convert shapefiles to json for rsm
    # project the network shapefile
    network_shape = gpd.read_file(os.path.join(scenario_dir, hywload_shape_file_name))
    network_shape_prj = network_shape.to_crs(epsg=4269)
    network_shape_prj.to_file(os.path.join(output_dir, hywload_json_file_name), driver='GeoJSON')

    #convert cpa shapefile to json
    cpa_orig_shp = gpd.read_file(os.path.join(shapefile_dir, cpa_orig_shp_file_name))
    cpa_orig_shp_prj = cpa_orig_shp.to_crs(epsg=4269)

    cpa_orig_shp_prj.to_file(os.path.join(output_dir, cpa_json_file_name), driver='GeoJSON')


def generate_rsm_shapefile(mgra_shapefile_dir, original_shapefile_name, rsm_shape_file_name, cross_reference_mgra_name, rsm_scenario ):
    
    scenario_dir = os.path.join("SimWrapper\\data\\external", rsm_scenario)
    # create and save rsm new shapefile
    mgra_orig_shp = gpd.read_file(os.path.join(mgra_shapefile_dir, original_shapefile_name))
    cross_reference_mgra = pd.read_csv(os.path.join(scenario_dir,cross_reference_mgra_name))
    mgra_orig_shp = mgra_orig_shp.merge(cross_reference_mgra, on = "MGRA", how = "left")
    mgra_rsm = gpd.GeoDataFrame(mgra_orig_shp)
    mgra_rsm = mgra_orig_shp.dissolve(by='cluster_id')
    mgra_rsm.to_file(os.path.join(scenario_dir, rsm_shape_file_name))


def combine_scenarios_summary (scenario_list, mode_summary_file_name, vmt_summary_file_name, vmt_intrazonal_df_file_name, out_dir):

    
    summary_reports_names = [mode_summary_file_name, vmt_summary_file_name]
    temp1 = pd.DataFrame()
    for scenario in scenario_list:
        scenario_dir = os.path.join("SimWrapper\\data\\processed", scenario)  
        summary_df = pd.read_csv(os.path.join(scenario_dir,mode_summary_file_name))
        temp1["tripMode"] = summary_df["tripMode"]
        temp1[scenario] = summary_df["share"]

    temp1.to_csv(os.path.join(out_dir, mode_summary_file_name))

    temp2 = pd.DataFrame()
    for scenario in scenario_list:
        scenario_dir = os.path.join("SimWrapper\\data\\processed", scenario)  
        summary_df = pd.read_csv(os.path.join(scenario_dir,vmt_summary_file_name))
        temp2["class"] = summary_df["class"]
        temp2[scenario] = summary_df["vmt_total"]

    temp2.to_csv(os.path.join(out_dir, vmt_summary_file_name))

    temp3 = pd.DataFrame()
    for scenario in scenario_list:
        scenario_dir = os.path.join("SimWrapper\\data\\processed", scenario)  
        summary_df = pd.read_csv(os.path.join(scenario_dir,vmt_intrazonal_df_file_name))
        temp2["type"] = summary_df["type"]
        temp2[scenario] = summary_df["vehicle_miles"]

    temp3.to_csv(os.path.join(out_dir, vmt_intrazonal_df_file_name))

def compare_network_summary (network_comparison_scenario_pair, network_summary_file_name, out_dir):

     
    scenario1_dir = os.path.join("SimWrapper\\data\\processed", network_comparison_scenario_pair[0])  
    scenario2_dir = os.path.join("SimWrapper\\data\\processed", network_comparison_scenario_pair[1])  
    network_summary1 = pd.read_csv(os.path.join(scenario1_dir,network_summary_file_name))
    network_summary2 = pd.read_csv(os.path.join(scenario2_dir,network_summary_file_name) )
    network_summary_dif = (network_summary1.set_index(['ID'])- network_summary2.set_index(['ID'])).reset_index()
    out_file_name = os.path.join(out_dir,  "netowrk_summary_" + network_comparison_scenario_pair[0] + "_" + network_comparison_scenario_pair[1] + "_difference.csv")
    network_summary_dif.to_csv(out_file_name)

def intrazonal_vmt_aggregation(vmt_summary_df_file_name, intrazonal_vmt_df_file_name, vmt_intrazonal_df_file_name, scenario):

    scenario_dir = os.path.join("SimWrapper\\data\\processed", scenario)
    vmt_summary_df = pd.read_csv(os.path.join(scenario_dir, vmt_summary_df_file_name))
    intrazonal_vmt_df = pd.read_csv(os.path.join(scenario_dir, intrazonal_vmt_df_file_name))
    intrazonal_vmt_df["vmt"] = intrazonal_vmt_df["distance"]
    intrazonal_vmt_df["vmt"][intrazonal_vmt_df['tripMode']== "Shared Ride 2"] = intrazonal_vmt_df["distance"]/2
    intrazonal_vmt_df["vmt"][intrazonal_vmt_df['tripMode'] == "Shared Ride 3+"] = intrazonal_vmt_df["distance"]/3
    intrazonal_vmt = intrazonal_vmt_df["distance"].sum() 
    vmt = vmt_summary_df["vmt_total"].sum()
    vmt_df = pd.DataFrame([intrazonal_vmt, vmt], index = ["intrazonal_vmt", "vmt"]).reset_index().set_axis(['type', 'vehicle_miles'], axis=1, inplace=False) 
    out_file_name = os.path.join(scenario_dir, vmt_intrazonal_df_file_name)
    vmt_df.to_csv(out_file_name)

if __name__ == "__main__":

    print("Running Visulizer Support Script")


    working_directory = ("C:\\projects\\SimWrapper\\RSM\\RSM\\visualizer\\")
    shapefile_dir =  "SimWrapper\\data\\external\\shapefile"
    original_shapefile_name = "MGRA13_gcs.shp"
    base_shape_file_name = "MGRA13_gcs.shp"
    cross_reference_mgra_name = "mgra_crosswalk.csv"
    hywload_shape_file_name = "hwyLoad.shp"
    cross_reference_mgra_cpa_name = "mgra_crosswalk.csv"
    cpa_shape_file_name = "CityCPA.shp"
    cpa_json_file_name = "CityCPA.geojson"
    network_summary_file_name = "network_summary.csv"
    scenario_list = ["donor_model", "run1", "run2", "run4","run7","run8","run9"]
    rsm_scenario_list = ["run9"]
    base_scenario = "donor_model"
    rsm_shapefile_names = ["MGRA13_gcs_run9.shp"]
    rsm_json_file_names = ["MGRA13_gcs_run1.geojson", "MGRA13_gcs_run2.geojson","MGRA13_gcs_run4.geojson","MGRA13_gcs_run7.geojson", "MGRA13_gcs_run8.geojson","MGRA13_gcs_run9.geojson"]
    base_json_file_name = "MGRA13_gcs.geojson"
    mode_summary_file_name = "trip_mode_summary.csv"
    vmt_summary_file_name = "vmt_summary.csv"
    network_summary_file_name = "network_summary.csv"
    compared_scenarios_dir = "SimWrapper\\data\\processed\\all_runs"
    vmt_summary_df_file_name = "vmt_summary.csv"
    intrazonal_vmt_df_file_name = "trips_intrazonal_summary.csv"
    vmt_intrazonal_df_file_name ="vmt_intrazonal_summary.csv"
    hywload_json_file_name = "hwyLoad.geojson"

    for scenario, shape_name in zip(rsm_scenario_list,rsm_shapefile_names):
        generate_rsm_shapefile (shapefile_dir, original_shapefile_name, shape_name, cross_reference_mgra_name, scenario )

    for scenario, shape_name, json_name in zip(rsm_scenario_list,rsm_shapefile_names, rsm_json_file_names):
        geo_post_processing(shape_name, shapefile_dir, json_name, hywload_shape_file_name, cpa_shape_file_name, cpa_json_file_name, scenario, base = 0)

    geo_post_processing(base_shape_file_name, shapefile_dir, base_json_file_name, hywload_shape_file_name, cpa_shape_file_name, cpa_json_file_name, scenario, base = 1)

    for scenario in scenario_list:
        intrazonal_vmt_aggregation(vmt_summary_df_file_name, intrazonal_vmt_df_file_name, vmt_intrazonal_df_file_name, scenario)

    combine_scenarios_summary (scenario_list, mode_summary_file_name, vmt_summary_file_name, compared_scenarios_dir)

#    for pair in list(itertools.combinations(scenario_list, 2)):
#        compare_network_summary (pair, network_summary_file_name, compared_scenarios_dir)