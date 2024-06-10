from pvgisprototype.algorithms.jenco.solar_altitude import calculate_solar_altitude_series_jenco
from pvgisprototype.algorithms.pvis.solar_altitude import calculate_solar_altitude_series_hofierka
from pvgisprototype.log import log_function_call
from pvgisprototype.log import log_data_fingerprint
from devtools import debug
from typing import Dict, List, Union, Sequence
from pandas import DatetimeIndex, Timestamp
from datetime import datetime
from zoneinfo import ZoneInfo
from pvgisprototype import Longitude
from pvgisprototype import Latitude
from pvgisprototype import SolarAltitude
from pvgisprototype.api.position.models import SolarPositionModel
from pvgisprototype.api.position.models import SolarTimeModel
from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.validation.functions import ModelSolarAltitudeTimeSeriesInputModel
from pvgisprototype.algorithms.noaa.solar_altitude import calculate_solar_altitude_series_noaa
from pvgisprototype.algorithms.jenco.solar_altitude import calculate_solar_altitude_series_jenco
from pvgisprototype.caching import custom_hashkey
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import TIME_ALGORITHM_NAME
from pvgisprototype.constants import POSITION_ALGORITHM_NAME
from pvgisprototype.constants import ALTITUDE_NAME
from pvgisprototype.constants import UNIT_NAME
from pvgisprototype.constants import HASH_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.constants import DEBUG_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.constants import DATA_TYPE_DEFAULT
from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT
from pvgisprototype.constants import NOT_AVAILABLE
from pvgisprototype.constants import RADIANS
from cachetools import cached
from rich import print
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import LOG_LEVEL_DEFAULT
from pvgisprototype.constants import ATMOSPHERIC_REFRACTION_FLAG_DEFAULT


@log_function_call
@cached(cache={}, key=custom_hashkey)
@validate_with_pydantic(ModelSolarAltitudeTimeSeriesInputModel)
def model_solar_altitude_series(
    longitude: Longitude,
    latitude: Latitude,
    timestamps: DatetimeIndex | Timestamp | None,
    timezone: ZoneInfo,
    solar_position_model: SolarPositionModel = SolarPositionModel.noaa,
    apply_atmospheric_refraction: bool = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
) -> SolarAltitude:
    """
    Notes
    -----

    The solar altitude angle measures from the horizon up towards the zenith
    (positive, and down towards the nadir (negative)). The altitude is zero all
    along the great circle between zenith and nadir.

    - All solar calculation functions return floating angular measurements in
      radians.

    pysolar :

    From https://pysolar.readthedocs.io:

    - Altitude is reckoned with zero at the horizon. The altitude is positive
      when the sun is above the horizon.

    - The result is returned with units.
    """
    solar_altitude_series = None

    if solar_position_model.value == SolarPositionModel.noaa:

        solar_altitude_series = calculate_solar_altitude_series_noaa(
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            timezone=timezone,
            apply_atmospheric_refraction=apply_atmospheric_refraction,
            dtype=dtype,
            array_backend=array_backend,
            verbose=verbose,
            log=log,
        )

    if solar_position_model.value == SolarPositionModel.skyfield:
        pass
    # if solar_position_model.value == SolarPositionModel.skyfield:
    #     solar_altitude, solar_azimuth = calculate_solar_altitude_azimuth_skyfield(
    #         longitude=longitude,
    #         latitude=latitude,
    #         timestamp=timestamp,
    #     )

    if solar_position_model.value == SolarPositionModel.suncalc:
        pass
    # if solar_position_model.value == SolarPositionModel.suncalc:
    #     # note : first azimuth, then altitude
    #     solar_azimuth_south_radians_convention, solar_altitude = suncalc.get_position(
    #         date=timestamp,  # this comes first here!
    #         lng=longitude.degrees,
    #         lat=latitude.degrees,
    #     ).values()  # zero points to south
    #     solar_altitude = SolarAltitude(
    #         value=solar_altitude,
    #         unit=RADIANS,
    #         position_algorithm='suncalc',
    #         timing_algorithm='suncalc',
    #     )
    #     if (
    #         not isfinite(solar_altitude.degrees)
    #         or not solar_altitude.min_degrees <= solar_altitude.degrees <= solar_altitude.max_degrees
    #     ):
    #         raise ValueError(
    #             f"The calculated solar altitude angle {solar_altitude.degrees} is out of the expected range\
    #             [{solar_altitude.min_degrees}, {solar_altitude.max_degrees}] degrees"
    #         )


    if solar_position_model.value == SolarPositionModel.pysolar:
        pass
    # if solar_position_model.value == SolarPositionModel.pysolar:

    #     timestamp = attach_timezone(timestamp, timezone)
    #     solar_altitude = pysolar.solar.get_altitude(
    #         latitude_deg=latitude.degrees,  # this comes first
    #         longitude_deg=longitude.degrees,
    #         when=timestamp,
    #     )  # returns degrees by default
    #     # required by output function
    #     solar_altitude = SolarAltitude(
    #         value=solar_altitude,
    #         unit=DEGREES,
    #         position_algorithm='pysolar',
    #         timing_algorithm='pysolar',
    #     )
    #     if (
    #         not isfinite(solar_altitude.degrees)
    #         or not solar_altitude.min_degrees <= solar_altitude.degrees <= solar_altitude.max_degrees
    #     ):
    #         raise ValueError(
    #             f"The calculated solar altitude angle {solar_altitude.degrees} is out of the expected range\
    #             [{solar_altitude.min_degrees}, {solar_altitude.max_degrees}] degrees"
    #         )


    if solar_position_model.value  == SolarPositionModel.jenco:

        solar_altitude_series = calculate_solar_altitude_series_jenco(
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            timezone=timezone,
            perigee_offset=perigee_offset,
            eccentricity_correction_factor=eccentricity_correction_factor,
            dtype=dtype,
            array_backend=array_backend,
            verbose=verbose,
            log=log,
        )

    if solar_position_model.value  == SolarPositionModel.hofierka:

        solar_altitude_series = calculate_solar_altitude_series_hofierka(
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            timezone=timezone,
            perigee_offset=perigee_offset,
            eccentricity_correction_factor=eccentricity_correction_factor,
            dtype=dtype,
            array_backend=array_backend,
            verbose=verbose,
            log=log,
        )

    if solar_position_model.value  == SolarPositionModel.pvlib:
        pass

    # if solar_position_model.value  == SolarPositionModel.pvlib:

    #     solar_altitude = calculate_solar_altitude_pvlib(
    #         longitude=longitude,
    #         latitude=latitude,
    #         timestamp=timestamp,
    #         timezone=timezone,
    #         verbose=verbose,
    #     )
    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    return solar_altitude_series


@log_function_call
def calculate_solar_altitude_series(
    longitude: Longitude,
    latitude: Latitude,
    timestamps: DatetimeIndex,
    timezone: ZoneInfo,
    solar_position_models: List[SolarPositionModel] = [SolarPositionModel.noaa],
    solar_time_model: SolarTimeModel = SolarTimeModel.noaa,
    apply_atmospheric_refraction: bool = True,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    angle_output_units: str = RADIANS,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
) -> Dict:
    """Calculates the solar position using the requested models and returns the
    results in a dictionary.
    """
    results = {}
    for solar_position_model in solar_position_models:
        if solar_position_model != SolarPositionModel.all:  # ignore 'all' in the enumeration
            solar_altitude_series = model_solar_altitude_series(
                longitude=longitude,
                latitude=latitude,
                timestamps=timestamps,
                timezone=timezone,
                solar_position_model=solar_position_model,
                apply_atmospheric_refraction=apply_atmospheric_refraction,
                perigee_offset=perigee_offset,
                eccentricity_correction_factor=eccentricity_correction_factor,
                dtype=dtype,
                array_backend=array_backend,
                verbose=verbose,
                log=log,
            )
            solar_position_model_overview = {
                solar_position_model.name: {
                    TIME_ALGORITHM_NAME: solar_altitude_series.timing_algorithm if solar_altitude_series else NOT_AVAILABLE,
                    POSITION_ALGORITHM_NAME: solar_position_model.value,
                    ALTITUDE_NAME: getattr(solar_altitude_series, angle_output_units, NOT_AVAILABLE) if solar_altitude_series else NOT_AVAILABLE,
                    UNIT_NAME: None,
                }
            }
            results = results | solar_position_model_overview

    return results
