import os
#import logging
import pandas as pd
from pathlib import Path
import openmatrix as omx
import shutil

#logger = logging.getLogger(__name__)

 
def _aggregate_matrix(input_mtx, aggregate_mapping_dict):
    matrix_array = input_mtx.read()
    matrix_df = pd.DataFrame(matrix_array, columns = list(aggregate_mapping_dict.keys()))
    
    matrix_agg_df = matrix_df.rename(columns=(aggregate_mapping_dict))
    matrix_agg_df.index = list(aggregate_mapping_dict.values())
    
    matrix_agg_df = matrix_agg_df.stack().groupby(level=[0,1]).sum().unstack()
    matrix_agg_df = matrix_agg_df[sorted(matrix_agg_df.columns)]
    matrix_agg_df = matrix_agg_df.sort_index()
    
    output_mtx = matrix_agg_df.to_numpy()
    
    return output_mtx


def translate_demand(
    matrix_names,
    agg_zone_mapping,
    input_dir=".",
    output_dir="."
): 
    """
    aggregates the omx demand matrix to aggregated zone system
    
    Parameters
    ----------
    matrix_names : list
        omx matrix filenames to aggregate
    agg_zone_mapping: Path-like or pandas.DataFrame
        zone number mapping between original and aggregated zones. 
        columns: original zones as 'taz' and aggregated zones as 'cluster_id'
    input_dir : Path-like, default "."
    output_dir : Path-like, default "."
    
    Returns
    -------
    
    """
    
    #input_dir = Path(input_dir or ".")
    #output_dir = Path(output_dir or ".")

    #print(input_dir)
    #print(output_dir)

    #agg_zone_mapping_df = _resolve_df(agg_zone_mapping)
    agg_zone_mapping_df = pd.read_csv(os.path.join(agg_zone_mapping))
    agg_zone_mapping_df = agg_zone_mapping_df.sort_values('taz')

    agg_zone_mapping_df.columns= agg_zone_mapping_df.columns.str.strip().str.lower()
    zone_mapping = dict(zip(agg_zone_mapping_df['taz'], agg_zone_mapping_df['cluster_id']))
    agg_zones = sorted(agg_zone_mapping_df['cluster_id'].unique())

    for mat_name in matrix_names:
        if '.omx' not in mat_name:
            mat_name = mat_name + ".omx"
        
        #logger.info("Aggregating Matrix: " + mat_name + " ...")

        input_skim_file = os.path.join(input_dir, mat_name) #Path(input_dir).expanduser().joinpath(mat_name)
        print(input_skim_file)
        output_skim_file = os.path.join(output_dir, mat_name) #Path(output_dir).expanduser().joinpath(mat_name)

        assert os.path.isfile(input_skim_file)

        input_matrix = omx.open_file(input_skim_file, mode="r") 
        input_mapping_name = input_matrix.list_mappings()[0]
        input_cores = input_matrix.list_matrices()

        output_matrix = omx.open_file(output_skim_file, mode="w")
    
        for core in input_cores:
            matrix = input_matrix[core]
            matrix_agg = _aggregate_matrix(matrix, zone_mapping)
            output_matrix[core] = matrix_agg

        output_matrix.create_mapping(title=input_mapping_name, entries=agg_zones)

        input_matrix.close()
        output_matrix.close()


def copy_transit_demand(
    matrix_names,
    input_dir=".",
    output_dir="."
):
    """
    copies the omx transit demand matrix to rsm directory
    
    Parameters
    ----------
    matrix_names : list
        omx matrix filenames to aggregate
    input_dir : Path-like, default "."
    output_dir : Path-like, default "."
    
    Returns
    -------
    
    """


    for mat_name in matrix_names:
        if '.omx' not in mat_name:
            mat_name = mat_name + ".omx"

        input_file_dir = os.path.join(input_dir, mat_name)
        output_file_dir = os.path.join(output_dir, mat_name)

        shutil.copy(input_file_dir, output_file_dir)

    
