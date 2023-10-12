from devtools import debug
from typing import Optional
from typing import List
from datetime import datetime
from zoneinfo import ZoneInfo
from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.validation.functions import ModelSolarAzimuthInputModel
from pvgisprototype import Latitude
from pvgisprototype import Longitude
from pvgisprototype import RefractedSolarZenith
from pvgisprototype import SolarAzimuth
from .models import SolarPositionModels
from .models import SolarTimeModels
from pvgisprototype.algorithms.noaa.solar_position import calculate_solar_azimuth_noaa
from pvgisprototype.algorithms.skyfield.solar_geometry import calculate_solar_altitude_azimuth_skyfield
import suncalc
import pysolar
from pvgisprototype.algorithms.pvis.solar_azimuth import calculate_solar_azimuth_pvis
from pvgisprototype.algorithms.pvlib.solar_azimuth import calculate_solar_azimuth_pvlib
from pvgisprototype.api.utilities.conversions import convert_south_to_north_radians_convention
from pvgisprototype.api.utilities.timestamp import attach_timezone
from pvgisprototype.constants import REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT
from pvgisprototype.constants import DAYS_IN_A_YEAR
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import TIME_ALGORITHM_NAME
from pvgisprototype.constants import POSITION_ALGORITHM_NAME
from pvgisprototype.constants import AZIMUTH_NAME
from pvgisprototype.constants import UNITS_NAME


@validate_with_pydantic(ModelSolarAzimuthInputModel)
def model_solar_azimuth(
    longitude: Longitude,
    latitude: Latitude,
    timestamp: datetime,
    timezone: ZoneInfo,
    solar_position_model: SolarPositionModels = SolarPositionModels.pvlib,
    apply_atmospheric_refraction: bool = True,
    solar_time_model: SolarTimeModels = SolarTimeModels.milne,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
) -> SolarAzimuth:
    """
    The solar azimuth angle measures horizontally around the horizon from north
    through east, south, and west.

    Notes
    -----

    - All solar calculation functions return floating angular measurements in
      radians.

    pysolar :

    From https://pysolar.readthedocs.io:

    - Azimuth is reckoned with zero corresponding to north. Positive azimuth
      estimates correspond to estimates east of north; negative estimates, or
      estimates larger than 180 are west of north. In the northern hemisphere,
      if we speak in terms of (altitude, azimuth), the sun comes up around
      (0, 90), reaches (70, 180) around noon, and sets around (0, 270).

    - The result is returned with units.
    """
    if solar_position_model.value == SolarPositionModels.noaa:

        solar_azimuth = calculate_solar_azimuth_noaa(
            longitude=longitude,
            latitude=latitude,
            timestamp=timestamp,
            timezone=timezone,
            apply_atmospheric_refraction=apply_atmospheric_refraction,
            verbose=verbose,
        )
    
    if solar_position_model.value == SolarPositionModels.skyfield:

        solar_altitude, solar_azimuth = calculate_solar_altitude_azimuth_skyfield(
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

    if solar_position_model.value == SolarPositionModels.pysolar:

        timestamp = attach_timezone(timestamp, timezone)

        solar_azimuth = pysolar.solar.get_azimuth(
            latitude_deg=longitude.degrees,  # this comes first
            longitude_deg=latitude.degrees,
            when=timestamp,
        )  # returns degrees by default
        # required by output function
        solar_azimuth = SolarAzimuth(value=solar_azimuth, unit="degrees")

    if solar_position_model.value  == SolarPositionModels.pvis:

        solar_azimuth = calculate_solar_azimuth_pvis(
            longitude=longitude,
            latitude=latitude,
            timestamp=timestamp,
            timezone=timezone,
            solar_time_model=solar_time_model,
        )

    if solar_position_model.value  == SolarPositionModels.pvlib:

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

    #     solar_azimuth = convert_to_radians_if_requested(solar_azimuth, angle_output_units)

    if verbose == 3:
        debug(locals())
    return solar_azimuth


def calculate_solar_azimuth(
    longitude: Longitude,
    latitude: Latitude,
    timestamp: datetime,
    timezone: ZoneInfo,
    solar_position_models: List[SolarPositionModels] = [SolarPositionModels.skyfield],
    solar_time_model: SolarTimeModels = SolarTimeModels.skyfield,
    apply_atmospheric_refraction: bool = True,
    refracted_solar_zenith: Optional[RefractedSolarZenith] = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,  # radians
    days_in_a_year: float = DAYS_IN_A_YEAR,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    time_offset_global: float = 0,
    hour_offset: float = 0,
    angle_output_units: str = 'radians',
    verbose: int = VERBOSE_LEVEL_DEFAULT,
) -> List:
    """
    Calculates the solar position using all models and returns the results in a table.
    """
    results = []
    for solar_position_model in solar_position_models:
        if solar_position_model != SolarPositionModels.all:  # ignore 'all' in the enumeration
            solar_azimuth = model_solar_azimuth(
                longitude=longitude,
                latitude=latitude,
                timestamp=timestamp,
                timezone=timezone,
                solar_position_model=solar_position_model,
                apply_atmospheric_refraction=apply_atmospheric_refraction,
                refracted_solar_zenith=refracted_solar_zenith,
                solar_time_model=solar_time_model,
                time_offset_global=time_offset_global,
                hour_offset=hour_offset,
                days_in_a_year=days_in_a_year,
                perigee_offset=perigee_offset,
                eccentricity_correction_factor=eccentricity_correction_factor,
                verbose=verbose,
            )
            results.append({
                TIME_ALGORITHM_NAME: solar_time_model.value,
                POSITION_ALGORITHM_NAME: solar_position_model.value,
                AZIMUTH_NAME if solar_azimuth else None: getattr(solar_azimuth, angle_output_units) if solar_azimuth else None,
                UNITS_NAME: angle_output_units,
            })

    return results
