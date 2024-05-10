from pandas import DatetimeIndex
from devtools import debug
from numpy import number
import numpy
from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.validation.functions import CalculateSolarIncidencePVISInputModel
from pvgisprototype import SolarIncidence
from pvgisprototype import Longitude
from pvgisprototype import Latitude
from datetime import datetime
from zoneinfo import ZoneInfo
from pvgisprototype.api.position.models import SolarTimeModel
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.constants import RADIANS
from pvgisprototype.algorithms.pvis.solar_declination import calculate_solar_declination_pvis, calculate_solar_declination_time_series_pvis
from pvgisprototype.api.position.solar_time import model_solar_time
from pvgisprototype.algorithms.pvis.solar_hour_angle import calculate_solar_hour_angle_pvis, calculate_solar_hour_angle_time_series_pvis
from math import sin
from math import cos
from math import acos
from pvgisprototype import SurfaceTilt
from pvgisprototype import SurfaceOrientation
from pvgisprototype.constants import DATA_TYPE_DEFAULT
from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT
from pvgisprototype.constants import RANDOM_DAY_SERIES_FLAG_DEFAULT
from pvgisprototype.constants import SURFACE_TILT_DEFAULT
from pvgisprototype.constants import SURFACE_ORIENTATION_DEFAULT
from pvgisprototype.api.utilities.timestamp import now_utc_datetimezone
from pvgisprototype.constants import HASH_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.constants import DEBUG_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.constants import COMPLEMENTARY_INCIDENCE_ANGLE_DEFAULT
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import LOG_LEVEL_DEFAULT
from pvgisprototype.log import log_function_call
from pvgisprototype.log import log_data_fingerprint


@validate_with_pydantic(CalculateSolarIncidencePVISInputModel)
def calculate_solar_incidence_pvis(
    longitude: Longitude,
    latitude: Latitude,
    timestamp: datetime,
    timezone: ZoneInfo,
    solar_time_model: SolarTimeModel = SolarTimeModel.milne,
    surface_tilt: float = 0,
    surface_orientation: float = 180,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    log: int = 0,
) -> SolarIncidence:
    """Calculate the angle of incidence (θ) between the direction of the sun
    ray and the line normal to the surface measured in radian.

    θ =
    acos(
         sin(Φ)
         * (
           sin(δ) * cos(β) + cos(δ) * cos(γ) * cos(ω) * sin(β)
           )
         + cos(Φ) * (cos(δ) * cos(ω) * cos(β) - sin(δ) * cos(γ) * sin(β))
         + cos(δ)
         * sin(γ)
         * sin(ω)
         * sin(β)
        )

    Parameters
    ----------

    latitude: float
        Latitude is the angle (Φ) between the sun's rays and its projection on
        the horizontal surface measured in radian.

    surface_tilt: float 
        Surface tilt or slope is the angle (β) between the inclined slope and
        the horizontal plane measured in radian.

    surface_orientiation: float
        Surface orientation or azimuth is the angle (γ) in the horizontal plane
        between the line due south and the horizontal projection of the normal
        to the inclined plane surface measured in radian.

    Returns
    -------
    solar_incidence: float
        The angle of incidence (θ) is the angle between the direction of the
        sun ray and the line normal to the surface measured in radian.
    """
    solar_declination = calculate_solar_declination_pvis(
        timestamp=timestamp,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
    )
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
    solar_incidence = acos(
        sin(latitude.radians)
        * (
            sin(solar_declination.radians)
            * cos(surface_tilt.radians)
            + cos(solar_declination.radians)
            * cos(surface_orientation.radians)
            * cos(hour_angle.radians)
            * sin(surface_tilt.radians)
        )
        + cos(latitude.radians)
        * (
            cos(solar_declination.radians)
            * cos(hour_angle.radians)
            * cos(surface_tilt.radians)
            - sin(solar_declination.radians)
            * cos(surface_orientation.radians)
            * sin(surface_tilt.radians)
        )
        + cos(solar_declination.radians)
        * sin(surface_orientation.radians)
        * sin(hour_angle.radians)
        * sin(surface_tilt.radians)
    )

    return SolarIncidence(value=solar_incidence, unit=RADIANS)


@log_function_call
# @validate_with_pydantic(CalculateSolarIncidenceTimeSeriesPVISInputModel)
def calculate_solar_incidence_time_series_pvis(
    longitude: Longitude,
    latitude: Latitude,
    surface_orientation: SurfaceOrientation = SURFACE_ORIENTATION_DEFAULT,
    surface_tilt: SurfaceTilt = SURFACE_TILT_DEFAULT,
    timestamps: DatetimeIndex = str(now_utc_datetimezone()),
    timezone: ZoneInfo | None = None,
    solar_time_model: SolarTimeModel = SolarTimeModel.milne,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
) -> SolarIncidence:
    """Calculate the angle of incidence (θ) between the direction of the sun
    ray and the line normal to the surface measured in radian.

    θ =
    acos(
         sin(Φ)
         * (
           sin(δ) * cos(β) + cos(δ) * cos(γ) * cos(ω) * sin(β)
           )
         + cos(Φ) * (cos(δ) * cos(ω) * cos(β) - sin(δ) * cos(γ) * sin(β))
         + cos(δ)
         * sin(γ)
         * sin(ω)
         * sin(β)
        )

    Parameters
    ----------

    latitude: float
        Latitude is the angle (Φ) between the sun's rays and its projection on
        the horizontal surface measured in radian.

    surface_tilt: float 
        Surface tilt or slope is the angle (β) between the inclined slope and
        the horizontal plane measured in radian.

    surface_orientiation: float
        Surface orientation or azimuth is the angle (γ) in the horizontal plane
        between the line due south and the horizontal projection of the normal
        to the inclined plane surface measured in radian.

    Returns
    -------
    solar_incidence: float
        The angle of incidence (θ) is the angle between the direction of the
        sun ray and the line normal to the surface measured in radian.
    """
    solar_declination_series = calculate_solar_declination_time_series_pvis(
        timestamps=timestamps,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
    )
    solar_hour_angle_series = calculate_solar_hour_angle_time_series_pvis(
        longitude=longitude,
        timestamps=timestamps,
        timezone=timezone,
    )
    solar_incidence_series = numpy.arccos(
        sin(latitude.radians)
        * (
            numpy.sin(solar_declination_series.radians)
            * cos(surface_tilt.radians)
            + numpy.cos(solar_declination_series.radians)
            * cos(surface_orientation.radians)
            * numpy.cos(solar_hour_angle_series.radians)
            * sin(surface_tilt.radians)
        )
        + cos(latitude.radians)
        * (
            numpy.cos(solar_declination_series.radians)
            * numpy.cos(solar_hour_angle_series.radians)
            * cos(surface_tilt.radians)
            - numpy.sin(solar_declination.radians)
            * cos(surface_orientation.radians)
            * sin(surface_tilt.radians)
        )
        + numpy.cos(solar_declination_series.radians)
        * sin(surface_orientation.radians)
        * numpy.sin(solar_hour_angle_series.radians)
        * sin(surface_tilt.radians)
    )

    return SolarIncidence(
            value=solar_incidence_series,
            unit=RADIANS,
            origin="East"
    )
