rem ##### Zone Aggregator #####

set INPUT_DIR=%1

docker run -v %cd%:/home/mambauser/sandag_rsm -w /home/mambauser/sandag_rsm sandag_rsm python rsm_zone_aggregator.py INPUT_DIR

