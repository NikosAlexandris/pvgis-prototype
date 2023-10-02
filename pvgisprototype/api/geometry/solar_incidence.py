from devtools import debug
from pvgisprototype.api.geometry.solar_hour_angle import calculate_hour_angle
from pvgisprototype.algorithms.jenco.solar_incidence import calculate_solar_incidence_jenco
from pvgisprototype import Latitude
from pvgisprototype import Longitude
from pvgisprototype import RefractedSolarZenith
from datetime import datetime
from zoneinfo import ZoneInfo
from .models import SolarTimeModels
from .models import SolarIncidenceModels
from pathlib import Path
from typing import List
from pvgisprototype import SolarIncidence
from pvgisprototype.api.geometry.solar_time import model_solar_time
from pvgisprototype.api.utilities.conversions import convert_to_degrees_if_requested
from pvgisprototype.constants import RANDOM_DAY_FLAG_DEFAULT
from pvgisprototype.constants import SURFACE_TILT_DEFAULT
from pvgisprototype.constants import SURFACE_ORIENTATION_DEFAULT
from pvgisprototype.constants import ATMOSPHERIC_REFRACTION_FLAG_DEFAULT
from pvgisprototype.constants import REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT
from pvgisprototype.constants import DAYS_IN_A_YEAR
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.constants import TIME_OFFSET_GLOBAL_DEFAULT
from pvgisprototype.constants import HOUR_OFFSET_DEFAULT
from pvgisprototype.constants import TIME_OUTPUT_UNITS_DEFAULT
from pvgisprototype.constants import ANGLE_OUTPUT_UNITS_DEFAULT
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import POSITION_ALGORITHM_NAME
from pvgisprototype.constants import INCIDENCE_NAME
from pvgisprototype.constants import UNITS_NAME


def model_solar_incidence(
    longitude: Longitude,
    latitude: Latitude,
    timestamp: datetime,
    timezone: ZoneInfo = None,
    solar_time_model: SolarTimeModels = SolarTimeModels.milne,
    random_time: bool = RANDOM_DAY_FLAG_DEFAULT,
    solar_incidence_model: SolarIncidenceModels = SolarIncidenceModels.effective,
    surface_tilt: float = SURFACE_TILT_DEFAULT,
    surface_orientation: float = SURFACE_ORIENTATION_DEFAULT,
    shadow_indicator: Path = None,
    horizon_heights: List = None,
    horizon_interval: float = None,
    apply_atmospheric_refraction: bool = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    refracted_solar_zenith: RefractedSolarZenith = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    days_in_a_year: float = DAYS_IN_A_YEAR,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    time_offset_global: float = TIME_OFFSET_GLOBAL_DEFAULT,
    hour_offset: float = HOUR_OFFSET_DEFAULT,
    # time_output_units: str = TIME_OUTPUT_UNITS_DEFAULT,
    # angle_units: str = "radians",
    # angle_output_units: str = ANGLE_OUTPUT_UNITS_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
) -> SolarIncidence:
    """ """
    if solar_incidence_model.value == SolarIncidenceModels.jenco:
        solar_time = model_solar_time(
            longitude=longitude,
            latitude=latitude,
            timestamp=timestamp,
            timezone=timezone,
            solar_time_model=solar_time_model,  # returns datetime.time object
            refracted_solar_zenith=refracted_solar_zenith,
            apply_atmospheric_refraction=apply_atmospheric_refraction,
            days_in_a_year=days_in_a_year,
            perigee_offset=perigee_offset,
            eccentricity_correction_factor=eccentricity_correction_factor,
            time_offset_global=time_offset_global,
            hour_offset=hour_offset,
            # time_output_units=time_output_units,
            # angle_units=angle_units,
            # angle_output_units=angle_output_units,
        )
        # if not hour_angle:
        #     hour_angle = calculate_hour_angle(
        #         solar_time=solar_time,
        #         angle_output_units=angle_output_units,
        #     )
        #     hour_angle = hour_angle.value
        solar_incidence = calculate_solar_incidence_jenco(
            longitude=longitude,
            latitude=latitude,
            timestamp=timestamp,
            timezone=timezone,
            random_time=random_time,
            # hour_angle=hour_angle,
            surface_tilt=surface_tilt,
            surface_orientation=surface_orientation,
            days_in_a_year=days_in_a_year,
            eccentricity_correction_factor=eccentricity_correction_factor,
            perigee_offset=perigee_offset,
            # time_output_units=time_output_units,
            # angle_units=angle_units,
            verbose=verbose,
        )
        # solar_incidence = convert_to_degrees_if_requested(
        #     solar_incidence,
        #     angle_output_units,
        # )

    return solar_incidence


def calculate_solar_incidence(
    longitude: Longitude,
    latitude: Latitude,
    timestamp: datetime,
    timezone: ZoneInfo = None,
    random_time: bool = RANDOM_DAY_FLAG_DEFAULT,
    solar_incidence_models: List[SolarIncidenceModels] = [SolarIncidenceModels.jenco],
    surface_tilt: float = SURFACE_TILT_DEFAULT,
    surface_orientation: float = SURFACE_ORIENTATION_DEFAULT,
    # shadow_indicator: Path = None,
    horizon_heights: List[float] = None,
    horizon_interval: float = None,
    days_in_a_year: float = DAYS_IN_A_YEAR,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    time_offset_global: float = TIME_OFFSET_GLOBAL_DEFAULT,
    hour_offset: float = HOUR_OFFSET_DEFAULT,
    # time_output_units: str = TIME_OUTPUT_UNITS_DEFAULT,
    # angle_units: str = "radians",
    # angle_output_units: str = ANGLE_OUTPUT_UNITS_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
) -> List:
    """Calculates the solar Incidence angle for the selected models and returns the results in a table"""
    results = []
    for model in solar_incidence_models:
        if model != SolarIncidenceModels.all:  # ignore 'all' in the enumeration
            solar_incidence = model_solar_incidence(
                longitude=longitude,
                latitude=latitude,
                timestamp=timestamp,
                timezone=timezone,
                random_time=random_time,
                solar_incidence_model=model,
                time_offset_global=time_offset_global,
                hour_offset=hour_offset,
                surface_tilt=surface_tilt,
                surface_orientation=surface_orientation,
                # shadow_indicator=shadow_indicator,
                horizon_heights=horizon_heights,
                horizon_interval=horizon_interval,
                days_in_a_year=days_in_a_year,
                eccentricity_correction_factor=eccentricity_correction_factor,
                perigee_offset=perigee_offset,
                # time_output_units=time_output_units,
                # angle_units=angle_units,
                # angle_output_units=angle_output_units,
                verbose=verbose,
            )
            results.append(
                {
                    POSITION_ALGORITHM_NAME: model.value,
                    INCIDENCE_NAME: getattr(solar_incidence, angle_output_units),
                    UNITS_NAME: angle_output_units,  # Don't trust me -- Redesign Me!
                }
            )
    return results
