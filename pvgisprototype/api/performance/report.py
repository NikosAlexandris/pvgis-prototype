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


def report_photovoltaic_performance(
    dictionary,
    timestamps: DatetimeIndex | Timestamp,
    frequency: str,
    rounding_places=1,
    dtype=DATA_TYPE_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
):
    """ """
    photovoltaic_performance_analysis = analyse_photovoltaic_performance(
        dictionary=dictionary,
        timestamps=timestamps,
        frequency=frequency,
        rounding_places=rounding_places,
        dtype=dtype,
        array_backend=ARRAY_BACKEND_DEFAULT,
        verbose=verbose,
    )

    inclined_irradiance = photovoltaic_performance_analysis.get(
        TOTAL_GLOBAL_IN_PLANE_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME, None
    )
    inclined_irradiance_unit = photovoltaic_performance_analysis.get(
        UNIT_FOR_TOTAL_GLOBAL_IN_PLANE_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME, None
    )
    inclined_irradiance_mean = photovoltaic_performance_analysis.get(
        MEAN_GLOBAL_IN_PLANE_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME, None
    )
    inclined_irradiance_mean_unit = photovoltaic_performance_analysis.get(
        UNIT_FOR_MEAN_GLOBAL_IN_PLANE_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME, None
    )
    inclined_irradiance_std = photovoltaic_performance_analysis.get(
        STANDARD_DEVIATION_GLOBAL_IN_PLANE_IRRADIANCE_COLUMN_NAME, None
    )
    inclined_irradiance_series = photovoltaic_performance_analysis.get(
        GLOBAL_IN_PLANE_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME, None
    )

    reflectivity_change = photovoltaic_performance_analysis.get(
        TOTAL_REFLECTIVITY_EFFECT_COLUMN_NAME, None
    )
    reflectivity_change_unit = photovoltaic_performance_analysis.get(
        UNIT_FOR_TOTAL_REFLECTIVITY_EFFECT_COLUMN_NAME, None
    )
    reflectivity_change_mean = photovoltaic_performance_analysis.get(
        MEAN_REFLECTIVITY_EFFECT_COLUMN_NAME, None
    )
    reflectivity_change_mean_unit = photovoltaic_performance_analysis.get(
        UNIT_FOR_MEAN_REFLECTIVITY_EFFECT_COLUMN_NAME, None
    )
    reflectivity_change_std = photovoltaic_performance_analysis.get(
        STANDARD_DEVIATION_REFLECTIVITY_EFFECT_COLUMN_NAME, None
    )
    reflectivity_change_percentage = photovoltaic_performance_analysis.get(
        REFLECTIVITY_EFFECT_PERCENTAGE_COLUMN_NAME, None
    )
    reflectivity_series = photovoltaic_performance_analysis.get(
        REFLECTIVITY_COLUMN_NAME, None
    )

    irradiance_after_reflectivity = photovoltaic_performance_analysis.get(
        GLOBAL_IN_PLANE_IRRADIANCE_AFTER_REFLECTIVITY_COLUMN_NAME, None
    )
    irradiance_after_reflectivity_unit = photovoltaic_performance_analysis.get(
        UNIT_FOR_GLOBAL_IN_PLANE_IRRADIANCE_AFTER_REFLECTIVITY_COLUMN_NAME, None
    )
    irradiance_after_reflectivity_mean = photovoltaic_performance_analysis.get(
        MEAN_GLOBAL_IN_PLANE_IRRADIANCE_AFTER_REFLECTIVITY_COLUMN_NAME, None
    )
    irradiance_after_reflectivity_mean_unit = photovoltaic_performance_analysis.get(
        UNIT_FOR_GLOBAL_IN_PLANE_IRRADIANCE_AFTER_REFLECTIVITY_COLUMN_NAME, None
    )

    spectral_effect = photovoltaic_performance_analysis.get(
        TOTAL_SPECTRAL_EFFECT_COLUMN_NAME, None
    )
    spectral_effect_unit = photovoltaic_performance_analysis.get(
        UNIT_FOR_TOTAL_SPECTRAL_EFFECT_COLUMN_NAME, None
    )
    spectral_effect_mean = photovoltaic_performance_analysis.get(
        MEAN_SPECTRAL_EFFECT_COLUMN_NAME, None
    )
    spectral_effect_mean_unit = photovoltaic_performance_analysis.get(
        UNIT_FOR_MEAN_SPECTRAL_EFFECT_COLUMN_NAME, None
    )
    spectral_effect_std = photovoltaic_performance_analysis.get(
        STANDARD_DEVIATION_SPECTRAL_EFFECT_COLUMN_NAME, None
    )
    spectral_effect_percentage = photovoltaic_performance_analysis.get(
        SPECTRAL_EFFECT_PERCENTAGE_COLUMN_NAME, None
    )
    spectral_effect_series = photovoltaic_performance_analysis.get(
        SPECTRAL_EFFECT_COLUMN_NAME, None
    )

    effective_irradiance = photovoltaic_performance_analysis.get(
        EFFECTIVE_IRRADIANCE_COLUMN_NAME, None
    )
    effective_irradiance_unit = photovoltaic_performance_analysis.get(
        UNIT_FOR_EFFECTIVE_IRRADIANCE_COLUMN_NAME, None
    )
    effective_irradiance_mean = photovoltaic_performance_analysis.get(
        MEAN_EFFECTIVE_IRRADIANCE_COLUMN_NAME, None
    )
    effective_irradiance_mean_unit = photovoltaic_performance_analysis.get(
        UNIT_FOR_MEAN_EFFECTIVE_IRRADIANCE_COLUMN_NAME, None
    )

    temperature_and_low_irradiance_change = photovoltaic_performance_analysis.get(
        TOTAL_TEMPERATURE_AND_LOW_IRRADIANCE_EFFECT_COLUMN_NAME, None
    )
    temperature_and_low_irradiance_change_unit = photovoltaic_performance_analysis.get(
        UNIT_FOR_TEMPERATURE_AND_LOW_IRRADIANCE_EFFECT_COLUMN_NAME, None
    )
    temperature_and_low_irradiance_change_mean = photovoltaic_performance_analysis.get(
        MEAN_TEMPERATURE_AND_LOW_IRRADIANCE_EFFECT_COLUMN_NAME, None
    )
    temperature_and_low_irradiance_change_mean_unit = (
        photovoltaic_performance_analysis.get(
            UNIT_FOR_MEAN_TEMPERATURE_AND_LOW_IRRADIANCE_EFFECT_COLUMN_NAME, None
        )
    )
    temperature_and_low_irradiance_change_percentage = (
        photovoltaic_performance_analysis.get(
            TEMPERATURE_AND_LOW_IRRADIANCE_EFFECT_PERCENTAGE_COLUMN_NAME, None
        )
    )

    photovoltaic_power_without_system_loss = photovoltaic_performance_analysis.get(
        TOTAL_PHOTOVOLTAIC_POWER_WITHOUT_SYSTEM_LOSS_COLUMN_NAME, None
    )
    photovoltaic_power_without_system_loss_unit = photovoltaic_performance_analysis.get(
        UNIT_FOR_TOTAL_PHOTOVOLTAIC_POWER_WITHOUT_SYSTEM_LOSS_COLUMN_NAME, None
    )
    photovoltaic_power_without_system_loss_mean = photovoltaic_performance_analysis.get(
        MEAN_PHOTOVOLTAIC_POWER_WITHOUT_SYSTEM_LOSS_COLUMN_NAME, None
    )
    photovoltaic_power_without_system_loss_mean_unit = (
        photovoltaic_performance_analysis.get(
            UNIT_FOR_MEAN_PHOTOVOLTAIC_POWER_WITHOUT_SYSTEM_LOSS_COLUMN_NAME, None
        )
    )
    photovoltaic_power_without_system_loss_std = photovoltaic_performance_analysis.get(
        STANDARD_DEVIATION_PHOTOVOLTAIC_POWER_WITHOUT_SYSTEM_LOSS_COLUMN_NAME, None
    )
    photovoltaic_power_without_system_loss_series = (
        photovoltaic_performance_analysis.get(
            PHOTOVOLTAIC_POWER_WITHOUT_SYSTEM_LOSS_COLUMN_NAME, None
        )
    )

    system_efficiency_change = photovoltaic_performance_analysis.get(
        TOTAL_SYSTEM_EFFICIENCY_EFFECT_COLUMN_NAME, None
    )
    system_efficiency_change_unit = photovoltaic_performance_analysis.get(
        UNIT_FOR_TOTAL_SYSTEM_EFFICIENCY_EFFECT_COLUMN_NAME, None
    )
    system_efficiency_change_mean = photovoltaic_performance_analysis.get(
        MEAN_SYSTEM_EFFICIENCY_EFFECT_COLUMN_NAME, None
    )
    system_efficiency_change_mean_unit = photovoltaic_performance_analysis.get(
        UNIT_FOR_MEAN_SYSTEM_EFFICIENCY_EFFECT_COLUMN_NAME, None
    )
    system_efficiency_change_percentage = photovoltaic_performance_analysis.get(
        SYSTEM_EFFICIENCY_EFFECT_PERCENTAGE_COLUMN_NAME, None
    )

    photovoltaic_power = photovoltaic_performance_analysis.get(
        TOTAL_PHOTOVOLTAIC_POWER_COLUMN_NAME, None
    )
    photovoltaic_power_unit = photovoltaic_performance_analysis.get(
        UNIT_FOR_TOTAL_PHOTOVOLTAIC_POWER_COLUMN_NAME, None
    )
    photovoltaic_power_mean = photovoltaic_performance_analysis.get(
        MEAN_PHOTOVOLTAIC_POWER_COLUMN_NAME, None
    )
    photovoltaic_power_mean_unit = photovoltaic_performance_analysis.get(
        UNIT_FOR_MEAN_PHOTOVOLTAIC_POWER_COLUMN_NAME, None
    )
    photovoltaic_power_std = photovoltaic_performance_analysis.get(
        STANDARD_DEVIATION_PHOTOVOLTAIC_POWER_COLUMN_NAME, None
    )
    photovoltaic_power_series = photovoltaic_performance_analysis.get(
        PHOTOVOLTAIC_POWER_COLUMN_NAME, None
    )

    photovoltaic_energy = photovoltaic_performance_analysis.get(
        PHOTOVOLTAIC_ENERGY_COLUMN_NAME, None
    )
    photovoltaic_energy_unit = photovoltaic_performance_analysis.get(
        UNIT_FOR_PHOTOVOLTAIC_ENERGY_COLUMN_NAME, None
    )
    photovoltaic_energy_mean = photovoltaic_performance_analysis.get(
        MEAN_PHOTOVOLTAIC_ENERGY_COLUMN_NAME, None
    )
    photovoltaic_energy_mean_unit = photovoltaic_performance_analysis.get(
        UNIT_FOR_MEAN_PHOTOVOLTAIC_ENERGY_COLUMN_NAME, None
    )

    total_change = photovoltaic_performance_analysis.get(TOTAL_EFFECT_COLUMN_NAME, None)
    total_change_unit = photovoltaic_performance_analysis.get(
        UNIT_FOR_TOTAL_EFFECT_COLUMN_NAME, None
    )
    total_change_mean = photovoltaic_performance_analysis.get(
        MEAN_EFFECT_COLUMN_NAME, None
    )
    total_change_mean_unit = photovoltaic_performance_analysis.get(
        UNIT_FOR_MEAN_EFFECT_COLUMN_NAME, None
    )
    total_change_percentage = photovoltaic_performance_analysis.get(
        EFFECT_PERCENTAGE_COLUMN_NAME, None
    )

    return {
        f"[bold purple]{IN_PLANE_IRRADIANCE}": (  # Label
            (inclined_irradiance, "bold purple"),  # Value, Style
            (inclined_irradiance_unit, "purple"),
            (inclined_irradiance_mean, "bold purple"),  # Mean Value, Style
            (inclined_irradiance_mean_unit, "purple"),
            inclined_irradiance_std,
            None,  # %
            "bold",  # Style for
            None,  # f"100 {GLOBAL_IRRADIANCE_NAME}",         # % of (which) Quantity
            inclined_irradiance_series,  # input series
            None,  # source
        ),
        f"{REFLECTIVITY}": (
            (reflectivity_change, "magenta"),
            (reflectivity_change_unit, "cyan dim"),
            (reflectivity_change_mean, "magenta"),
            (reflectivity_change_mean_unit, "cyan dim"),
            reflectivity_change_std,
            reflectivity_change_percentage,
            "bold",
            IN_PLANE_IRRADIANCE,
            reflectivity_series,
            None,
        ),
        f"[white dim]{IRRADIANCE_AFTER_REFLECTIVITY}": (
            (irradiance_after_reflectivity, "white dim"),
            (irradiance_after_reflectivity_unit, "white dim"),
            (irradiance_after_reflectivity_mean, "white dim"),
            (irradiance_after_reflectivity_mean_unit, "white dim"),
            None,
            None,
            "bold",
            IN_PLANE_IRRADIANCE,
            numpy.array([], dtype=dtype),
            None,
        ),
        f"{SPECTRAL_EFFECT_NAME}": (
            (spectral_effect, "magenta"),
            (spectral_effect_unit, "cyan dim"),
            (spectral_effect_mean, "magenta"),
            (spectral_effect_mean_unit, "cyan dim"),
            spectral_effect_std,
            spectral_effect_percentage,
            "bold",
            IN_PLANE_IRRADIANCE,
            spectral_effect_series,
            None,
        ),
        f"[white dim]{EFFECTIVE_IRRADIANCE_NAME}": (
            (effective_irradiance, "white dim"),
            (effective_irradiance_unit, "white dim"),
            (effective_irradiance_mean, "white dim"),
            (effective_irradiance_mean_unit, "white dim"),
            None,
            None,
            "bold",
            None,
            numpy.array([]),
            None,
        ),
        f"{TEMPERATURE_AND_LOW_IRRADIANCE_COLUMN_NAME}": (
            (temperature_and_low_irradiance_change, "magenta"),
            (temperature_and_low_irradiance_change_unit, "cyan dim"),
            (temperature_and_low_irradiance_change_mean, "magenta"),
            (temperature_and_low_irradiance_change_mean_unit, "cyan dim"),
            None,
            temperature_and_low_irradiance_change_percentage,
            "bold",
            EFFECTIVE_IRRADIANCE_NAME,
            numpy.array([]),
            None,
        ),
        f"[white dim]{PHOTOVOLTAIC_POWER_WITHOUT_SYSTEM_LOSS_COLUMN_NAME}": (
            (photovoltaic_power_without_system_loss, "white dim"),
            (photovoltaic_power_without_system_loss_unit, "white dim"),
            (photovoltaic_power_without_system_loss_mean, "white dim"),
            (photovoltaic_power_without_system_loss_mean_unit, "white dim"),
            photovoltaic_power_without_system_loss_std,
            None,
            "bold",
            EFFECTIVE_IRRADIANCE_NAME,
            photovoltaic_power_without_system_loss_series,
            None,
        ),
        f"{SYSTEM_LOSS}": (
            (system_efficiency_change, "magenta"),
            (system_efficiency_change_unit, "cyan dim"),
            (system_efficiency_change_mean, "magenta"),
            (system_efficiency_change_mean_unit, "cyan dim"),
            None,
            system_efficiency_change_percentage,
            "bold",
            PHOTOVOLTAIC_POWER_WITHOUT_SYSTEM_LOSS_COLUMN_NAME,
            numpy.array([]),
            None,
        ),
        f"[white dim]{POWER_NAME_WITH_SYMBOL}": (
            (photovoltaic_power, "white dim"),
            (photovoltaic_power_unit, "white dim"),
            (photovoltaic_power_mean, "white dim"),
            (photovoltaic_power_mean_unit, "white dim"),
            photovoltaic_power_std,
            None,
            "bold",
            EFFECTIVE_IRRADIANCE_NAME,
            photovoltaic_power_series,
            None,
        ),
        f"[green bold]{ENERGY_NAME_WITH_SYMBOL}": (
            (photovoltaic_energy, "green"),
            (photovoltaic_energy_unit, "green"),
            (photovoltaic_energy_mean, "bold green"),
            (photovoltaic_energy_mean_unit, "green"),
            None,
            None,
            "bold",
            EFFECTIVE_IRRADIANCE_NAME,
            numpy.array([]),
            None,
        ),
        f"[white dim]{NET_EFFECT}": (
            (total_change, "white dim"),
            (total_change_unit, "white dim"),
            (total_change_mean, "white dim"),
            (total_change_mean_unit, "white dim"),
            None,
            total_change_percentage,
            "dim",
            IN_PLANE_IRRADIANCE,
            numpy.array([]),
            None,
        ),
    }



def summarise_photovoltaic_performance(
    longitude=None,
    latitude=None,
    elevation=None,
    surface_orientation: bool = True,
    surface_tilt: bool = True,
    dictionary: dict = None,
    timestamps: DatetimeIndex | None = None,
    frequency: str = Frequency.Hourly,
    analysis: AnalysisLevel = AnalysisLevel.Simple,
    angle_output_units: str = RADIANS,
    rounding_places: int = ROUNDING_PLACES_DEFAULT,
    dtype=DATA_TYPE_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
):
    """
    Generate a simplified report for photovoltaic performance, focusing only on quantities and their values.
    """
    positioning_rounding_places = 3  # Review-Me !
    from pvgisprototype.api.utilities.conversions import round_float_values

    latitude = round_float_values(
        latitude, positioning_rounding_places
    )  # rounding_places)
    # position_table.add_row(f"{LATITUDE_NAME}", f"[bold]{latitude}[/bold]")
    longitude = round_float_values(
        longitude, positioning_rounding_places
    )  # rounding_places)
    surface_orientation = (
        dictionary.get(SURFACE_ORIENTATION_COLUMN_NAME, None)
        if surface_orientation
        else None
    )
    surface_orientation = round_float_values(
        surface_orientation, positioning_rounding_places
    )
    surface_tilt = (
        dictionary.get(SURFACE_TILT_COLUMN_NAME, None) if surface_tilt else None
    )
    surface_tilt = round_float_values(surface_tilt, positioning_rounding_places)

    photovoltaic_performance_analysis = analyse_photovoltaic_performance(
        dictionary=dictionary,
        timestamps=timestamps,
        frequency=frequency,
        rounding_places=rounding_places,
        dtype=dtype,
        array_backend=ARRAY_BACKEND_DEFAULT,
        verbose=verbose,
    )
    photovoltaic_module, mount_type = dictionary.get(TECHNOLOGY_NAME, None).split(":")
    peak_power = dictionary.get(PEAK_POWER_COLUMN_NAME, None)

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
            SURFACE_ORIENTATION_COLUMN_NAME: {
                "value": surface_orientation,
                "unit": angle_output_units,
            },
            SURFACE_TILT_COLUMN_NAME: {"value": surface_tilt, "unit": angle_output_units},
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
