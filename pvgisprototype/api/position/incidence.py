"""
API modules to calculate the solar incidence angle between the direction of the
sun-to-surface vector and either the direction of the normal-to-surface vector
or the direction of the surface-plane vector.

Attention is required im handling the rotational solar azimuth and surface
orientation (also referred to as surface azimuth) anngles. The origin of
measuring azimuthal angles will obvisouly impact the direction of the
calculated angles. See also the API azimuth.py module.
"""

from pvgisprototype.algorithms.pvis.solar_incidence import calculate_solar_incidence_series_hofierka
from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.validation.functions import ModelSolarIncidenceTimeSeriesInputModel
from pvgisprototype import Longitude
from pvgisprototype import Latitude
from typing import Optional
from typing import List
from typing import Union
from zoneinfo import ZoneInfo
from pvgisprototype import SurfaceTilt
from pvgisprototype import SurfaceOrientation
from pvgisprototype.api.position.models import SolarTimeModel
from pvgisprototype.api.position.models import SolarIncidenceModel
from pvgisprototype import RefractedSolarZenith
from pvgisprototype.constants import DATA_TYPE_DEFAULT
from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT
from pvgisprototype.constants import RANDOM_DAY_SERIES_FLAG_DEFAULT
from pvgisprototype.constants import SURFACE_TILT_DEFAULT
from pvgisprototype.constants import SURFACE_ORIENTATION_DEFAULT
from pvgisprototype.constants import HORIZON_HEIGHT_UNIT
from pvgisprototype.constants import ATMOSPHERIC_REFRACTION_FLAG_DEFAULT
from pvgisprototype.constants import REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.constants import TIME_OUTPUT_UNITS_DEFAULT
from pvgisprototype.constants import ANGLE_OUTPUT_UNITS_DEFAULT
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import LOG_LEVEL_DEFAULT
from pvgisprototype.constants import COMPLEMENTARY_INCIDENCE_ANGLE_DEFAULT
from pvgisprototype.constants import NO_SOLAR_INCIDENCE
from pvgisprototype.constants import RADIANS
from pvgisprototype import SolarIncidence
from pvgisprototype.algorithms.jenco.solar_incidence import calculate_solar_incidence_series_jenco
from pvgisprototype.algorithms.iqbal.solar_incidence import calculate_solar_incidence_series_iqbal
import numpy as np
from pandas import DatetimeIndex
from pvgisprototype.api.position.conversions import convert_north_to_east_radians_convention
from pvgisprototype.api.position.conversions import convert_north_to_south_radians_convention


@validate_with_pydantic(ModelSolarIncidenceTimeSeriesInputModel)
def model_solar_incidence_series(
    longitude: Longitude,
    latitude: Latitude,
    timestamps: DatetimeIndex,
    timezone: Optional[ZoneInfo] = None,
    surface_orientation: SurfaceOrientation = SURFACE_ORIENTATION_DEFAULT,
    surface_tilt: SurfaceTilt = SURFACE_TILT_DEFAULT,
    apply_atmospheric_refraction: bool = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    solar_time_model: SolarTimeModel = SolarTimeModel.milne,
    solar_incidence_model: SolarIncidenceModel = SolarIncidenceModel.iqbal,
    complementary_incidence_angle: bool = COMPLEMENTARY_INCIDENCE_ANGLE_DEFAULT,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
) -> SolarIncidence:
    """
    """
    solar_incidence_series = None

    if solar_incidence_model.value == SolarIncidenceModel.jenco:

        # Update-Me ----------------------------------------------------------
        # Hofierka (2002) measures azimuth angles from East !
        # Convert the user-defined North-based surface orientation angle to East-based
        # surface_orientation_east_convention = SurfaceOrientation(
        #     value=convert_north_to_east_radians_convention(
        #         north_based_angle=surface_orientation
        #     ),
        #     unit=RADIANS,
        # )
        # # And apparently, defined the complementary surface tilt angle too!
        # from math import pi
        # surface_tilt = SurfaceTilt(
        #         value=(pi/2 - surface_tilt.radians),
        #         unit=RADIANS,
        #         )
        # ---------------------------------------------------------- Update-Me

        solar_incidence_series = calculate_solar_incidence_series_jenco(
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            timezone=timezone,
            surface_orientation=surface_orientation,
            # surface_orientation=surface_orientation_east_convention,
            surface_tilt=surface_tilt,
            apply_atmospheric_refraction=apply_atmospheric_refraction,
            # complementary_incidence_angle=complementary_incidence_angle,
            complementary_incidence_angle=complementary_incidence_angle,
            dtype=dtype,
            array_backend=array_backend,
            verbose=verbose,
            log=log,
        )

    if solar_incidence_model.value == SolarIncidenceModel.iqbal:

        # Iqbal (1983) measures azimuthal angles from South !
        surface_orientation_south_convention = SurfaceOrientation(
            value=convert_north_to_south_radians_convention(
                north_based_angle=surface_orientation
            ),
            unit=RADIANS,
        )
        solar_incidence_series = calculate_solar_incidence_series_iqbal(
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            timezone=timezone,
            surface_orientation=surface_orientation_south_convention,
            surface_tilt=surface_tilt,
            apply_atmospheric_refraction=apply_atmospheric_refraction,
            complementary_incidence_angle=complementary_incidence_angle,
            dtype=dtype,
            array_backend=array_backend,
            verbose=verbose,
            log=log,
        )

    if solar_incidence_model.value == SolarIncidenceModel.pvis:

        solar_incidence_series = calculate_solar_incidence_series_hofierka(
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            timezone=timezone,
            surface_orientation=surface_orientation,
            surface_tilt=surface_tilt,
            apply_atmospheric_refraction=apply_atmospheric_refraction,
            complementary_incidence_angle=complementary_incidence_angle,
            dtype=dtype,
            array_backend=array_backend,
            verbose=verbose,
            log=log,
        )

    return solar_incidence_series


def calculate_solar_incidence_series(
):
    pass
#     longitude: Longitude,
#     latitude: Latitude,
#     timestamp: datetime,
#     timezone: ZoneInfo = None,
#     random_time: bool = RANDOM_DAY_FLAG_DEFAULT,
#     surface_orientation: SurfaceOrientation = SURFACE_ORIENTATION_DEFAULT,
#     surface_tilt: SurfaceTilt = SURFACE_TILT_DEFAULT,
#     solar_incidence_models: List[SolarIncidenceModel] = [SolarIncidenceModel.iqbal],
#     complementary_incidence_angle: bool = COMPLEMENTARY_INCIDENCE_ANGLE_DEFAULT,
#     horizon_heights: List[float] = None,
#     horizon_interval: float = None,
#     solar_time_model: SolarTimeModel = SolarTimeModel.milne,
#     perigee_offset: float = PERIGEE_OFFSET,
#     eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
#     time_offset_global: float = TIME_OFFSET_GLOBAL_DEFAULT,
#     hour_offset: float = HOUR_OFFSET_DEFAULT,
#     angle_output_units: str = ANGLE_OUTPUT_UNITS_DEFAULT,
#     verbose: int = VERBOSE_LEVEL_DEFAULT,
# ) -> List:
#     """Calculates the solar Incidence angle for the selected models and returns the results in a table"""
#     results = []
#     for solar_incidence_model in solar_incidence_models:
#         if solar_incidence_model != SolarIncidenceModel.all:  # ignore 'all' in the enumeration
#             solar_incidence = model_solar_incidence(
#                 longitude=longitude,
#                 latitude=latitude,
#                 timestamp=timestamp,
#                 timezone=timezone,
#                 surface_orientation=surface_orientation,
#                 surface_tilt=surface_tilt,
#                 solar_time_model=solar_time_model,
#                 solar_incidence_model=solar_incidence_model,
#                 complementary_incidence_angle=complementary_incidence_angle,
#                 time_offset_global=time_offset_global,
#                 hour_offset=hour_offset,
#                 eccentricity_correction_factor=eccentricity_correction_factor,
#                 perigee_offset=perigee_offset,
#                 verbose=verbose,
#             )
#             results.append(
#                 {
#                     TIME_ALGORITHM_NAME: solar_time_model.value,
#                     POSITION_ALGORITHM_NAME: solar_incidence_model.value,
#                     INCIDENCE_NAME: getattr(solar_incidence, angle_output_units, None) if solar_incidence else None,
#                     'Sun-to-Plane': complementary_incidence_angle,
#                     UNITS_NAME: angle_output_units,
#                 }
#             )
#     return results
