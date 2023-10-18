from typing import List
from datetime import datetime
from zoneinfo import ZoneInfo
#from math import isfinite
from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.validation.functions import ModelSolarAltitudeInputModel
from pvgisprototype import Latitude
from pvgisprototype import Longitude
from pvgisprototype.api.geometry.models import SolarPositionModels
from pvgisprototype.api.geometry.models import SolarTimeModels
from pvgisprototype import SolarAltitude
from pvgisprototype.algorithms.noaa.solar_position import calculate_solar_altitude_noaa
from pvgisprototype.algorithms.skyfield.solar_geometry import calculate_solar_altitude_azimuth_skyfield
import suncalc
import pysolar
from pvgisprototype.api.utilities.timestamp import attach_timezone
from pvgisprototype.algorithms.noaa.solar_position import calculate_solar_altitude_noaa
from pvgisprototype.algorithms.skyfield.solar_geometry import calculate_solar_altitude_azimuth_skyfield
from pvgisprototype.algorithms.pvis.solar_altitude import calculate_solar_altitude_pvis
from pvgisprototype.algorithms.pvlib.solar_altitude import calculate_solar_altitude_pvlib
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import TIME_ALGORITHM_NAME
from pvgisprototype.constants import POSITION_ALGORITHM_NAME
from pvgisprototype.constants import ALTITUDE_NAME
from pvgisprototype.constants import UNITS_NAME


@validate_with_pydantic(ModelSolarAltitudeInputModel)
def model_solar_altitude(
    longitude: Longitude,
    latitude: Latitude,
    timestamp: datetime,
    timezone: ZoneInfo,
    solar_time_model: SolarTimeModels = SolarTimeModels.milne,
    solar_position_model: SolarPositionModels = SolarPositionModels.pvlib,
    apply_atmospheric_refraction: bool = True,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
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
    if solar_position_model.value == SolarPositionModels.noaa:

        solar_altitude = calculate_solar_altitude_noaa(
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
            verbose=verbose,
        )

    if solar_position_model.value == SolarPositionModels.suncalc:
        # note : first azimuth, then altitude
        solar_azimuth_south_radians_convention, solar_altitude = suncalc.get_position(
            date=timestamp,  # this comes first here!
            lng=longitude.degrees,
            lat=latitude.degrees,
        ).values()  # zero points to south
        solar_altitude = SolarAltitude(
            value=solar_altitude,
            unit=RADIANS,
            position_algorithm='suncalc',
            timing_algorithm='suncalc',
        )

#        if (
#            not isfinite(solar_altitude.degrees)
#            or not solar_altitude.min_degrees <= solar_altitude.degrees <= solar_altitude.max_degrees
#        ):
#            raise ValueError(
#                f"The calculated solar altitude angle {solar_altitude.degrees} is out of the expected range\
#                [{solar_altitude.min_degrees}, {solar_altitude.max_degrees}] radians"
#            )

    if solar_position_model.value == SolarPositionModels.pysolar:

        timestamp = attach_timezone(timestamp, timezone)
        solar_altitude = pysolar.solar.get_altitude(
            latitude_deg=latitude.degrees,  # this comes first
            longitude_deg=longitude.degrees,
            when=timestamp,
        )  # returns degrees by default
        # required by output function
        solar_altitude = SolarAltitude(
            value=solar_altitude,
            unit="degrees",
            position_algorithm='pysolar',
            timing_algorithm='pysolar',
        )

#        if (
#            not isfinite(solar_altitude.degrees)
#            or not solar_altitude.min_degrees <= solar_altitude.degrees <= solar_altitude.max_degrees
#        ):
#            raise ValueError(
#                f"The calculated solar altitude angle {solar_altitude.degrees} is out of the expected range\
#                [{solar_altitude.min_degrees}, {solar_altitude.max_degrees}] radians"
#            )

    if solar_position_model.value  == SolarPositionModels.pvis:

        solar_altitude = calculate_solar_altitude_pvis(
            longitude=longitude,
            latitude=latitude,
            timestamp=timestamp,
            timezone=timezone,
            perigee_offset=perigee_offset,
            eccentricity_correction_factor=eccentricity_correction_factor,
            solar_time_model=solar_time_model,
            verbose=verbose,
        )

    if solar_position_model.value  == SolarPositionModels.pvlib:

        solar_altitude = calculate_solar_altitude_pvlib(
            longitude=longitude,
            latitude=latitude,
            timestamp=timestamp,
            timezone=timezone,
            verbose=verbose,
        )

    return solar_altitude


def calculate_solar_altitude(
    longitude: Longitude,
    latitude: Latitude,
    timestamp: datetime,
    timezone: ZoneInfo,
    solar_position_models: List[SolarPositionModels] = [SolarPositionModels.skyfield],
    solar_time_model: SolarTimeModels = SolarTimeModels.skyfield,
    apply_atmospheric_refraction: bool = True,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    verbose: int = 0,
) -> List:
    """
    Calculates the solar position using all models and returns the results in a table.
    """
    results = []
    for solar_position_model in solar_position_models:
        if solar_position_model != SolarPositionModels.all:  # ignore 'all' in the enumeration
            solar_altitude = model_solar_altitude(
                longitude=longitude,
                latitude=latitude,
                timestamp=timestamp,
                timezone=timezone,
                solar_position_model=solar_position_model,
                solar_time_model=solar_time_model,
                apply_atmospheric_refraction=apply_atmospheric_refraction,
                perigee_offset=perigee_offset,
                eccentricity_correction_factor=eccentricity_correction_factor,
                verbose=verbose,
            )
            results.append({
                TIME_ALGORITHM_NAME: solar_altitude.timing_algorithm,
                POSITION_ALGORITHM_NAME: solar_position_model.value,
                ALTITUDE_NAME: getattr(solar_altitude, angle_output_units, None) if solar_altitude else None,
                UNITS_NAME: angle_output_units,
            })

    return results
