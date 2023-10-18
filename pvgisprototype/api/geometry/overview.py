from devtools import debug
from typing import Optional
from typing import List
from datetime import datetime
from zoneinfo import ZoneInfo
import suncalc
import pysolar
from ..utilities.conversions import convert_south_to_north_radians_convention
from ..utilities.timestamp import attach_timezone

from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.validation.functions import ModelSolarPositionInputModel
from pvgisprototype import Latitude
from pvgisprototype import Longitude
from pvgisprototype import SolarAltitude
from pvgisprototype import SolarAzimuth
from pvgisprototype import SolarZenith

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
from pvgisprototype.algorithms.pvis.solar_hour_angle import calculate_solar_hour_angle_pvis
from pvgisprototype.algorithms.pvis.solar_hour_angle import calculate_solar_hour_angle_pvis
from pvgisprototype.algorithms.skyfield.solar_geometry import calculate_solar_hour_angle_declination_skyfield
from pvgisprototype.algorithms.skyfield.solar_geometry import calculate_solar_altitude_azimuth_skyfield
from pvgisprototype.algorithms.pvlib.solar_altitude import calculate_solar_altitude_pvlib
from pvgisprototype.algorithms.pvlib.solar_azimuth import calculate_solar_azimuth_pvlib
from pvgisprototype.algorithms.pvlib.solar_declination import calculate_solar_declination_pvlib
from pvgisprototype.algorithms.pvlib.solar_hour_angle import calculate_solar_hour_angle_pvlib
from pvgisprototype.algorithms.pvlib.solar_zenith import calculate_solar_zenith_pvlib
from pvgisprototype.algorithms.milne1921.solar_time import calculate_apparent_solar_time_milne1921
from pvgisprototype.algorithms.milne1921.solar_time import calculate_apparent_solar_time_milne1921
from pvgisprototype.algorithms.pvgis.solar_geometry import calculate_solar_geometry_pvgis_constants
from pvgisprototype.constants import (
    POSITION_ALGORITHM_NAME,
    ALTITUDE_NAME,
    AZIMUTH_NAME,
    DECLINATION_NAME,
    HOUR_ANGLE_NAME,
    ZENITH_NAME,
    UNITS_NAME,
    TIME_ALGORITHM_NAME,
)


@validate_with_pydantic(ModelSolarPositionInputModel)
def model_solar_geometry_overview(
    longitude: Longitude,
    latitude: Latitude,
    timestamp: datetime,
    timezone: Optional[ZoneInfo],
    solar_position_model: SolarPositionModels,
    apply_atmospheric_refraction: bool,
    solar_time_model: SolarTimeModels,
    days_in_a_year: float,
    perigee_offset: float,
    eccentricity_correction_factor: float,
    verbose: int = 0,
) -> List:
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

    if solar_position_model.value == SolarPositionModels.noaa:

        print('NOAA')
        solar_declination = calculate_solar_declination_noaa(
            timestamp=timestamp,
        )
        solar_hour_angle = calculate_solar_hour_angle_noaa(
            longitude=longitude,
            timestamp=timestamp,
            timezone=timezone,
            verbose=verbose,
        )
        solar_zenith = calculate_solar_zenith_noaa(
            latitude=latitude,
            timestamp=timestamp,
            solar_hour_angle=solar_hour_angle,
            apply_atmospheric_refraction=apply_atmospheric_refraction,
            verbose=verbose,
        )
        solar_altitude = calculate_solar_altitude_noaa(
            longitude=longitude,
            latitude=latitude,
            timestamp=timestamp,
            timezone=timezone,
            apply_atmospheric_refraction=apply_atmospheric_refraction,
            verbose=verbose,
        )
        solar_azimuth = calculate_solar_azimuth_noaa(
            longitude=longitude,
            latitude=latitude,
            timestamp=timestamp,
            timezone=timezone,
            apply_atmospheric_refraction=apply_atmospheric_refraction,
            verbose=verbose,
        )
    
    if solar_position_model.value == SolarPositionModels.skyfield:

        print('Skyfield')
        solar_altitude, solar_azimuth = calculate_solar_altitude_azimuth_skyfield(
                longitude=longitude,
                latitude=latitude,
                timestamp=timestamp,
                timezone=timezone,
                )
        # ------------------------------------ TODO: calculate_solar_zenith_skyfield
        solar_zenith = SolarZenith(
            value = 90 - solar_altitude.degrees,
            unit = 'degrees'
        )
        # --------------------------------------------------------------------
        solar_hour_angle, solar_declination = calculate_solar_hour_angle_declination_skyfield(
            longitude=longitude,
            latitude=latitude,
            timestamp=timestamp,
            timezone=timezone,
        )

    if solar_position_model.value == SolarPositionModels.suncalc:
        # note : first azimuth, then altitude
        solar_azimuth_south_radians_convention, solar_altitude = suncalc.get_position(
            date=timestamp,  # this comes first here!
            lng=longitude.degrees,
            lat=latitude.degrees,
        ).values()  # zero points to south
        solar_azimuth = convert_south_to_north_radians_convention(
            solar_azimuth_south_radians_convention
        )
        solar_azimuth = SolarAzimuth(value=solar_azimuth, unit="radians")

        solar_altitude = SolarAltitude(value=solar_altitude, unit='radians')
        # ------------------------------------ TODO: calculate_solar_zenith_suncalc
        solar_zenith = SolarZenith(
            value = 90 - solar_altitude.degrees,
            unit = 'degrees'
        )
        # --------------------------------------------------------------------

    if solar_position_model.value == SolarPositionModels.pysolar:

        timestamp = attach_timezone(timestamp, timezone)

        solar_altitude = pysolar.solar.get_altitude(
            latitude_deg=latitude.degrees,  # this comes first
            longitude_deg=longitude.degrees,
            when=timestamp,
        )  # returns degrees by default
        # required by output function
        solar_altitude = SolarAltitude(value=solar_altitude, unit="degrees")

        # ------------------------------------ TODO: calculate_solar_zenith_pysolar
        solar_zenith = SolarZenith(
            value = 90 - solar_altitude.degrees,
            unit = 'degrees'
        )
        # --------------------------------------------------------------------

        solar_azimuth = pysolar.solar.get_azimuth(
            latitude_deg=latitude.degrees,  # this comes first
            longitude_deg=longitude.degrees,
            when=timestamp,
        )  # returns degrees by default
        # required by output function
        solar_azimuth = SolarAzimuth(value=solar_azimuth, unit="degrees")

    if solar_position_model.value  == SolarPositionModels.pvis:

        print('PVIS')
        solar_declination = calculate_solar_declination_pvis(
            timestamp=timestamp,
            timezone=timezone,
            eccentricity_correction_factor=eccentricity_correction_factor,
            perigee_offset=perigee_offset,
        )
        solar_time_milne1921 = calculate_apparent_solar_time_milne1921(
            longitude=longitude,
            timestamp=timestamp,
            timezone=timezone,
            verbose=verbose,
        )
        solar_hour_angle = calculate_solar_hour_angle_pvis(
            solar_time=solar_time_milne1921,
        )
        solar_altitude = calculate_solar_altitude_pvis(
            longitude=longitude,
            latitude=latitude,
            timestamp=timestamp,
            timezone=timezone,
            days_in_a_year=days_in_a_year,
            perigee_offset=perigee_offset,
            eccentricity_correction_factor=eccentricity_correction_factor,
            solar_time_model=solar_time_model,
            )
        # ------------------------------------ TODO: calculate_solar_zenith_pvis
        solar_zenith = SolarZenith(
            value = 90 - solar_altitude.degrees,
            unit = 'degrees'
        )
        # --------------------------------------------------------------------
        solar_azimuth = calculate_solar_azimuth_pvis(
            longitude=longitude,
            latitude=latitude,
            timestamp=timestamp,
            timezone=timezone,
            solar_time_model=solar_time_model,
        )

    if solar_position_model.value == SolarPositionModels.pvlib:

        solar_declination = calculate_solar_declination_pvlib(
            timestamp=timestamp,
        )
        solar_hour_angle = calculate_solar_hour_angle_pvlib(
            longitude=longitude,
            timestamp=timestamp,
        )
        solar_zenith = calculate_solar_zenith_pvlib(
            longitude=longitude,
            latitude=latitude,
            timestamp=timestamp,
            timezone=timezone,
        )
        solar_altitude = calculate_solar_altitude_pvlib(
            longitude=longitude,
            latitude=latitude,
            timestamp=timestamp,
            timezone=timezone,
            )
        solar_azimuth = calculate_solar_azimuth_pvlib(
            longitude=longitude,
            latitude=latitude,
            timestamp=timestamp,
            timezone=timezone,
        )

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

    position = (
            solar_declination if solar_declination is not None else None,
            solar_hour_angle if solar_hour_angle is not None else None,
            solar_zenith if solar_zenith is not None else None,
            solar_altitude if solar_altitude is not None else None,
            solar_azimuth if solar_azimuth is not None else None,
    )
    if verbose == 3:
        debug(locals())
    return position


def calculate_solar_geometry_overview(
    longitude: Longitude,
    latitude: Latitude,
    timestamp: datetime,
    timezone: Optional[ZoneInfo],
    solar_position_models: List[SolarPositionModels] = [SolarPositionModels.skyfield],
    solar_time_model: SolarTimeModels = SolarTimeModels.skyfield,
    apply_atmospheric_refraction: bool = True,
    days_in_a_year: float = 365.25,
    perigee_offset: float = 0.048869,
    eccentricity_correction_factor: float = 0.01672,
    angle_output_units: str = 'radians',
    verbose: int = 0,
) -> List:
    """
    Calculates the solar position using all models and returns the results in a table.
    """
    results = []
    for solar_position_model in solar_position_models:
        if solar_position_model != SolarPositionModels.all:  # ignore 'all' in the enumeration
            solar_declination, solar_hour_angle, solar_zenith, solar_altitude, solar_azimuth = model_solar_geometry_overview(
                longitude=longitude,
                latitude=latitude,
                timestamp=timestamp,
                timezone=timezone,
                solar_position_model=solar_position_model,
                apply_atmospheric_refraction=apply_atmospheric_refraction,
                solar_time_model=solar_time_model,
                days_in_a_year=days_in_a_year,
                perigee_offset=perigee_offset,
                eccentricity_correction_factor=eccentricity_correction_factor,
                verbose=verbose,
            )
            results.append({
                TIME_ALGORITHM_NAME: solar_time_model,
                DECLINATION_NAME if solar_declination else None: getattr(solar_declination, angle_output_units) if solar_declination else None,
                HOUR_ANGLE_NAME if solar_hour_angle else None: getattr(solar_hour_angle, angle_output_units) if solar_hour_angle else None,
                POSITION_ALGORITHM_NAME: solar_position_models.value,
                ZENITH_NAME if solar_zenith else None: getattr(solar_zenith, angle_output_units) if solar_zenith else None,
                ALTITUDE_NAME if solar_altitude else None: getattr(solar_altitude, angle_output_units) if solar_altitude else None,
                AZIMUTH_NAME if solar_azimuth else None: getattr(solar_azimuth, angle_output_units) if solar_azimuth else None,
                UNITS_NAME: angle_output_units,
            })

    return results
