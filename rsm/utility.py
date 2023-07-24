import re
import glob
import shutil
import os
import logging
import geopandas as gpd
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class ReplacementOfString:
    """
    This class provides a mechanism to edit a file, replacing
    the string value of a particular parameter with a new value.
    """
    def __init__(self, varname, assign_operator="="):
        self.varname = varname
        self.regex = re.compile(f"({varname}\s*{assign_operator}[ \t\f\v]*)([^#\n]*)(#.*)?\n", flags=re.MULTILINE)
    def sub(self, value, s):
        s, n = self.regex.subn(f"\g<1>{value}\g<3>\n", s)
        logger.info(f"For '{self.varname}': {n} substitutions made")
        return s


def extract_number_in_filename(f):
    """
    extrcats the number from the file name.
    It is used in extracting the iteration number from school and work shadow pricing files
    """
    s = re.findall("\d+",f)
    return (int(s[0]) if s else -1,f)


def get_shadow_pricing_files(folder):
    """
    folder is path to location of shadow pricing files.
    """
    sp_work_files = glob.glob(os.path.join(folder, 'ShadowPricingOutput_work*.csv'), recursive=True)
    sp_sch_files = glob.glob(os.path.join(folder, 'ShadowPricingOutput_school*.csv'), recursive=True)

    sp_work_files =  [os.path.split(x)[1] for x in sp_work_files]
    sp_sch_files = [os.path.split(x)[1] for x in sp_sch_files]

    sp_work_max = max(sp_work_files, key=extract_number_in_filename)
    sp_school_max = max(sp_sch_files, key=extract_number_in_filename)

    return sp_work_max, sp_school_max


def copy_file(src, dest):
    """
    Create copy of file 

    """
    shutil.copy(src, dest)

def get_property(properties_file, property_name):
    """
    Extracts the property_value for a property_name from sandag_abm.properties files
    """
    with open(properties_file, "r") as f:
        lines = f.readlines()
        key_found = False
        for line in lines:
            if property_name in line:
                key = line.split("=")[0].strip()
                value = line.split("=")[1].strip()

                if property_name == key:
                    key_found = True
                    break

    if not key_found:
        raise Exception("{} not found in sandag_abm.properties file".format(property_name))

    return value

def set_property(properties_file, property_name, property_value):
    """
    Modifies the sandag properties file

    """

    with open(properties_file) as f:
        y = f.read()

    y = ReplacementOfString(property_name).sub(property_value, y)

    with open(properties_file, 'wt') as f:
        f.write(y)

def fix_zero_enrollment(mgra_df):

    """
    adjusts the elementary and high school enrollments for RSM

    """
    
    ech_check = mgra_df.groupby(['ech_dist'])['enrollgradekto8'].sum().reset_index()
    ech_dist_df = ech_check.loc[ech_check['enrollgradekto8']==0]
    if len(ech_dist_df) > 0:
        ech_dist_mod = list(ech_dist_df['ech_dist'])
        # print(ech_dist_mod)
        mgra_df.loc[mgra_df['ech_dist'].isin(ech_dist_mod), 'enrollgradekto8'] = 99999

    hch_check = mgra_df.groupby(['hch_dist'])['enrollgrade9to12'].sum().reset_index()
    hch_dist_df = hch_check.loc[hch_check['enrollgrade9to12']==0]
    if len(hch_dist_df) > 0:
        hch_dist_mod = list(hch_dist_df['hch_dist'])
        # print(hch_dist_mod)
        mgra_df.loc[mgra_df['hch_dist'].isin(ech_dist_mod), 'enrollgrade9to12'] = 99999
        
    return mgra_df

def add_intersection_count(model_dir, mgra_data):
    
    RSM_ABM_PROPERTIES = os.path.join(model_dir, "conf", "sandag_abm.properties")
    links_file = os.path.join(model_dir, "input", os.path.basename(get_property(RSM_ABM_PROPERTIES, "active.edge.file")))
    nodes_file = os.path.join(model_dir, "input", os.path.basename(get_property(RSM_ABM_PROPERTIES, "active.node.file")))
    
    links = gpd.read_file(links_file)
    links = pd.DataFrame(links.drop(columns='geometry'))
    
    nodes = gpd.read_file(nodes_file)
    nodes = pd.DataFrame(nodes.drop(columns='geometry'))
    
    nodes_int = nodes.loc[(nodes.NodeLev_ID < 100000000)]

    #links
    #remove taz, mgra, and tap connectors
    links = links.loc[(links.A <100000000) & (links.B <100000000)]

    #remove freeways (Func_Class=1), ramps (Func_Class=2), and others (Func_Class =0  or -1)
    links = links.loc[(links.Func_Class > 2)]
    links['link_count'] = 1

    #aggregate by Node A and Node B
    links_nodeA = links[['A', 'link_count']].groupby('A').sum().reset_index()
    links_nodeB = links[['B', 'link_count']].groupby('B').sum().reset_index()

    #merge the two and keep all records from both dataframes (how='outer')
    nodes_linkcount = pd.merge(links_nodeA, links_nodeB, left_on='A', right_on='B', how = 'outer')
    nodes_linkcount = nodes_linkcount.fillna(0)
    nodes_linkcount['link_count'] = nodes_linkcount['link_count_x'] + nodes_linkcount['link_count_y']

    #get node id from both dataframes
    nodes_linkcount['N']=0
    nodes_linkcount['N'][nodes_linkcount.A>0] = nodes_linkcount['A']
    nodes_linkcount['N'][nodes_linkcount.B>0] = nodes_linkcount['B']
    nodes_linkcount['N']=nodes_linkcount['N'].astype(float)
    nodes_linkcount = nodes_linkcount[['N','link_count']]

    #keep nodes with 3+ link count
    intersections_temp = nodes_linkcount.loc[nodes_linkcount.link_count>=3]

    #get node X and Y
    intersections = pd.merge(intersections_temp,nodes_int[['NodeLev_ID','XCOORD','YCOORD']], left_on = 'N', right_on = 'NodeLev_ID', how = 'left')
    intersections = intersections[['N','XCOORD','YCOORD']]
    intersections = intersections.rename(columns = {'XCOORD': 'X', 'YCOORD': 'Y'})

    mgra_nodes = nodes[nodes.MGRA > 0][['MGRA','XCOORD','YCOORD']]
    mgra_nodes.columns = ['mgra','x','y']
    int_dict = {}
    for int in intersections.iterrows():
        mgra_nodes['dist'] = np.sqrt((int[1][1] - mgra_nodes['x'])**2+(int[1][2] - mgra_nodes['y'])**2)
        int_dict[int[1][0]] = mgra_nodes.loc[mgra_nodes['dist'] == mgra_nodes['dist'].min()]['mgra'].values[0]

    intersections['near_mgra'] = intersections['N'].map(int_dict)
    intersections = intersections.groupby('near_mgra', as_index = False).count()[['near_mgra','N']].rename(columns = {'near_mgra':'mgra','N':'icnt'})
    
    try:
        mgra_data = mgra_data.drop('icnt',axis = 1).merge(intersections, how = 'outer', on = "mgra")
    except:
        mgra_data = mgra_data.merge(intersections, how = 'outer', on = "mgra")
        
    return mgra_data

def add_density_variables(model_dir, mgra_data):
    #new_cols = ['totint','duden','empden','popden','retempden','totintbin','empdenbin','dudenbin','PopEmpDenPerMi']
    new_cols = ['totint', 'duden', 'empden', 'popden', 'retempden', 'PopEmpDenPerMi']

    for col in new_cols:
        if col in mgra_data.columns.tolist():
            mgra_data = mgra_data.drop(col, axis=1)

    #all street distance
    RSM_ABM_PROPERTIES = os.path.join(model_dir, "conf", "sandag_abm.properties")
    equivmins_file = get_property(RSM_ABM_PROPERTIES, "active.logsum.matrix.file.walk.mgra")
    equiv_min = pd.read_csv(os.path.join(model_dir, "output", equivmins_file))

    equiv_min['dist'] = equiv_min['actual']/60*3

    def _density_function(mgra_in):
        int_radius = 0.65 #mile
        oth_radius = 0.65 #mile
        eqmn = equiv_min[equiv_min['i'] == mgra_in]
        mgra_circa_int = eqmn[eqmn['dist'] < int_radius]['j'].unique()
        mgra_circa_oth = eqmn[eqmn['dist'] < oth_radius]['j'].unique()
        totEmp = mgra_data[mgra_data.mgra.isin(mgra_circa_oth)]['emp_total'].sum()
        totRet = mgra_data[mgra_data.mgra.isin(mgra_circa_oth)]['emp_retail'].sum() + mgra_data[mgra_data.mgra.isin(mgra_circa_oth)]['emp_personal_svcs_retail'].sum() + mgra_data[mgra_data.mgra.isin(mgra_circa_oth)]['emp_restaurant_bar'].sum()
        totHH = mgra_data[mgra_data.mgra.isin(mgra_circa_oth)]['hh'].sum()
        totPop = mgra_data[mgra_data.mgra.isin(mgra_circa_oth)]['pop'].sum()
        totAcres = mgra_data[mgra_data.mgra.isin(mgra_circa_oth)]['land_acres'].sum()
        totInt = mgra_data[mgra_data.mgra.isin(mgra_circa_int)]['icnt'].sum()
        if(totAcres>0):
            empDen = totEmp/totAcres
            retDen = totRet/totAcres
            duDen = totHH/totAcres
            popDen = totPop/totAcres
            popEmpDenPerMi = (totEmp+totPop)/(totAcres/640) #Acres to miles
            tot_icnt = totInt
        else:
            empDen = 0
            retDen = 0
            duDen = 0
            popDen = 0
            popEmpDenPerMi = 0
            tot_icnt = 0
        
        return tot_icnt,duDen,empDen,popDen,retDen,popEmpDenPerMi
        
    mgra_data["totint"],mgra_data["duden"],mgra_data["empden"],mgra_data["popden"],mgra_data["retempden"],mgra_data["PopEmpDenPerMi"] = zip(*mgra_data['mgra'].map(_density_function))

    # mgra_data["totintbin"] = np.where(mgra_data["totint"] < 80, 1, np.where(mgra_data["totint"] < 130, 2, 3))
    # mgra_data["empdenbin"] = np.where(mgra_data["empden"] < 10, 1, np.where(mgra_data["empden"] < 30, 2,3))
    # mgra_data["dudenbin"] = np.where(mgra_data["duden"] < 5, 1, np.where(mgra_data["duden"] < 10, 2,3))

    mgra_data = mgra_data.fillna(0)

    return mgra_data


def scaleup_to_rsm_samplingrate(df, 
                                household, 
                                taz_crosswalk, 
                                scale_factor, 
                                study_area_tazs=None):
    """
    scales up the trips based on the sampling rate. 
    
    """
    
    hh = pd.read_csv(household)
    hh = hh[['hhid', 'taz']]

    rsm_zones = pd.read_csv(taz_crosswalk)
    dict_clusters = dict(zip(rsm_zones["taz"], rsm_zones["cluster_id"]))

    hh["taz"] = hh["taz"].map(dict_clusters)
    hh['scale_factor'] = scale_factor
    
    if study_area_tazs:       
        hh.loc[hh['taz'].isin(study_area_tazs), 'scale_factor'] = 1
    
    df = pd.merge(df, hh, left_on='hh_id', right_on='hhid', how='left')
    final_df = df.loc[np.repeat(df.index, df['scale_factor'])]
    final_df = final_df.drop(columns=['hhid', 'scale_factor', 'taz'])
    
    return final_df

def check_column_names(df, columns):
    """
    Check column names of study area file 
    """
    df_columns = df.columns.tolist()
    if set(columns) != set(df_columns):
        raise ValueError("Column names do not match the expected column names : taz and group. Please fix the column names")
    return True

def create_list_study_area_taz(study_area_file):
    """
    Creates list[int or list] based on the values of the group column
    """

    try:
        df = pd.read_csv(study_area_file)
        columns_to_check = ['taz', 'group']
        match = check_column_names(df, columns_to_check)

    except ValueError as e:
        print("Error:", str(e))
        logger.info("Error:", str(e))
        return None
        
    grouped_taz = df.groupby('group')['taz'].apply(list).values.tolist()

    return grouped_taz


def find_rsm_zone_of_study_area(study_area_file, taz_crosswalk):
    """
    finds the RSM zones for the study area using the TAZ crosswalks
    """

    try:
        df = pd.read_csv(study_area_file)
        taz_cwk = pd.read_csv(taz_crosswalk)
        study_area_taz = set(df['taz'])
        rsm_zone = set(taz_cwk.loc[taz_cwk['taz'].isin(study_area_taz), 'cluster_id'])

    except Exception as e:
        logger.info("Error in identifying RSM zone for study area:", str(e))
        return None

    return list(rsm_zone)