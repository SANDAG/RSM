import os
#import logging
import pandas as pd
import openmatrix as omx
import shutil

#logger = logging.getLogger(__name__)

 
def _aggregate_matrix(input_mtx_array, aggregate_mapping_dict):
    matrix_df = pd.DataFrame(input_mtx_array, columns = list(aggregate_mapping_dict.keys()))
    
    matrix_agg_df = matrix_df.rename(columns=(aggregate_mapping_dict))
    matrix_agg_df.index = list(aggregate_mapping_dict.values())
    
    matrix_agg_df = matrix_agg_df.stack().groupby(level=[0,1]).sum().unstack()
    matrix_agg_df = matrix_agg_df[sorted(matrix_agg_df.columns)]
    matrix_agg_df = matrix_agg_df.sort_index()
    
    output_mtx = matrix_agg_df.to_numpy()
    
    return output_mtx


def translate_omx_demand(
    matrix_names,
    agg_zone_mapping,
    input_dir=".",
    output_dir="."
): 
    """
    aggregates the omx demand matrix to aggregated zone system
    
    Parameters
    ----------
    matrix_names : matrix_names (list)
        omx matrix filenames to aggregate
    agg_zone_mapping: agg_zone_mapping (path_like or pandas.DataFrame)
        zone number mapping between original and aggregated zones. 
        columns: original zones as 'taz' and aggregated zones as 'cluster_id'
    input_dir : input_dir (path_like)
        default "."
    output_dir : output_dir (path_like) 
        default "."
    
    Returns
    -------
    
    """
    
    agg_zone_mapping_df = pd.read_csv(os.path.join(agg_zone_mapping))
    agg_zone_mapping_df = agg_zone_mapping_df.sort_values('taz')

    agg_zone_mapping_df.columns= agg_zone_mapping_df.columns.str.strip().str.lower()
    zone_mapping = dict(zip(agg_zone_mapping_df['taz'], agg_zone_mapping_df['cluster_id']))
    agg_zones = sorted(agg_zone_mapping_df['cluster_id'].unique())

    for mat_name in matrix_names:
        if '.omx' not in mat_name:
            mat_name = mat_name + ".omx"
        
        #logger.info("Aggregating Matrix: " + mat_name + " ...")

        input_skim_file = os.path.join(input_dir, mat_name)
        print(input_skim_file)
        output_skim_file = os.path.join(output_dir, mat_name)

        assert os.path.isfile(input_skim_file)

        input_matrix = omx.open_file(input_skim_file, mode="r") 
        input_mapping_name = input_matrix.list_mappings()[0]
        input_cores = input_matrix.list_matrices()

        output_matrix = omx.open_file(output_skim_file, mode="w")
    
        for core in input_cores:
            matrix = input_matrix[core]
            matrix_array = matrix.read()
            matrix_agg = _aggregate_matrix(matrix_array, zone_mapping)
            output_matrix[core] = matrix_agg

        output_matrix.create_mapping(title=input_mapping_name, entries=agg_zones)

        input_matrix.close()
        output_matrix.close()


def translate_emmebank_demand(
    input_databank,
    output_databank,
    cores_to_aggregate,
    agg_zone_mapping,
): 
    """
    aggregates the demand matrix cores from one emme databank and loads them into another databank
    
    Parameters
    ----------
    input_databank : input_databank (Emme databank)
        Emme databank
    output_databank : output_databank (Emme databank)
        Emme databank
    cores_to_aggregate : cores_to_aggregate (list)
        matrix corenames to aggregate
    agg_zone_mapping: agg_zone_mapping (Path-like or pandas.DataFrame)
        zone number mapping between original and aggregated zones. 
        columns: original zones as 'taz' and aggregated zones as 'cluster_id'
    
    Returns
    -------
    None. Loads the trip matrices into emmebank.
    
    """
    
    agg_zone_mapping_df = pd.read_csv(os.path.join(agg_zone_mapping))
    agg_zone_mapping_df = agg_zone_mapping_df.sort_values('taz')
    
    agg_zone_mapping_df.columns= agg_zone_mapping_df.columns.str.strip().str.lower()
    zone_mapping = dict(zip(agg_zone_mapping_df['taz'], agg_zone_mapping_df['cluster_id']))
        
    for core in cores_to_aggregate: 
        matrix = input_databank.matrix(core).get_data()
        matrix_array = matrix.to_numpy()
        
        matrix_agg = _aggregate_matrix(matrix_array, zone_mapping)
        
        output_matrix = output_databank.matrix(core)
        output_matrix.set_numpy_data(matrix_agg)
        
    
def copy_transit_demand(
    matrix_names,
    input_dir=".",
    output_dir="."
):
    """
    copies the omx transit demand matrix to rsm directory
    
    Parameters
    ----------
    matrix_names : matrix_names (list)
        omx matrix filenames to aggregate
    input_dir : input_dir (Path-like) 
        default "."
    output_dir : output_dir (Path-like)
        default "."
    
    Returns
    -------
    
    """


    for mat_name in matrix_names:
        if '.omx' not in mat_name:
            mat_name = mat_name + ".omx"

        input_file_dir = os.path.join(input_dir, mat_name)
        output_file_dir = os.path.join(output_dir, mat_name)

        shutil.copy(input_file_dir, output_file_dir)

    
