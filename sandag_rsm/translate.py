import os
import logging
import pandas as pd
from pathlib import Path

from .data_load.skims import open_skims

logger = logging.getLogger(__name__)


def translate_demand(
        skims_file, matrix_name, agg_map, data_dir=None, export_dir=None
):
    matrix_load = load_matrix(skims_file, matrix_name, data_dir)
    matrix = aggregate_matrix(matrix_load, agg_map)
    export_matrix(matrix, matrix_name, export_dir)

    return matrix_load, matrix


def load_matrix(
        skims_file, matrix_name, data_dir
):
    logger.info('Loading Matrix: matrix_name')
    # if isinstance(skims_file, emme_path):
    #     matrix_load = load_matrix_emme(skims_file, emme_path=emme_path)
    if isinstance(skims_file, (str, Path)):
        matrix_load = open_skims(skims_file, data_dir=data_dir)

    return pd.DataFrame(matrix_load[matrix_name])

def aggregate_matrix(
        matrix, agg_map
):
    logger.info('\tAggregating Matrix')
    matrix = matrix.rename(columns=(agg_map))
    matrix = matrix.rename(index=(agg_map))

    return matrix.stack().groupby(level=[0,1]).sum().unstack()

def export_matrix(
        matrix, matrix_name, export_dir
):
    logger.info('\tExporting Matrix')
    matrix.to_csv(os.path.join(export_dir, f'{matrix_name}.csv'))
    # save_matrix_emme(emme_path, matrix_name)
