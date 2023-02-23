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
import os
import sys
import pandas as pd

class EmmebankAggregator(_m.Tool()):

    def __init__(self):
        self.emmebank = _m.Modeller().emmebank
    
    @_m.logbook_trace('Emmebank Aggregator')
    def __call__(self, main_dir, orig_model_dir, agg_zone_mapping_file):
        #self.emmebank = emmebank 
        
        orig_emmebank_path = os.path.join(orig_model_dir, "emme_project", "Database", "emmebank")
        orig_emmebank = _eb.Emmebank(orig_emmebank_path)
        
        agg_zone_mapping_path = os.path.join(main_dir, agg_zone_mapping_file)

        periods = ["EA", "AM", "MD", "PM", "EV"]
        trk_cores = ["TRK_L_VEH", "TRKLGP_VEH", "TRKLTOLL_VEH", "TRK_M_VEH", "TRKMGP_VEH", "TRKMTOLL_VEH", "TRK_H_VEH", "TRKHGP_VEH", "TRKHTOLL_VEH"]
        ee_cores = ["SOV_EETRIPS", "HOV2_EETRIPS", "HOV3_EETRIPS"]
        ei_cores = ["SOVGP_EIWORK", "SOVGP_EINONWORK", "SOVTOLL_EIWORK", "SOVTOLL_EINONWORK",
                    "HOV2HOV_EIWORK", "HOV2HOV_EINONWORK", "HOV2TOLL_EIWORK", "HOV2TOLL_EINONWORK",
                    "HOV3HOV_EIWORK", "HOV3HOV_EINONWORK", "HOV3TOLL_EIWORK", "HOV3TOLL_EINONWORK"]
        
        emmebank_cores_to_aggregate = []
        
        for period in periods: 
            for core in trk_cores: 
                emmebank_cores_to_aggregate.append("mf" + period + "_" + core)

            for core in ee_cores: 
                emmebank_cores_to_aggregate.append("mf" + period + "_" + core)

            for core in ei_cores: 
                emmebank_cores_to_aggregate.append("mf" + period + "_" + core)

        agg_zone_mapping_df = pd.read_csv(agg_zone_mapping_path)
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
        
        for core in emmebank_cores_to_aggregate: 
            matrix = orig_emmebank.matrix(core).get_data()
            matrix_array = matrix.to_numpy()
    
            matrix_agg = _aggregate_matrix(matrix_array, zone_mapping)
        
            matrix = self.emmebank.matrix(core)
            matrix.set_numpy_data(matrix_agg)
   
   
