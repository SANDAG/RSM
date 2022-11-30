import re
import glob
import shutil

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
        print(f"For '{self.varname}': {n} substitutions made")
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

    sp_work_max = max(sp_work_files, key=extract_number_in_filename)
    sp_school_max = max(sp_sch_files, key=extract_number_in_filename)

    return sp_work_max, sp_school_max

def modify_sandag_properties(src_file, wrok_file, sch_file, iteration):
    """
    
    """

    #create a copy of the sandag_abm.properties file with iteration number
    file_path = os.path.split(src_file)[0]
    file_name_with_ext = os.path.split(src_file)[1]
    file_name = os.path.splitext(file_name_with_ext)[0]

    dest_file = file_path+file_name+'_'+str(iteration-1),'.properties'

    shutil.copy(src_file, dest_file)

    #modfiying the sandag properties file
    with open(src_file) as f:
        y = f.read()

    strings_to_levers_file = {
    'UsualWorkLocationChoice.ShadowPrice.Input.File' : 'input/' + wrok_file,
    'UsualSchoolLocationChoice.ShadowPrice.Input.File' : 'input/' + sch_file,
    'uwsl.ShadowPricing.Work.MaximumIterations' : 1,
    'uwsl.ShadowPricing.School.MaximumIterations' : 1,
    'acc.read.input.file' : 'true'
    }

    for keys in strings_to_levers_file:
        y = ReplacementOfString(keys).sub(strings_to_levers_file[keys], y)

    with open(src_file, 'wt') as f:
        f.write(y)

