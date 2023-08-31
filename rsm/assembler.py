import logging
import os
from pathlib import Path
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


# function to convert to final trip roster
def _merge_joint_and_indiv_trips(indiv_trips, joint_trips):
    joint_trips = joint_trips[["hh_id", "tour_id", "num_participants", "trip_mode"]]
    joint_trips = joint_trips.reindex(
        joint_trips.index.repeat(joint_trips.num_participants)
    ).reset_index(drop=True)
    joint_trips = joint_trips.drop(columns=["num_participants"])

    indiv_trips = indiv_trips[["hh_id", "tour_id", "trip_mode"]]
    trips = pd.concat([joint_trips, indiv_trips], ignore_index=True).reset_index(
        drop=True
    )

    return trips


def rsm_assemble(
    orig_indiv,
    orig_joint,
    rsm_indiv,
    rsm_joint,
    households,
    mgra_crosswalk=None,
    sample_rate=0.25,
    run_assembler=1
):
    """
    Assemble and evaluate RSM trip making.

    Parameters
    ----------
    orig_indiv : orig_indiv (path_like)
        Trips table from "original" model run, should be comprehensive simulation
        of all individual trips for all synthetic households.
    orig_joint : orig_joint (path_like)
        Joint trips table from "original" model run, should be comprehensive simulation
        of all joint trips for all synthetic households.
    rsm_indiv : rsm_indiv (path_like)
        Trips table from RSM model run, should be a simulation of all individual
        trips for potentially only a subset of all synthetic households.
    rsm_joint : rsm_joint (path_like)
        Trips table from RSM model run, should be a simulation of all joint
        trips for potentially only a subset of all synthetic households (the
        same sampled households as in `rsm_indiv`).
    households : households (path_like)
        Synthetic household file, used to get home zones for households.
    mgra_crosswalk : mgra_crosswalk (path_like, optional)
        Crosswalk from original MGRA to clustered zone ids.  Provide this crosswalk
        if the `orig_indiv` and `orig_joint` files reference the original MGRA system
        and those id's need to be converted to aggregated values before merging.
    sample_rate : sample_rate (float)
        Default/fixed sample rate if sampler was turned off
        this is used to scale the trips if run_assembler is 0
    run_assembler : run_assembler (boolean)
        Flag to indicate whether to run RSM assembler or not. 
        1 is to run assembler, 0 is to turn if off
        setting this to 0 is only an option if sampler is turned off       
    
    Returns
    -------
    final_trips_rsm : final_ind_trips (pd.DataFrame)
        Assembled trip table for RSM run, filling in archived trip values for
        non-resimulated households.
    combined_trips_by_zone : final_jnt_trips (pd.DataFrame)
        Summary table of changes in trips by mode, by household home zone.
        Used to check whether undersampled zones have stable travel behavior.
    
    Separate tables for individual and joint trips, as required by java.
    
    
    """
    orig_indiv = Path(orig_indiv).expanduser()
    orig_joint = Path(orig_joint).expanduser()
    rsm_indiv = Path(rsm_indiv).expanduser()
    rsm_joint = Path(rsm_joint).expanduser()
    households = Path(households).expanduser()

    assert os.path.isfile(orig_indiv)
    assert os.path.isfile(orig_joint)
    assert os.path.isfile(rsm_indiv)
    assert os.path.isfile(rsm_joint)
    assert os.path.isfile(households)

    if mgra_crosswalk is not None:
        mgra_crosswalk = Path(mgra_crosswalk).expanduser()
        assert os.path.isfile(mgra_crosswalk)

    # load trip data - partial simulation of RSM model
    logger.info("reading ind_trips_rsm")
    ind_trips_rsm = pd.read_csv(rsm_indiv)
    logger.info("reading jnt_trips_rsm")
    jnt_trips_rsm = pd.read_csv(rsm_joint)

    if run_assembler == 1:
        # load trip data - full simulation of residual/source model
        logger.info("reading ind_trips_full")
        ind_trips_full = pd.read_csv(orig_indiv)
        logger.info("reading jnt_trips_full")
        jnt_trips_full = pd.read_csv(orig_joint)

        if mgra_crosswalk is not None:
            logger.info("applying mgra_crosswalk to original data")
            mgra_crosswalk = pd.read_csv(mgra_crosswalk).set_index("MGRA")["cluster_id"]
            mgra_crosswalk[-1] = -1
            mgra_crosswalk[0] = 0
            for col in [c for c in ind_trips_full.columns if c.lower().endswith("_mgra")]:
                ind_trips_full[col] = ind_trips_full[col].map(mgra_crosswalk)
            for col in [c for c in jnt_trips_full.columns if c.lower().endswith("_mgra")]:
                jnt_trips_full[col] = jnt_trips_full[col].map(mgra_crosswalk)
        
        # convert to rsm trips
        logger.info("convert to common table platform")
        rsm_trips = _merge_joint_and_indiv_trips(ind_trips_rsm, jnt_trips_rsm)
        original_trips = _merge_joint_and_indiv_trips(ind_trips_full, jnt_trips_full)
        
        logger.info("get all hhids in trips produced by RSM")
        hh_ids_rsm = rsm_trips["hh_id"].unique()
        
        logger.info("remove orginal model trips made by households chosen in RSM trips")
        original_trips_not_resimulated = original_trips.loc[
            ~original_trips["hh_id"].isin(hh_ids_rsm)
        ]
        original_ind_trips_not_resimulated = ind_trips_full[
            ~ind_trips_full["hh_id"].isin(hh_ids_rsm)
        ]
        original_jnt_trips_not_resimulated = jnt_trips_full[
            ~jnt_trips_full["hh_id"].isin(hh_ids_rsm)
        ]
        
        logger.info("concatenate trips from rsm and original model")
        final_trips_rsm = pd.concat(
            [rsm_trips, original_trips_not_resimulated], ignore_index=True
        ).reset_index(drop=True)
        final_ind_trips = pd.concat(
            [ind_trips_rsm, original_ind_trips_not_resimulated], ignore_index=True
        ).reset_index(drop=True)
        final_jnt_trips = pd.concat(
            [jnt_trips_rsm, original_jnt_trips_not_resimulated], ignore_index=True
        ).reset_index(drop=True)
        
        # Get percentage change in total trips by mode for each home zone
        
        # extract trips made by households in RSM and Original model
        original_trips_that_were_resimulated = original_trips.loc[
            original_trips["hh_id"].isin(hh_ids_rsm)
        ]
        
        def _agg_by_hhid_and_tripmode(df, name):
            return df.groupby(["hh_id", "trip_mode"]).size().rename(name).reset_index()
        
        # combining trips by hhid and trip mode
        combined_trips = pd.merge(
            _agg_by_hhid_and_tripmode(original_trips_that_were_resimulated, "n_trips_orig"),
            _agg_by_hhid_and_tripmode(rsm_trips, "n_trips_rsm"),
            on=["hh_id", "trip_mode"],
            how="outer",
            sort=True,
        ).fillna(0)
        
        # aggregating by Home zone
        hh_rsm = pd.read_csv(households)
        hh_id_col_names = ["hhid", "hh_id", "household_id"]
        for hhid in hh_id_col_names:
            if hhid in hh_rsm.columns:
                break
        else:
            raise KeyError(f"none of {hh_id_col_names!r} in household file")
        homezone_col_names = ["mgra", "home_mgra"]
        for zoneid in homezone_col_names:
            if zoneid in hh_rsm.columns:
                break
        else:
            raise KeyError(f"none of {homezone_col_names!r} in household file")
        hh_rsm = hh_rsm[[hhid, zoneid]]
        
        # attach home zone id
        combined_trips = pd.merge(
            combined_trips, hh_rsm, left_on="hh_id", right_on=hhid, how="left"
        )
        
        combined_trips_by_zone = (
            combined_trips.groupby([zoneid, "trip_mode"])[["n_trips_orig", "n_trips_rsm"]]
            .sum()
            .reset_index()
        )
        
        combined_trips_by_zone = combined_trips_by_zone.eval(
            "net_change = (n_trips_rsm - n_trips_orig)"
        )
        
        combined_trips_by_zone["max_trips"] = np.fmax(
            combined_trips_by_zone.n_trips_rsm, combined_trips_by_zone.n_trips_orig
        )
        combined_trips_by_zone = combined_trips_by_zone.eval(
            "pct_change = net_change / max_trips * 100"
        )
        combined_trips_by_zone = combined_trips_by_zone.drop(columns="max_trips")
    else:
        # if assembler is set to be turned off
        # then scale the trips in the trip list using the fixed sample rate 
        # trips in the final trip lists will be 100%
        scale_factor = int(1.0/sample_rate)
        
        # concat is slow
        # https://stackoverflow.com/questions/50788508/how-can-i-replicate-rows-of-a-pandas-dataframe
        #final_ind_trips = pd.concat([ind_trips_rsm]*scale_factor, ignore_index=True)
        #final_jnt_trips = pd.concat([jnt_trips_rsm]*scale_factor, ignore_index=True)
        
        final_ind_trips = pd.DataFrame(
            np.repeat(ind_trips_rsm.values, scale_factor, axis=0),
            columns=ind_trips_rsm.columns
        )
        
        final_jnt_trips = pd.DataFrame(
            np.repeat(jnt_trips_rsm.values, scale_factor, axis=0),
            columns=jnt_trips_rsm.columns
        )        
       
    return final_ind_trips, final_jnt_trips
