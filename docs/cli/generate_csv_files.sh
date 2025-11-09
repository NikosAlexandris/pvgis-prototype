#!bash
# Generate CSV files for examples in docs/cli

pvgis-prototype power broadband \
7.9672 45.9684 2000 180 33 \
--start-time '2010-06-01 04:00:00' \
--end-time '2010-06-01 19:00:00' \
-v \
--csv power_broadband_example.csv

pvgis-prototype power broadband \
7.9672 45.9684 2000 180 33 \
--start-time '2010-06-01 04:00:00' \
--end-time '2010-06-01 19:00:00' \
-vvv \
--csv power_broadband_example_vvv.csv

pvgis-prototype power broadband \
7.9672 45.9684 2000 180 33 \
--start-time '2010-06-01 04:00:00' \
--end-time '2010-06-01 19:00:00' \
-vvv \
--csv power_broadband_example_vvv.csv \
--fingerprint

pvgis-prototype performance broadband \
    8.628 45.812 214 180 44 \
    --start-time '2010-01-01' \
    --end-time '2010-12-31' \
    -aou degrees \
    --csv performance_broadband_example.csv

pvgis-prototype performance broadband \
    8.628 45.812 214 180 44 \
    --start-time '2010-01-01' \
    --end-time '2010-12-31' \
    --global-horizontal-irradiance ../../sarah2_sis_over_esti_jrc.nc \
    --direct-horizontal-irradiance ../../sarah2_sid_over_esti_jrc.nc \
    --spectral-factor-series ../../spectral_effect_cSi_over_esti_jrc.nc \
    --temperature-series ../../era5_t2m_over_esti_jrc.nc \
    --wind-speed-series ../../era5_ws2m_over_esti_jrc.nc \
    --neighbor-lookup nearest \
    -aou degrees \
    --csv performance_broadband_example_with_real_data.csv

pvgis-prototype position overview \
8.610 45.815 \
--start-time 2010-01-01 \
--end-time "2010-12-31 23:00:00" \
--rounding-places 2 \
--quiet \
--csv pvgis6_solar_position_overview_8.610_45.815_2010.csv
