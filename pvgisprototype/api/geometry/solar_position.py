from devtools import debug
from typing import Annotated
from typing import Optional
from typing import List
from typing import Tuple
from enum import Enum
import numpy as np
from datetime import datetime
from zoneinfo import ZoneInfo
from math import pi
import suncalc
import pysolar
from ..utilities.conversions import convert_float_to_degrees_if_requested
from ..utilities.conversions import convert_to_degrees_if_requested
from ..utilities.conversions import convert_float_to_radians_if_requested
from ..utilities.conversions import convert_to_radians_if_requested
from ..utilities.conversions import convert_to_radians
from ..utilities.timestamp import now_utc_datetimezone
from ..utilities.timestamp import ctx_convert_to_timezone
from ..utilities.timestamp import attach_timezone

from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.validation.functions import ModelSolarPositionInputModel
from pvgisprototype import Latitude
from pvgisprototype import Longitude
from pvgisprototype import SolarAltitude
from pvgisprototype import SolarAzimuth

from .models import SolarTimeModels
from .models import SolarPositionModels

from pvgisprototype.algorithms.noaa.solar_position import calculate_solar_declination_noaa
from pvgisprototype.algorithms.noaa.solar_position import calculate_solar_hour_angle_noaa
from pvgisprototype.algorithms.noaa.solar_zenith import calculate_solar_zenith_noaa
from pvgisprototype.algorithms.noaa.solar_position import calculate_solar_altitude_noaa
from pvgisprototype.algorithms.noaa.solar_position import calculate_solar_azimuth_noaa
from pvgisprototype.algorithms.pvis.solar_declination import calculate_solar_declination_pvis
from pvgisprototype.algorithms.pvis.solar_altitude import calculate_solar_altitude_pvis
from pvgisprototype.algorithms.pvis.solar_azimuth import calculate_solar_azimuth_pvis
from pvgisprototype.algorithms.skyfield.solar_geometry import calculate_solar_position_skyfield
from pvgisprototype.algorithms.skyfield.solar_geometry import calculate_solar_altitude_azimuth_skyfield
from pvgisprototype.algorithms.pvlib.solar_altitude import calculate_solar_altitude_pvlib
from pvgisprototype.algorithms.pvlib.solar_azimuth import calculate_solar_azimuth_pvlib
from pvgisprototype.algorithms.pvlib.solar_declination import calculate_solar_declination_pvlib
from pvgisprototype.algorithms.pvlib.solar_hour_angle import calculate_solar_hour_angle_pvlib
from pvgisprototype.algorithms.pvlib.solar_zenith import calculate_solar_zenith_pvlib
# from pvgisprototype.algorithms.pvgis.solar_geometry import calculate_solar_position_pvgis
# from pvgisprototype.algorithms.pvgis.solar_geometry import calculate_solar_time_pvgis
from pvgisprototype.algorithms.pvgis.solar_geometry import calculate_solar_geometry_pvgis_constants


def convert_south_to_north_degrees_convention(azimuth_south_degrees):
    return (azimuth_south_degrees + 180) % 360


def convert_south_to_north_radians_convention(azimuth_south_radians):
    return (azimuth_south_radians + pi) % 2 * pi


@validate_with_pydantic(ModelSolarPositionInputModel)
def model_solar_position(
    longitude: Longitude,
    latitude: Latitude,
    timestamp: datetime,
    timezone: ZoneInfo,
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
) -> Tuple[SolarAltitude, SolarAzimuth]:
    """
    The solar altitude angle measures from the horizon up towards the zenith
    (positive, and down towards the nadir (negative)). The altitude is zero all
    along the great circle between zenith and nadir.

    The solar azimuth angle measures horizontally around the horizon from north
    through east, south, and west.

    Notes
    -----

    - All solar calculation functions return floating angular measurements in
      radians.


    pysolar :

    From https://pysolar.readthedocs.io:

    - Altitude is reckoned with zero at the horizon. The altitude is positive
      when the sun is above the horizon.

    - Azimuth is reckoned with zero corresponding to north. Positive azimuth
      estimates correspond to estimates east of north; negative estimates, or
      estimates larger than 180 are west of north. In the northern hemisphere,
      if we speak in terms of (altitude, azimuth), the sun comes up around
      (0, 90), reaches (70, 180) around noon, and sets around (0, 270).

    - The result is returned with units.
    """
    solar_declination = None  # updated if applicable
    solar_hour_angle = None
    solar_zenith = None  # updated if applicable
    solar_altitude = None
    solar_azimuth = None

    if model.value == SolarPositionModels.noaa:

        solar_declination = calculate_solar_declination_noaa(
            timestamp=timestamp,
            angle_output_units=angle_output_units
        )
        solar_declination = convert_to_degrees_if_requested(
            solar_declination,
            angle_output_units,
        )
        solar_hour_angle = calculate_solar_hour_angle_noaa(
            longitude=longitude,
            timestamp=timestamp,
            timezone=timezone,
            time_output_units=time_output_units,
            angle_output_units=angle_output_units,
        )
        solar_zenith = calculate_solar_zenith_noaa(
            latitude=latitude,
            timestamp=timestamp,
            solar_hour_angle=solar_hour_angle.value,
            apply_atmospheric_refraction=apply_atmospheric_refraction,
            angle_output_units=angle_output_units,
        )
        solar_zenith = convert_to_degrees_if_requested(
            solar_zenith,
            angle_output_units,
        )
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
        solar_azimuth = calculate_solar_azimuth_noaa(
            longitude=longitude,
            latitude=latitude,
            timestamp=timestamp,
            timezone=timezone,
            apply_atmospheric_refraction=apply_atmospheric_refraction,
            time_output_units=time_output_units,
            angle_units=angle_units,
            angle_output_units=angle_output_units,
        )
        solar_azimuth = convert_to_degrees_if_requested(
            solar_azimuth,
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
        solar_azimuth = convert_to_degrees_if_requested(
            solar_azimuth,
            angle_output_units,
            )

    if model.value == SolarPositionModels.suncalc:
        # note : first azimuth, then altitude
        solar_azimuth_south_radians_convention, solar_altitude = suncalc.get_position(
            date=timestamp,  # this comes first here!
            lng=longitude.value,
            lat=latitude.value,
        ).values()  # zero points to south
        solar_azimuth = convert_south_to_north_radians_convention(
            solar_azimuth_south_radians_convention
        )
        solar_azimuth = SolarAzimuth(value=solar_azimuth, unit="radians")
        solar_azimuth = convert_to_degrees_if_requested(
            solar_azimuth, angle_output_units
        )
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

        solar_azimuth = pysolar.solar.get_azimuth(
            latitude_deg=latitude_in_degrees,  # this comes first
            longitude_deg=longitude_in_degrees,
            when=timestamp,
        )  # returns degrees by default
        # required by output function
        solar_azimuth = SolarAzimuth(value=solar_azimuth, unit="degrees")
        solar_azimuth = convert_to_radians_if_requested(
            solar_azimuth, angle_output_units
        )

    if model.value  == SolarPositionModels.pvis:

        solar_declination = calculate_solar_declination_pvis(
            timestamp=timestamp,
            timezone=timezone,
            days_in_a_year=days_in_a_year,
            eccentricity_correction_factor=eccentricity_correction_factor,
            perigee_offset=perigee_offset,
            angle_output_units=angle_output_units,
        )
        solar_declination = convert_to_degrees_if_requested(
            solar_declination,
            angle_output_units,
        )

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

        solar_azimuth = calculate_solar_azimuth_pvis(
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
        solar_azimuth = convert_to_degrees_if_requested(solar_azimuth, angle_output_units)

        solar_declination = calculate_solar_declination_pvis(
            timestamp=timestamp,
            timezone=timezone,
            days_in_a_year=days_in_a_year,
            eccentricity_correction_factor=eccentricity_correction_factor,
            perigee_offset=perigee_offset,
            angle_output_units=angle_output_units,
        )
        solar_declination = convert_to_degrees_if_requested(
            solar_declination,
            angle_output_units,
        )

    if model.value == SolarPositionModels.pvlib:

        solar_declination = calculate_solar_declination_pvlib(
            timestamp=timestamp,
            angle_output_units=angle_output_units,
        )
        solar_declination = convert_to_degrees_if_requested(
            solar_declination,
            angle_output_units,
        )
        
        # solar_hour_angle = calculate_solar_hour_angle_pvlib(
        #     longitude=longitude,
        #     timestamp=timestamp,
        #     angle_output_units=angle_output_units,
        # )
        # solar_hour_angle = convert_to_degrees_if_requested(
        #     solar_hour_angle,
        #     angle_output_units,
        # )

        solar_zenith = calculate_solar_zenith_pvlib(
            longitude=longitude,
            latitude=latitude,
            timestamp=timestamp,
            timezone=timezone,
            angle_output_units=angle_output_units,
        )
        solar_zenith = convert_to_degrees_if_requested(
            solar_zenith,
            angle_output_units,
        )

        solar_altitude = calculate_solar_altitude_pvlib(
            longitude=longitude,
            latitude=latitude,
            timestamp=timestamp,
            timezone=timezone,
            angle_output_units=angle_output_units,
            )
        solar_altitude = convert_to_degrees_if_requested(solar_altitude, angle_output_units)

        solar_azimuth = calculate_solar_azimuth_pvlib(
            longitude=longitude,
            latitude=latitude,
            timestamp=timestamp,
            timezone=timezone,
            angle_output_units=angle_output_units,
        )
        solar_azimuth = convert_to_degrees_if_requested(solar_azimuth, angle_output_units)

    # if model.value  == SolarPositionModels.pvgis:
        
    #     solar_declination = calculate_solar_declination(timestamp)
    #     local_solar_time, _units = calculate_solar_time_pvgis(
    #             longitude=longitude,
    #             latitude=latitude,
    #             timestamp=timestamp,
    #             )

    #     solar_geometry_pvgis_day_constants = calculate_solar_geometry_pvgis_constants(
    #             longitude=longitude,
    #             latitude=latitude,
    #             local_solar_time=local_solar_time,
    #             solar_declination=solar_declination.value,
    #             )

    #     solar_altitude, solar_azimuth, sun_azimuth = calculate_solar_position_pvgis(
    #             solar_geometry_pvgis_day_constants,
    #             timestamp,
    #             )

    #     solar_altitude = convert_to_radians_if_requested(solar_altitude, angle_output_units)
    #     solar_azimuth = convert_to_radians_if_requested(solar_azimuth, angle_output_units)

    position = (
            solar_declination if solar_declination is not None else None,
            solar_hour_angle if solar_hour_angle is not None else None,
            solar_zenith if solar_zenith is not None else None,
            solar_altitude,
            solar_azimuth
    )
    return position


def calculate_solar_position(
    longitude: Longitude,
    latitude: Latitude,
    timestamp: datetime,
    timezone: ZoneInfo = None,
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
            solar_declination, solar_hour_angle, solar_zenith, solar_altitude, solar_azimuth = model_solar_position(
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
                # 'Declination': solar_declination.value,
                'Declination' if solar_declination is not None else None: solar_declination.value if solar_declination is not None else None,
                'Hour Angle' if solar_hour_angle is not None else None: solar_hour_angle.value if solar_hour_angle is not None else None,
                'Zenith' if solar_zenith is not None else None: solar_zenith.value if solar_zenith is not None else None,
                'Altitude' if solar_altitude is not None else None: solar_altitude.value if solar_altitude is not None else None,
                'Azimuth' if solar_azimuth is not None else None: solar_azimuth.value if solar_azimuth is not None else None,
                'Units': angle_output_units
            })

    return results
