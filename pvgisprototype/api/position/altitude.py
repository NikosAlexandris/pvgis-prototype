from typing import Dict, List
from zoneinfo import ZoneInfo

from devtools import debug
from pandas import DatetimeIndex, Timestamp

from pvgisprototype import Latitude, Longitude, SolarAltitude
from pvgisprototype.algorithms.jenco.solar_altitude import (
    calculate_solar_altitude_series_jenco,
)
from pvgisprototype.algorithms.noaa.solar_altitude import (
    calculate_solar_altitude_series_noaa,
)
from pvgisprototype.algorithms.pvis.solar_altitude import (
    calculate_solar_altitude_series_hofierka,
)
from pvgisprototype.algorithms.pvlib.solar_altitude import (
    calculate_solar_altitude_series_pvlib,
)
from pvgisprototype.api.position.models import SolarPositionModel, SolarPositionParameter, SolarTimeModel
from pvgisprototype.core.caching import custom_cached
from pvgisprototype.constants import (
    ALTITUDE_NAME,
    ARRAY_BACKEND_DEFAULT,
    ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    ECCENTRICITY_CORRECTION_FACTOR,
    LOG_LEVEL_DEFAULT,
    NOT_AVAILABLE,
    PERIGEE_OFFSET,
    POSITION_ALGORITHM_NAME,
    RADIANS,
    TIME_ALGORITHM_NAME,
    UNIT_NAME,
    VERBOSE_LEVEL_DEFAULT,
    VALIDATE_OUTPUT_DEFAULT,
)
from pvgisprototype.log import log_function_call, logger
from pvgisprototype.validation.functions import (
    ModelSolarAltitudeTimeSeriesInputModel,
    validate_with_pydantic,
)


@log_function_call
@custom_cached
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
    validate_output: bool = VALIDATE_OUTPUT_DEFAULT,
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
    logger.info(
            f"Executing solar positioning modelling function model_solar_altitude_series() for\n{timestamps}",
            alt=f"Executing [underline]solar positioning modelling[/underline] function model_solar_altitude_series() for\n{timestamps}"
            )
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
            validate_output=validate_output,
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

    if solar_position_model.value == SolarPositionModel.jenco:
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

    if solar_position_model.value == SolarPositionModel.hofierka:
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

    if solar_position_model.value == SolarPositionModel.pvlib:
        solar_altitude_series = calculate_solar_altitude_series_pvlib(
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            dtype=dtype,
            array_backend=array_backend,
            verbose=verbose,
            log=log,
        )

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    logger.info(
            f"Returning solar altitude time series :\n{solar_altitude_series}",
            alt=f"Returning [yellow]solar altitude[/yellow] time series :\n{solar_altitude_series}",
            )
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
    validate_output: bool = VALIDATE_OUTPUT_DEFAULT,
) -> Dict:
    """Calculates the solar position using the requested models and returns the
    results in a dictionary.
    """
    results = {}
    for solar_position_model in solar_position_models:
        if (
            solar_position_model != SolarPositionModel.all
        ):  # ignore 'all' in the enumeration
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
                validate_output=validate_output,
            )
            solar_position_model_overview = {
                solar_position_model.name: {
                    SolarPositionParameter.timing: (
                        solar_altitude_series.timing_algorithm
                        if solar_altitude_series
                        else NOT_AVAILABLE
                    ),
                    SolarPositionParameter.positioning: solar_position_model.value,
                    SolarPositionParameter.altitude: (
                        getattr(
                            solar_altitude_series, angle_output_units, NOT_AVAILABLE
                        )
                        if solar_altitude_series
                        else NOT_AVAILABLE
                    ),
                    UNIT_NAME: None,
                }
            }
            results = results | solar_position_model_overview

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    return results
