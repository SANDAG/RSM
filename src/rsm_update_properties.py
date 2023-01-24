import sys
from rsm.utility import *

rsm_dir = sys.argv[1]
iteration = sys.argv[2]

properties_file = os.path.join(rsm_dir, "conf", "sandag_abm.properties")
input_dir = os.path.join(rsm_dir, "input")
output_dir = os.path.join(rsm_dir, "output")

set_property(properties_file, 'acc.read.input.file', 'false')
set_property(properties_file, 'PopulationSynthesizer.InputToCTRAMP.HouseholdFile', 'input/sampled_households.csv')
set_property(properties_file, 'PopulationSynthesizer.InputToCTRAMP.PersonFile', 'input/sampled_person.csv')

if iteration == 1: 
    # modifies the sandag_abm.properties file to run the shadow pricing in first iteration
    set_property(properties_file, 'UsualWorkLocationChoice.ShadowPrice.Input.File', '')
    set_property(properties_file, 'UsualSchoolLocationChoice.ShadowPrice.Input.File', '')
    set_property(properties_file, 'uwsl.ShadowPricing.Work.MaximumIterations', 10)
    set_property(properties_file, 'uwsl.ShadowPricing.School.MaximumIterations', 10)
else: 
    work_file, sch_file = get_shadow_pricing_files(output_dir)

    copy_file(
        os.path.join(output_dir, work_file), os.path.join(input_dir, work_file)
    )

    copy_file(
        os.path.join(output_dir, sch_file), os.path.join(input_dir, sch_file)
    )

    # modifies the sandag_abm.properties file to reflect the shadow pricing files
    set_property(properties_file, 'UsualWorkLocationChoice.ShadowPrice.Input.File', 'input/' + work_file)
    set_property(properties_file, 'UsualSchoolLocationChoice.ShadowPrice.Input.File', 'input/' + sch_file)
    set_property(properties_file, 'uwsl.ShadowPricing.Work.MaximumIterations', 1)
    set_property(properties_file, 'uwsl.ShadowPricing.School.MaximumIterations', 1)