import numpy
from devtools import debug
from pandas import DatetimeIndex, Timestamp
from pvgisprototype.web_api.schemas import AnalysisLevel, Frequency
from pvgisprototype.api.performance.analysis import analyse_photovoltaic_performance
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    EFFECT_PERCENTAGE_COLUMN_NAME,
    EFFECTIVE_IRRADIANCE_COLUMN_NAME,
    EFFECTIVE_IRRADIANCE_NAME,
    ELEVATION_COLUMN_NAME,
    ENERGY_NAME_WITH_SYMBOL,
    GLOBAL_IN_PLANE_IRRADIANCE_AFTER_REFLECTIVITY_COLUMN_NAME,
    GLOBAL_IN_PLANE_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME,
    IN_PLANE_IRRADIANCE,
    IRRADIANCE_AFTER_REFLECTIVITY,
    LATITUDE_COLUMN_NAME,
    LONGITUDE_COLUMN_NAME,
    MEAN_EFFECT_COLUMN_NAME,
    MEAN_EFFECTIVE_IRRADIANCE_COLUMN_NAME,
    MEAN_GLOBAL_IN_PLANE_IRRADIANCE_AFTER_REFLECTIVITY_COLUMN_NAME,
    MEAN_GLOBAL_IN_PLANE_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME,
    MEAN_PHOTOVOLTAIC_ENERGY_COLUMN_NAME,
    MEAN_PHOTOVOLTAIC_POWER_COLUMN_NAME,
    MEAN_PHOTOVOLTAIC_POWER_WITHOUT_SYSTEM_LOSS_COLUMN_NAME,
    MEAN_REFLECTIVITY_EFFECT_COLUMN_NAME,
    MEAN_SPECTRAL_EFFECT_COLUMN_NAME,
    MEAN_SYSTEM_EFFICIENCY_EFFECT_COLUMN_NAME,
    MEAN_TEMPERATURE_AND_LOW_IRRADIANCE_EFFECT_COLUMN_NAME,
    NET_EFFECT,
    PEAK_POWER_COLUMN_NAME,
    PHOTOVOLTAIC_ENERGY_COLUMN_NAME,
    PHOTOVOLTAIC_POWER_COLUMN_NAME,
    PHOTOVOLTAIC_POWER_WITHOUT_SYSTEM_LOSS_COLUMN_NAME,
    POWER_NAME_WITH_SYMBOL,
    RADIANS,
    REFLECTIVITY,
    REFLECTIVITY_COLUMN_NAME,
    REFLECTIVITY_EFFECT_PERCENTAGE_COLUMN_NAME,
    ROUNDING_PLACES_DEFAULT,
    SPECTRAL_EFFECT_COLUMN_NAME,
    SPECTRAL_EFFECT_NAME,
    SPECTRAL_EFFECT_PERCENTAGE_COLUMN_NAME,
    STANDARD_DEVIATION_GLOBAL_IN_PLANE_IRRADIANCE_COLUMN_NAME,
    STANDARD_DEVIATION_PHOTOVOLTAIC_POWER_COLUMN_NAME,
    STANDARD_DEVIATION_PHOTOVOLTAIC_POWER_WITHOUT_SYSTEM_LOSS_COLUMN_NAME,
    STANDARD_DEVIATION_REFLECTIVITY_EFFECT_COLUMN_NAME,
    STANDARD_DEVIATION_SPECTRAL_EFFECT_COLUMN_NAME,
    SURFACE_ORIENTATION_COLUMN_NAME,
    SURFACE_TILT_COLUMN_NAME,
    SYSTEM_EFFICIENCY_EFFECT_PERCENTAGE_COLUMN_NAME,
    SYSTEM_LOSS,
    TECHNOLOGY_NAME,
    TEMPERATURE_AND_LOW_IRRADIANCE_COLUMN_NAME,
    TEMPERATURE_AND_LOW_IRRADIANCE_EFFECT_PERCENTAGE_COLUMN_NAME,
    TOTAL_EFFECT_COLUMN_NAME,
    TOTAL_GLOBAL_IN_PLANE_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME,
    TOTAL_PHOTOVOLTAIC_POWER_COLUMN_NAME,
    TOTAL_PHOTOVOLTAIC_POWER_WITHOUT_SYSTEM_LOSS_COLUMN_NAME,
    TOTAL_REFLECTIVITY_EFFECT_COLUMN_NAME,
    TOTAL_SPECTRAL_EFFECT_COLUMN_NAME,
    TOTAL_SYSTEM_EFFICIENCY_EFFECT_COLUMN_NAME,
    TOTAL_TEMPERATURE_AND_LOW_IRRADIANCE_EFFECT_COLUMN_NAME,
    UNIT_FOR_EFFECTIVE_IRRADIANCE_COLUMN_NAME,
    UNIT_FOR_GLOBAL_IN_PLANE_IRRADIANCE_AFTER_REFLECTIVITY_COLUMN_NAME,
    UNIT_FOR_MEAN_EFFECT_COLUMN_NAME,
    UNIT_FOR_MEAN_EFFECTIVE_IRRADIANCE_COLUMN_NAME,
    UNIT_FOR_MEAN_GLOBAL_IN_PLANE_IRRADIANCE_AFTER_REFLECTIVITY_COLUMN_NAME,
    UNIT_FOR_MEAN_GLOBAL_IN_PLANE_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME,
    UNIT_FOR_MEAN_PHOTOVOLTAIC_ENERGY_COLUMN_NAME,
    UNIT_FOR_MEAN_PHOTOVOLTAIC_POWER_COLUMN_NAME,
    UNIT_FOR_MEAN_PHOTOVOLTAIC_POWER_WITHOUT_SYSTEM_LOSS_COLUMN_NAME,
    UNIT_FOR_MEAN_REFLECTIVITY_EFFECT_COLUMN_NAME,
    UNIT_FOR_MEAN_SPECTRAL_EFFECT_COLUMN_NAME,
    UNIT_FOR_MEAN_SYSTEM_EFFICIENCY_EFFECT_COLUMN_NAME,
    UNIT_FOR_MEAN_TEMPERATURE_AND_LOW_IRRADIANCE_EFFECT_COLUMN_NAME,
    UNIT_FOR_PHOTOVOLTAIC_ENERGY_COLUMN_NAME,
    UNIT_FOR_TEMPERATURE_AND_LOW_IRRADIANCE_EFFECT_COLUMN_NAME,
    UNIT_FOR_TOTAL_EFFECT_COLUMN_NAME,
    UNIT_FOR_TOTAL_GLOBAL_IN_PLANE_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME,
    UNIT_FOR_TOTAL_PHOTOVOLTAIC_POWER_COLUMN_NAME,
    UNIT_FOR_TOTAL_PHOTOVOLTAIC_POWER_WITHOUT_SYSTEM_LOSS_COLUMN_NAME,
    UNIT_FOR_TOTAL_REFLECTIVITY_EFFECT_COLUMN_NAME,
    UNIT_FOR_TOTAL_SPECTRAL_EFFECT_COLUMN_NAME,
    UNIT_FOR_TOTAL_SYSTEM_EFFICIENCY_EFFECT_COLUMN_NAME,
    VERBOSE_LEVEL_DEFAULT,
)


def summarise_photovoltaic_performance(
    dictionary: dict,
    longitude,
    latitude,
    elevation,
    # surface_orientation: bool = True,
    # surface_tilt: bool = True,
    timestamps: DatetimeIndex | Timestamp,
    frequency: Frequency = Frequency.Hourly,
    analysis: AnalysisLevel = AnalysisLevel.Simple,
    angle_output_units: str = RADIANS,
    rounding_places: int = ROUNDING_PLACES_DEFAULT,
    dtype: str = DATA_TYPE_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
):
    """
    Generate a simplified report for photovoltaic performance, focusing only on quantities and their values.
    """
    from pvgisprototype.api.utilities.conversions import round_float_values

    latitude = round_float_values(
        latitude, rounding_places
    )
    # position_table.add_row(f"{LATITUDE_NAME}", f"[bold]{latitude}[/bold]")
    longitude = round_float_values(
        longitude, rounding_places
    )
    # surface_orientation = (
    #     dictionary.get(SURFACE_ORIENTATION_COLUMN_NAME, None)
    #     if surface_orientation
    #     else None
    # )
    # surface_orientation = round_float_values(
    #     surface_orientation, rounding_places
    # )
    # surface_tilt = (
    #     dictionary.get(SURFACE_TILT_COLUMN_NAME, None) if surface_tilt else None
    # )
    # surface_tilt = round_float_values(surface_tilt, rounding_places)

    photovoltaic_performance_analysis = analyse_photovoltaic_performance(
        dictionary=dictionary,
        timestamps=timestamps,
        frequency=frequency,
        rounding_places=rounding_places,
        dtype=dtype,
        array_backend=ARRAY_BACKEND_DEFAULT,
        verbose=verbose,
    )
    from devtools import debug
    debug(locals())
    photovoltaic_module, mount_type = dictionary.technology.split(":")
    peak_power = photovoltaic_performance_analysis.get(PEAK_POWER_COLUMN_NAME, None)

    def get_value(value_key, unit_key, default=None):
        value = photovoltaic_performance_analysis.get(value_key, default)
        unit = photovoltaic_performance_analysis.get(unit_key, default)
        return {"value": value, "unit": unit}

    # longitude = convert_float_to_degrees_if_requested(longitude, angle_output_units)
    # latitude = convert_float_to_degrees_if_requested(latitude, angle_output_units)
    # surface_orientation = convert_float_to_degrees_if_requested(surface_orientation, angle_output_units)
    # surface_tilt = convert_float_to_degrees_if_requested(surface_tilt, angle_output_units)

    performance_analysis_container = {
        "Location & Position": lambda: {
            LATITUDE_COLUMN_NAME: {"value": latitude, "unit": angle_output_units},
            LONGITUDE_COLUMN_NAME: {"value": longitude, "unit": angle_output_units},
            ELEVATION_COLUMN_NAME: {"value": elevation, "unit": "meters"},
            # SURFACE_ORIENTATION_COLUMN_NAME: {
            #     "value": surface_orientation,
            #     "unit": angle_output_units,
            # },
            # SURFACE_TILT_COLUMN_NAME: {"value": surface_tilt, "unit": angle_output_units},
            "Start time": str(timestamps[0].strftime("%Y-%m-%d %H:%M")),
            "End time": str(timestamps[-1].strftime("%Y-%m-%d %H:%M")),
            "Frequency": frequency,
        },
        "Minimal": lambda: (
            {
                PHOTOVOLTAIC_ENERGY_COLUMN_NAME: get_value(
                    PHOTOVOLTAIC_ENERGY_COLUMN_NAME,
                    UNIT_FOR_PHOTOVOLTAIC_ENERGY_COLUMN_NAME,
                ),
                TECHNOLOGY_NAME: photovoltaic_module,
                PEAK_POWER_COLUMN_NAME: peak_power,
                "Mount type": mount_type,
            }
            if analysis.value == AnalysisLevel.Minimal
            else {}
        ),
        "Simple": lambda: (
            {
                TOTAL_GLOBAL_IN_PLANE_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME: get_value(
                    TOTAL_GLOBAL_IN_PLANE_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME,
                    UNIT_FOR_TOTAL_GLOBAL_IN_PLANE_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME,
                ),
                PHOTOVOLTAIC_ENERGY_COLUMN_NAME: get_value(
                    PHOTOVOLTAIC_ENERGY_COLUMN_NAME,
                    UNIT_FOR_PHOTOVOLTAIC_ENERGY_COLUMN_NAME,
                ),
                TOTAL_EFFECT_COLUMN_NAME: get_value(
                    TOTAL_EFFECT_COLUMN_NAME,
                    UNIT_FOR_TOTAL_EFFECT_COLUMN_NAME,
                ),
                TECHNOLOGY_NAME: photovoltaic_module,
                PEAK_POWER_COLUMN_NAME: peak_power,
                "Mount type": mount_type,
            }
            if analysis.value == AnalysisLevel.Simple
            else {}
        ),
        "Advanced": lambda: (
            {
                TOTAL_GLOBAL_IN_PLANE_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME: get_value(
                    TOTAL_GLOBAL_IN_PLANE_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME,
                    UNIT_FOR_TOTAL_GLOBAL_IN_PLANE_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME,
                ),
                GLOBAL_IN_PLANE_IRRADIANCE_AFTER_REFLECTIVITY_COLUMN_NAME: get_value(
                    GLOBAL_IN_PLANE_IRRADIANCE_AFTER_REFLECTIVITY_COLUMN_NAME,
                    UNIT_FOR_MEAN_GLOBAL_IN_PLANE_IRRADIANCE_AFTER_REFLECTIVITY_COLUMN_NAME,
                ),
                EFFECTIVE_IRRADIANCE_COLUMN_NAME: get_value(
                    EFFECTIVE_IRRADIANCE_COLUMN_NAME,
                    UNIT_FOR_EFFECTIVE_IRRADIANCE_COLUMN_NAME,
                ),
                TOTAL_PHOTOVOLTAIC_POWER_WITHOUT_SYSTEM_LOSS_COLUMN_NAME: get_value(
                    TOTAL_PHOTOVOLTAIC_POWER_WITHOUT_SYSTEM_LOSS_COLUMN_NAME,
                    UNIT_FOR_TOTAL_PHOTOVOLTAIC_POWER_WITHOUT_SYSTEM_LOSS_COLUMN_NAME,
                ),
                TOTAL_PHOTOVOLTAIC_POWER_COLUMN_NAME: get_value(
                    TOTAL_PHOTOVOLTAIC_POWER_COLUMN_NAME,
                    UNIT_FOR_TOTAL_PHOTOVOLTAIC_POWER_COLUMN_NAME,
                ),
                PHOTOVOLTAIC_ENERGY_COLUMN_NAME: get_value(
                    PHOTOVOLTAIC_ENERGY_COLUMN_NAME,
                    UNIT_FOR_PHOTOVOLTAIC_ENERGY_COLUMN_NAME,
                ),
                TOTAL_EFFECT_COLUMN_NAME: get_value(
                    TOTAL_EFFECT_COLUMN_NAME,
                    UNIT_FOR_TOTAL_EFFECT_COLUMN_NAME,
                ),
                TECHNOLOGY_NAME: photovoltaic_module,
                PEAK_POWER_COLUMN_NAME: peak_power,
                "Mount type": mount_type,
            }
            if analysis.value == AnalysisLevel.Advanced
            else {}
        ),
        "Extended": lambda: (
            {
                TOTAL_GLOBAL_IN_PLANE_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME: get_value(
                    TOTAL_GLOBAL_IN_PLANE_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME,
                    UNIT_FOR_TOTAL_GLOBAL_IN_PLANE_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME,
                ),
                TOTAL_REFLECTIVITY_EFFECT_COLUMN_NAME: get_value(
                    TOTAL_REFLECTIVITY_EFFECT_COLUMN_NAME,
                    UNIT_FOR_TOTAL_REFLECTIVITY_EFFECT_COLUMN_NAME,
                ),
                GLOBAL_IN_PLANE_IRRADIANCE_AFTER_REFLECTIVITY_COLUMN_NAME: get_value(
                    GLOBAL_IN_PLANE_IRRADIANCE_AFTER_REFLECTIVITY_COLUMN_NAME,
                    UNIT_FOR_MEAN_GLOBAL_IN_PLANE_IRRADIANCE_AFTER_REFLECTIVITY_COLUMN_NAME,
                ),
                TOTAL_SPECTRAL_EFFECT_COLUMN_NAME: get_value(
                    TOTAL_SPECTRAL_EFFECT_COLUMN_NAME,
                    UNIT_FOR_TOTAL_SPECTRAL_EFFECT_COLUMN_NAME,
                ),
                EFFECTIVE_IRRADIANCE_COLUMN_NAME: get_value(
                    EFFECTIVE_IRRADIANCE_COLUMN_NAME,
                    UNIT_FOR_EFFECTIVE_IRRADIANCE_COLUMN_NAME,
                ),
                TOTAL_TEMPERATURE_AND_LOW_IRRADIANCE_EFFECT_COLUMN_NAME: get_value(
                    TOTAL_TEMPERATURE_AND_LOW_IRRADIANCE_EFFECT_COLUMN_NAME,
                    UNIT_FOR_TEMPERATURE_AND_LOW_IRRADIANCE_EFFECT_COLUMN_NAME,
                ),
                TOTAL_PHOTOVOLTAIC_POWER_WITHOUT_SYSTEM_LOSS_COLUMN_NAME: get_value(
                    TOTAL_PHOTOVOLTAIC_POWER_WITHOUT_SYSTEM_LOSS_COLUMN_NAME,
                    UNIT_FOR_TOTAL_PHOTOVOLTAIC_POWER_WITHOUT_SYSTEM_LOSS_COLUMN_NAME,
                ),
                TOTAL_SYSTEM_EFFICIENCY_EFFECT_COLUMN_NAME: get_value(
                    TOTAL_SYSTEM_EFFICIENCY_EFFECT_COLUMN_NAME,
                    UNIT_FOR_TOTAL_SYSTEM_EFFICIENCY_EFFECT_COLUMN_NAME,
                ),
                TOTAL_PHOTOVOLTAIC_POWER_COLUMN_NAME: get_value(
                    TOTAL_PHOTOVOLTAIC_POWER_COLUMN_NAME,
                    UNIT_FOR_TOTAL_PHOTOVOLTAIC_POWER_COLUMN_NAME,
                ),
                PHOTOVOLTAIC_ENERGY_COLUMN_NAME: get_value(
                    PHOTOVOLTAIC_ENERGY_COLUMN_NAME,
                    UNIT_FOR_PHOTOVOLTAIC_ENERGY_COLUMN_NAME,
                ),
                TOTAL_EFFECT_COLUMN_NAME: get_value(
                    TOTAL_EFFECT_COLUMN_NAME,
                    UNIT_FOR_TOTAL_EFFECT_COLUMN_NAME,
                ),
                TECHNOLOGY_NAME: photovoltaic_module,
                PEAK_POWER_COLUMN_NAME: peak_power,
                "Mount type": mount_type,
            }
            if analysis.value == AnalysisLevel.Extended
            else {}
        ),
    }
    performance_analysis = {}
    for _, level in performance_analysis_container.items():
        performance_analysis.update(level())

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    return performance_analysis
