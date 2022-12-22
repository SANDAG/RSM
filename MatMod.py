import openmatrix as omx
import os
import numpy as np




input_folder = r"T:\ABM\CS_Space\sandbox2-rsmMY2016\GitHub\trips"
output_folder = r"T:\ABM\CS_Space\sandbox2-rsmMY2016\GitHub\trips2"
files = os.listdir(input_folder)


for file in files:
    input_skim_file = os.path.join(input_folder, file) 
    print(input_skim_file)

    input_matrix = omx.open_file(input_skim_file, mode="r")
    #input_mapping_name = input_matrix.list_mappings()[0]
    input_cores = input_matrix.list_matrices()

    output_skim_file = os.path.join(output_folder, file) 
    output_matrix = omx.open_file(output_skim_file, mode="w")

    for core in input_cores:
        print(core)
        if file == 'autoTrips_AM_low.omx' and core == 'SOVNOTRPDR_AM':
            matrix = input_matrix[core]
            print(core + " multiplying by 1 " + str(np.array(matrix).sum()))
            matrix_mod = np.array(matrix)
            print(core + " multiplying by 1 " + str(np.array(matrix).sum()))
            output_matrix[core] = matrix_mod

        else : 
            matrix = input_matrix[core]
            print(core +  " multiplying by 0 " + str(np.array(matrix).sum()))
            matrix_mod = np.array(matrix) * 0
            print(core +  " multiplying by 0 " + str(np.array(matrix).sum()))
            output_matrix[core] = matrix_mod

    input_matrix.close()
    output_matrix.close()








