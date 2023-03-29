import re
import glob
import shutil
import os
import logging

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
        for line in lines:
            if property_name in line:
                final_line = line

    if final_line:
        property_value = final_line.split()[2]

    else:
        raise Exception("{} not found in sandag_agbm.properties file".format(property_name))

    return property_value

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
