from devtools import debug
from datetime import datetime
from zoneinfo import ZoneInfo
from math import sin
from math import cos
from math import acos
from math import isfinite
import numpy
from numpy.core import numeric
from pvgisprototype.algorithms.pvis.solar_declination import calculate_solar_declination_time_series_pvis
from pvgisprototype.algorithms.noaa.solar_hour_angle import calculate_solar_hour_angle_time_series_noaa
from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.validation.functions import CalculateSolarAzimuthPVISInputModel
from pvgisprototype import Longitude
from pvgisprototype import Latitude
from pvgisprototype.api.position.models import SolarTimeModel
from pvgisprototype import SolarAzimuth
from pvgisprototype.api.position.declination import calculate_solar_declination_pvis
from pvgisprototype.api.position.solar_time import model_solar_time
from pvgisprototype.algorithms.pvis.solar_hour_angle import calculate_solar_hour_angle_pvis
from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT, DATA_TYPE_DEFAULT, LOG_LEVEL_DEFAULT, RADIANS, VERBOSE_LEVEL_DEFAULT
from pandas import DatetimeIndex
from pvgisprototype.algorithms.noaa.solar_declination import calculate_solar_declination_time_series_noaa
from pvgisprototype.algorithms.noaa.solar_hour_angle import calculate_solar_hour_angle_time_series_noaa
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR


# def convert_east_to_north_radians_convention(azimuth_east_radians):
#     return (azimuth_east_radians + 3 * pi / 2) % (2 * pi)


@validate_with_pydantic(CalculateSolarAzimuthPVISInputModel)
def calculate_solar_azimuth_pvis(
    longitude: Longitude,
    latitude: Latitude,
    timestamp: datetime,
    timezone: ZoneInfo,
    solar_time_model: SolarTimeModel,
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
    According to Hofierka (2002) solar azimuth is measured from East!
    Conflicht with Jenvco 1992?
    """
    solar_declination = calculate_solar_declination_pvis(
        timestamp=timestamp,
    )
    C11 = sin(latitude.radians) * cos(solar_declination.radians)
    C13 = -cos(latitude.radians) * sin(solar_declination.radians)
    C22 = cos(solar_declination.radians)
    solar_time = model_solar_time(
        longitude=longitude,
        latitude=latitude,
        timestamp=timestamp,
        timezone=timezone,
        solar_time_model=solar_time_model,
    )
    hour_angle = calculate_solar_hour_angle_pvis(
        solar_time=solar_time,
    )
    cosine_solar_azimuth = (C11 * cos(hour_angle.radians) + C13) / pow(
        pow((C22 * sin(hour_angle.radians)), 2)
        + pow((C11 * cos(hour_angle.radians) + C13), 2),
        0.5,
    )
    solar_azimuth = acos(cosine_solar_azimuth)
    # -------------------------- convert east to north zero degrees convention
    # PVGIS' follows Hofierka (2002) who states : azimuth is measured from East
    # solar_azimuth = convert_east_to_north_radians_convention(solar_azimuth)
    # convert east to north zero degrees convention --------------------------
    solar_azimuth = SolarAzimuth(
        value=solar_azimuth,
        unit=RADIANS,
        position_algorithm='PVIS',
        timing_algorithm=solar_time_model.value,
    ) # zero_direction='East'
    if (
        not isfinite(solar_azimuth.degrees)
        or not solar_azimuth.min_degrees <= solar_azimuth.degrees <= solar_azimuth.max_degrees
    ):
        raise ValueError(
            f"The calculated solar azimuth angle {solar_azimuth.degrees} is out of the expected range\
            [{solar_azimuth.min_degrees}, {solar_azimuth.max_degrees}] degrees"
        )
    return solar_azimuth


def calculate_solar_azimuth_time_series_pvis(
    longitude: Longitude,   # radians
    latitude: Latitude,     # radians
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
    solar_declination_series = calculate_solar_declination_time_series_pvis(
        timestamps=timestamps,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,
        log=log,
    )
    C11 = sin(latitude.radians) * numpy.cos(solar_declination_series.radians)
    C13 = - cos(latitude.radians) * numpy.sin(solar_declination_series.radians)  # Attention to the - sign
    C22 = numpy.cos(solar_declination_series.radians)
    solar_hour_angle_series = calculate_solar_hour_angle_time_series_noaa(
        longitude=longitude,
        timestamps=timestamps,
        timezone=timezone,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,
        log=log,
    )
    x_solar_vector_component = - C22 * numpy.sin(solar_hour_angle_series.radians)
    y_solar_vector_component = C11 * numpy.cos(solar_hour_angle_series.radians) + C13

    # numerator = y_solar_vector_component
    denominator_a = numpy.power(x_solar_vector_component, 2)
    denominator_b = numpy.power(y_solar_vector_component, 2)
    event_hour_angle_inclined = numpy.power(denominator_a + denominator_b, 0.5)
    cosine_solar_azimuth_series = numpy.clip(y_solar_vector_component / event_hour_angle_inclined, -1, 1)
    solar_azimuth_series = numpy.arccos(cosine_solar_azimuth_series)
    solar_azimuth_series = numpy.where(
        - C22 * numpy.sin(solar_hour_angle_series.radians) < 0,
        numpy.pi / 2 - solar_azimuth_series,
        solar_azimuth_series
    )

    # from math import pi
    # solar_azimuth_series = numpy.where(
    #     solar_azimuth_series < pi / 2,
    #     pi / 2 - solar_azimuth_series,
    #     5 * pi / 2 - solar_azimuth_series
    # )
    # solar_azimuth_series = numpy.where(
    #     solar_azimuth_series >= 2 * pi,
    #     solar_azimuth_series - 2 * pi,
    #     solar_azimuth_series
    # )

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

    return SolarAzimuth(
        value=solar_azimuth_series,
        unit=RADIANS,
        position_algorithm='PVIS',
        timing_algorithm='PVIS',
        origin='East'
        # definition=incidence_angle_definition,
        # description=incidence_angle_description,
    ) # zero_direction='East'
