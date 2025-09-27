#!/bin/bash -
#===============================================================================
#
#          FILE: Run pvgis-prototype example/s
#
#
#   DESCRIPTION: Run pvgis-prototype examples with minimal repetition.
#
# 		 - NOTE : run me AT YOUR OWN RISK like this : `./run_power_example.sh` 
#
#  REQUIREMENTS: bash, pvgis-prototype
#
#         To Do: Test! It works for me.-
#
#        AUTHOR: Nikos Alexandris
#  ORGANIZATION: Project Officer, PVGIS, C2, JRC, EC
#
#       CREATED: Sat 23 Mar 2024 10:12:05 EET
#      REVISION: Tue 02 Apr 2024 02:24:00 EET | See git commit logs
#===============================================================================

set -uo pipefail
set -o nounset  # Treat unset variables as an error


# Constants

LOGFILE="run_log.txt"
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")
BASE_COMMAND=(
    pvgis-prototype
)
LOCATION=(
    ' -14' 8 214  # Coordinates and elevation
)
LOCATION_2=(
    ' -14' 8 214  90 # Coordinates, elevation and orientation
    ' -14' 8 214  90 0.1 # Coordinates, elevation, orientation and tilt
)
TIMESTAMPS=(
    --start-time '2005-01-01'
    --end-time '2020-12-31'
)
COMMON_PARAMETERS=(
    --quiet
)

# Data

GLOBAL_HORIZONTAL_IRRADIANCE=sarah2_sis_over_esti_jrc.nc
DIRECT_HORIZONTAL_IRRADIANCE=sarah2_sid_over_esti_jrc.nc
TEMPERATURE_SERIES=era5_t2m_over_esti_jrc.nc
WIND_SPEED_SERIES=era5_ws2m_over_esti_jrc.nc
SPECTRAL_FATOR_SERIES=gitignore/spectraleffect_maps/spectral_effect_cSi_2013_x.nc

# Options

POWER_OPTIONS=(
    "--fingerprint"
    "--fingerprint --metadata"
    "--fingerprint --uniplot"
    "--fingerprint --statistics"
    "--fingerprint --timezone 'Europe/Athens'"
    "--fingerprint --dtype float64"
    "--fingerprint --multi-thread"
    "--fingerprint --no-apply-atmospheric-refraction"
    "--fingerprint --no-apply-reflectivity-factor"
    # '--fingerprint --photovoltaic-module "cSi:Integrated"'
    # '--fingerprint --photovoltaic-module "Old cSi:Free standing"'
    # '--fingerprint --photovoltaic-module "Old cSi:Integrated"'
    # '--fingerprint --photovoltaic-module "CIS:Free standing"'
    # '--fingerprint --photovoltaic-module "CIS:Integrated"'
    # '--fingerprint --photovoltaic-module "CdTe:Free standing"'
    # '--fingerprint --photovoltaic-module "CdTe:Integrated"'
    "--fingerprint --system-efficiency-factor 0.5"
    "--fingerprint --power-model None"
    "--fingerprint --power-model IV"
    "--fingerprint --temperature-model None"
    "--fingerprint --efficiency-factor 0.75"
    "--statistics --rounding-places 2"
    "--statistics --groupby Y"
    "--statistics --groupby monthly"
)
IRRADIANCE_OPTIONS=(
    "--fingerprint"
    "--fingerprint --metadata"
    "--fingerprint --uniplot"
    "--fingerprint --statistics"
)


# Helpers

log() {
    # echo "$TIMESTAMP - $1" | tee -a "$LOGFILE"
    echo "$TIMESTAMP - $1" >> "$LOGFILE"  # log only command
}
log_result() {
    local message=$1
    echo "$message" >> "$LOGFILE"
}
run_command() {
    local -n base_cmd=$1
    shift  # Removing the first argument which is the name of the base command array
    local options=("$@")  # Additional options passed to the function

    # log "Testing : ${BASE_COMMAND[@]} with ${options[@]}"

    for option in "${options[@]}"; do
        local command_and_option="${base_cmd[*]} $option"
        echo "> Running : $command_and_option"
        log "> Running : $command_and_option"

        # Run command, preserve colors using FORCE_COLOR
        export FORCE_COLOR=1
        # time "${base_cmd[@]}" $option 2>&1 | tee -a "$LOGFILE"
        # time "${base_cmd[@]}" $option >/dev/null 2>&1
        { time "${base_cmd[@]}" $option 2>&1; } | tee /dev/tty > /dev/null  # Output to terminal only
        local exit_code=$?

        # ANSI color codes for redm green and reset
        RED='\033[0;31m'
        GREEN='\033[0;32m'
        NC='\033[0m'  # No Color (reset)

        # Log success or failure
        if [ $exit_code -eq 0 ]; then
            echo -e "  + ${GREEN}OK${NC}"
            log "  + OK"
        else
            echo -e "  - ${RED}Failed${NC} : Exit code: $exit_code"
            log "  - FAILED : Exit code: $exit_code"
        fi
        echo -e "\n\n"  # Adding extra newlines for spacing
    done
}


POWER_BROADBAND=(
    "${BASE_COMMAND[@]}"
    power broadband
    "${LOCATION[@]}"
    "${TIMESTAMPS[@]}"
    "${COMMON_PARAMETERS[@]}"
    --neighbor-lookup nearest
)
IRRADIANCE=(
    "${BASE_COMMAND[@]}"
    irradiance
    # "${LOCATION[@]}"
    # "${TIMESTAMPS[@]}"
    # "${COMMON_PARAMETERS[@]}"
)
POWER_BROADBAND_WITH_GLOBAL=(
    "${POWER_BROADBAND[@]}"
    --global-horizontal-irradiance $GLOBAL_HORIZONTAL_IRRADIANCE
)
POWER_BROADBAND_WITH_DIRECT=(
    "${POWER_BROADBAND[@]}"
    --direct-horizontal-irradiance $DIRECT_HORIZONTAL_IRRADIANCE
)
POWER_BROADBAND_WITH_TEMP_WIND=(
    "${POWER_BROADBAND[@]}"
    --temperature-series $TEMPERATURE_SERIES
    --wind-speed-series $WIND_SPEED_SERIES
)
POWER_BROADBAND_WITH_SARAH3_GLOBAL=(
    "${POWER_BROADBAND[@]}"
    --global-horizontal-irradiance $GLOBAL_HORIZONTAL_IRRADIANCE
)
POWER_BROADBAND_WITH_SARAH3_DIRECT=(
    "${POWER_BROADBAND[@]}"
    --direct-horizontal-irradiance $DIRECT_HORIZONTAL_IRRADIANCE
)
POWER_BROADBAND_WITH_SARAH3_GLOBAL_DIRECT=(
    "${POWER_BROADBAND[@]}"
    --global-horizontal-irradiance $GLOBAL_HORIZONTAL_IRRADIANCE
    --direct-horizontal-irradiance $DIRECT_HORIZONTAL_IRRADIANCE
)
POWER_BROADBAND_WITH_SARAH3_GLOBAL_DIRECT_ERA5_T2M=(
    "${POWER_BROADBAND[@]}"
    --global-horizontal-irradiance $GLOBAL_HORIZONTAL_IRRADIANCE
    --direct-horizontal-irradiance $DIRECT_HORIZONTAL_IRRADIANCE
    --temperature-series $TEMPERATURE_SERIES
)
POWER_BROADBAND_WITH_SARAH3_GLOBAL_DIRECT_ERA5_WINDSPEED=(
    "${POWER_BROADBAND[@]}"
    --global-horizontal-irradiance $GLOBAL_HORIZONTAL_IRRADIANCE
    --direct-horizontal-irradiance $DIRECT_HORIZONTAL_IRRADIANCE
    --wind-speed-series $WIND_SPEED_SERIES
)
POWER_BROADBAND_WITH_SARAH3_GLOBAL_DIRECT_ERA5_T2M_WINDSPEED=(
    "${POWER_BROADBAND[@]}"
    --global-horizontal-irradiance $GLOBAL_HORIZONTAL_IRRADIANCE
    --direct-horizontal-irradiance $DIRECT_HORIZONTAL_IRRADIANCE
    --temperature-series $TEMPERATURE_SERIES
    --wind-speed-series $WIND_SPEED_SERIES
)
POWER_BROADBAND_WITH_SARAH3_GLOBAL_DIRECT_ERA5_T2M_WINDSPEED_SPECTRAL_FACTOR=(
    "${POWER_BROADBAND[@]}"
    --global-horizontal-irradiance $GLOBAL_HORIZONTAL_IRRADIANCE
    --direct-horizontal-irradiance $DIRECT_HORIZONTAL_IRRADIANCE
    --temperature-series $TEMPERATURE_SERIES
    --wind-speed-series $WIND_SPEED_SERIES
    --spectral-factor-series $SPECTRAL_FATOR_SERIES

)
IRRADIANCE_GLOBAL=(
    "${IRRADIANCE[@]}"
    global
    # "${LOCATION[@]}"
    # "${TIMESTAMPS[@]}"
    # "${COMMON_PARAMETERS[@]}"
)
IRRADIANCE_GLOBAL_HORIZONTAL=(
    "${IRRADIANCE_GLOBAL[@]}"
    horizontal
    "${LOCATION[@]}"
    "${TIMESTAMPS[@]}"
    "${COMMON_PARAMETERS[@]}"
)
IRRADIANCE_GLOBAL_INCLINED=(
    "${IRRADIANCE_GLOBAL[@]}"
    inclined
    "${LOCATION[@]}"
    "${TIMESTAMPS[@]}"
    "${COMMON_PARAMETERS[@]}"
)
IRRADIANCE_DIRECT=(
    "${IRRADIANCE[@]}"
    direct
)
IRRADIANCE_DIRECT_NORMAL=(
    "${IRRADIANCE_DIRECT[@]}"
    normal
    "${LOCATION[@]}"
    "${TIMESTAMPS[@]}"
    "${COMMON_PARAMETERS[@]}"
)
IRRADIANCE_DIRECT_HORIZONTAL=(
    "${IRRADIANCE_DIRECT[@]}"
    horizontal
    "${LOCATION[@]}"
    "${TIMESTAMPS[@]}"
    "${COMMON_PARAMETERS[@]}"
)
IRRADIANCE_DIRECT_INCLINED=(
    "${IRRADIANCE_DIRECT[@]}"
    inclined
    "${LOCATION[@]}"
    "${TIMESTAMPS[@]}"
    "${COMMON_PARAMETERS[@]}"
)
IRRADIANCE_DIFFUSE=(
    "${IRRADIANCE[@]}"
    diffuse
)
IRRADIANCE_DIFFUSE_HORIZONTAL=(
    "${IRRADIANCE_DIFFUSE[@]}"
    horizontal
    "${LOCATION[@]}"
    "${TIMESTAMPS[@]}"
    "${COMMON_PARAMETERS[@]}"
)
IRRADIANCE_DIFFUSE_FROM_SARAH=(
    "${IRRADIANCE_DIFFUSE[@]}"
    from-global-and-direct-irradiance
    $GLOBAL_HORIZONTAL_IRRADIANCE  # shortwave
    $DIRECT_HORIZONTAL_IRRADIANCE
    "${LOCATION[@]}"
    "${TIMESTAMPS[@]}"
    "${COMMON_PARAMETERS[@]}"
)
IRRADIANCE_REFLECTED=(
    "${IRRADIANCE[@]}"
    reflected
)
IRRADIANCE_REFLECTED_INCLINED=(
    "${IRRADIANCE_REFLECTED[@]}"
    reflected inclined
    "${LOCATION[@]}"
    "${TIMESTAMPS[@]}"
    "${COMMON_PARAMETERS[@]}"
)


# Run commands

run_command POWER_BROADBAND "${POWER_OPTIONS[@]}"
run_command POWER_BROADBAND_WITH_GLOBAL "${POWER_OPTIONS[@]}"
run_command POWER_BROADBAND_WITH_DIRECT_DIFFUSE "${POWER_OPTIONS[@]}"
run_command POWER_BROADBAND_WITH_TEMP_WIND "${POWER_OPTIONS[@]}"

# run_command IRRADIANCE "${IRRADIANCE_OPTIONS[@]}"

# run_command IRRADIANCE_GLOBAL "${IRRADIANCE_OPTIONS[@]}"
run_command IRRADIANCE_GLOBAL_HORIZONTAL "${IRRADIANCE_OPTIONS[@]}"
run_command IRRADIANCE_GLOBAL_INCLINED "${IRRADIANCE_OPTIONS[@]}"

# run_command IRRADIANCE_DIRECT "${IRRADIANCE_OPTIONS[@]}"
run_command IRRADIANCE_DIRECT_NORMAL "${IRRADIANCE_OPTIONS[@]}"
run_command IRRADIANCE_DIRECT_HORIZONTAL "${IRRADIANCE_OPTIONS[@]}"
run_command IRRADIANCE_DIRECT_INCLINED "${IRRADIANCE_OPTIONS[@]}"

# run_command IRRADIANCE_DIFFUSE "${IRRADIANCE_OPTIONS[@]}"
run_command IRRADIANCE_DIFFUSE_HORIZONTAL "${IRRADIANCE_OPTIONS[@]}"
run_command IRRADIANCE_DIFFUSE_FROM_SARAH "${IRRADIANCE_OPTIONS[@]}"

# run_command IRRADIANCE_REFLECTED "${IRRADIANCE_OPTIONS[@]}"
run_command IRRADIANCE_REFLECTED_INCLINED "${IRRADIANCE_OPTIONS[@]}"
