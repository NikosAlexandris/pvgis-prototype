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
from pandas import DatetimeIndex

from pvgisprototype import SolarDeclination
from pvgisprototype.algorithms.noaa.solar_declination import (
    calculate_solar_declination_series_noaa,
)
from pvgisprototype.algorithms.hofierka.position.solar_declination import (
    calculate_solar_declination_series_hofierka,
)
from pvgisprototype.algorithms.pvlib.solar_declination import (
    calculate_solar_declination_series_pvlib,
)
from pvgisprototype.api.position.models import SolarDeclinationModel
from pvgisprototype.api.utilities.conversions import (
    convert_series_to_degrees_if_requested,
)
from pvgisprototype.core.caching import custom_cached
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    DECLINATION_NAME,
    ECCENTRICITY_CORRECTION_FACTOR,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    LOG_LEVEL_DEFAULT,
    FINGERPRINT_FLAG_DEFAULT,
    NOT_AVAILABLE,
    ECCENTRICITY_PHASE_OFFSET,
    POSITION_ALGORITHM_NAME,
    RADIANS,
    UNIT_NAME,
    VERBOSE_LEVEL_DEFAULT,
    VALIDATE_OUTPUT_DEFAULT,
)
from pvgisprototype.log import log_data_fingerprint, log_function_call


@log_function_call
@custom_cached
def model_solar_declination_series(
    timestamps: DatetimeIndex,
    timezone: ZoneInfo = ZoneInfo("UTC"),
    solar_declination_model: SolarDeclinationModel = SolarDeclinationModel.pvis,
    eccentricity_phase_offset: float = ECCENTRICITY_PHASE_OFFSET,
    eccentricity_amplitude: float = ECCENTRICITY_CORRECTION_FACTOR,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = VERBOSE_LEVEL_DEFAULT,
    validate_output: bool = VALIDATE_OUTPUT_DEFAULT,
) -> SolarDeclination:
    """ """
    solar_declination_series = None

    if solar_declination_model.value == SolarDeclinationModel.noaa:
        solar_declination_series = calculate_solar_declination_series_noaa(
            timestamps=timestamps,
            dtype=dtype,
            array_backend=array_backend,
            verbose=verbose,
            log=log,
            validate_output=validate_output,
        )

    if solar_declination_model.value == SolarDeclinationModel.pvis:

        solar_declination_series = calculate_solar_declination_series_hofierka(
            timestamps=timestamps,
            dtype=dtype,
            array_backend=array_backend,
            verbose=verbose,
            log=log,
        )

    if solar_declination_model.value == SolarDeclinationModel.hargreaves:
        pass

    if solar_declination_model.value == SolarDeclinationModel.pvlib:
        solar_declination_series = calculate_solar_declination_series_pvlib(
            timestamps=timestamps,
            # dtype=dtype,
            # array_backend=array_backend,
            # verbose=verbose,
            # log=log,
        )

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=solar_declination_series.value,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return solar_declination_series


def calculate_solar_declination_series(
    timestamps: DatetimeIndex,
    timezone: ZoneInfo,
    solar_declination_models: List[SolarDeclinationModel] = [
        SolarDeclinationModel.pvis
    ],
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
    """Calculate the solar declination angle

    The solar declination is the angle between the rays of the sun and the
    equator of the earth. It is used to calculate the solar elevation and
    azimuth angles.
    """
    results = {}
    for solar_declination_model in solar_declination_models:
        if (
            solar_declination_model != SolarDeclinationModel.all
        ):  # ignore 'all' in the enumeration
            solar_declination_series = model_solar_declination_series(
                timestamps=timestamps,
                timezone=timezone,
                solar_declination_model=solar_declination_model,
                eccentricity_phase_offset=eccentricity_phase_offset,
                eccentricity_amplitude=eccentricity_amplitude,
                array_backend=array_backend,
                dtype=dtype,
                verbose=verbose,
                log=log,
                validate_output=validate_output,
            )
            solar_declination_series.build_output(
                verbose=verbose,
                fingerprint=fingerprint,
                angle_output_units=angle_output_units,
            )
            solar_declination_overview = {
                solar_declination_model.name: solar_declination_series.output
            }
            results = results | solar_declination_overview

    return results
