from math import cos, sin
from zoneinfo import ZoneInfo

import numpy
from devtools import debug
from pandas import DatetimeIndex

from pvgisprototype import Latitude, Longitude, SolarAzimuth
from pvgisprototype.algorithms.pvis.solar_declination import (
    calculate_solar_declination_series_hofierka,
)
from pvgisprototype.algorithms.pvis.solar_hour_angle import (
    calculate_solar_hour_angle_series_hofierka,
)
from pvgisprototype.api.position.models import SolarPositionModel
from pvgisprototype.core.caching import custom_cached
from pvgisprototype.cli.messages import WARNING_NEGATIVE_VALUES
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    ECCENTRICITY_CORRECTION_FACTOR,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    LOG_LEVEL_DEFAULT,
    NO_SOLAR_INCIDENCE,
    PERIGEE_OFFSET,
    RADIANS,
    VERBOSE_LEVEL_DEFAULT,
)
from pvgisprototype.log import log_data_fingerprint, log_function_call, logger


@log_function_call
@custom_cached
# @validate_with_pydantic(CalculateSolarAzimuthPVISInputModel)
def calculate_solar_azimuth_series_hofierka(
    longitude: Longitude,  # radians
    latitude: Latitude,  # radians
    timestamps: DatetimeIndex,
    timezone: ZoneInfo,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
) -> SolarAzimuth:
    """Calculate the solar azimuth angle

    Returns
    -------
    solar_azimuth: float


    Returns
    -------
    solar_azimuth: float

    Notes
    -----
    According to Hofierka! solar azimuth is measured from East!
    Conflicht with Jenvco 1992?
    """
    solar_declination_series = calculate_solar_declination_series_hofierka(
        timestamps=timestamps,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,
        log=log,
    )
    # Idea for alternative solar time modelling, i.e. Milne 1921 -------------
    # solar_time = model_solar_time(
    #     longitude=longitude,
    #     latitude=latitude,
    #     timestamp=timestamp,
    #     timezone=timezone,
    #     solar_time_model=solar_time_model,  # returns datetime.time object
    #     perigee_offset=perigee_offset,
    #     eccentricity_correction_factor=eccentricity_correction_factor,
    # )
    # hour_angle = calculate_solar_hour_angle_pvis(
    #         solar_time=solar_time,
    # )
    # ------------------------------------------------------------------------
    solar_hour_angle_series = calculate_solar_hour_angle_series_hofierka(
        longitude=longitude,
        timestamps=timestamps,
        timezone=timezone,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,
        log=log,
    )
    C11 = sin(latitude.radians) * numpy.cos(solar_declination_series.radians)
    C13 = -cos(latitude.radians) * numpy.sin(
        solar_declination_series.radians
    )  # Attention to the - sign
    C22 = numpy.cos(solar_declination_series.radians)
    x_solar_vector_component = -C22 * numpy.sin(solar_hour_angle_series.radians)
    y_solar_vector_component = C11 * numpy.cos(solar_hour_angle_series.radians) + C13

    # numerator = y_solar_vector_component
    denominator_a = numpy.power(x_solar_vector_component, 2)
    denominator_b = numpy.power(y_solar_vector_component, 2)
    event_hour_angle_inclined = numpy.power(denominator_a + denominator_b, 0.5)

    # mask_positive_event_hour_angle_inclined = event_hour_angle_inclined > 1e-7
    mask_negative_event_hour_angle_inclined = event_hour_angle_inclined < 1e-7  # ?

    azimuth_origin = "East"
    cosine_solar_azimuth_series = numpy.clip(
        y_solar_vector_component / event_hour_angle_inclined, -1, 1
    )
    solar_azimuth_series = numpy.arccos(cosine_solar_azimuth_series)
    solar_azimuth_series = numpy.where(
        x_solar_vector_component < 0,
        numpy.pi * 2 - solar_azimuth_series,
        solar_azimuth_series,
    )
    solar_azimuth_series = numpy.where(
        mask_negative_event_hour_angle_inclined,
        NO_SOLAR_INCIDENCE,
        solar_azimuth_series,
    )

    from math import pi

    solar_azimuth_series = numpy.where(
        solar_azimuth_series < pi / 2,
        pi / 2 - solar_azimuth_series,
        5 * pi / 2 - solar_azimuth_series,
    )
    solar_azimuth_series = numpy.where(
        solar_azimuth_series >= 2 * pi,
        solar_azimuth_series - 2 * pi,
        solar_azimuth_series,
    )

    # -------------------------- convert east to north zero degrees convention
    # PVGIS' follows Hofierka (2002) who states : azimuth is measured from East
    # solar_azimuth_series = convert_east_to_north_radians_convention(solar_azimuth_series)
    # convert east to north zero degrees convention --------------------------
    # if (
    #     not isfinite(solar_azimuth.degrees)
    #     or not solar_azimuth.min_degrees <= solar_azimuth.degrees <= solar_azimuth.max_degrees
    # ):
    #     raise ValueError(
    #         f"The calculated solar azimuth angle {solar_azimuth.degrees} is out of the expected range\
    #         [{solar_azimuth.min_degrees}, {solar_azimuth.max_degrees}] degrees"
    #     )
    if (
        (solar_azimuth_series < SolarAzimuth().min_radians)
        | (solar_azimuth_series > SolarAzimuth().max_radians)
    ).any():
        out_of_range_values = solar_azimuth_series[
            (solar_azimuth_series < SolarAzimuth().min_radians)
            | (solar_azimuth_series > SolarAzimuth().max_radians)
        ]
        # raise ValueError(# ?
        logger.warning(
            f"{WARNING_NEGATIVE_VALUES} "
            f"[{SolarAzimuth().min_radians}, {SolarAzimuth().max_radians}] radians"
            f" in [code]solar_azimuth_series[/code] : {out_of_range_values}"
        )
    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=solar_azimuth_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return SolarAzimuth(
        value=solar_azimuth_series,
        unit=RADIANS,
        position_algorithm=SolarPositionModel.hofierka,
        timing_algorithm="PVIS",
        origin=azimuth_origin,
        # definition=incidence_angle_definition,
        # description=incidence_angle_description,
    )  # zero_direction='East'
