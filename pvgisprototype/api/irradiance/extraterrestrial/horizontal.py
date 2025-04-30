from zoneinfo import ZoneInfo
from numpy import ndarray
from devtools import debug
from pandas import DatetimeIndex, Timestamp
from pvgisprototype.algorithms.hofierka.irradiance.extraterrestrial.horizontal import calculate_extraterrestrial_horizontal_irradiance_series_hofierka
from pvgisprototype.algorithms.hofierka.irradiance.extraterrestrial.normal import (
    calculate_extraterrestrial_normal_irradiance_hofierka,
)
from pvgisprototype.api.position.altitude import model_solar_altitude_series
from pvgisprototype.api.position.models import SOLAR_POSITION_ALGORITHM_DEFAULT, SOLAR_TIME_ALGORITHM_DEFAULT, SolarPositionModel, SolarTimeModel
from pvgisprototype.core.caching import custom_cached
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    ECCENTRICITY_CORRECTION_FACTOR,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    PERIGEE_OFFSET,
    UNREFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    SOLAR_CONSTANT,
    VERBOSE_LEVEL_DEFAULT,
)
from pvgisprototype.log import log_data_fingerprint, log_function_call
from pvgisprototype import ExtraterrestrialNormalIrradiance


@log_function_call
@custom_cached
def calculate_extraterrestrial_horizontal_irradiance(
    longitude: float,
    latitude: float,
    extraterrestrial_normal_irradiance: ExtraterrestrialNormalIrradiance | None = ExtraterrestrialNormalIrradiance(),
    timestamps: DatetimeIndex | None = DatetimeIndex([Timestamp.now(tz='UTC')]),
    timezone: ZoneInfo | None = None,
    adjust_for_atmospheric_refraction: bool = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    # refracted_solar_zenith: (
    #     float | None
    # ) = UNREFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,  # radians
    solar_position_model: SolarPositionModel = SOLAR_POSITION_ALGORITHM_DEFAULT,
    # solar_time_model: SolarTimeModel = SOLAR_TIME_ALGORITHM_DEFAULT,
    solar_constant: float = SOLAR_CONSTANT,
    eccentricity_phase_offset: float = PERIGEE_OFFSET,
    eccentricity_amplitude: float = ECCENTRICITY_CORRECTION_FACTOR,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = 0,
    fingerprint: bool = False,
) -> ndarray | dict:
    """
    Calculate the normal extraterrestrial irradiance over a period of time

    Notes
    -----
    Symbol in ... `G0`

    """
    if extraterrestrial_normal_irradiance is None:
        extraterrestrial_normal_irradiance = (
            calculate_extraterrestrial_normal_irradiance_hofierka(
                timestamps=timestamps,
                solar_constant=solar_constant,
                eccentricity_phase_offset=eccentricity_phase_offset,
                eccentricity_amplitude=eccentricity_amplitude,
                dtype=dtype,
                array_backend=array_backend,
                verbose=verbose,
                log=log,
            )
        )
    solar_altitude_series = model_solar_altitude_series(
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        timezone=timezone,
        solar_position_model=solar_position_model,
        adjust_for_atmospheric_refraction=adjust_for_atmospheric_refraction,
        # unrefracted_solar_zenith=unrefracted_solar_zenith,
        # solar_time_model=solar_time_model,
        eccentricity_phase_offset=eccentricity_phase_offset,
        eccentricity_amplitude=eccentricity_amplitude,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,  # Is this wanted here ? i.e. not setting = 0 ?
        log=log,
    )
    extraterrestrial_horizontal_irradiance = calculate_extraterrestrial_horizontal_irradiance_series_hofierka(
    extraterrestrial_normal_irradiance=extraterrestrial_normal_irradiance,
    solar_altitude_series=solar_altitude_series,
)
    extraterrestrial_horizontal_irradiance.build_output(verbose, fingerprint)

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=extraterrestrial_horizontal_irradiance.value,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return extraterrestrial_horizontal_irradiance
