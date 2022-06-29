import os
import inro.emme.database.emmebank as _eb
import inro.modeller as _m


def load_matrix_emme(
        skims_file, emme_path
):
"""
SAMPLE CODE
_m = inro.modeller
NAMESPACE = "inro.emme.data.matrix.export_to_omx"
export_to_omx = _m.Modeller().tool(NAMESPACE)
emmebank_dir = os.path.dirname(_m.Modeller().emmebank.path)
omx_file = os.path.join(emmebank_dir, "exported_demand_matrices.omx")
export_to_omx(matrices=["mf1", "mf2"],
              export_file=omx_file,
              append_to_file=False)
"""



def save_matrix_emme(
        emme_path, matrix_name
):
"""
SAMPLE CODE
_m = inro.modeller
NAMESPACE = "inro.emme.data.matrix.create_matrix"
create_matrix = _m.Modeller().tool(NAMESPACE)
new_mat = create_matrix(matrix_id="mf13",
                        matrix_name="diftrt",
                        matrix_description="transit time difference",
                        default_value=0)



