""" Data Pipeline Tool

The Data Pipeline Tool works as follows:
    - Load data
    - Transform data
    - Summarize data
    - Write out summaries to output directory

Each of these steps are configurable through the 'settings.yaml'
file in the 'config' directory of this tool.

@author: Enrique Sanchez
"""


# Import libraries
#import openmatrix as omx
import pandas as pd
import numpy as np
import logging
import glob
import os
import pdb

from collections import defaultdict
from inspect import getmembers, isfunction

import config.user_added_functions as user_added_functions

# TODO: Handle warnings
#       1. Warning - RuntimeWarning: The values in the array are unorderable.
#          Reason: Concatenating two series with null index
import warnings
warnings.simplefilter(action='ignore')


def search_files(root_path, patterns):
    """
    Helper function for extract_data

    Searches files satisfying a pattern (regex) in a specified root directory

    :param root_path: Root directory to search in
    :param patterns: List of patterns to search for
    :returns: Dictionary where keys are patterns and values are a list
              of file names satisfying the pattern
    """

    # Dictionary to store pattern and file name pairs
    file_dict = {}

    for pattern in patterns:
        search_results = glob.glob(os.path.join(root_path, pattern))
        file_dict[pattern.split('.')[0]] = [
            os.path.basename(path) for path in search_results]
        assert search_results, "No file identified by '{}'".format(pattern)

    return file_dict

def load_user_defined_functions(data_dict):
    """
    Adds user-defined functions to memory

    :data_dict: Dictionary containing pipeline data
    """
    #Read functions from user-added function script
    user_fn = dict(getmembers(user_added_functions, isfunction))

    #Vectorize functions
    for fn in user_fn:
        user_fn[fn] = np.vectorize(user_fn[fn])

    #Add functions to `data_dict`
    data_dict.update(user_fn)


def extract_data(data_settings):
    """
    Extracts and loads data for pipeline into memory

    :data_settings: Dictionary containing user-specified needed data
    :returns: Dictionary containing extracted data where keys are file names
              and the values are the associated data
    """

    data_dict = {}
    for source in data_settings:

        # Get file names for needed data
        file_dict = search_files(source['filepath'], source['data'])

        # TODO: Add support for data caching (hdf5)
        for name_id, file_names in file_dict.items():

            # The list file_names will consist of more than one element if the
            # name_id was a wildcard that matched more than one file name.
            # This name_id and file names mapping will be stored for downstream
            # processes (e.g. concatenation).
            if len(file_names) > 1:
                if 'wildcards' not in data_dict.keys():
                    data_dict['wildcards'] = {}
                data_dict['wildcards'][name_id] = file_names

            # Load data
            for file_name in file_names:
                file_id, extension = os.path.splitext(file_name)
                logging.info('Loading {}'.format(file_id))

                file_path = os.path.join(source['filepath'], file_name)
                if extension == '.csv':
                    data = pd.read_csv(file_path, nrows=source['test_size'])
                elif extension == '.omx':
                    data = omx.open_file(file_path, mode='r')
                else:
                    ftype_log = 'File type {} not supported'.format(extension)
                    logging.error(ftype_log)
                    raise NotImplementedError(ftype_log)

                data_dict[file_id] = data

    # Load user-added functions
    load_user_defined_functions(data_dict)

    return data_dict


def process(processor, data_dict):
    """
    Processes data frames through the following supported function:
        - Variable creation
        - Variable renaming
        - Value replacement
        - Value binning
        - Value capping
        - Function application on values
        - Column summation
        - Skim querying
        - Raw evaluation

    :processor: Processor DataFrame
    :data_dict: Dictionary containing data
    :returns: Updated data_dict with updated data
    """

    for _, row in processor.iterrows():

        # Create variable
        if row['Type'] == 'column':
            col_log = "Adding column '{}' to {}"
            logging.info(col_log.format(row['Out Col'], row['Table']))

            if row['Func'].replace(' ', '').isalpha():
                result = row['Func']
            else:
                result = data_dict[row['Table']].eval(row['Func'])

            data_dict[row['Table']][row['Out Col']] = result

        # Rename variable
        elif row['Type'] == 'rename':
            rename_log = "Renaming {} columns using {}"
            logging.info(rename_log.format(row['Table'], row['Func']))

            data_dict[row['Table']] = eval(
                '{}.rename({}, axis=1)'.format(
                    row['Table'],
                    row['Func']
                ), data_dict
            )

        # Replace values
        elif row['Type'] == 'replace':
            replace_log = "Replacing {} values in {} using {}"
            logging.info(
                replace_log.format(row['In Col'], row['Table'], row['Func'])
            )

            data_dict[row['Table']][row['Out Col']] = eval(
                "{}['{}'].replace({})".format(
                    row['Table'],
                    row['In Col'],
                    row['Func']
                ), data_dict
            )

        # Bin column values
        elif row['Type'] == 'bin':
            bin_log = "Binning {} values in {} using {}"
            logging.info(
                bin_log.format(row['In Col'], row['Table'], row['Func'])
            )
            data_dict[row['Table']][row['Out Col']] = eval(
                "pd.cut({}['{}'], {}, include_lowest=True)".format(
                    row['Table'],
                    row['In Col'],
                    row['Func']
                ), globals(), data_dict
            ).astype(str)

        # Cap values
        elif row['Type'] == 'cap':
            cap_log = "Capping {} values in {} at {}"
            logging.info(
                cap_log.format(row['In Col'], row['Table'], row['Func'])
            )
            data_dict[row['Table']][row['Out Col']] = eval(
                "np.minimum({}['{}'], {})".format(
                    row['Table'],
                    row['In Col'],
                    row['Func']
                ), globals(), data_dict
            )

        # Apply function to column
        elif row['Type'] == 'apply':
            apply_log = "Applying {} to {} values in {}"
            logging.info(
                apply_log.format(row['Func'], row['In Col'], row['Table'])
            )
            data_dict[row['Table']][row['Out Col']] = eval(
                "{}['{}'].apply({})".format(
                    row['Table'],
                    row['In Col'],
                    row['Func']
                ), globals(), data_dict
            )

        # Add columns together
        elif row['Type'] == 'sum':
            sum_log = "Setting {} values in {} to sum of {} values"
            logging.info(
                sum_log.format(row['Out Col'], row['Table'], row['In Col'])
            )
            cols = str(row['In Col'].split(','))
            data_dict[row['Table']][row['Out Col']] = eval(
                "{}[{}].sum(1)".format(
                    row['Table'],
                    cols
                ), globals(), data_dict
            )

        # Query skim O-D pairs
        elif row['Type'] == 'skim':
            skim_log = "Querying skim values from {} for columns {} in {}"
            logging.info(
                skim_log.format(row['Func'], row['In Col'], row['Table'])
            )

            # Get skim mapping
            skim_name = row['Func'].split('[')[0]
            map_name = data_dict[skim_name].list_mappings()[0]
            mapping = data_dict[skim_name].mapping(map_name)
            mapping[np.nan] = -1

            # Convert skim matrix to array
            # NOTE: Additional row/column consisting of -1 added for missing
            #       skim indices
            raw_matrix = eval(
                "np.array({})".format(row['Func']), globals(), data_dict)
            matrix = -np.ones((raw_matrix.shape[0]+1, raw_matrix.shape[1]+1))
            matrix[:raw_matrix.shape[0], :raw_matrix.shape[1]] = raw_matrix

            cols = row['In Col'].split(',')
            skim_query = (
                "matrix[{}['{}'].map(mapping).fillna(-1).astype(int)," +
                "{}['{}'].map(mapping).fillna(-1).astype(int)]"
            )
            data_dict[row['Table']][row['Out Col']] = eval(
                skim_query.format(
                    row['Table'],
                    cols[0],
                    row['Table'],
                    cols[1]
                ), locals(), data_dict
            )

        # Raw evaluation
        elif row['Type'] == 'raw':
            raw_log = "Raw evaluating {}"
            logging.info(raw_log.format(row['Func']))
            exec(row['Func'], globals(), data_dict)

        # Open Python Debugger
        elif row['Type'] == 'debug':
            pdb.set_trace()

    return data_dict


def merge(merge_blocks, data_dict):
    """
    Helper function for 'transform'

    Merges data frames together

    :param merge_blocks: List containing dictionaries (blocks) that describe
                         how to merge data frames. Specified using the
                         key-value pairs table_name:(str), include:(list),
                         merge_cols:(list) and merge_type:(str)
    :param data_dict: Dictionary containing data to merge
    :returns: Updated data_dict with merged data
    """

    for block in merge_blocks:

        # Read merge information and initialize with first table
        tables = block['include']
        merge_cols = block['merge_cols']
        merged_data = data_dict.get(tables[0])
        merge_type = block['merge_type']

        merge_log = 'Merging tables {} into {}'
        logging.info(merge_log.format(', '.join(tables), block['table_name']))

        # Merge data
        for table_idx in range(len(tables)-1):
            merged_data = merged_data.merge(
                data_dict.get(tables[table_idx+1]),
                left_on=merge_cols[table_idx],
                right_on=merge_cols[table_idx+1],
                how=merge_type
            )
        data_dict[block['table_name']] = merged_data

    return data_dict


def concat(concat_blocks, data_dict):
    """
    Helper function for transform

    Concatenates data frames together

    :param concat_blocks: List containing dictionaries (blocks) that describe
                          how to concatenate data frames. Specified using the
                          key-value pairs table_name:(str) and include:(list)
    :param data_dict: Dictionary containing data to concatenate
    :returns: Updated data_dict with concatenated data
    """

    for block in concat_blocks:
        # Check if any of the tables are wildcards
        if 'wildcards' in data_dict.keys():
            wildcard_dict = data_dict['wildcards']
            wildcards = (
                set(block['include']).intersection(wildcard_dict.keys()))
            table_names = sum(
                [wildcard_dict[table] if table in wildcards else [table]
                 for table in block['include']], []
            )
        else:
            table_names = block['include']

        concat_log = 'Concatenating tables {} into {}'
        logging.info(concat_log.format(table_names, block['table_name']))

        # Concatenate and store result
        # NOTE: Before concatenation, a column 'table' will be added to each
        #       table where values are the name of the table
        table_data = []
        for table in table_names:
            table_name = table.split('.')[0]
            data_dict[table_name]['table'] = table_name
            table_data.append(data_dict.get(table_name))
        data_dict[block['table_name']] = pd.concat(table_data, axis=0)

    return data_dict


def transform(processor, expressions, steps, data_dict):
    """
    Transforms data according to user specified steps

    :param processor: Processor data frame
    :param expressions: Expressions data frame
    :param steps: Dictionary consisting of transformation steps
    :param data_dict: Dictionary containing data to transform
    :returns: Updated data dictionary
    """

    # Iterate through transformation steps
    for step in steps:
        step_name = step['name']
        for type, blocks in list(step.items())[1:]:
            if type == 'concat':
                data_dict = concat(blocks, data_dict)
            elif type == 'merge':
                data_dict = merge(blocks, data_dict)
            elif type == 'process':
                step_processor = processor[processor['Step'] == step_name]
                data_dict = process(step_processor, data_dict)
            elif type == 'summarize':
                data_dict = eval_expressions(expressions, data_dict)

    return data_dict


def eval_expressions(expressions, data_dict):
    """
    Evaluates user-specifed expressions for summarization

    :param expressions: Expressions DataFrame
    :param data_dict: Dictionary containing data to summarize
    :returns: Dictionary containing expression results where keys are output
              table names and values are the results of the expressions
    """

    # Dictionary to store expression results
    expression_dict = defaultdict(dict)

    for _, row in expressions.iterrows():

        # Calculate a measure to be used in expressions
        if pd.isnull(row['In Col']):
            measure_log = "Running measure '{}' on {}"
            logging.info(measure_log.format(row['Func'], row['Out Table']))
            result = eval(row['Func'], data_dict)

        # Build and evaluate user-specified expression
        else:
            expression = '{}'.format(row['In Table'])
            if not pd.isnull(row['Filter']):
                query_str = (
                    '.query("{}", engine="python")'.format(row['Filter'])
                )
                expression += query_str
            if not pd.isnull(row['Group']):
                group_list = row['Group'].split(',')
                group_str = ".groupby({}, dropna=False)".format(group_list)
                expression += group_str
            expression += "['{}'].{}()".format(row['In Col'], row['Func'])

            logging.info('Evaluating {}'.format(expression))
            result = eval(expression, data_dict)

        if not np.isscalar(result):
            result.name = row['Out Col']

        # Add expression result to dictionary
        # TODO: Result being stored twice, store only in data_dict
        expression_dict[row['Out Table']][row['Out Col']] = result
        data_dict[row['Out Col']] = result

    # Convert expression dict to a dict of data frames
    expression_results = coalesce_expressions(expression_dict)

    # Load user-defined functions
    load_user_defined_functions(expression_results)

    return expression_results


def coalesce_expressions(expression_dict):
    """"
    Coalesces summary expresion results into Pandas dataframes

    :param expression_dict: Dictionary containing results from user-specified
                            expressions
    :returns: Summary dataframes dictionary
    """

    expression_dfs = {}
    for table_name in expression_dict.keys():
        coalesce_log = "Coalescing summary table {}"
        logging.info(coalesce_log.format(table_name))

        # Read table results
        table_dict = expression_dict[table_name]

        # Remove temporary results
        out_cols = list(table_dict.keys())
        for col in out_cols:
            if col.startswith('_'):
                table_dict.pop(col)

        # Convert result to data frame
        if np.all([np.isscalar(val) for val in table_dict.values()]):
            for key, value in table_dict.items():
                table_dict[key] = [value]
            df = pd.DataFrame(table_dict)
        else:
            df = pd.concat(list(table_dict.values()), axis=1)
            df = df.reset_index(drop=False)

        # Store coalesced expressions
        expression_dfs[table_name] = df

    return expression_dfs


def write_results(results_dict, empty_fill, outdir):
    """"
    Writes out resulting summaries

    :param results_dict: Dictionary containing results from user-specified
                         expressions
    :param empty_fill: Value to fill null values with
    :param outdir: Output directory to write out expression results
    """

    for table_name in results_dict.keys():
        if table_name.startswith('_') or type(results_dict[table_name]) != pd.DataFrame:
            continue
        logging.info('Writing {}.csv'.format(table_name))

        # Read summary table results
        summary_df = results_dict[table_name]

        # Fill null values with user specified value
        if not pd.isnull(empty_fill):
            summary_df.fillna(empty_fill)

        # Write out results
        fname = '{}.csv'.format(table_name)
        summary_df.to_csv(os.path.join(outdir, fname), index=False)

    return
