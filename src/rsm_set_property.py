import sys
from rsm.utility import *

properties_file = sys.argv[1]
property_name = sys.argv[2]
property_value = sys.argv[3]

set_property(properties_file, property_name, property_value)