from typing import Dict, List
import numpy as np
from zoneinfo import ZoneInfo
from devtools import debug
from pandas import DatetimeIndex

from pvgisprototype import Latitude, Longitude, SolarAltitude, SolarZenith
from pvgisprototype.algorithms.jenco.solar_altitude import (
    calculate_solar_altitude_series_jenco,
)
from pvgisprototype.algorithms.noaa.solar_zenith import (
    calculate_solar_zenith_series_noaa,
)
from pvgisprototype.algorithms.pvis.solar_altitude import (
    calculate_solar_altitude_series_hofierka,
)
from pvgisprototype.api.position.models import SolarPositionModel
from pvgisprototype.core.caching import custom_cached
from pvgisprototype.constants import (
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
    ZENITH_NAME,
    VALIDATE_OUTPUT_DEFAULT,
)
from pvgisprototype.log import log_function_call
from pvgisprototype.validation.functions import (
    ModelSolarAltitudeTimeSeriesInputModel,
    validate_with_pydantic,
)


@log_function_call
@custom_cached
@validate_with_pydantic(ModelSolarAltitudeTimeSeriesInputModel)
def model_solar_zenith_series(
    longitude: Longitude,
    latitude: Latitude,
    timestamps: DatetimeIndex,
    timezone: ZoneInfo,
    solar_position_model: SolarPositionModel = SolarPositionModel.noaa,
    adjust_for_atmospheric_refraction: bool = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    eccentricity_phase_offset: float = PERIGEE_OFFSET,
    eccentricity_amplitude: float = ECCENTRICITY_CORRECTION_FACTOR,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
    validate_output: bool = VALIDATE_OUTPUT_DEFAULT,
) -> SolarZenith:
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
    solar_zenith_series = None
    solar_altitude_series = None

    if solar_position_model.value == SolarPositionModel.noaa:
        solar_zenith_series = calculate_solar_zenith_series_noaa(
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            timezone=timezone,
            adjust_for_atmospheric_refraction=adjust_for_atmospheric_refraction,
            dtype=dtype,
            array_backend=array_backend,
            verbose=verbose,
            log=log,
            validate_output=validate_output,
        )

    if solar_position_model.value == SolarPositionModel.skyfield:
        pass
    # if solar_position_model.value == SolarPositionModel.skyfield:
    #     solar_zenith, solar_azimuth = calculate_solar_zenith_azimuth_skyfield(
    #         longitude=longitude,
    #         latitude=latitude,
    #         timestamp=timestamp,
    #     )

    if solar_position_model.value == SolarPositionModel.suncalc:
        pass
    # if solar_position_model.value == SolarPositionModel.suncalc:
    #     # note : first azimuth, then altitude
    #     solar_azimuth_south_radians_convention, solar_zenith = suncalc.get_position(
    #         date=timestamp,  # this comes first here!
    #         lng=longitude.degrees,
    #         lat=latitude.degrees,
    #     ).values()  # zero points to south
    #     solar_zenith = SolarAltitude(
    #         value=solar_zenith,
    #         unit=RADIANS,
    #         position_algorithm='suncalc',
    #         timing_algorithm='suncalc',
    #     )
    #     if (
    #         not isfinite(solar_zenith.degrees)
    #         or not solar_zenith.min_degrees <= solar_zenith.degrees <= solar_zenith.max_degrees
    #     ):
    #         raise ValueError(
    #             f"The calculated solar altitude angle {solar_zenith.degrees} is out of the expected range\
    #             [{solar_zenith.min_degrees}, {solar_zenith.max_degrees}] degrees"
    #         )

    if solar_position_model.value == SolarPositionModel.pysolar:
        pass
    # if solar_position_model.value == SolarPositionModel.pysolar:

    #     timestamp = attach_timezone(timestamp, timezone)
    #     solar_zenith = pysolar.solar.get_altitude(
    #         latitude_deg=latitude.degrees,  # this comes first
    #         longitude_deg=longitude.degrees,
    #         when=timestamp,
    #     )  # returns degrees by default
    #     # required by output function
    #     solar_zenith = SolarAltitude(
    #         value=solar_zenith,
    #         unit=DEGREES,
    #         position_algorithm='pysolar',
    #         timing_algorithm='pysolar',
    #     )
    #     if (
    #         not isfinite(solar_zenith.degrees)
    #         or not solar_zenith.min_degrees <= solar_zenith.degrees <= solar_zenith.max_degrees
    #     ):
    #         raise ValueError(
    #             f"The calculated solar altitude angle {solar_zenith.degrees} is out of the expected range\
    #             [{solar_zenith.min_degrees}, {solar_zenith.max_degrees}] degrees"
    #         )

    if solar_position_model.value == SolarPositionModel.jenco:
        solar_altitude_series = calculate_solar_altitude_series_jenco(
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            timezone=timezone,
            eccentricity_phase_offset=eccentricity_phase_offset,
            eccentricity_amplitude=eccentricity_amplitude,
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
            eccentricity_phase_offset=eccentricity_phase_offset,
            eccentricity_amplitude=eccentricity_amplitude,
            dtype=dtype,
            array_backend=array_backend,
            verbose=verbose,
            log=log,
        )

    if solar_position_model.value == SolarPositionModel.pvlib:
        pass

    # if solar_position_model.value  == SolarPositionModel.pvlib:

    #     solar_zenith = calculate_solar_zenith_pvlib(
    #         longitude=longitude,
    #         latitude=latitude,
    #         timestamp=timestamp,
    #         timezone=timezone,
    #         verbose=verbose,
    #     )
    if isinstance(solar_altitude_series, SolarAltitude):
        solar_zenith_series = SolarZenith(
            value=solar_altitude_series.radians - (np.pi / 2),
            unit=RADIANS,
            position_algorithm=solar_altitude_series.position_algorithm,
            timing_algorithm=solar_altitude_series.timing_algorithm,
        )

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    return solar_zenith_series


@log_function_call
def calculate_solar_zenith_series(
    longitude: Longitude,
    latitude: Latitude,
    timestamps: DatetimeIndex,
    timezone: ZoneInfo,
    solar_position_models: List[SolarPositionModel] = [SolarPositionModel.noaa],
    # solar_time_model: SolarTimeModel = SolarTimeModel.noaa,
    adjust_for_atmospheric_refraction: bool = True,
    eccentricity_phase_offset: float = PERIGEE_OFFSET,
    eccentricity_amplitude: float = ECCENTRICITY_CORRECTION_FACTOR,
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
            solar_zenith_series = model_solar_zenith_series(
                longitude=longitude,
                latitude=latitude,
                timestamps=timestamps,
                timezone=timezone,
                solar_position_model=solar_position_model,
                adjust_for_atmospheric_refraction=adjust_for_atmospheric_refraction,
                eccentricity_phase_offset=eccentricity_phase_offset,
                eccentricity_amplitude=eccentricity_amplitude,
                dtype=dtype,
                array_backend=array_backend,
                verbose=verbose,
                log=log,
                validate_output=validate_output,
            )
            solar_position_model_overview = {
                solar_position_model.name: {
                    TIME_ALGORITHM_NAME: (
                        solar_zenith_series.timing_algorithm
                        if solar_zenith_series
                        else NOT_AVAILABLE
                    ),
                    POSITION_ALGORITHM_NAME: solar_position_model.value,
                    ZENITH_NAME: (
                        getattr(solar_zenith_series, angle_output_units, NOT_AVAILABLE)
                        if solar_zenith_series
                        else NOT_AVAILABLE
                    ),
                    UNIT_NAME: None,
                }
            }
            results = results | solar_position_model_overview

    return results
