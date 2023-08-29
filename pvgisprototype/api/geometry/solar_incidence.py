from devtools import debug
from pvgisprototype.api.geometry.solar_time import model_solar_time
from pvgisprototype.api.geometry.solar_hour_angle import calculate_hour_angle
from pvgisprototype.models.jenco.solar_incidence import calculate_solar_incidence_jenco
from pvgisprototype.models.jenco.solar_incidence import calculate_effective_solar_incidence_angle
from pvgisprototype.api.data_classes.models import Latitude
from pvgisprototype.api.data_classes.models import Longitude
from datetime import datetime
from zoneinfo import ZoneInfo
from pvgisprototype.api.data_classes.models import SolarIncidence
from .models import SolarIncidenceModels
from .models import SolarTimeModels
from typing import List
from pathlib import Path
from pvgisprototype.api.utilities.conversions import convert_to_degrees_if_requested


def model_solar_incidence(
    longitude: Longitude,
    latitude: Latitude,
    timestamp: datetime,
    timezone: ZoneInfo = None,
    solar_time_model: SolarTimeModels = SolarTimeModels.skyfield,
    random_time: bool = False,
    solar_incidence_model: SolarIncidenceModels = SolarIncidenceModels.effective,
    hour_angle: float = None,
    surface_tilt: float = 45,
    surface_orientation: float = 180,
    shadow_indicator: Path = None,
    horizon_heights: List = None,
    horizon_interval: float = None,
    apply_atmospheric_refraction: bool = True,
    refracted_solar_zenith: float = 1.5853349194640094,  # radians
    days_in_a_year: float = 365.25,
    perigee_offset: float = 0.048869,
    eccentricity_correction_factor: float = 0.01672,
    time_offset_global: float = 0,
    hour_offset: float = 0,
    time_output_units: str = 'minutes',
    angle_units: str = 'radians',
    angle_output_units: str = 'radians',
    verbose: bool = False,
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
            time_output_units=time_output_units,
            angle_units=angle_units,
            angle_output_units=angle_output_units,
        )
        hour_angle = calculate_hour_angle(
            solar_time=solar_time,
            angle_output_units=angle_output_units,
        )
        solar_incidence = calculate_solar_incidence_jenco(
            longitude=longitude,
            latitude=latitude,
            timestamp=timestamp,
            timezone=timezone,
            random_time=random_time,
            hour_angle=hour_angle.value,
            surface_tilt=surface_tilt,
            surface_orientation=surface_orientation,
            days_in_a_year=days_in_a_year,
            eccentricity_correction_factor=eccentricity_correction_factor,
            perigee_offset=perigee_offset,
            time_output_units=time_output_units,
            angle_units=angle_units,
            angle_output_units=angle_output_units,
            verbose=verbose,
        )
        solar_incidence = convert_to_degrees_if_requested(
            solar_incidence,
            angle_output_units,
        )

    if solar_incidence_model.value == SolarIncidenceModels.effective:

        solar_incidence = calculate_effective_solar_incidence_angle(
            longitude=longitude,
            latitude=latitude,
            hour_angle=hour_angle,
            surface_tilt=surface_tilt,
            surface_orientation=surface_orientation,
            solar_azimuth=solar_azimuth,
            solar_altitude=solar_altitude,
            shadow_indicator=shadow_indicator,
            horizon_heights=horizon_heights,
            horizon_interval=horizon_interval,
        )
        solar_incidence = convert_to_degrees_if_requested(
            solar_incidence,
            angle_output_units,
        )

    return solar_incidence


def calculate_solar_incidence(
    longitude: Longitude,
    latitude: Latitude,
    timestamp: datetime,
    timezone: ZoneInfo = None,
    random_time: bool = False,
    solar_incidence_models: List[SolarIncidenceModels] = [SolarIncidenceModels.jenco],
    surface_tilt: float = 45,
    surface_orientation: float = 180,
    shadow_indicator = None,
    horizon_heights: List[float] = None,
    horizon_interval: float = None,
    days_in_a_year: float = 365.25,
    perigee_offset: float = 0.048869,
    eccentricity_correction_factor: float = 0.01672,
    time_offset_global: float = 0,
    hour_offset: float = 0,
    time_output_units: str = 'minutes',
    angle_units: str = 'radians',
    angle_output_units: str = 'radians',
    verbose: bool = False,
) -> List:
    """
    Calculates the solar Incidence angle for the selected models and returns the results in a table.
    """
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
                shadow_indicator=shadow_indicator,
                horizon_heights=horizon_heights,
                horizon_interval=horizon_interval,
                days_in_a_year=days_in_a_year,
                eccentricity_correction_factor=eccentricity_correction_factor,
                perigee_offset=perigee_offset,
                time_output_units=time_output_units,
                angle_units=angle_units,
                angle_output_units=angle_output_units,
                verbose=verbose,
            )
            results.append({
                'Model': model.value,
                'Incidence': solar_incidence.value,
                'Units': solar_incidence.unit,  # Don't trust me -- Redesign Me!
            })
    return results
