
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from tabulate import tabulate

import itertools

# to convert dataframe to fixed width column format
def to_fwf(df, 
    fname
    ):
    content = tabulate(df.values.tolist(), tablefmt="plain")
    open(fname, "w").write(content)

pd.DataFrame.to_fwf = to_fwf

# aggregating input/uec files
def agg_input_files(
    model_dir = ".", 
    rsm_dir = ".",
    taz_cwk_file = "taz_crosswalk.csv",
    mgra_cwk_file = "mgra_crosswalk.csv",
    agg_zones=2000,
    ext_zones=12,
    input_files = ["microMgraEquivMinutes.csv", "microMgraTapEquivMinutes.csv", 
    "walkMgraTapEquivMinutes.csv", "walkMgraEquivMinutes.csv", "bikeTazLogsum.csv",
    "bikeMgraLogsum.csv", "zone.term", "zones.park", "tap.ptype", "accessam.csv",
    "ParkLocationAlts.csv", "CrossBorderDestinationChoiceSoaAlternatives.csv", 
    "households.csv", "TourDcSoaDistanceAlts.csv", "DestinationChoiceAlternatives.csv", "SoaTazDistAlts.csv",
    "TripMatrices.csv"]
    ):
    
    """
        Parameters
        ----------
        model_dir : path to full model run, default "."
        rsm_dir : path to RSM, default "."
        taz_cwk_file : csv file, default taz_crosswalk.csv
            taz to aggregated zones file. Should be located in RSM input folder
        mgra_cwk_file : csv file, default mgra_crosswalk.csv
            mgra to aggregated zones file. Should be located in RSM input folder
        mgra_zone_file : csv file, deafult mgra13_based_input2016.csv.csv
        input_files : list of input files to be aggregated. 
            Should include the following files
                "microMgraEquivMinutes.csv", "microMgraTapEquivMinutes.csv", 
                "walkMgraTapEquivMinutes.csv", "walkMgraEquivMinutes.csv", "bikeTazLogsum.csv",
                "bikeMgraLogsum.csv", "zone.term", "zones.park", "tap.ptype", "accessam.csv",
                "ParkLocationAlts.csv", "CrossBorderDestinationChoiceSoaAlternatives.csv", 
                "households.csv", "ShadowPricingOutput_school_9.csv", "ShadowPricingOutput_work_9.csv",
                "TourDcSoaDistanceAlts"
        
        Returns
        -------
        Aggregated files in the RSM input/uec directory
    """

    df_clusters = pd.read_csv(os.path.join(rsm_dir, "input", taz_cwk_file))
    df_clusters.columns= df_clusters.columns.str.strip().str.lower()
    dict_clusters = dict(zip(df_clusters['taz'], df_clusters['cluster_id']))

    mgra_cwk = pd.read_csv(os.path.join(rsm_dir, "input", mgra_cwk_file))
    mgra_cwk.columns= mgra_cwk.columns.str.strip().str.lower()
    mgra_cwk = dict(zip(mgra_cwk['mgra'], mgra_cwk['cluster_id']))
    
    taz_zones = int(agg_zones) + int(ext_zones)
    mgra_zones = int(agg_zones)

    # aggregating microMgraEquivMinutes.csv
    if "microMgraEquivMinutes.csv" in input_files: 
        df_mm_eqmin = pd.read_csv(os.path.join(model_dir, "output", "microMgraEquivMinutes.csv"))
        df_mm_eqmin['i_new'] = df_mm_eqmin['i'].map(mgra_cwk)
        df_mm_eqmin['j_new'] = df_mm_eqmin['j'].map(mgra_cwk)

        df_mm_eqmin_agg = df_mm_eqmin.groupby(['i_new', 'j_new'])['walkTime', 'dist', 'mmTime', 'mmCost', 'mtTime', 'mtCost',
       'mmGenTime', 'mtGenTime', 'minTime'].mean().reset_index()

        df_mm_eqmin_agg = df_mm_eqmin_agg.rename(columns = {'i_new' : 'i', 'j_new' : 'j'})
        df_mm_eqmin_agg.to_csv(os.path.join(rsm_dir, "input", "microMgraEquivMinutes.csv"), index = False)

    else:
        raise FileNotFoundError("microMgraEquivMinutes.csv")


    # aggregating microMgraTapEquivMinutes.csv"   
    if "microMgraTapEquivMinutes.csv" in input_files:
        df_mm_tap = pd.read_csv(os.path.join(model_dir, "output", "microMgraTapEquivMinutes.csv"))
        df_mm_tap['mgra'] = df_mm_tap['mgra'].map(mgra_cwk)

        df_mm_tap_agg = df_mm_tap.groupby(['mgra', 'tap'])['walkTime', 'dist', 'mmTime', 'mmCost', 'mtTime',
       'mtCost', 'mmGenTime', 'mtGenTime', 'minTime'].mean().reset_index()

        df_mm_tap_agg.to_csv(os.path.join(rsm_dir, "input", "microMgraTapEquivMinutes.csv"), index = False)

    else:
        raise FileNotFoundError("microMgraTapEquivMinutes.csv")

    # aggregating walkMgraTapEquivMinutes.csv
    if "walkMgraTapEquivMinutes.csv" in input_files: 
        df_wlk_mgra_tap = pd.read_csv(os.path.join(model_dir, "output", "walkMgraTapEquivMinutes.csv"))
        df_wlk_mgra_tap["mgra"] = df_wlk_mgra_tap["mgra"].map(mgra_cwk)

        df_wlk_mgra_agg = df_wlk_mgra_tap.groupby(["mgra", "tap"])["boardingPerceived", "boardingActual","alightingPerceived","alightingActual","boardingGain","alightingGain"].mean().reset_index()
        df_wlk_mgra_agg.to_csv(os.path.join(rsm_dir, "input", "walkMgraTapEquivMinutes.csv"), index = False)

    else:
        FileNotFoundError("walkMgraTapEquivMinutes.csv")

    # aggregating walkMgraEquivMinutes.csv
    if "walkMgraEquivMinutes.csv" in input_files:
        df_wlk_min = pd.read_csv(os.path.join(model_dir, "output", "walkMgraEquivMinutes.csv"))
        df_wlk_min["i"] = df_wlk_min["i"].map(mgra_cwk)
        df_wlk_min["j"] = df_wlk_min["j"].map(mgra_cwk)

        df_wlk_min_agg = df_wlk_min.groupby(["i", "j"])["percieved","actual", "gain"].mean().reset_index()

        df_wlk_min_agg.to_csv(os.path.join(rsm_dir, "input", "walkMgraEquivMinutes.csv"), index = False)

    else:
        FileNotFoundError("walkMgraEquivMinutes.csv")

    # aggregating biketazlogsum
    if "bikeTazLogsum.csv" in input_files:
        bike_taz = pd.read_csv(os.path.join(model_dir, "output", "bikeTazLogsum.csv"))

        bike_taz["i"] = bike_taz["i"].map(dict_clusters)
        bike_taz["j"] = bike_taz["j"].map(dict_clusters)

        bike_taz_agg = bike_taz.groupby(["i", "j"])["logsum", "time"].mean().reset_index()
        bike_taz_agg.to_csv(os.path.join(rsm_dir, "input", "bikeTazLogsum.csv"), index = False)

    else:
        raise FileNotFoundError("bikeTazLogsum.csv")

    # aggregating bikeMgraLogsum.csv
    if "bikeMgraLogsum.csv" in input_files:
        bike_mgra = pd.read_csv(os.path.join(model_dir, "output", "bikeMgraLogsum.csv"))
        bike_mgra["i"] = bike_mgra["i"].map(mgra_cwk)
        bike_mgra["j"] = bike_mgra["j"].map(mgra_cwk)

        bike_mgra_agg = bike_mgra.groupby(["i", "j"])["logsum", "time"].mean().reset_index()
        bike_mgra_agg.to_csv(os.path.join(rsm_dir, "input", "bikeMgraLogsum.csv"), index = False)
    else:
        raise FileNotFoundError("bikeMgraLogsum.csv")

    # aggregating zone.term
    if "zone.term" in input_files:
        df_zone_term = pd.read_fwf(os.path.join(model_dir, "input", "zone.term"), header = None)
        df_zone_term.columns = ["taz", "terminal_time"]

        df_agg = pd.merge(df_zone_term, df_clusters, on = "taz", how = 'left')
        df_zones_agg = df_agg.groupby(["cluster_id"])['terminal_time'].max().reset_index()

        df_zones_agg.columns = ["taz", "terminal_time"]
        df_zones_agg.to_fwf(os.path.join(rsm_dir, "input", "zone.term"))
    
    else:
        raise FileNotFoundError("zone.term")

    # aggregating zones.park
    if "zones.park" in input_files:
        df_zones_park = pd.read_fwf(os.path.join(model_dir, "input", "zone.park"), header = None)
        df_zones_park.columns = ["taz", "park_zones"]

        df_zones_park_agg = pd.merge(df_zones_park, df_clusters, on = "taz", how = 'left')
        df_zones_park_agg = df_zones_park_agg.groupby(["cluster_id"])['park_zones'].max().reset_index()
        df_zones_park_agg.columns = ["taz", "park_zones"]
        df_zones_park_agg.to_fwf(os.path.join(rsm_dir, "input", "zone.park"))

    else:
        raise FileNotFoundError("zone.park")


    # aggregating tap.ptype 
    if "tap.ptype" in input_files:
        df_tap_ptype = pd.read_fwf(os.path.join(model_dir, "input", "tap.ptype"), header = None)
        df_tap_ptype.columns = ["tap", "lot id", "parking type", "taz", "capacity", "distance", "transit mode"]

        df_tap_ptype = pd.merge(df_tap_ptype, df_clusters, on = "taz", how = 'left')

        df_tap_ptype = df_tap_ptype[["tap", "lot id", "parking type", "cluster_id", "capacity", "distance", "transit mode"]]
        df_tap_ptype = df_tap_ptype.rename(columns = {"cluster_id": "taz"})
        df_tap_ptype.to_fwf(os.path.join(rsm_dir, "input", "tap.ptype"))

    else:
        raise FileNotFoundError("tap.ptype")

    #aggregating accessam.csv
    if "accessam.csv" in input_files:
        df_acc = pd.read_csv(os.path.join(model_dir, "input", "accessam.csv"), header = None)
        df_acc.columns = ['TAZ', 'TAP', 'TIME', 'DISTANCE', 'MODE']

        df_acc['TAZ'] = df_acc['TAZ'].map(dict_clusters)
        df_acc_agg = df_acc.groupby(['TAZ', 'TAP', 'MODE'])['TIME', 'DISTANCE'].mean().reset_index()
        df_acc_agg = df_acc_agg[["TAZ", "TAP", "TIME", "DISTANCE", "MODE"]]

        df_acc_agg.to_csv(os.path.join(rsm_dir, "input", "accessam.csv"), index = False, header =False)
    else:
        raise FileNotFoundError("accessam.csv")

    # aggregating ParkLocationAlts.csv
    if "ParkLocationAlts.csv" in input_files:
        df_park = pd.read_csv(os.path.join(model_dir, "uec", "ParkLocationAlts.csv"))
        df_park['mgra_new'] = df_park["mgra"].map(mgra_cwk)
        df_park_agg = df_park.groupby(["mgra_new"])["parkarea"].min().reset_index() # assuming 1 is "parking" and 2 is "no parking"
        df_park_agg['a'] = [i+1 for i in range(len(df_park_agg))]

        df_park_agg.columns = ["a", "mgra", "parkarea"]
        df_park_agg.to_csv(os.path.join(rsm_dir, "uec", "ParkLocationAlts.csv"), index = False)

    else:
        FileNotFoundError("ParkLocationAlts.csv")

    # aggregating CrossBorderDestinationChoiceSoaAlternatives.csv
    if "CrossBorderDestinationChoiceSoaAlternatives.csv" in input_files:
        df_cb = pd.read_csv(os.path.join(model_dir, "uec","CrossBorderDestinationChoiceSoaAlternatives.csv"))

        df_cb["mgra_entry"] = df_cb["mgra_entry"].map(mgra_cwk)
        df_cb["mgra_return"] = df_cb["mgra_return"].map(mgra_cwk)
        df_cb["a"] = df_cb["a"].map(mgra_cwk)

        df_cb = pd.merge(df_cb, df_clusters, left_on = "dest", right_on = "taz", how = 'left')
        df_cb = df_cb.drop(columns = ["dest", "taz"])
        df_cb = df_cb.rename(columns = {'cluster_id' : 'dest'})

        df_cb_final  = df_cb.drop_duplicates()

        df_cb_final = df_cb_final[["a", "dest", "poe", "mgra_entry", "mgra_return", "poe_taz"]]
        df_cb_final.to_csv(os.path.join(rsm_dir, "uec", "CrossBorderDestinationChoiceSoaAlternatives.csv"), index = False)

    else:
        FileNotFoundError("CrossBorderDestinationChoiceSoaAlternatives.csv")

    # aggregating households.csv
    if "households.csv" in input_files:
        df_hh = pd.read_csv(os.path.join(model_dir, "input","households.csv"))
        df_hh["mgra"] = df_hh["mgra"].map(mgra_cwk)
        df_hh["taz"] = df_hh["taz"].map(dict_clusters)

        df_hh.to_csv(os.path.join(rsm_dir, "input", "households.csv"), index = False)

    else:
        FileNotFoundError("households.csv")

    # aggregating ShadowPricingOutput_school_9.csv
    if "ShadowPricingOutput_school_9.csv" in input_files:
        df_sp_sch = pd.read_csv(os.path.join(model_dir, "input", "ShadowPricingOutput_school_9.csv"))

        agg_instructions = {}
        for col in df_sp_sch.columns:
            if "size" in col:
                agg_instructions.update({col: "sum"})
                
            if "shadowPrices" in col:
                agg_instructions.update({col: "max"})
                
            if "_origins" in col:
                agg_instructions.update({col: "sum"})
                
            if "_modeledDests" in col:
                agg_instructions.update({col: "sum"})

        df_sp_sch['mgra'] = df_sp_sch['mgra'].map(mgra_cwk)
        df_sp_sch_agg = df_sp_sch.groupby(['mgra']).agg(agg_instructions).reset_index()

        alt = list(df_sp_sch_agg['mgra'])
        df_sp_sch_agg.insert(loc=0, column="alt", value=alt)
        df_sp_sch_agg.loc[len(df_sp_agg.index)] = 0

        df_sp_sch_agg.to_csv(os.path.join(rsm_dir, "input", "ShadowPricingOutput_school_9.csv"), index=False)

    else:
        FileNotFoundError("ShadowPricingOutput_school_9.csv")

    # aggregating ShadowPricingOutput_work_9.csv
    if "ShadowPricingOutput_work_9.csv" in input_files:
        df_sp_wrk = pd.read_csv(os.path.join(model_dir, "input", "ShadowPricingOutput_work_9.csv"))

        agg_instructions = {}
        for col in df_sp_wrk.columns:
            if "size" in col:
                agg_instructions.update({col: "sum"})
                
            if "shadowPrices" in col:
                agg_instructions.update({col: "max"})
                
            if "_origins" in col:
                agg_instructions.update({col: "sum"})
                
            if "_modeledDests" in col:
                agg_instructions.update({col: "sum"})

        df_sp_wrk['mgra'] = df_sp_wrk['mgra'].map(mgra_cwk)

        df_sp_wrk_agg = df_sp_wrk.groupby(['mgra']).agg(agg_instructions).reset_index()

        alt = list(df_sp_wrk_agg['mgra'])
        df_sp_wrk_agg.insert(loc=0, column="alt", value=alt)

        df_sp_wrk_agg.loc[len(df_sp_wrk_agg.index)] = 0

        df_sp_wrk_agg.to_csv(os.path.join(rsm_dir, "input", "ShadowPricingOutput_work_9.csv"), index=False)

    else:
        FileNotFoundError("ShadowPricingOutput_work_9.csv")
        
    if "TourDcSoaDistanceAlts.csv" in input_files:
        df_TourDcSoaDistanceAlts = pd.DataFrame({"a" : range(1,taz_zones+1), "dest" : range(1, taz_zones+1)})
        df_TourDcSoaDistanceAlts.to_csv(os.path.join(rsm_dir, "uec", "TourDcSoaDistanceAlts.csv"), index=False)
        
    if "DestinationChoiceAlternatives.csv" in input_files:
        df_DestinationChoiceAlternatives = pd.DataFrame({"a" : range(1,mgra_zones+1), "mgra" : range(1, mgra_zones+1)})
        df_DestinationChoiceAlternatives.to_csv(os.path.join(rsm_dir, "uec", "DestinationChoiceAlternatives.csv"), index=False)
        
    if "SoaTazDistAlts.csv" in input_files:
        df_SoaTazDistAlts = pd.DataFrame({"a" : range(1,taz_zones+1), "dest" : range(1, taz_zones+1)})
        df_SoaTazDistAlts.to_csv(os.path.join(rsm_dir, "uec", "SoaTazDistAlts.csv"), index=False)

    if "TripMatrices.csv" in input_files:
        trips = pd.read_csv(os.path.join(model_dir,"output", "TripMatrices.csv"))
        trips['i'] = trips['i'].map(dict_clusters)
        trips['j'] = trips['j'].map(dict_clusters)

        cols = list(trips.columns)
        cols.remove("i")
        cols.remove("j")

        trips_df = trips.groupby(['i', 'j'])[cols].sum().reset_index()
        trips_df.to_csv(os.path.join(rsm_dir, "output", "TripMatrices.csv"), index = False)

    else:
        FileNotFoundError("TripMatrices.csv")

    if "crossBorderTours.csv" in input_files: 
        df = pd.read_csv(os.path.join(model_dir, "output", "crossBorderTours.csv"))
        df['originMGRA'] = df['originMGRA'].map(mgra_cwk)
        df['destinationMGRA'] = df['destinationMGRA'].map(mgra_cwk)

        df['originTAZ'] = df['originTAZ'].map(dict_clusters)
        df['destinationTAZ'] = df['destinationTAZ'].map(dict_clusters)
        df.to_csv(os.path.join(rsm_dir, "output", "crossBorderTours.csv"), index = False)

    else:
        raise FileNotFoundError("crossBorderTours.csv")

    if "crossBorderTrips.csv" in input_files: 
        df = pd.read_csv(os.path.join(model_dir, "output", "crossBorderTrips.csv"))
        df['originMGRA'] = df['originMGRA'].map(mgra_cwk)
        df['destinationMGRA'] = df['destinationMGRA'].map(mgra_cwk)
        
        df['originTAZ'] = df['originTAZ'].map(dict_clusters)
        df['destinationTAZ'] = df['destinationTAZ'].map(dict_clusters)
        df.to_csv(os.path.join(rsm_dir, "output", "crossBorderTrips.csv"), index = False)

    else:
        raise FileNotFoundError("crossBorderTrips.csv")

    if "internalExternalTrips.csv" in input_files: 
        df = pd.read_csv(os.path.join(model_dir, "output", "internalExternalTrips.csv"))
        df['originMGRA'] = df['originMGRA'].map(mgra_cwk)
        df['destinationMGRA'] = df['destinationMGRA'].map(mgra_cwk)

        df['originTAZ'] = df['originTAZ'].map(dict_clusters)
        df['destinationTAZ'] = df['destinationTAZ'].map(dict_clusters)
        df.to_csv(os.path.join(rsm_dir, "output", "internalExternalTrips.csv"), index = False)

    else:
        raise FileNotFoundError("internalExternalTrips.csv")

    if "visitorTours.csv" in input_files: 
        df = pd.read_csv(os.path.join(model_dir, "output", "visitorTours.csv"))
        
        df['originMGRA'] = df['originMGRA'].map(mgra_cwk)
        df['destinationMGRA'] = df['destinationMGRA'].map(mgra_cwk)
        
        df.to_csv(os.path.join(rsm_dir, "output", "visitorTours.csv"), index = False)

    else:
        raise FileNotFoundError("visitorTours.csv")
        
    if "visitorTrips.csv" in input_files: 
        df = pd.read_csv(os.path.join(model_dir, "output", "visitorTrips.csv"))
        
        df['originMGRA'] = df['originMGRA'].map(mgra_cwk)
        df['destinationMGRA'] = df['destinationMGRA'].map(mgra_cwk)
        
        df.to_csv(os.path.join(rsm_dir, "output", "visitorTrips.csv"), index = False)

    else:
        raise FileNotFoundError("visitorTrips.csv")

    if "householdAVTrips.csv" in input_files: 
        df = pd.read_csv(os.path.join(model_dir, "output", "householdAVTrips.csv"))
        #print(os.path.join(model_dir, "output", "householdAVTrips.csv"))
        df['orig_mgra'] = df['orig_mgra'].map(mgra_cwk)
        df['dest_gra'] = df['dest_gra'].map(mgra_cwk)

        df['trip_orig_mgra'] = df['trip_orig_mgra'].map(mgra_cwk)
        df['trip_dest_mgra'] = df['trip_dest_mgra'].map(mgra_cwk)
        df.to_csv(os.path.join(rsm_dir, "output", "householdAVTrips.csv"), index = False)

    else:
        raise FileNotFoundError("householdAVTrips.csv")

    if "airport_out.CBX.csv" in input_files: 
        df = pd.read_csv(os.path.join(model_dir, "output", "airport_out.CBX.csv"))
        df['originMGRA'] = df['originMGRA'].map(mgra_cwk)
        df['destinationMGRA'] = df['destinationMGRA'].map(mgra_cwk)
        
        df['originTAZ'] = df['originTAZ'].map(dict_clusters)
        df['destinationTAZ'] = df['destinationTAZ'].map(dict_clusters)
        df.to_csv(os.path.join(rsm_dir, "output", "airport_out.CBX.csv"), index = False)

    else:
        raise FileNotFoundError("airport_out.CBX.csv")

    if "airport_out.SAN.csv" in input_files: 
        df = pd.read_csv(os.path.join(model_dir, "output", "airport_out.SAN.csv"))
        df['originMGRA'] = df['originMGRA'].map(mgra_cwk)
        df['destinationMGRA'] = df['destinationMGRA'].map(mgra_cwk)
        
        df['originTAZ'] = df['originTAZ'].map(dict_clusters)
        df['destinationTAZ'] = df['destinationTAZ'].map(dict_clusters)
        df.to_csv(os.path.join(rsm_dir, "output", "airport_out.SAN.csv"), index = False)

    else:
        raise FileNotFoundError("airport_out.SAN.csv")

    if "TNCtrips.csv" in input_files: 
        df = pd.read_csv(os.path.join(model_dir, "output", "TNCtrips.csv"))
        df['originMgra'] = df['originMgra'].map(mgra_cwk)
        df['destinationMgra'] = df['destinationMgra'].map(mgra_cwk)
        
        df['originTaz'] = df['originTaz'].map(dict_clusters)
        df['destinationTaz'] = df['destinationTaz'].map(dict_clusters)
        df.to_csv(os.path.join(rsm_dir, "output", "TNCtrips.csv"), index = False)

    else:
        raise FileNotFoundError("TNCtrips.csv")

    files = ["Trip" + "_" + i + "_" + j + ".csv" for i, j in
                itertools.product(["FA", "GO", "IN", "RE", "SV", "TH", "WH"],
                                   ["OE", "AM", "MD", "PM", "OL"])]

    for file in files:
        df = pd.read_csv(os.path.join(model_dir, "output", file))
        df['I'] = df['I'].map(dict_clusters)
        df['J'] = df['J'].map(dict_clusters)
        df['HomeZone'] = df['HomeZone'].map(dict_clusters)
        df.to_csv(os.path.join(rsm_dir, "output",file), index = False)

    

    