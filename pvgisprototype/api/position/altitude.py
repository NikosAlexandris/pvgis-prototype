#
# Copyright (C) 2025 European Union
#  
#  
# Licensed under the EUPL, Version 1.2 or – as soon they will be approved by the
# European Commission – subsequent versions of the EUPL (the “Licence”);
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at:
# *
# https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12 
# *
# Unless required by applicable law or agreed to in writing, software distributed under
# the Licence is distributed on an “AS IS” basis, WITHOUT WARRANTIES OR CONDITIONS
# OF ANY KIND, either express or implied. See the Licence for the specific language
# governing permissions and limitations under the Licence.
#
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
from pvgisprototype.algorithms.hofierka.position.solar_altitude import (
    calculate_solar_altitude_series_hofierka,
)
from pvgisprototype.algorithms.pvlib.solar_altitude import (
    calculate_solar_altitude_series_pvlib,
)
from pvgisprototype.api.position.models import (
    SolarPositionModel,
    SolarPositionParameter,
    SolarTimeModel,
)
from pvgisprototype.core.caching import custom_cached
from pvgisprototype.constants import (
    ALTITUDE_NAME,
    ARRAY_BACKEND_DEFAULT,
    ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    ECCENTRICITY_CORRECTION_FACTOR,
    FINGERPRINT_FLAG_DEFAULT,
    LOG_LEVEL_DEFAULT,
    NOT_AVAILABLE,
    ECCENTRICITY_PHASE_OFFSET,
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
    adjust_for_atmospheric_refraction: bool = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    eccentricity_phase_offset: float = ECCENTRICITY_PHASE_OFFSET,
    eccentricity_amplitude: float = ECCENTRICITY_CORRECTION_FACTOR,
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

    """
    logger.debug(
        f"Executing solar positioning modelling function model_solar_altitude_series() for\n{timestamps}",
        alt=f"Executing [underline]solar positioning modelling[/underline] function model_solar_altitude_series() for\n{timestamps}",
    )
    solar_altitude_series = None

    if solar_position_model.value == SolarPositionModel.noaa:
        solar_altitude_series = calculate_solar_altitude_series_noaa(
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
    #         solar_positioning_algorithm='suncalc',
    #         solar_timing_algorithm='suncalc',
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

    logger.debug(
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
    adjust_for_atmospheric_refraction: bool = True,
    eccentricity_phase_offset: float = ECCENTRICITY_PHASE_OFFSET,
    eccentricity_amplitude: float = ECCENTRICITY_CORRECTION_FACTOR,
    angle_output_units: str = RADIANS,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
    fingerprint: bool = FINGERPRINT_FLAG_DEFAULT,
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
                adjust_for_atmospheric_refraction=adjust_for_atmospheric_refraction,
                eccentricity_phase_offset=eccentricity_phase_offset,
                eccentricity_amplitude=eccentricity_amplitude,
                dtype=dtype,
                array_backend=array_backend,
                verbose=verbose,
                log=log,
                validate_output=validate_output,
            )
            solar_altitude_series.build_output(verbose=verbose, fingerprint=fingerprint)
            solar_altitude_overview = {
                solar_position_model.name: solar_altitude_series.output
            }
            results = results | solar_altitude_overview

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    return results
