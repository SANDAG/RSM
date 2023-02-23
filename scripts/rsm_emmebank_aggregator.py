#
# Aggregates demand matrices from emme databank to RSM zone structure
# This python file is being called in bin\runRSMEmmebankMatrixAggregator.cmd
#
# Inputs:
#   rsm_main_dir: RSM main directory
#   orig_model_dir: Donor model main directory
#   agg_zone_mapping: TAZ to RSM zone crosswalk
#
# Outputs:
#   Aggregated matrices based on new zone structure loaded into RSM databank
#

import inro.emme.database.emmebank as _eb
import inro.modeller as _m
#import inro.emme.desktop.app as _app
import os
import sys
import pandas as pd

dem_utils = _m.Modeller().module('sandag.utilities.demand')

import dem_utils.load_matrix_to_databank

scenario = sys.argv[1]
rsm_main_dir = os.path.join(sys.argv[2])
orig_model_dir = os.path.join(sys.argv[3])
agg_zone_mapping = os.path.join(rsm_main_dir, sys.argv[4])

orig_emmebank_path = os.path.join(orig_model_dir, "emme_project", "Database", "emmebank")
orig_emmebank = _eb.Emmebank(orig_emmebank_path)

#1. Lock file 'emlocki' exists
#rsm_emmebank_path = os.path.join(rsm_main_dir, "emme_project", "Database", "emmebank")
#rsm_emmebank = _eb.Emmebank(rsm_emmebank_path)

#2. Lock file 'emlocki' exists
#rsm_emmebank = _eb.Emmebank(rsm_emmebank)

#3. AssertionError
#rsm_emmebank = _m.Modeller().emmebank

#4. AssertionError
#print(_m.Modeller().scenario)
#my_scenario = _m.Modeller().scenario
#rsm_emmebank = scenario.emmebank

#5. AssertionError
#desktop = _m.Modeller().desktop
#desktop.refresh_data()
#data_explorer = desktop.data_explorer()
#rsm_emmebank = data_explorer.active_database().core_emmebank


###########

periods = ["EA", "AM", "MD", "PM", "EV"]

emmebank_cores = ["mfAM_TRK_L_VEH", "mfAM_TRK_M_VEH"]

#for period in periods:
#    emmebank_cores.append('trip' + period)

agg_zone_mapping_df = pd.read_csv(agg_zone_mapping)
agg_zone_mapping_df = agg_zone_mapping_df.sort_values('taz')
agg_zone_mapping_df.columns= agg_zone_mapping_df.columns.str.strip().str.lower()
zone_mapping = dict(zip(agg_zone_mapping_df['taz'], agg_zone_mapping_df['cluster_id']))

def _aggregate_matrix(input_mtx_array, aggregate_mapping_dict):
    matrix_df = pd.DataFrame(input_mtx_array, columns = list(aggregate_mapping_dict.keys()))
    
    matrix_agg_df = matrix_df.rename(columns=(aggregate_mapping_dict))
    matrix_agg_df.index = list(aggregate_mapping_dict.values())
    
    matrix_agg_df = matrix_agg_df.stack().groupby(level=[0,1]).sum().unstack()
    matrix_agg_df = matrix_agg_df[sorted(matrix_agg_df.columns)]
    matrix_agg_df = matrix_agg_df.sort_index()
    
    output_mtx = matrix_agg_df.to_numpy()
    
    return output_mtx

    
for core in emmebank_cores: 
    matrix = orig_emmebank.matrix(core).get_data()
    matrix_array = matrix.to_numpy()
    
    matrix_agg = _aggregate_matrix(matrix_array, zone_mapping)
        
    #matrix = rsm_emmebank.matrix(core)
    #matrix.set_numpy_data(matrix_agg)
    dem_utils.load_matrix_to_databank(matrix_agg, core)