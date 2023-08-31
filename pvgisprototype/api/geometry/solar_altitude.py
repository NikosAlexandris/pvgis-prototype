from typing import List
from datetime import datetime
from zoneinfo import ZoneInfo
from math import cos
from math import sin
from math import asin
from math import pi
from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.api.function_models import ModelSolarAltitudeInputModel
from pvgisprototype.api.models import Latitude
from pvgisprototype.api.models import Longitude
from pvgisprototype.api.geometry.models import SolarPositionModels
from pvgisprototype.api.geometry.models import SolarTimeModels
from pvgisprototype.api.models import SolarAltitude
from pvgisprototype.algorithms.noaa.solar_position import calculate_solar_altitude_noaa
from pvgisprototype.algorithms.skyfield.solar_geometry import calculate_solar_altitude_azimuth_skyfield
import suncalc
import pysolar
from pvgisprototype.algorithms.pvis.solar_altitude import calculate_solar_altitude_pvis
from pvgisprototype.api.utilities.conversions import convert_float_to_degrees_if_requested
from pvgisprototype.api.utilities.conversions import convert_to_degrees_if_requested
from pvgisprototype.api.utilities.conversions import convert_to_radians_if_requested
from pvgisprototype.api.utilities.timestamp import attach_timezone


@validate_with_pydantic(ModelSolarAltitudeInputModel)
def model_solar_altitude(
    longitude: Longitude,
    latitude: Latitude,
    timestamp: datetime,
    timezone: str,
    model: SolarPositionModels,
    apply_atmospheric_refraction: bool,
    refracted_solar_zenith: float,
    solar_time_model: SolarTimeModels,
    time_offset_global: float,
    hour_offset: float,
    days_in_a_year: float,
    perigee_offset: float,
    eccentricity_correction_factor: float,
    time_output_units: str,
    angle_units: str,
    angle_output_units: str,
) -> SolarAltitude:
    """
    The solar altitude angle measures from the horizon up towards the zenith
    (positive, and down towards the nadir (negative)). The altitude is zero all
    along the great circle between zenith and nadir.

    Notes
    -----

    - All solar calculation functions return floating angular measurements in
      radians.

    pysolar :

    From https://pysolar.readthedocs.io:

    - Altitude is reckoned with zero at the horizon. The altitude is positive
      when the sun is above the horizon.

    - The result is returned with units.
    """
    if model.value == SolarPositionModels.noaa:

        solar_altitude = calculate_solar_altitude_noaa(
            longitude=longitude,
            latitude=latitude,
            timestamp=timestamp,
            timezone=timezone,
            apply_atmospheric_refraction=apply_atmospheric_refraction,
            time_output_units=time_output_units,
            angle_output_units=angle_output_units,
        )
        solar_altitude = convert_to_degrees_if_requested(
            solar_altitude,
            angle_output_units,
        )

    if model.value == SolarPositionModels.skyfield:
        solar_altitude, solar_azimuth = calculate_solar_altitude_azimuth_skyfield(
                longitude=longitude,
                latitude=latitude,
                timestamp=timestamp,
                timezone=timezone,
                angle_output_units=angle_output_units,
                )
        solar_altitude = convert_to_degrees_if_requested(
            solar_altitude,
            angle_output_units,
            )

    if model.value == SolarPositionModels.suncalc:
        # note : first azimuth, then altitude
        solar_azimuth_south_radians_convention, solar_altitude = suncalc.get_position(
            date=timestamp,  # this comes first here!
            lng=longitude.value,
            lat=latitude.value,
        ).values()  # zero points to south
        solar_altitude = SolarAltitude(value=solar_altitude, unit='radians')
        solar_altitude = convert_to_degrees_if_requested(
            solar_altitude, angle_output_units
        )

    if model.value == SolarPositionModels.pysolar:

        timestamp = attach_timezone(timestamp, timezone)
        longitude_in_degrees = convert_float_to_degrees_if_requested(longitude.value, 'degrees')
        latitude_in_degrees = convert_float_to_degrees_if_requested(latitude.value, 'degrees')

        solar_altitude = pysolar.solar.get_altitude(
            latitude_deg=latitude_in_degrees,  # this comes first
            longitude_deg=longitude_in_degrees,
            when=timestamp,
        )  # returns degrees by default
        # required by output function
        solar_altitude = SolarAltitude(value=solar_altitude, unit="degrees")
        solar_altitude = convert_to_radians_if_requested(
            solar_altitude, angle_output_units
        )

    if model.value  == SolarPositionModels.pvis:

        solar_altitude = calculate_solar_altitude_pvis(
            longitude=longitude,
            latitude=latitude,
            timestamp=timestamp,
            timezone=timezone,
            apply_atmospheric_refraction=apply_atmospheric_refraction,
            refracted_solar_zenith=refracted_solar_zenith.value,
            days_in_a_year=days_in_a_year,
            perigee_offset=perigee_offset,
            eccentricity_correction_factor=eccentricity_correction_factor,
            time_offset_global=time_offset_global,
            hour_offset=hour_offset,
            solar_time_model=solar_time_model,
            time_output_units=time_output_units,
            angle_units=angle_units,
            angle_output_units=angle_output_units,
            )
        solar_altitude = convert_to_degrees_if_requested(solar_altitude, angle_output_units)

    return solar_altitude


def calculate_solar_altitude(
    longitude: Longitude,
    latitude: Latitude,
    timestamp: datetime,
    timezone: ZoneInfo,
    models: List[SolarPositionModels] = [SolarPositionModels.skyfield],
    solar_time_model: SolarTimeModels = SolarTimeModels.skyfield,
    apply_atmospheric_refraction: bool = True,
    refracted_solar_zenith: float = 1.5853349194640094,
    days_in_a_year: float = 365.25,
    perigee_offset: float = 0.048869,
    eccentricity_correction_factor: float = 0.01672,
    time_offset_global: float = 0,
    hour_offset: float = 0,
    time_output_units: str = 'minutes',
    angle_units: str = 'radians',
    angle_output_units: str = 'radians',
) -> List:
    """
    Calculates the solar position using all models and returns the results in a table.
    """
    results = []
    for model in models:
        if model != SolarPositionModels.all:  # ignore 'all' in the enumeration
            solar_altitude = model_solar_altitude(
                longitude=longitude,
                latitude=latitude,
                timestamp=timestamp,
                timezone=timezone,
                model=model,
                apply_atmospheric_refraction=apply_atmospheric_refraction,
                refracted_solar_zenith=refracted_solar_zenith,
                solar_time_model=solar_time_model,
                time_offset_global=time_offset_global,
                hour_offset=hour_offset,
                days_in_a_year=days_in_a_year,
                perigee_offset=perigee_offset,
                eccentricity_correction_factor=eccentricity_correction_factor,
                time_output_units=time_output_units,
                angle_units=angle_units,
                angle_output_units=angle_output_units,
            )
            results.append({
                'Model': model.value,
                'Altitude': solar_altitude.value,
                'Units': solar_altitude.unit,  # Don't trust me -- Redesign Me!
            })

    return results
