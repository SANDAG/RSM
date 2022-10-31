rem ##### Input and UEC files Aggregator #####

set ORG_MODEL_DIR=%1
set RSM_MODEL_DIR=%2

docker run -v %cd%:/home/mambauser/sandag_rsm -w /home/mambauser/sandag_rsm sandag_rsm python rsm_input_aggregator.py ORG_MODEL_DIR RSM_MODEL_DIR
