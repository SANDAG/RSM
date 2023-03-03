import logging
from pathlib import Path

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def rsm_household_sampler(
    input_dir=".",
    output_dir=".",
    prev_iter_access=None,
    curr_iter_access=None,
    study_area=None,
    input_household="households.csv",
    input_person="persons.csv",
    taz_crosswalk="taz_crosswalk.csv",
    mgra_crosswalk="mgra_crosswalk.csv",
    compare_access_columns=(
        "NONMAN_AUTO",
        "NONMAN_TRANSIT",
        "NONMAN_NONMOTOR",
        "NONMAN_SOV_0",
    ),
    default_sampling_rate=0.25,  # fix the values of this after some testing
    lower_bound_sampling_rate=0.15,  # fix the values of this after some testing
    upper_bound_sampling_rate=1.0,  # fix the values of this after some testing
    random_seed=42,
    output_household="sampled_households.csv",
    output_person="sampled_person.csv",
):
    """
    Take an intelligent sampling of households.

    Parameters
    ----------
    input_dir : Path-like, default "."
    output_dir : Path-like, default "."
    prev_iter_access : Path-like or pandas.DataFrame
        Accessibility in an old (default, no treatment, etc) run is given (preloaded)
        or read in from here. Give as a relative path (from `input_dir`) or an
        absolute path.
    curr_iter_access : Path-like or pandas.DataFrame
        Accessibility in the latest run is given (preloaded) or read in from here.
        Give as a relative path (from `input_dir`) or an absolute path.
    study_area : array-like
        Array of RSM zone id's in the study area.  These zones are sampled at 100%.
    input_household : Path-like or pandas.DataFrame
        Complete synthetic household file.  This data will be filtered to match the
        sampling of households and written out to a new CSV file.
    input_person : Path-like or pandas.DataFrame
        Complete synthetic persons file.  This data will be filtered to match the
        sampling of households and written out to a new CSV file.
    compare_access_columns : Collection[str]
        Column names in the accessibility file to use for comparing accessibility.
        Only changes in the values in these columns will be evaluated.
    default_sampling_rate : float
        The default sampling rate, in the range (0,1]
    lower_bound_sampling_rate : float
        Sampling rates by zone will be truncated so they are never lower than this.
    upper_bound_sampling_rate : float
        Sampling rates by zone will be truncated so they are never higher than this.

    Returns
    -------
    sample_households_df, sample_persons_df : pandas.DataFrame
        These are the sampled population to resimulate.  They are also written to
        the output_dir
    """

    input_dir = Path(input_dir or ".")
    output_dir = Path(output_dir or ".")

    logger.debug("CALL rsm_household_sampler")
    logger.debug(f"  {input_dir=}")
    logger.debug(f"  {output_dir=}")

    def _resolve_df(x, directory, make_index=None):
        if isinstance(x, (str, Path)):
            # read in the file to a pandas DataFrame
            x = Path(x).expanduser()
            if not x.is_absolute():
                x = Path(directory or ".").expanduser().joinpath(x)
            try:
                result = pd.read_csv(x)
            except FileNotFoundError:
                raise
        elif isinstance(x, pd.DataFrame):
            result = x
        elif x is None:
            result = None
        else:
            raise TypeError("must be path-like or DataFrame")
        if (
            result is not None
            and make_index is not None
            and make_index in result.columns
        ):
            result = result.set_index(make_index)
        return result

    def _resolve_out_filename(x):
        x = Path(x).expanduser()
        if not x.is_absolute():
            x = Path(output_dir).expanduser().joinpath(x)
        x.parent.mkdir(parents=True, exist_ok=True)
        return x

    prev_iter_access_df = _resolve_df(
        prev_iter_access, input_dir, make_index="MGRA"
    )
    curr_iter_access_df = _resolve_df(
        curr_iter_access, input_dir, make_index="MGRA"
    )
    rsm_zones = _resolve_df(taz_crosswalk, input_dir)
    dict_clusters = dict(zip(rsm_zones["taz"], rsm_zones["cluster_id"]))

    rsm_mgra_zones = _resolve_df(mgra_crosswalk, input_dir)
    rsm_mgra_zones.columns = rsm_mgra_zones.columns.str.strip().str.lower()
    dict_clusters_mgra = dict(zip(rsm_mgra_zones["mgra"], rsm_mgra_zones["cluster_id"]))

    # changing the taz and mgra to new cluster ids
    input_household_df = _resolve_df(input_household, input_dir)
    input_household_df["taz"] = input_household_df["taz"].map(dict_clusters)
    input_household_df["mgra"] = input_household_df["mgra"].map(dict_clusters_mgra)
    input_household_df["count"] = 1

    taz_hh = input_household_df.groupby(["taz"]).size().rename("n_hh").to_frame()

    if curr_iter_access_df is None or prev_iter_access_df is None:

        if curr_iter_access_df is None:
            logger.warning(f"missing curr_iter_access_df from {curr_iter_access}")
        if prev_iter_access_df is None:
            logger.warning(f"missing prev_iter_access_df from {prev_iter_access}")
        # true when sampler is turned off. default_sampling_rate should be set to 1

        taz_hh["sampling_rate"] = default_sampling_rate
        if study_area is not None:
            taz_hh.loc[taz_hh.index.isin(study_area), "sample_rate"] = 1

        sample_households = []

        for taz_id, row in taz_hh.iterrows():
            df = input_household_df.loc[input_household_df["taz"] == taz_id]
            sampling_rate = row["sampling_rate"]
            logger.info(f"{taz_id=} {sampling_rate=}")
            df = df.sample(frac=sampling_rate, random_state=taz_id + random_seed)
            sample_households.append(df)

        # combine study are and non-study area households into single dataframe
        sample_households_df = pd.concat(sample_households)

    else:
        # restrict to rows only where TAZs have households
        prev_iter_access_df = prev_iter_access_df[
            prev_iter_access_df.index.isin(taz_hh.index)
        ].copy()
        curr_iter_access_df = curr_iter_access_df[
            curr_iter_access_df.index.isin(taz_hh.index)
        ].copy()

        # compare accessibility columns
        compare_results = pd.DataFrame()

        for column in compare_access_columns:
            compare_results[column] = (
                curr_iter_access_df[column] - prev_iter_access_df[column]
            ).abs()  # take absolute difference
        compare_results["MGRA"] = prev_iter_access_df.index

        compare_results = compare_results.set_index("MGRA")

        # Take row sums of all difference
        compare_results["Total"] = compare_results[list(compare_access_columns)].sum(
            axis=1
        )

        # TODO: potentially adjust this later after we figure out a better approach
        wgts = compare_results["Total"] + 0.01
        wgts /= wgts.mean() / default_sampling_rate
        compare_results["sampling_rate"] = np.clip(
            wgts, lower_bound_sampling_rate, upper_bound_sampling_rate
        )

        sample_households = []
        sample_rate_df = compare_results[["sampling_rate"]].copy()
        if study_area is not None:
            sample_rate_df.loc[
                sample_rate_df.index.isin(study_area), "sampling_rate"
            ] = 1

        for taz_id, row in sample_rate_df.iterrows():
            df = input_household_df.loc[input_household_df["taz"] == taz_id]
            sampling_rate = row["sampling_rate"]
            logger.info(f"Sampling rate of {taz_id}: {sampling_rate}")
            df = df.sample(frac=sampling_rate, random_state=taz_id + random_seed)
            sample_households.append(df)

        # combine study are and non-study area households into single dataframe
        sample_households_df = pd.concat(sample_households)

    sample_households_df = sample_households_df.sort_values(by=["hhid"])
    sample_households_df.to_csv(_resolve_out_filename(output_household), index=False)

    # select persons belonging to sampled households
    sample_hhids = sample_households_df["hhid"].to_numpy()

    persons_df = _resolve_df(input_person, input_dir)
    sample_persons_df = persons_df.loc[persons_df["hhid"].isin(sample_hhids)]
    sample_persons_df.to_csv(_resolve_out_filename(output_person), index=False)

    global_sample_rate = round(len(sample_households_df) / len(input_household_df),2)
    logger.info(f"Total Sampling Rate : {global_sample_rate}")

    return sample_households_df, sample_persons_df
