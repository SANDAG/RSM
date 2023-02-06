# Import libraries
import pandas as pd
import logging
import os
import yaml

import src.pipeline as pipeline

# Settings file path
SETTINGS = 'config/settings.yaml'


def load_yaml(fp):
    """
    Loads and converts a YAML file to a Python dictionary

    :param fp: File path to YAML file
    :returns: Python dictionary
    """
    try:
        with open(fp) as fh:
            param = yaml.safe_load(fh)
    except Exception:
        msg = 'settings.yml file not properly formatted.'
        raise Exception(msg)

    return param


def start_logger(outdir):
    """
    Initializes a logger for terminal and file logging

    :param outdir: Output directory to write log file to
    """

    # Customize log format
    log_format = '%(asctime)s - %(levelname)s (%(funcName)s): %(message)s'

    # Define handlers to allow writing logs to file
    log_fp = os.path.join(outdir, 'pipeline.log')
    log_handlers = [logging.FileHandler(log_fp, 'w'), logging.StreamHandler()]

    # Initialize logger
    logging.basicConfig(
        format=log_format,
        level=logging.DEBUG,
        handlers=log_handlers
    )

    return


def output_dir(dir, name):
    """
    Creates an output directory

    :param dir: File path to create directory in
    :param name: Name to give to output directory
    :returns: File path of output directory
    """

    # Output directory file path
    directory_fp = os.path.join(dir, name)

    # Create directory
    if not os.path.exists(directory_fp):
        os.mkdir(directory_fp)

    return directory_fp


def main():
    """
    Runs the Data Pipeline tool
    """

    # Load settings
    settings = load_yaml(SETTINGS)
    data = settings['extract']
    transform = settings['transform']
    processor_fp = transform['processor']
    summarizer_fp = transform['summarizer']
    steps = transform['steps']
    load = settings['load']

    # Initialize logger
    start_logger(load['outdir'])

    # Extract and load data
    data_dict = pipeline.extract_data(data)

    # Transform data
    processor = pd.read_csv(processor_fp, comment='#')
    expressions = pd.read_csv(summarizer_fp, comment='#')
    results = pipeline.transform(processor, expressions, steps, data_dict)

    # Write results
    pipeline.write_results(results, load['empty_fill'], load['outdir'])

    return


if __name__ == '__main__':
    main()
