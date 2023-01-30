import sys
main_path = os.path.dirname(os.path.realpath(__file__)) + "/../"
sys.path.append(main_path)
from rsm.utility import *

properties_file = sys.argv[1]
property_name = sys.argv[2]
property_value = sys.argv[3]

set_property(properties_file, property_name, property_value)