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


def modify_sandag_properties_for_shadowpricing(src_file, wrok_file, sch_file, iteration):
    """
    Modifies the the sandag properties file with shadow pricing file names

    """

    #modfiying the sandag properties file
    with open(src_file) as f:
        y = f.read()

    strings_to_levers_file = {
    'UsualWorkLocationChoice.ShadowPrice.Input.File' : 'input/' + wrok_file,
    'UsualSchoolLocationChoice.ShadowPrice.Input.File' : 'input/' + sch_file,
    'uwsl.ShadowPricing.Work.MaximumIterations' : 1,
    'uwsl.ShadowPricing.School.MaximumIterations' : 1
    }

    for keys in strings_to_levers_file:
        y = ReplacementOfString(keys).sub(strings_to_levers_file[keys], y)

    with open(src_file, 'wt') as f:
        f.write(y)

def modify_sandag_properties_for_accessibility(src_file, value):
    """
    Modifies the sandag properties file by setting the acc.read.input.file as True or False

    """
    
    #modfiying the sandag properties file
    with open(src_file) as f:
        y = f.read()

    strings_to_levers_file = {

    'acc.read.input.file' : value
    }

    for keys in strings_to_levers_file:
        y = ReplacementOfString(keys).sub(strings_to_levers_file[keys], y)

    with open(src_file, 'wt') as f:
        f.write(y)



def get_user_input(src_file, value):
    """
    Extracts the value of variable from sandag_abm.properties files

    """
    with open(src_file, "r") as f:
        lines = f.readlines()
        for line in lines:
            if value in line:
                final_line = line

    if final_line:
        extracted_value = final_line.split()[2]

    else:
        raise Exception("{} not found in sandag_agbm.properties file".format(value))

    return extracted_value

def set_default_sandag_properties_file(src_file):
    """
    Set default valies in sandag_abm.properties file for RSM

    """
    #modfiying the sandag properties file
    with open(src_file) as f:
        y = f.read()

    strings_to_levers_file = {
    'acc.read.input.file' : 'false',
    'PopulationSynthesizer.InputToCTRAMP.HouseholdFile' : 'input/sampled_households.csv',
    'PopulationSynthesizer.InputToCTRAMP.PersonFile' : 'input/sampled_person.csv',
    'UsualWorkLocationChoice.ShadowPrice.Input.File' : '',
    'UsualSchoolLocationChoice.ShadowPrice.Input.File' : '',  
    'uwsl.ShadowPricing.Work.MaximumIterations' : 10,
    'uwsl.ShadowPricing.School.MaximumIterations' : 10
    }

    for keys in strings_to_levers_file:
        y = ReplacementOfString(keys).sub(strings_to_levers_file[keys], y)

    with open(src_file, 'wt') as f:
        f.write(y)





