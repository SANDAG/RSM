#import openmatrix as omx
import pandas as pd
import numpy as np
import os
import yaml
import itertools
import geopandas as gpd
import sys

def shapefile_to_jason(shapefile_dir, base_scenario):
    
    base_dir = os.path.join("SimWrapper\\data\\external", base_scenario)   
    output_dir = os.path.join("SimWrapper\\data\\processed", base_scenario)
    base_json_file_name = "MGRA13_gcs" + "_" + base_scenario + ".json"
    # convert shapefiles to json for base
    mgra_base_shp = gpd.read_file(os.path.join(shapefile_dir, "MGRA13_gcs.shp"))
    mgra_base_shp.to_file(os.path.join(output_dir, base_json_file_name), driver='GeoJSON')
    #convert cpa shapefile to json
    cpa_orig_shp = gpd.read_file(os.path.join(shapefile_dir, "SRA.shp"))
    cpa_orig_shp_prj = cpa_orig_shp.to_crs(epsg=4269)
    cpa_orig_shp_prj.to_file(os.path.join(shapefile_dir, "SRA.json"), driver='GeoJSON')
    #convert network files to json
    network_shape = gpd.read_file(os.path.join(base_dir, "report", "hwyload_458.shp"))
    network_shape_prj = network_shape.to_crs(epsg=4269)
    network_shape_prj.to_file(os.path.join(output_dir, "hywload.json"), driver='GeoJSON')    

def rsm_geo_post_processing(scenario):

    scenario_dir = os.path.join("SimWrapper\\data\\external", scenario)  
    output_dir = os.path.join("SimWrapper\\data\\processed", scenario)
    rsm_shape_file_name = "MGRA13_gcs" + "_" + scenario + ".shp"
    rsm_json_file_name = "MGRA13_gcs" + "_" + scenario + ".json"
    # convert shapefiles to json for base
    mgra_rsm_shp = gpd.read_file(os.path.join(output_dir, rsm_shape_file_name))
    mgra_rsm_shp.to_file(os.path.join(output_dir, rsm_json_file_name), driver='GeoJSON')
    #convert network files to json
    network_shape = gpd.read_file(os.path.join(scenario_dir, "report", "hwyload.shp"))
    network_shape_prj = network_shape.to_crs(epsg=4269)
    network_shape_prj.to_file(os.path.join(output_dir, "hywload.json"), driver='GeoJSON')


def generate_rsm_shapefile(mgra_shapefile_dir, cross_reference_mgra_name, rsm_scenario):
    
    scenario_dir = os.path.join("SimWrapper\\data\\external", rsm_scenario)
    output_dir = os.path.join("SimWrapper\\data\\processed", scenario)
    output_shapefile_name = "MGRA13_gcs" + "_" + rsm_scenario + ".shp"
    # create and save rsm new shapefile
    mgra_orig_shp = gpd.read_file(os.path.join(mgra_shapefile_dir, "MGRA13_gcs.shp"))
    cross_reference_mgra = pd.read_csv(os.path.join(scenario_dir, "input", cross_reference_mgra_name))
    mgra_orig_shp = mgra_orig_shp.merge(cross_reference_mgra, on="MGRA", how="left")
    mgra_rsm = gpd.GeoDataFrame(mgra_orig_shp)
    mgra_rsm = mgra_orig_shp.dissolve(by='cluster_id')
    mgra_rsm.to_file(os.path.join(output_dir, output_shapefile_name))


def combine_scenarios_summary(scenario_list, mode_summary_file_name, vmt_summary_file_name, intrazonal_vmt_file_name, out_dir):

    
    temp1 = pd.DataFrame()
    for scenario in scenario_list:
        scenario_dir = os.path.join("SimWrapper\\data\\processed", scenario)  
        summary_df = pd.read_csv(os.path.join(scenario_dir, mode_summary_file_name))
        temp1["tripMode"] = summary_df["tripMode"]
        temp1[scenario] = summary_df["share"]
    temp1.to_csv(os.path.join(out_dir, mode_summary_file_name), index=False)

    temp2 = pd.DataFrame()
    for scenario in scenario_list:
        scenario_dir = os.path.join("SimWrapper\\data\\processed", scenario)  
        summary_df = pd.read_csv(os.path.join(scenario_dir,vmt_summary_file_name))
        temp2["class"] = summary_df["class"]
        temp2[scenario] = summary_df["vmt_total"]
    temp2.to_csv(os.path.join(out_dir, vmt_summary_file_name), index=False)

    temp3 = pd.DataFrame()
    for scenario in scenario_list:
        scenario_dir = os.path.join("SimWrapper\\data\\processed", scenario)  
        summary_df = pd.read_csv(os.path.join(scenario_dir, intrazonal_vmt_file_name))
        temp3["type"] = summary_df["type"]
        temp3[scenario] = summary_df["vehicle_miles"]

    temp3.to_csv(os.path.join(out_dir, intrazonal_vmt_file_name), index=False)

def compare_network_summary (network_comparison_scenario_pair, network_summary_file_name, out_dir):

     
    scenario1_dir = os.path.join("SimWrapper\\data\\processed", network_comparison_scenario_pair[0])  
    scenario2_dir = os.path.join("SimWrapper\\data\\processed", network_comparison_scenario_pair[1])  
    network_summary1 = pd.read_csv(os.path.join(scenario1_dir,network_summary_file_name))
    network_summary2 = pd.read_csv(os.path.join(scenario2_dir,network_summary_file_name) )
    network_summary_dif = (network_summary1.set_index(['ID'])- network_summary2.set_index(['ID'])).reset_index()
    out_file_name = os.path.join(out_dir,  "netowrk_summary_" + network_comparison_scenario_pair[0] + "_" + network_comparison_scenario_pair[1] + "_difference.csv")
    network_summary_dif.to_csv(out_file_name, index=False)

def intrazonal_vmt_aggregation(vmt_summary_df_file_name, intrazonal_distance_mode_file_name, intrazonal_vmt_file_name, scenario):

    scenario_dir = os.path.join("SimWrapper\\data\\processed", scenario)
    vmt_summary_df = pd.read_csv(os.path.join(scenario_dir, vmt_summary_df_file_name))
    intrazonal_vmt_df = pd.read_csv(os.path.join(scenario_dir, intrazonal_distance_mode_file_name))
    intrazonal_vmt_df["vmt"] = intrazonal_vmt_df["distance"]
    intrazonal_vmt_df["vmt"][intrazonal_vmt_df['tripMode']=="Shared Ride 2"] = intrazonal_vmt_df["distance"] / 2
    intrazonal_vmt_df["vmt"][intrazonal_vmt_df['tripMode']=="Shared Ride 3+"] = intrazonal_vmt_df["distance"] / 3
    intrazonal_vmt = intrazonal_vmt_df["distance"].sum() 
    vmt = vmt_summary_df["vmt_total"].sum()
    vmt_total = intrazonal_vmt + vmt
    vmt_df = pd.DataFrame([vmt_total], index = ["total_vmt"]).reset_index().set_axis(['type', 'vehicle_miles'], axis=1, inplace=False) 
    out_file_name = os.path.join(scenario_dir, intrazonal_vmt_file_name)
    vmt_df.to_csv(out_file_name, index=False)

if __name__ == "__main__":
    args = sys.argv
    config_filename = args[1]
    # print(config_filename)

    if not os.path.exists(config_filename):
        msg = "Configuration file doesn't exist at: {}".format(config_filename)
        raise ValueError(msg)

    with open(config_filename, "r") as yml_file:
        config = yaml.safe_load(yml_file)

    print("Running Visulizer Support Script")

    # read config: 
    shapefile_dir = config['inputs']['shapefile_dir']
    cross_reference_mgra_file_name = config['inputs']['cross_reference_mgra_file_name']
    mode_summary_file_name = config['inputs']['mode_summary_file_name']
    vmt_summary_file_name = config['inputs']['vmt_summary_file_name']
    compared_scenarios_dir = config['inputs']['compared_scenarios_dir']
    intrazonal_distance_mode_file_name = config['inputs']['intrazonal_distance_mode_file_name']
    rsm_scenario_list = config['parameters']['rsm_scenario_list']
    base_scenario = config['parameters']['base_scenario']
    total_vmt_file_name = config['outputs']['total_vmt_file_name']

    for scenario in (rsm_scenario_list):
        generate_rsm_shapefile(shapefile_dir, cross_reference_mgra_file_name, scenario)

    shapefile_to_jason(shapefile_dir, base_scenario)      

    for scenario in (rsm_scenario_list):
        rsm_geo_post_processing(scenario)


    for scenario in (rsm_scenario_list + [base_scenario]):
        intrazonal_vmt_aggregation(vmt_summary_file_name, intrazonal_distance_mode_file_name, total_vmt_file_name, scenario)

    combine_scenarios_summary(rsm_scenario_list + [base_scenario], mode_summary_file_name, vmt_summary_file_name, total_vmt_file_name, compared_scenarios_dir)

#    for pair in list(itertools.combinations(scenario_list, 2)):
#        compare_network_summary (pair, network_summary_file_name, compared_scenarios_dir)