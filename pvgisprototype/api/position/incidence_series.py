"""
API modules to calculate the solar incidence angle between the direction of the
sun-to-surface vector and either the direction of the normal-to-surface vector
or the direction of the surface-plane vector.

Attention is required im handling the rotational solar azimuth and surface
orientation (also referred to as surface azimuth) anngles. The origin of
measuring azimuthal angles will obvisouly impact the direction of the
calculated angles.

An overview of conventions and conversions from a North-based system to either
East- or South-based systems is:

             ┌─────────────┐  ┌────────────┐  ┌────────────┐
             │     N=0     │  │     N      │  │      N     │
             │      ▲      │  │     ▲      │  │      ▲     │
     Origin  │   W ◄┼► E   │  │  W ◄┼► E=0 │  │   W ◄┼► E  │
             │      ▼      │  │     ▼      │  │      ▼     │
             │      S      │  │     S      │  │      S=0   │
             └─────────────┘  └────────────┘  └────────────┘
             ┌─────────────┐  ┌────────────┐  ┌────────────┐
             │             │  │            │  │            │
             │             │  │            │  │            │
Input South  │     180     │  │     90     │  │     0      │
    (IS)     │             │  │            │  │            │
             │             │  │            │  │            │
             └─────────────┘  └────────────┘  └────────────┘
             ┌─────────────┐  ┌────────────┐  ┌────────────┐
             │             │  │            │  │            │
   Internal  │             │  │            │  │            │
             │      =      │  │  IS - 90   │  │  IS - 180  │
  Conversion │             │  │            │  │            │
             │             │  │            │  │            │
             └─────────────┘  └────────────┘  └────────────┘
"""

from pvgisprototype.algorithms.pvis.solar_incidence import calculate_solar_incidence_time_series_pvis
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
from pvgisprototype.algorithms.jenco.solar_incidence import calculate_solar_incidence_time_series_jenco
from pvgisprototype.algorithms.iqbal.solar_incidence import calculate_solar_incidence_time_series_iqbal
import numpy as np
from pandas import DatetimeIndex
from pvgisprototype.api.position.conversions import convert_north_to_east_radians_convention
from pvgisprototype.api.position.conversions import convert_north_to_south_radians_convention
from pvgisprototype.constants import ZERO_NEGATIVE_SOLAR_INCIDENCE_ANGLES_DEFAULT


@validate_with_pydantic(ModelSolarIncidenceTimeSeriesInputModel)
def model_solar_incidence_time_series(
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
    zero_negative_solar_incidence_angles: bool = ZERO_NEGATIVE_SOLAR_INCIDENCE_ANGLES_DEFAULT,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
) -> SolarIncidence:
    """
    """
    if solar_incidence_model.value == SolarIncidenceModel.jenco:

        # Hofierka (2002) measures azimuth angles from East !
        # Convert the user-defined North-based surface orientation angle to East-based
        surface_orientation_east_convention = SurfaceOrientation(
            value=convert_north_to_east_radians_convention(
                north_based_angle=surface_orientation
            ),
            unit=RADIANS,
        )
        # And apparently, defined the complementary surface tilt angle too!
        from math import pi
        surface_tilt = SurfaceTilt(
                value=(pi/2 - surface_tilt.radians),
                unit=RADIANS,
                )
        solar_incidence_series = calculate_solar_incidence_time_series_jenco(
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            timezone=timezone,
            surface_orientation=surface_orientation_east_convention,
            surface_tilt=surface_tilt,
            apply_atmospheric_refraction=apply_atmospheric_refraction,
            # complementary_incidence_angle=complementary_incidence_angle,
            complementary_incidence_angle=True,
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
        solar_incidence_series = calculate_solar_incidence_time_series_iqbal(
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            timezone=timezone,
            surface_orientation=surface_orientation_south_convention,
            surface_tilt=surface_tilt,
            apply_atmospheric_refraction=apply_atmospheric_refraction,
            complementary_incidence_angle=complementary_incidence_angle,
            zero_negative_solar_incidence_angles=zero_negative_solar_incidence_angles,
            dtype=dtype,
            array_backend=array_backend,
            verbose=verbose,
            log=log,
        )

    if solar_incidence_model.value == SolarIncidenceModel.pvis:

        solar_incidence_series = calculate_solar_incidence_time_series_pvis(
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
